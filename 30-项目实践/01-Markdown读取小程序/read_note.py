"""第一阶段练习：读取一篇 Markdown，显示正文，并可另存为 JSON。"""

import argparse
import json
import sys
from pathlib import Path


def read_note(source):
    """读取 UTF-8 笔记，用第一个一级标题或文件名作为标题。"""
    if source.suffix.lower() != ".md":
        raise ValueError("输入文件应为 .md 格式。")

    content = source.read_text(encoding="utf-8-sig")
    title = source.stem
    for line in content.splitlines():
        if line.startswith("# ") and line[2:].strip():
            title = line[2:].strip()
            break

    return {
        "file_name": source.name,
        "title": title,
        "content": content,
        "character_count": len(content),
    }


def save_json(note, destination):
    """只创建新文件，避免覆盖已有笔记或输出。"""
    if destination.suffix.lower() != ".json":
        raise ValueError("输出文件应为 .json 格式。")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as output_file:
        json.dump(note, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent / "examples" / "示例笔记.md",
        help="要读取的 Markdown 文件，默认使用配套示例。",
    )
    parser.add_argument("--output", type=Path, help="可选：保存到一个新的 JSON 文件。")
    args = parser.parse_args()

    try:
        source = args.input.expanduser()
        destination = args.output.expanduser() if args.output else None
        if destination is not None and destination.resolve() == source.resolve():
            raise ValueError("输入和输出不能指向同一个文件。")
        note = read_note(source)
        if destination is not None:
            save_json(note, destination)
    except FileExistsError:
        print("输出文件已存在，请换一个新文件名。", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"读取或保存失败：{error}", file=sys.stderr)
        return 1

    print(f"文件：{note['file_name']}")
    print(f"字符数：{note['character_count']}")
    print("\n正文：")
    print(note["content"])
    if destination is not None:
        print(f"\n已保存 JSON：{destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
