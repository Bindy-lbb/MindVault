"""真正优化小矩阵的低秩更新；它不是语言模型微调，产物不兼容 PEFT/Ollama。"""

import argparse
import json
import math
from pathlib import Path
import random
import sys

from principles_lab import finite_vector


TRAIN_X = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 1.0]]
VALID_X = [[2.0, -1.0], [-1.0, -1.0]]


def target(x):
    return [2 * x[0] + 2 * x[1], 2 * x[0] + 5 * x[1]]


def predict(x, a, b):
    t = sum(v * w for v, w in zip(a, x))
    return [x[i] + b[i] * t for i in range(2)]


def loss_and_grad(a, b, inputs):
    loss, ga, gb = 0.0, [0.0, 0.0], [0.0, 0.0]
    for x in inputs:
        y, expected = predict(x, a, b), target(x)
        t = sum(v * w for v, w in zip(a, x))
        for i in range(2):
            diff = y[i] - expected[i]
            loss += diff * diff / (2 * len(inputs))
            factor = diff / len(inputs)
            gb[i] += factor * t
            for j in range(2):
                ga[j] += factor * b[i] * x[j]
    return loss, ga, gb


def train(steps=400, lr=0.03, seed=42):
    if type(steps) is not int or not 1 <= steps <= 5000 or not math.isfinite(lr) or not 0 < lr <= 0.1:
        raise ValueError("步数限1–5000，学习率限0–0.1。")
    rng = random.Random(seed)
    a, b = [rng.uniform(-0.1, 0.1) for _ in range(2)], [0.0, 0.0]
    before = {"train_mse": loss_and_grad(a, b, TRAIN_X)[0], "validation_mse": loss_and_grad(a, b, VALID_X)[0]}
    history = []
    for step in range(steps):
        loss, ga, gb = loss_and_grad(a, b, TRAIN_X)
        if not math.isfinite(loss):
            raise ValueError("数值发散，请减小学习率。")
        a = [v - lr * g for v, g in zip(a, ga)]
        b = [v - lr * g for v, g in zip(b, gb)]
        if step == 0 or (step + 1) % 50 == 0 or step + 1 == steps:
            history.append({"step": step + 1, "train_mse": loss_and_grad(a, b, TRAIN_X)[0]})
    finite_vector(a); finite_vector(b)
    adapter = {"format": "toy-linear-lora-v1", "base_id": "identity2-v1", "rank": 1, "alpha": 1,
               "A": a, "B": b, "base_weights": [[1, 0], [0, 1]]}
    report = {"scope": "小矩阵真实梯度训练，不是 LLM", "seed": seed, "steps": steps, "learning_rate": lr,
              "base_frozen": True, "train_examples": len(TRAIN_X), "validation_examples": len(VALID_X),
              "before": before, "after": {"train_mse": loss_and_grad(a, b, TRAIN_X)[0],
              "validation_mse": loss_and_grad(a, b, VALID_X)[0]}, "history": history}
    return adapter, report


def load_adapter(path):
    item = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(item, dict) or set(item) != {"format", "base_id", "rank", "alpha", "A", "B", "base_weights"}:
        raise ValueError("不是本库玩具适配器格式。")
    if item["format"] != "toy-linear-lora-v1" or item["base_id"] != "identity2-v1" or item["base_weights"] != [[1, 0], [0, 1]] or item["rank"] != 1 or item["alpha"] != 1:
        raise ValueError("玩具基座或 rank/alpha 不兼容。")
    for key in ("A", "B"):
        finite_vector(item[key])
        if len(item[key]) != 2:
            raise ValueError("玩具 A/B 长度必须为2。")
    return item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["train", "infer"])
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--x", nargs=2, type=float, default=[2.0, 1.0])
    args = parser.parse_args()
    try:
        if args.command == "train":
            if not args.output or args.output.exists():
                raise ValueError("训练请提供新的 --output 目录。")
            adapter, report = train(args.steps, args.learning_rate, args.seed)
            args.output.mkdir(parents=True, exist_ok=False)
            for name, item in [("adapter.json", adapter), ("report.json", report)]:
                (args.output / name).write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report["after"], ensure_ascii=False, indent=2))
        else:
            if not args.adapter:
                raise ValueError("infer 请提供 --adapter。")
            finite_vector(args.x)
            item = load_adapter(args.adapter)
            print(json.dumps({"base_output": args.x, "adapted_output": predict(args.x, item["A"], item["B"]),
                              "toy_target": target(args.x)}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, OverflowError) as exc:
        print("玩具实验失败：" + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
