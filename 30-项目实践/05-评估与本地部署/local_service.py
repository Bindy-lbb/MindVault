"""本机教学检索服务：固定监听 127.0.0.1，无模型 API、文件浏览或写入接口。"""

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import logging
from pathlib import Path
import sys
import time
from urllib.parse import parse_qs, urlsplit
import uuid


HERE = Path(__file__).resolve().parent
DEFAULT_CORPUS = HERE.parent / "03-RAG知识库问答" / "examples" / "notes"


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_rag():
    packaged = HERE / "rag_practice.py"
    path = packaged if packaged.is_file() else HERE.parent / "03-RAG知识库问答" / "rag_practice.py"
    return load_module("stage5_rag", path)


def read_config(path):
    path = path.resolve(strict=True)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or set(data) != {"corpus", "index", "log", "port", "chunk_lines", "overlap_lines"}:
        raise ValueError("配置字段应为 corpus/index/log/port/chunk_lines/overlap_lines。")
    for field in ("corpus", "index", "log"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError("配置路径必须是非空字符串。")
        data[field] = (path.parent / data[field]).resolve()
    if type(data["port"]) is not int or not 0 <= data["port"] <= 65535:
        raise ValueError("端口应为0–65535整数；0表示操作系统分配测试端口。")
    size, overlap = data["chunk_lines"], data["overlap_lines"]
    if type(size) is not int or type(overlap) is not int or not 1 <= size <= 100 or not 0 <= overlap < size:
        raise ValueError("切分与重叠参数不合法。")
    if data["index"].suffix.lower() != ".json" or data["log"].suffix.lower() != ".jsonl" or data["index"] == data["log"]:
        raise ValueError("索引用 .json，日志用独立的 .jsonl 文件。")
    return data


def check_index(rag, settings):
    index = rag.load_index(settings["index"])
    if index["backend"] != "keyword" or Path(index["corpus"]).resolve() != settings["corpus"]:
        raise ValueError("索引必须是当前资料的 keyword 索引。")
    if (index["chunk_lines"], index["overlap_lines"]) != (settings["chunk_lines"], settings["overlap_lines"]):
        raise ValueError("索引切分参数与配置不同，请另建新索引。")
    return index


def make_server(settings):
    rag = load_rag()
    check_index(rag, settings)
    settings["log"].parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("mindvault.local." + uuid.uuid4().hex)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(settings["log"], encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # 不记录原始 URL，避免把查询正文写入访问日志。

        def send_result(self, status, body):
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            started, request_id = time.perf_counter(), uuid.uuid4().hex
            route, status, hits_count = "unknown", 404, 0
            body = {"error": "not_found"}
            try:
                url = urlsplit(self.path)
                route = url.path if url.path in {"/health", "/ready", "/search"} else "unknown"
                if route == "/health":
                    status, body = 200, {"status": "ok", "mode": "local_keyword_extractive"}
                elif route in {"/ready", "/search"}:
                    index = check_index(rag, settings)
                    if route == "/ready":
                        status, body = 200, {"status": "ready", "documents": len(index["manifest"]), "chunks": len(index["chunks"])}
                    else:
                        if len(url.query) > 6000:
                            raise ValueError("查询过长。")
                        params = parse_qs(url.query, keep_blank_values=True, max_num_fields=3)
                        if set(params) - {"q", "k"} or "q" not in params or any(len(v) != 1 for v in params.values()):
                            raise ValueError("仅接受单个 q 与可选 k。")
                        question = params["q"][0]
                        if not 1 <= len(question.strip()) <= 300:
                            raise ValueError("q 应为1至300字符。")
                        k = int(params.get("k", ["3"])[0])
                        if not 1 <= k <= 3:
                            raise ValueError("k 应为1至3。")
                        hits = rag.retrieve(index, question, k, 0)
                        hits_count = len(hits)
                        status, body = 200, {"mode": "keyword_extractive", "hits": hits, "model_api_requests": 0}
            except (OSError, ValueError, KeyError, TypeError):
                try:
                    check_index(rag, settings)
                    status, body = 400, {"error": "invalid_query"}
                except (OSError, ValueError, KeyError, TypeError):
                    status, body = 503, {"error": "index_unavailable", "hint": "核对资料与配置，用新索引名重建后重新启动。"}
            body["request_id"] = request_id
            try:
                self.send_result(status, body)
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                event = {"time_utc": datetime.now(timezone.utc).isoformat(), "request_id": request_id,
                         "route": route, "status": status, "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                         "hits_count": hits_count}
                logger.info(json.dumps(event, ensure_ascii=False))

    try:
        server = ThreadingHTTPServer(("127.0.0.1", settings["port"]), Handler)
    except OSError:
        handler.close()
        logger.removeHandler(handler)
        raise
    server.event_logger, server.event_handler = logger, handler
    return server


def close_server(server):
    server.server_close()
    server.event_handler.close()
    server.event_logger.removeHandler(server.event_handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["index", "serve"])
    parser.add_argument("--config", type=Path, default=HERE / "service.example.json")
    parser.add_argument("--port", type=int, help="仅 serve：临时覆盖端口，不修改配置文件或发布清单。")
    args = parser.parse_args()
    try:
        settings = read_config(args.config)
        if args.port is not None:
            if args.command != "serve" or not 0 <= args.port <= 65535:
                raise ValueError("--port 仅用于 serve，范围0–65535。")
            settings["port"] = args.port
        if args.command == "index":
            if settings["index"].exists():
                raise ValueError("索引已存在；需要更新时在新配置中使用新索引名。")
            rag = load_rag()
            index = rag.build_index(settings["corpus"], "keyword", settings["chunk_lines"], settings["overlap_lines"])
            rag.write_new(settings["index"], dump(index))
            print("已建立索引：" + str(settings["index"]))
            return 0
        server = make_server(settings)
        print(f"本机教学服务：http://127.0.0.1:{server.server_port}/health （Ctrl+C 停止）", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("已停止服务。")
        finally:
            close_server(server)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"启动失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
