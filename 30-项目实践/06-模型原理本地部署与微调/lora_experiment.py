"""选修真实模型 LoRA：plan 默认只检查数据；train/evaluate 才加载权重与依赖。"""

import argparse
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import time

from data_tools import HERE, MODEL, REVISION, encode_example, read_data, sha, verify_run


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_runtime(device, seed):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import peft
    except ImportError:
        raise ValueError("真实训练需要独立环境中的 torch、transformers、peft；先阅读实践四。") from None
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("未发现可用 CUDA，未加载或下载模型；请核对环境或选择 CPU。")
    torch.manual_seed(seed)
    if device == "cuda":
        torch.cuda.manual_seed_all(seed)
    else:
        torch.set_num_threads(min(4, torch.get_num_threads()))
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, torch_dtype=torch.float32,
                                              trust_remote_code=False, use_safetensors=True).to(device)
    versions = {name: importlib.metadata.version(name) for name in ("torch", "transformers", "peft")}
    return torch, peft, tokenizer, model, versions


def tensors(torch, encoded, device):
    ids = torch.tensor([encoded["input_ids"]], dtype=torch.long, device=device)
    labels = torch.tensor([encoded["labels"]], dtype=torch.long, device=device)
    return {"input_ids": ids, "attention_mask": torch.ones_like(ids), "labels": labels}


def mean_loss(torch, model, encoded_rows, device):
    model.eval()
    values = []
    with torch.no_grad():
        for encoded in encoded_rows:
            value = float(model(**tensors(torch, encoded, device)).loss.item())
            if not math.isfinite(value):
                raise ValueError("损失不是有限数值，请检查样本和数值设置。")
            values.append(value)
    return sum(values) / len(values)


def generate(torch, model, tokenizer, encoded, device):
    ids = torch.tensor([encoded["prompt_ids"]], dtype=torch.long, device=device)
    model.eval()
    with torch.no_grad():
        output = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), do_sample=False,
                                max_new_tokens=96, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(output[0, ids.shape[1]:], skip_special_tokens=True)


def execute(args, data, data_info):
    # 先确认输出可创建；仅显式 train/evaluate 会进入第三方依赖与模型下载分支。
    previous = None
    if args.mode == "evaluate":
        if not args.run_dir:
            raise ValueError("evaluate 需要已完成训练的 --run-dir。")
        previous = verify_run(args.run_dir, data_info["sha256"])
        if not (args.run_dir / "adapter/adapter_model.safetensors").is_file():
            raise ValueError("需要本项目保存的 safetensors 适配器。")
        if previous.get("max_length") != args.max_length:
            raise ValueError("请使用训练记录相同的 --max-length。")
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    torch, peft, tokenizer, model, versions = load_runtime(args.device, args.seed)
    if previous and previous.get("dependencies") != versions:
        raise ValueError("依赖版本与训练记录不一致，请先复现原环境后再比较。")
    if args.mode == "train":
        train_rows = [encode_example(tokenizer, row, args.max_length) for row in data["train"]]
        validation_rows = [encode_example(tokenizer, row, args.max_length) for row in data["validation"]]
        baseline_loss = mean_loss(torch, model, validation_rows, args.device)
        config = peft.LoraConfig(task_type="CAUSAL_LM", r=4, lora_alpha=8, lora_dropout=0.05,
                                 target_modules=["q_proj", "v_proj"], bias="none")
        model = peft.get_peft_model(model, config)
        trainable = [(name, param) for name, param in model.named_parameters() if param.requires_grad]
        if not trainable or any("lora_" not in name for name, _ in trainable):
            raise ValueError("可训练参数不符合预期，仅允许 LoRA 参数更新。")
        optimizer = torch.optim.AdamW([param for _, param in trainable], lr=args.learning_rate)
        model.config.use_cache = False
        losses = []
        model.train()
        for step in range(args.steps):
            encoded = train_rows[step % len(train_rows)]
            optimizer.zero_grad(set_to_none=True)
            loss = model(**tensors(torch, encoded, args.device)).loss
            if not math.isfinite(float(loss.item())):
                raise ValueError("训练损失异常，保留目录并检查设置；本脚本不自动续训。")
            loss.backward()
            torch.nn.utils.clip_grad_norm_([param for _, param in trainable], 1.0)
            optimizer.step()
            losses.append({"step": step + 1, "loss": float(loss.item())})
        adapted_loss = mean_loss(torch, model, validation_rows, args.device)
        model.save_pretrained(args.output / "adapter", safe_serialization=True)
        tokenizer.save_pretrained(args.output / "tokenizer")
        artifact_hashes = {p.relative_to(args.output).as_posix(): sha(p) for p in args.output.rglob("*") if p.is_file()}
        result = {"mode": "real_lora_train", "base_model": MODEL, "revision": REVISION,
                  "data_sha256": data_info["sha256"], "data_counts": data_info["counts"], "python": sys.version.split()[0],
                  "dependencies": versions, "device": args.device, "precision": "float32", "quantization": None,
                  "seed": args.seed, "steps": args.steps, "batch_size": 1, "learning_rate": args.learning_rate,
                  "max_length": args.max_length, "rank": 4, "alpha": 8,
                  "trainable_parameters": sum(param.numel() for _, param in trainable),
                  "validation_mean_example_answer_loss": {"base": baseline_loss, "adapted": adapted_loss},
                  "test_model_evaluation": "not_run", "train_history": losses, "artifact_sha256": artifact_hashes,
                  "wall_seconds": round(time.perf_counter() - started, 3)}
        write_json(args.output / "run.json", result)
    else:
        test_rows = [encode_example(tokenizer, row, args.max_length) for row in data["test"]]
        baseline_loss = mean_loss(torch, model, test_rows, args.device)
        baseline_text = [generate(torch, model, tokenizer, row, args.device) for row in test_rows]
        model = peft.PeftModel.from_pretrained(model, args.run_dir / "adapter", is_trainable=False)
        adapted_loss = mean_loss(torch, model, test_rows, args.device)
        adapted_text = [generate(torch, model, tokenizer, row, args.device) for row in test_rows]
        rows = [{"id": item["id"], "question": item["messages"][0]["content"],
                 "reference": item["messages"][1]["content"], "base_answer": before, "adapted_answer": after,
                 "manual_score": None} for item, before, after in zip(data["test"], baseline_text, adapted_text)]
        result = {"mode": "real_lora_test_comparison", "base_model": MODEL, "revision": REVISION,
                  "data_sha256": data_info["sha256"], "device": args.device, "seed": args.seed, "dependencies": versions,
                  "decoding": {"do_sample": False, "max_new_tokens": 96},
                  "mean_example_answer_loss": {"base": baseline_loss, "adapted": adapted_loss}, "rows": rows,
                  "training_steps": previous["steps"], "wall_seconds": round(time.perf_counter() - started, 3),
                  "scope": "同题比较；loss不是事实正确率，人工评分待填"}
        write_json(args.output / "comparison.json", result)
    print("已保存真实模型实验：" + str(args.output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["plan", "train", "evaluate"], default="plan")
    parser.add_argument("--data-dir", type=Path, default=HERE / "data")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if not 1 <= args.steps <= 200 or not math.isfinite(args.learning_rate) or not 1e-6 <= args.learning_rate <= 1e-2 or not 64 <= args.max_length <= 1024 or not 0 <= args.seed < 2 ** 32:
            raise ValueError("检查步数1–200、学习率1e-6–1e-2、长度64–1024与seed。")
        if args.output and args.output.exists():
            raise ValueError("输出目录已存在，请用新目录。")
        data, info = read_data(args.data_dir)
        if args.mode == "plan":
            plan = {"mode": "plan_only", "base_model": MODEL, "revision": REVISION, "data": info,
                    "training": {"device": args.device, "dtype": "float32", "steps": args.steps, "learning_rate": args.learning_rate,
                                 "max_length": args.max_length, "rank": 4, "alpha": 8},
                    "model_loaded": False, "training_executed": False, "test_model_evaluation": "not_run"}
            if args.output:
                args.output.mkdir(parents=True, exist_ok=False)
                write_json(args.output / "plan.json", plan)
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            if not args.output:
                raise ValueError("train/evaluate 需要新的 --output 目录。")
            execute(args, data, info)
        return 0
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print("微调实验失败：" + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
