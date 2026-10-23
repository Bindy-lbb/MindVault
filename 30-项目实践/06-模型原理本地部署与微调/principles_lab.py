"""标准库数值实验：矩阵、单头因果注意力、交叉熵的一步更新；不是完整 LLM。"""

import argparse
import json
import math
from pathlib import Path
import sys


def finite_vector(values):
    if not isinstance(values, list) or not values or not all(type(v) in (int, float) and math.isfinite(v) for v in values):
        raise ValueError("需要非空有限数值列表。")


def matrix_shape(matrix):
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("矩阵不能为空。")
    for row in matrix:
        finite_vector(row)
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("矩阵各行长度应相同。")
    return len(matrix), len(matrix[0])


def matmul(left, right):
    rows, width = matrix_shape(left)
    height, cols = matrix_shape(right)
    if width != height:
        raise ValueError("矩阵乘法内维不匹配。")
    return [[sum(left[i][k] * right[k][j] for k in range(width)) for j in range(cols)] for i in range(rows)]


def softmax(logits):
    finite_vector(logits)
    weights = [math.exp(v - max(logits)) for v in logits]
    return [v / sum(weights) for v in weights]


def cross_entropy(logits, target):
    finite_vector(logits)
    if type(target) is not int or not 0 <= target < len(logits):
        raise ValueError("目标下标不合法。")
    maximum = max(logits)
    return maximum + math.log(sum(math.exp(v - maximum) for v in logits)) - logits[target]


def causal_attention(queries, keys, values):
    n, width = matrix_shape(queries)
    if matrix_shape(keys) != (n, width) or matrix_shape(values)[0] != n:
        raise ValueError("Q/K/V 形状不匹配。")
    weights = []
    for i, q in enumerate(queries):
        scores = [sum(a * b for a, b in zip(q, keys[j])) / math.sqrt(width) for j in range(i + 1)]
        weights.append(softmax(scores) + [0.0] * (n - i - 1))
    return {"weights": weights, "output": matmul(weights, values)}


def experiment(lr=0.2):
    if not math.isfinite(lr) or not 0 < lr <= 2:
        raise ValueError("教学学习率应在0与2之间。")
    q = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    logits, target = [2.0, 0.0, -1.0], 1
    probabilities = softmax(logits)
    gradient = [p - int(i == target) for i, p in enumerate(probabilities)]
    updated = [v - lr * g for v, g in zip(logits, gradient)]
    return {"scope": "自写小矩阵与可调 logits，无模型权重、无真实 Tokenizer", "attention": causal_attention(q, q, q),
            "prediction": {"logits_before": logits, "target_index": target, "probabilities": probabilities,
                           "gradient": gradient, "learning_rate": lr, "logits_after": updated,
                           "loss_before": cross_entropy(logits, target), "loss_after": cross_entropy(updated, target)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = json.dumps(experiment(args.learning_rate), ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as file:
                file.write(result + "\n")
        else:
            print(result)
        return 0
    except (OSError, ValueError, OverflowError) as exc:
        print("实验失败：" + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
