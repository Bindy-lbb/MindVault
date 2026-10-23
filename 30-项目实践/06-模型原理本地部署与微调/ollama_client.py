"""只连接固定回环地址，默认预览；live 需提前安装 Ollama 与指定本地模型。"""

import argparse
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


BASE = "http://127.0.0.1:11434"
MODEL = "qwen2.5:0.5b"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def payload(question):
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 1000:
        raise ValueError("问题应为1–1000字符。")
    return {"model": MODEL, "messages": [{"role": "user", "content": question}], "stream": False,
            "options": {"temperature": 0, "seed": 42, "num_ctx": 1024, "num_predict": 128}}


def request_json(path, body, timeout):
    raw = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = Request(BASE + path, data=raw, headers={"Content-Type": "application/json"}, method="GET" if body is None else "POST")
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        code = exc.code
        exc.close()
        raise ValueError(f"Ollama HTTP {code}，请检查服务、模型与日志；没有自动重试。") from None
    except (URLError, TimeoutError):
        raise ValueError("无法连接本机 Ollama 或等待超时；请先确认服务已启动。") from None


def validate_response(response):
    if not isinstance(response, dict) or response.get("done") is not True or response.get("model") != MODEL:
        raise ValueError("模型响应未完成或模型名不符合教学请求。")
    message = response.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant" or not isinstance(message.get("content"), str) or not message["content"].strip():
        raise ValueError("缺少有效 assistant 内容。")
    for field in ("load_duration", "prompt_eval_count", "eval_count", "eval_duration"):
        value = response.get(field)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("模型计数与纳秒耗时必须是非负整数或缺省。")
    count, duration = response.get("eval_count"), response.get("eval_duration")
    speed = count * 1_000_000_000 / duration if type(count) is int and count >= 0 and type(duration) is int and duration > 0 else None
    return {"answer": message["content"], "done_reason": response.get("done_reason"),
            "load_duration_ns": response.get("load_duration"), "prompt_eval_count": response.get("prompt_eval_count"),
            "eval_count": count, "eval_duration_ns": duration, "tokens_per_second": speed}


def live(body, timeout):
    tags = request_json("/api/tags", None, timeout)
    if not isinstance(tags, dict) or not isinstance(tags.get("models"), list):
        raise ValueError("模型清单格式无效。")
    selected = next((m for m in tags["models"] if isinstance(m, dict) and m.get("name") == MODEL), None)
    if selected is None:
        raise ValueError("未找到 qwen2.5:0.5b；请自行确认硬件并提前拉取，客户端不会下载。")
    if selected.get("remote_host") or selected.get("remote_model"):
        raise ValueError("检测到远程模型信息，本练习只使用明确的本地模型。")
    return request_json("/api/chat", body, timeout), selected.get("digest")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["preview", "fixture", "live"], default="preview")
    parser.add_argument("--question", default="请用一句话解释什么是大模型。")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--output", type=Path, help="fixture/live 的新结果目录。")
    args = parser.parse_args()
    try:
        if not 1 <= args.timeout <= 120:
            raise ValueError("等待时间应为1–120秒。")
        body = payload(args.question)
        if args.mode == "preview":
            if args.output:
                raise ValueError("preview 在终端显示，请省略 --output。")
            print(json.dumps({"mode": "preview", "preflight": BASE + "/api/tags", "endpoint": BASE + "/api/chat", "body": body}, ensure_ascii=False, indent=2))
            return 0
        if not args.output or args.output.exists():
            raise ValueError("请提供一个新的 --output 目录。")
        if args.mode == "fixture" and args.question != parser.get_default("question"):
            raise ValueError("固定响应只配套默认问题；其他问题可先 preview，再按需 live。")
        started, digest = time.perf_counter(), None
        if args.mode == "live":
            response, digest = live(body, args.timeout)
        else:
            response = {"model": MODEL, "done": True, "done_reason": "fixture", "message": {
                "role": "assistant", "content": "固定教学响应：大模型可以根据输入生成文字；这里没有运行模型。"}}
        result = validate_response(response)
        result.update(execution_mode=args.mode, model=MODEL, local_model_digest=digest,
                      wall_ms=round((time.perf_counter() - started) * 1000, 3))
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("已保存 " + args.mode + " 结果：" + str(args.output))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("调用失败：" + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
