"""标准库检查：自写对话数据、分组隔离、版本摘要；不下载模型。"""

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"
SPLITS = ("train", "validation", "test")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_data(folder):
    result, ids, prompts, hashes = {}, set(), set(), {}
    for split in SPLITS:
        path = folder / (split + ".jsonl")
        if path.stat().st_size > 2_000_000:
            raise ValueError("每组教学文件限2MB。")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not 1 <= len(rows) <= 200:
            raise ValueError("每组需1–200条示例。")
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"id", "messages"} or not isinstance(row["id"], str) or not row["id"].strip() or row["id"] in ids:
                raise ValueError("数据需要唯一 id 和 messages。")
            ids.add(row["id"])
            messages = row["messages"]
            if not isinstance(messages, list) or len(messages) != 2:
                raise ValueError("教学对话固定为一条 user 与一条 assistant。")
            for message, role in zip(messages, ("user", "assistant")):
                if not isinstance(message, dict) or set(message) != {"role", "content"} or message["role"] != role or not isinstance(message["content"], str) or not 1 <= len(message["content"].strip()) <= 6000:
                    raise ValueError("对话角色或正文不符合约定。")
            prompt = re.sub(r"\s+", "", messages[0]["content"]).casefold()
            if prompt in prompts:
                raise ValueError("发现完全重复/空白归一化后重复的问题；人工检查分组泄漏。")
            prompts.add(prompt)
        result[split], hashes[split] = rows, sha(path)
    return result, {"counts": {key: len(value) for key, value in result.items()}, "sha256": hashes,
                    "scope": "格式与完全重复检查，不代替语义泄漏、版权和事实人工核对"}


def encode_example(tokenizer, row, max_length):
    messages = row["messages"]
    prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=True, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
    if not isinstance(prompt, list) or not isinstance(full, list) or not prompt or full[:len(prompt)] != prompt or len(full) <= len(prompt):
        raise ValueError("聊天模板前缀不兼容或没有回答 Token，请先检查模板。")
    if len(full) > max_length:
        raise ValueError("示例超过 max_length；本项目不静默截断回答，请缩短样本或检查资源后调整。")
    return {"input_ids": full, "labels": [-100] * len(prompt) + full[len(prompt):], "prompt_ids": prompt}


def verify_run(folder, expected_hashes):
    metadata = json.loads((folder / "run.json").read_text(encoding="utf-8-sig"))
    if not isinstance(metadata, dict) or metadata.get("base_model") != MODEL or metadata.get("revision") != REVISION:
        raise ValueError("运行记录的基座或 revision 不兼容。")
    if metadata.get("data_sha256") != expected_hashes:
        raise ValueError("数据版本变化，不能直接作为本次同题评估。")
    if not isinstance(metadata.get("artifact_sha256"), dict) or not metadata["artifact_sha256"]:
        raise ValueError("缺少适配器文件摘要。")
    for relative, digest in metadata["artifact_sha256"].items():
        path = (folder / relative).resolve()
        if not path.is_relative_to(folder.resolve()) or not path.is_file() or sha(path) != digest:
            raise ValueError("适配器或 Tokenizer 文件缺失、越界或已改变。")
    return metadata
