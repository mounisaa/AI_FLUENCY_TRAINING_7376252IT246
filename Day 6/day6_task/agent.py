import json

from config import client, MODEL, banner
from schemas import TOOLS
from validator import parse_arguments, validate_arguments
from tools import FUNCTIONS


MAX_STEPS = 6
INITIAL_MAX_TOKENS = 500
RETRY_MAX_TOKENS = 1000


SYSTEM_MESSAGE = """
You are a reliable Student Study Planner assistant.

You have two tools:

1. calculate_study_hours
   - Calculates total study time in hours.

2. check_subject
   - Checks whether a subject is in the student's allowed study list.

Rules:
- Use tools when the user asks for calculations or subject checking.
- Tool arguments must be valid JSON.
- Follow the provided tool schemas.
- Do not invent arguments.
- If a tool call fails validation, explain the problem clearly.
- If the user asks something that does not require a tool, answer normally.
"""


def make_tool_message(tool_call_id, content):
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": str(content)
    }


def execute_tool_call(tool_call):

    tool_name = tool_call.function.name
    raw_arguments = tool_call.function.arguments

    arguments, error = parse_arguments(raw_arguments)

    if error:
        return error

    error = validate_arguments(tool_name, arguments)

    if error:
        return error

    if tool_name not in FUNCTIONS:
        return f"Unknown tool '{tool_name}'."

    function = FUNCTIONS[tool_name]

    try:
        result = function(**arguments)
        return str(result)

    except Exception as e:
        return f"Tool execution failed: {e}"


def run_agent(user_question):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_MESSAGE
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    seen_calls = set()
    max_tokens = INITIAL_MAX_TOKENS

    for step in range(1, MAX_STEPS + 1):

        print()
        print(f"--- STEP {step} ---")

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
                max_tokens=max_tokens
            )

        except Exception as e:
            return f"Model/API error: {e}"

        choice = response.choices[0]
        message = choice.message
        finish_reason = choice.finish_reason

        if finish_reason == "length":

            if max_tokens < RETRY_MAX_TOKENS:

                print("Output was cut short.")
                print("Retrying with larger max_tokens...")

                max_tokens = RETRY_MAX_TOKENS
                continue

            return (
                "The model reached the maximum token limit "
                "after retrying."
            )

        if not message.tool_calls:
            return message.content or ""

        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                    for call in message.tool_calls
                ]
            }
        )

        for tool_call in message.tool_calls:

            signature = (
                tool_call.function.name,
                tool_call.function.arguments
            )

            if signature in seen_calls:

                result = (
                    "Repeated identical tool call detected. "
                    "Stopping to avoid an infinite loop."
                )

                messages.append(
                    make_tool_message(
                        tool_call.id,
                        result
                    )
                )

                return result

            seen_calls.add(signature)

            result = execute_tool_call(tool_call)

            print()
            print(f"Tool: {tool_call.function.name}")
            print(f"Arguments: {tool_call.function.arguments}")
            print(f"Result: {result}")

            messages.append(
                make_tool_message(
                    tool_call.id,
                    result
                )
            )

        max_tokens = INITIAL_MAX_TOKENS

    return (
        "Maximum number of agent steps reached. "
        "Stopping safely."
    )


if __name__ == "__main__":

    banner("DAY 6 - RELIABLE TOOL CALLING")

    questions = [
        "How many hours will 3 subjects take if I study each for 60 minutes?",
        "Check whether Java is allowed and calculate the study time for 2 subjects at 90 minutes each.",
        "Check whether Biology is an allowed subject.",
        "What is the purpose of studying regularly?"
    ]

    for question in questions:

        print()
        print("=" * 70)
        print("USER:")
        print(question)
        print("=" * 70)

        answer = run_agent(question)

        print()
        print("FINAL ANSWER:")
        print(answer)