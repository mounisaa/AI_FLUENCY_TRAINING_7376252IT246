"""Day 3: a ReAct agent written from scratch."""

import json
import sys
import os

# Find config.py inside Day 1/day1_lab
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


# ---------- System prompt ----------
SYSTEM_PROMPT = (
    "You are a college assistant. "

    "When the user mentions a file or webpage, ALWAYS use read_webpage first. "
    
    "If the exact file path does not exist, try the filename alone. "

    "After reading the page, identify the required course fees. "

    "For arithmetic, ALWAYS use the calculator tool. "

    "For the fee and scholarship question, use TWO separate calculator calls. "

    "First calculator call: add the two course fees. "
    "For example: 12000+18000. "

    "Second calculator call: apply the 10% scholarship to the total. "
    "For example: 30000*0.9. "

    "Do NOT combine these two calculations into one expression. "

    "Do not calculate arithmetic yourself. "
    
    "Never guess a number that should come from a page. "

    "If no tool is needed, answer directly."
)


# ---------- ReAct Agent ----------
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
            temperature=0
        )

        message = response.choices[0].message

        # 2. STOP
        # If the model does not request a tool,
        # it has produced the final answer.
        if not message.tool_calls:
            return message.content.strip()

        # 3. RECORD the model's tool request
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

        # 4. ACT and 5. OBSERVE
        for call in message.tool_calls:

            name = call.function.name
            arguments = {}

            try:

                # Convert JSON arguments into Python dictionary
                arguments = json.loads(
                    call.function.arguments or "{}"
                )

                # Find the requested tool
                function = TOOL_FUNCTIONS.get(name)

                if function is None:

                    result = (
                        f"Unknown tool: {name}. "
                        f"Available: {list(TOOL_FUNCTIONS)}"
                    )

                else:

                    # Execute the tool
                    result = function(**arguments)

            except json.JSONDecodeError as error:

                result = (
                    f"Argument error: {error}. "
                    "Send valid JSON."
                )

            except TypeError as error:

                result = f"Argument error: {error}"

            # Show the ReAct trace
            if verbose:

                print(
                    f"   step {step}: "
                    f"{name}({arguments}) -> "
                    f"{str(result)[:120]}"
                )

            # Send tool result back to the LLM
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result)
                }
            )

    # 6. SAFETY EXIT
    return "Stopped: maximum steps reached without a final answer."


# ---------- Main program ----------
if __name__ == "__main__":

    banner("MY AGENT (no guards)")

    question = (
        "Read Day_3/notice.html and tell me the total fee for CS101 and AI202 "
        "after the merit scholarship."
    )

    print("Q:", question)

    print("A:", agent(question))