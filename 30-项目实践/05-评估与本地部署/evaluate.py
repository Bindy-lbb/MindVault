"""离线评估与同代码参数对比：不请求生成模型，不自动评价答案含义。"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time

from local_service import DEFAULT_CORPUS, HERE, dump, load_module, load_rag


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases(path, docs, split):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise ValueError("题集应为非空数组。")
    seen, selected = set(), []
    for case in data:
        if not isinstance(case, dict) or set(case) != {"id", "split", "question", "expected"}:
            raise ValueError("题目字段应为 id/split/question/expected。")
        cid = case["id"]
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError("题目 ID 必须是唯一非空字符串。")
        seen.add(cid)
        if case["split"] not in {"dev", "holdout"} or not isinstance(case["question"], str) or not case["question"].strip():
            raise ValueError("题目分组或问题无效。")
        expected = case["expected"]
        if not isinstance(expected, list):
            raise ValueError("expected 应为数组，资料外问题为空数组。")
        paths = set()
        for item in expected:
            if not isinstance(item, dict) or set(item) != {"path", "quote"} or not isinstance(item["path"], str) or item["path"] not in docs or item["path"] in paths:
                raise ValueError("目标来源缺失、重复或格式不正确。")
            if not isinstance(item["quote"], str) or not item["quote"].strip() or item["quote"] not in docs[item["path"]]["text"]:
                raise ValueError("预期原句不在对应资料中，请重新人工核对标签。")
            paths.add(item["path"])
        if case["split"] == split:
            selected.append(case)
    if not selected or not any(c["expected"] for c in selected) or not any(not c["expected"] for c in selected):
        raise ValueError("所选分组需要同时包含有依据题与资料外题。")
    return selected


def agent_checks(corpus):
    if corpus.resolve() != DEFAULT_CORPUS.resolve():
        return {"executed": False, "reason": "预写 Agent 情节仅适用于默认五篇示例。"}
    project = HERE.parent / "04-工具调用与学习Agent"
    agent = load_module("stage5_agent", project / "study_agent.py")
    fixtures = json.loads((project / "examples/scripted_responses.json").read_text(encoding="utf-8"))
    rows = []
    for name, stop, rounds, calls, budget in [
        ("success", "completed", 3, 2, 6), ("bad_arguments", "completed", 4, 3, 6),
        ("no_results", "insufficient_evidence", 2, 1, 6), ("loop", "tool_limit", 3, 2, 2),
    ]:
        run = agent.run_agent(agent.NoteTools(corpus), agent.DEFAULT_TASK,
                              lambda body, step: fixtures[name][step - 1], max_tool_calls=budget)
        passed = (run["stop_reason"], run["model_requests"], run["tool_attempts"]) == (stop, rounds, calls)
        rows.append({"scenario": name, "passed": passed, "stop_reason": run["stop_reason"],
                     "scripted_responses": run["model_requests"], "tool_attempts": run["tool_attempts"]})
    return {"executed": True, "scope": "预写响应的行为检查，非真实模型效果", "all_passed": all(r["passed"] for r in rows), "rows": rows}


def run_evaluation(corpus, cases_file, split, top_k, chunk_lines, overlap_lines):
    rag = load_rag()
    docs = rag.read_corpus(corpus)
    cases = load_cases(cases_file, docs, split)
    chunks = rag.split_docs(docs, chunk_lines, overlap_lines)
    index = {"backend": "keyword", "chunks": chunks}
    rows, timings, positives, negatives = [], [], [], []
    for case in cases:
        started = time.perf_counter()
        hits = rag.retrieve(index, case["question"], top_k, 0)
        elapsed = (time.perf_counter() - started) * 1000
        timings.append(elapsed)
        paths = {h["path"] for h in hits}
        expected = case["expected"]
        row = {"id": case["id"], "question": case["question"], "expected": expected,
               "retrieved": [{k: h[k] for k in ("path", "start_line", "end_line", "score")} for h in hits],
               "latency_ms": round(elapsed, 4), "manual_answer_score": None, "manual_citation_score": None}
        if expected:
            recall = sum(e["path"] in paths for e in expected) / len(expected)
            coverage = sum(any(h["path"] == e["path"] and e["quote"] in h["text"] for h in hits) for e in expected) / len(expected)
            row.update(source_hit=float(recall > 0), source_recall=recall, quote_coverage=coverage)
            positives.append(row)
        else:
            row["no_candidates"] = not hits
            negatives.append(row)
        rows.append(row)
    metrics = {field: sum(r[key] for r in positives) / len(positives) for field, key in [
        ("source_hit_at_k", "source_hit"), ("source_recall_at_k", "source_recall"), ("quote_coverage_at_k", "quote_coverage")]}
    metrics["no_candidate_rate_on_negatives"] = sum(r["no_candidates"] for r in negatives) / len(negatives)
    code = {"rag_practice.py": sha(Path(rag.__file__)), "evaluate.py": sha(Path(__file__)),
            "local_service.py": sha(HERE / "local_service.py"),
            "study_agent.py": sha(HERE.parent / "04-工具调用与学习Agent/study_agent.py"),
            "scripted_responses.json": sha(HERE.parent / "04-工具调用与学习Agent/examples/scripted_responses.json")}
    return {"schema_version": 1, "time_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version.split()[0],
            "mode": "offline_keyword_and_scripted", "api_requests": 0, "usage": None,
            "suite_sha256": sha(cases_file), "split": split, "code_sha256": code,
            "corpus_manifest": {p: d["sha256"] for p, d in docs.items()},
            "config": {"top_k": top_k, "chunk_lines": chunk_lines, "overlap_lines": overlap_lines},
            "retrieval": {"positive_cases": len(positives), "negative_cases": len(negatives), "metrics": metrics,
                          "latency_ms": {"scope": "仅检索，少量离线样本", "samples": len(timings), "median": statistics.median(timings),
                                         "p95_nearest_rank": sorted(timings)[math.ceil(0.95 * len(timings)) - 1]}, "rows": rows},
            "agent_scripted": agent_checks(corpus)}


def compare_reports(baseline, candidate):
    for field in ("schema_version", "mode", "python", "suite_sha256", "split", "code_sha256", "corpus_manifest"):
        if baseline[field] != candidate[field]:
            raise ValueError("报告条件不同，不能直接比较：" + field)
    for field in ("chunk_lines", "overlap_lines"):
        if baseline["config"][field] != candidate["config"][field]:
            raise ValueError("本比较器只支持相同代码与切分改变 K。")
    before, after = baseline["retrieval"]["metrics"], candidate["retrieval"]["metrics"]
    if set(before) != set(after):
        raise ValueError("指标字段不同。")
    for value in list(before.values()) + list(after.values()):
        if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("指标必须是0–1有限数值。")
    deltas = {key: after[key] - before[key] for key in before}
    scripted = candidate["agent_scripted"]
    behavior_ok = scripted.get("all_passed", True) if scripted["executed"] else True
    return {"scope": "离线自动条件，非答案正确性与上线批准", "baseline_config": baseline["config"],
            "candidate_config": candidate["config"], "metric_deltas": deltas,
            "automatic_checks_passed": all(v >= -1e-12 for v in deltas.values()) and behavior_ok,
            "manual_review_required": True}


def review_markdown(report):
    lines = ["# 人工评审待办", "", "此报告没有生成真实模型答案；先运行项目03/04，再人工核对。", "",
             "| 题目ID | 答案是否正确 | 引文是否支持 | 是否应拒答 | 理由与实际输出路径 |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {r['id']} | 待评 | 待评 | 待评 | |" for r in report["retrieval"]["rows"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "compare"])
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--cases", type=Path, default=HERE / "examples/eval_cases.json")
    parser.add_argument("--split", choices=["dev", "holdout"], default="dev")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--chunk-lines", type=int, default=8)
    parser.add_argument("--overlap-lines", type=int, default=2)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="尚不存在的报告目录。")
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("报告目录已存在，请换新目录名。")
        if args.command == "run":
            result = run_evaluation(args.corpus, args.cases, args.split, args.top_k, args.chunk_lines, args.overlap_lines)
        else:
            if not args.baseline or not args.candidate:
                raise ValueError("compare 需要 --baseline 与 --candidate report.json。")
            result = compare_reports(json.loads(args.baseline.read_text(encoding="utf-8-sig")), json.loads(args.candidate.read_text(encoding="utf-8-sig")))
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "report.json").write_text(dump(result) + "\n", encoding="utf-8")
        if args.command == "run":
            (args.output / "review.md").write_text(review_markdown(result), encoding="utf-8")
        print(dump({"report": str(args.output / "report.json"), "metrics": result.get("retrieval", {}).get("metrics"),
                    "automatic_checks_passed": result.get("automatic_checks_passed")}))
        return 2 if args.command == "compare" and not result["automatic_checks_passed"] else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"评估失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
