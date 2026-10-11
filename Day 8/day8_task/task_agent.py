import ast
import operator

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from lc_config import get_model, get_vectorstore, EMBED_PROVIDER

# Course fees from the lab
COURSE_FEES = {
    "CS101": 12000,
    "AI202": 18000,
    "DS303": 15000,
}

store = get_vectorstore()

# Change this after checking your actual similarity scores.
MAX_DISTANCE = 0.6


# --------------------------------------------------
# TOOL 1: SEARCH HANDBOOK WITH RELEVANCE GUARD
# --------------------------------------------------
@tool
def search_handbook(query: str) -> str:
    """Search college documents for rules, policies, fees,
    hostel information, exams, library and placements."""

    results = store.similarity_search_with_score(query, k=3)

    # Print the scores for evidence in results.md.
    print(f"\nSearch scores for: {query}")

    for doc, score in results:
        print(f"  {score:.4f} [{doc.metadata['source']}]")

    # Keep only relevant chunks.
    relevant_docs = [
        doc for doc, score in results
        if score <= MAX_DISTANCE
    ]

    if not relevant_docs:
        return "NO_MATCH: this is not covered in the college handbook."

    return "\n\n".join(
        f"[{doc.metadata['source']}] {doc.page_content}"
        for doc in relevant_docs
    )


# --------------------------------------------------
# TOOL 2: GET COURSE FEE
# --------------------------------------------------
@tool
def get_course_fee(course_code: str) -> str:
    """Get the fee for CS101, AI202 or DS303."""

    code = course_code.strip().upper()
    fee = COURSE_FEES.get(code)

    if fee is None:
        return f"Unknown course code: {code}"

    return f"{code} fee is Rs. {fee}"


# --------------------------------------------------
# TOOL 3: CALCULATOR
# --------------------------------------------------
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


@tool
def calculator(expression: str) -> str:
    """Calculate simple arithmetic using +, -, * and /."""

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](
                evaluate(node.left),
                evaluate(node.right),
            )

        raise ValueError("Only simple arithmetic is allowed.")

    try:
        result = evaluate(ast.parse(expression, mode="eval").body)
        return str(result)
    except Exception as error:
        return f"Calculation error: {error}"


# --------------------------------------------------
# TOOL 4: EXAM ELIGIBILITY
# --------------------------------------------------
@tool
def check_exam_eligibility(attendance_percent: float) -> str:
    """Check whether a student with attendance from 0 to 100
    may write the end-semester exam."""

    if not 0 <= attendance_percent <= 100:
        return "ERROR: Attendance must be between 0 and 100."

    if attendance_percent >= 75:
        return (
            f"ELIGIBLE: Attendance is {attendance_percent}%. "
            "You may write the end-semester exam."
        )

    if attendance_percent >= 65:
        return (
            f"CONDONATION: Attendance is {attendance_percent}%. "
            "You may apply for condonation. "
            "Fee: Rs. 500 per course."
        )

    return (
        f"NOT ELIGIBLE: Attendance is {attendance_percent}%, "
        "which is below 65%."
    )


# --------------------------------------------------
# REGISTER ALL TOOLS
# --------------------------------------------------
tools = [
    search_handbook,
    get_course_fee,
    calculator,
    check_exam_eligibility,
]

model = get_model().bind_tools(tools)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------
SYSTEM = """
You are the Greenfield College helpdesk agent.

Rules:
1. Use search_handbook for college rules, policies,
   examination regulations and placement eligibility.
2. Use check_exam_eligibility for attendance-based
   end-semester exam eligibility questions.
3. Use get_course_fee for course fee questions.
4. Use calculator for arithmetic and totals.
5. If search_handbook returns NO_MATCH, say:
   "I don't know. This is not covered in the college handbook."
6. Never invent college policies or unsupported facts.
7. Answer briefly and name the source file when available.
8. For follow-up questions, use the conversation history.
9. For a total, obtain the necessary fees and late fee
   from the appropriate tools or handbook before calculating.
"""


# --------------------------------------------------
# LANGGRAPH AGENT
# --------------------------------------------------
def agent(state: MessagesState):
    reply = model.invoke(
        [("system", SYSTEM)] + state["messages"]
    )
    return {"messages": [reply]}


builder = StateGraph(MessagesState)

builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=InMemorySaver())


# --------------------------------------------------
# ASK QUESTIONS AND DISPLAY TOOL CALLS
# --------------------------------------------------
def ask(question, thread_id="task-run"):
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 15,
    }

    print(f"\n[{thread_id}] USER: {question}")

    for step in graph.stream(
        {"messages": [("user", question)]},
        config,
        stream_mode="updates",
    ):
        for node, update in step.items():
            for msg in update.get("messages", []):

                if getattr(msg, "tool_calls", None):
                    for call in msg.tool_calls:
                        print(
                            f"  {node} -> "
                            f"{call['name']}({call['args']})"
                        )

                elif node == "tools":
                    print(
                        f"  tools -> {msg.name}: "
                        f"{str(msg.content)[:250]}"
                    )

                else:
                    print(f"  ANSWER: {msg.content}")


# --------------------------------------------------
# MAIN: DAY 8 TESTS
# --------------------------------------------------
if __name__ == "__main__":

    print("MODEL:", get_model().__class__.__name__)
    print("EMBEDDING PROVIDER:", EMBED_PROVIDER)
    print("MAX_DISTANCE:", MAX_DISTANCE)

    # Test the eligibility tool directly.
    print("\n--- DIRECT ELIGIBILITY TESTS ---")

    for attendance in [82, 70, 50, 120]:
        result = check_exam_eligibility.invoke(
            {"attendance_percent": attendance}
        )
        print(f"{attendance}% -> {result}")

    # Five questions in ONE thread.
    print("\n--- FIVE DAY 8 QUESTIONS ---")

    ask(
        "What CGPA do I need to be eligible for placements?"
    )

    ask(
        "My attendance is 70%. Can I write the exam?"
    )

    ask(
        "What is the total of the CS101 fee, the AI202 fee "
        "and the maximum late fee?"
    )

    ask(
        "And if I pay only 5 days late instead?"
    )

    ask(
        "What is the capital of France?"
    )

    # Actual distance evidence for results.md.
    print("\n--- RELEVANCE SCORE EVIDENCE ---")

    for query in [
        "What CGPA do I need to be eligible for placements?",
        "What is the capital of France?",
    ]:
        print(f"\nQuery: {query}")

        for doc, score in store.similarity_search_with_score(
            query, k=3
        ):
            print(
                f"{score:.4f} "
                f"[{doc.metadata['source']}]"
            )

    print("\n--- END OF DAY 8 TESTS ---")