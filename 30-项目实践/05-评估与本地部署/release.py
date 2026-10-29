"""创建或核对本地教学发布目录；不上传文件、不创建云资源或 GitHub Release。"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from local_service import DEFAULT_CORPUS, HERE, dump, load_rag


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(output, version, corpus):
    if output.exists():
        raise ValueError("发布目录已存在，请换一个新目录。")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("教学版本号使用例如 0.1.0 的三段数字。")
    rag = load_rag()
    docs = rag.read_corpus(corpus)
    output.mkdir(parents=True, exist_ok=False)
    for name, source in [("local_service.py", HERE / "local_service.py"), ("rag_practice.py", Path(rag.__file__))]:
        (output / name).write_bytes(source.read_bytes())
    for relative, doc in docs.items():
        target = output / "notes" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = (corpus.resolve() / relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != doc["sha256"]:
            raise ValueError("复制期间资料发生变化，停止打包；请检查后换新目录重试。")
        target.write_bytes(raw)
    config = {"corpus": "notes", "index": ".local/index-v1.json", "log": ".local/events.jsonl",
              "port": 8765, "chunk_lines": 8, "overlap_lines": 2}
    (output / "service.json").write_text(dump(config) + "\n", encoding="utf-8")
    instructions = ("# 本地教学发布包\n\n版本：" + version + "\n\n"
                    "在发布目录终端运行，或给 --config 传完整路径：\n\n"
                    "```powershell\npython -B local_service.py index --config service.json\n"
                    "python -B local_service.py serve --config service.json\n```\n\n"
                    "用另一个终端检查 http://127.0.0.1:8765/ready 。Ctrl+C 停止。\n\n"
                    "只提供本机关键词检索，不调用模型。先把发布包放到最终位置再建索引；不要复制旧索引。\n"
                    "保留 -B 选项，避免 __pycache__ 造成清单外文件；运行数据只放 .local/。\n"
                    "重启可复用当前索引。资料变化时另建新版本与索引，保留旧版本用于恢复。\n"
                    "当前仅为本机学习服务，没有认证、HTTPS或生产进程管理。\n")
    (output / "START.md").write_text(instructions, encoding="utf-8")
    files = {p.relative_to(output).as_posix(): sha(p) for p in sorted(output.rglob("*")) if p.is_file()}
    record = {"schema_version": 1, "version": version, "built_at_utc": datetime.now(timezone.utc).isoformat(),
              "build_python": sys.version.split()[0], "scope": "本地教学目录；清单不是数字签名", "files": files}
    (output / "RELEASE.json").write_text(dump(record) + "\n", encoding="utf-8")
    return record


def verify(folder):
    folder = folder.resolve(strict=True)
    record = json.loads((folder / "RELEASE.json").read_text(encoding="utf-8-sig"))
    if not isinstance(record, dict) or record.get("schema_version") != 1 or not isinstance(record.get("files"), dict) or not record["files"]:
        raise ValueError("发布清单格式不正确。")
    for relative, digest in record["files"].items():
        path = Path(relative)
        target = (folder / path).resolve()
        if path.is_absolute() or ".." in path.parts or not target.is_relative_to(folder) or not target.is_file() or sha(target) != digest:
            raise ValueError("发布文件缺失、范围错误或摘要不符：" + relative)
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and ".local" not in p.relative_to(folder).parts}
    if actual != set(record["files"]) | {"RELEASE.json"}:
        raise ValueError("发布目录出现清单以外的文件。运行数据只允许放在 .local/。")
    return {"verified": True, "version": record["version"], "files": len(record["files"]), "scope": "文件完整性，非代码安全认证"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["package", "verify"])
    parser.add_argument("--output", type=Path, help="package 的新目录，或 verify 的现有发布目录。")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    args = parser.parse_args()
    try:
        if not args.output:
            raise ValueError("请提供 --output 发布目录。")
        result = package(args.output, args.version, args.corpus) if args.command == "package" else verify(args.output)
        print(dump({"output": str(args.output), "version": result["version"], "files": len(result["files"]) if isinstance(result["files"], dict) else result["files"],
                    "verified": result.get("verified")}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"发布检查失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
