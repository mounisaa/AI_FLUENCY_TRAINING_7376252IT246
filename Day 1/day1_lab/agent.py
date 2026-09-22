"""System 3: an AI agent. LLM + tools + loop."""

import json

from config import client, MODEL, QUESTIONS, banner
from tools import TOOLS, TOOL_FUNCTIONS


SYSTEM_PROMPT = (
    "You are a college fee assistant. "
    "Never guess a fee: always use get_course_fee. "
    "Use calculator for any arithmetic. "
    "Available course codes: CS101, AI202, DS303. "
    "If no tool is needed, answer directly. "
    "Keep final answers very short and concise. "
    "For comparison questions, give only the conclusion "
    "and the difference. "
    "Do not mention the individual course prices unless necessary. "
    "Use this exact style for comparisons: "
    "'Yes. DS303 costs Rs. 3,000 more than CS101.'"
)


def agent(question, max_steps=6, verbose=True):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for step in range(1, max_steps + 1):

        # 1. REASON
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0
        )

        message = response.choices[0].message

        # 2. If no tool is requested,
        # the LLM has finished
        if not message.tool_calls:
            return message.content.strip()

        # Add assistant's response
        messages.append(message)

        # 3. ACT and OBSERVE
        for call in message.tool_calls:

            name = call.function.name

            # Protect against malformed tool names
            if "<|channel|>" in name:
                name = name.split("<|channel|>")[0]

            arguments = json.loads(
                call.function.arguments or "{}"
            )

            function = TOOL_FUNCTIONS.get(name)

            if function:
                result = function(**arguments)
            else:
                result = f"Unknown tool: {name}"

            if verbose:
                print(
                    f"   step {step}: "
                    f"{name}({arguments}) -> {result}"
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result)
                }
            )

    return (
        "Stopped: maximum steps reached "
        "without a final answer."
    )


if __name__ == "__main__":

    banner("SYSTEM 3: AI AGENT")

    for question in QUESTIONS:

        print("Q:", question)

        print(
            "A:",
            agent(question)
        )

        print("-" * 70)