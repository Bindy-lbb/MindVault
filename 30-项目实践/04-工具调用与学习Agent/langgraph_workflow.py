"""选修：把同样的搜索与读取包装为 LangGraph 固定工作流，无模型请求。"""

import argparse
from typing import TypedDict

from study_agent import DEFAULT_CORPUS, NoteTools, READ_ARGS, dump


class State(TypedDict, total=False):
    query: str
    search_result: dict
    read_result: dict


def build_graph(tools):
    from langgraph.graph import END, START, StateGraph

    def search(state):
        result = tools.execute("search_notes", dump({"query": state["query"], "top_k": 1}))
        return {"search_result": result}

    def read(state):
        found = state["search_result"]
        if not found["ok"] or not found["data"]:
            return {"read_result": {"ok": False, "error": {"code": "no_evidence", "message": "没有可读取的搜索依据。"}}}
        hit = found["data"][0]
        return {"read_result": tools.execute("read_note", dump({key: hit[key] for key in READ_ARGS}))}

    builder = StateGraph(State)
    builder.add_node("search", search)
    builder.add_node("read", read)
    builder.add_edge(START, "search")
    builder.add_edge("search", "read")
    builder.add_edge("read", END)
    return builder.compile()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="API 密钥环境变量")
    args = parser.parse_args()
    try:
        result = build_graph(NoteTools(DEFAULT_CORPUS)).invoke({"query": args.query})
        print(dump({"execution_mode": "langgraph_fixed_workflow", "model_requests": 0, "state": result}))
        return 0
    except ImportError:
        print("请先在独立环境安装 langgraph，参见实践三；本示例没有调用模型。")
        return 1
    except (OSError, ValueError) as exc:
        print("运行失败：" + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
