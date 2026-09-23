"""Day 3: a ReAct agent with guards."""

import json
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Day 1",
            "day1_lab"
        )
    )
)

from config import client, MODEL, banner
from my_tools import TOOLS, TOOL_FUNCTIONS


SYSTEM_PROMPT = (
    "You are a college assistant. "
    "Use read_webpage to read any page or file the user mentions. "
    "Use calculator for arithmetic calculations. "
    "Never guess a number that should come from a page. "
    "If no tool is needed, answer directly."
)


def agent(question, max_steps=6, verbose=True):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    # Guard: remember previous tool calls
    previous_calls = {}
    previous_results = {}

    for step in range(1, max_steps + 1):

        # 1. REASON
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0
        )

        message = response.choices[0].message

        # 2. STOP if no tool is requested
        if not message.tool_calls:
            return message.content.strip()

        # 3. RECORD the model's request
        messages.append({
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
        })

        # 4. ACT and 5. OBSERVE
        for call in message.tool_calls:

            name = call.function.name
            arguments = {}

            try:

                arguments = json.loads(
                    call.function.arguments or "{}"
                )

                # Identify the exact same tool call
                call_key = (
                    name,
                    json.dumps(
                        arguments,
                        sort_keys=True
                    )
                )

                previous_calls[call_key] = (
                    previous_calls.get(call_key, 0) + 1
                )

                # GUARD
                if previous_calls[call_key] >= 3:

                    last_result = previous_results.get(
                        call_key,
                        ""
                    )

                    # Only short preview, like your reference output
                    last_result = last_result[:300]

                    return (
                        f"Stopped: the tool {name} was called "
                        f"3 times with the same arguments and no "
                        f"progress was made. Last result: "
                        f"{last_result}"
                    )

                # Find tool
                function = TOOL_FUNCTIONS.get(name)

                if function is None:

                    result = (
                        f"Unknown tool: {name}. "
                        f"Available: {list(TOOL_FUNCTIONS)}"
                    )

                else:

                    result = function(**arguments)

                result = str(result)

                # Save result
                previous_results[call_key] = result

            except json.JSONDecodeError as error:

                result = (
                    f"Argument error: {error}. "
                    "Send valid JSON."
                )

            except TypeError as error:

                result = f"Argument error: {error}"

            # Print trace
            if verbose:

                print(
                    f"   step {step}: "
                    f"{name}({arguments}) -> "
                    f"{result[:300]}"
                )

            # Send tool result to model
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

    return "Stopped: maximum steps reached without a final answer."


if __name__ == "__main__":

    banner("MY AGENT (guards on)")

    # Question 1
    question = (
        "Read notice.html and tell me the total fee for CS101 and AI202 "
        "after the merit scholarship."
    )

    print("\nQ:", question)
    print("A:", agent(question))


    # Question 2
    question = (
        "Read fees.html and tell me the fee for CS101."
    )

    print("\nQ:", question)
    print("A:", agent(question))


    # Question 3
    question = (
        "Read big.html and tell me how many students are listed."
    )

    print("\nQ:", question)
    print("A:", agent(question))