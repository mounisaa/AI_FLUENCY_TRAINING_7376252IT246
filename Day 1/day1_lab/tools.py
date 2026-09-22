"""Tools used by the AI agent."""

import ast
import operator

from config import COURSE_FEES


def get_course_fee(course_code: str) -> str:

    """Look up the fee for one course code."""

    fee = COURSE_FEES.get(
        course_code.strip().upper()
    )

    if fee is not None:

        return str(fee)

    return (
        f"Unknown course code: "
        f"{course_code}"
    )


# Safe calculator operations
_OPS = {

    ast.Add: operator.add,

    ast.Sub: operator.sub,

    ast.Mult: operator.mul,

    ast.Div: operator.truediv,

    ast.USub: operator.neg
}


def _evaluate(node):

    if isinstance(
        node,
        ast.Constant
    ):

        if isinstance(
            node.value,
            (int, float)
        ):

            return node.value


    if isinstance(
        node,
        ast.BinOp
    ):

        if type(node.op) in _OPS:

            return _OPS[type(node.op)](
                _evaluate(node.left),
                _evaluate(node.right)
            )


    if isinstance(
        node,
        ast.UnaryOp
    ):

        if type(node.op) in _OPS:

            return _OPS[type(node.op)](
                _evaluate(node.operand)
            )


    raise ValueError(
        "Unsupported expression"
    )


def calculator(expression: str) -> str:

    """Evaluate a basic arithmetic expression."""

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        return str(
            _evaluate(tree.body)
        )

    except Exception as error:

        return (
            f"Calculator error: {error}"
        )


# Functions the agent can call
TOOL_FUNCTIONS = {

    "get_course_fee":
        get_course_fee,

    "calculator":
        calculator
}


# Tool descriptions given to the LLM
TOOLS = [

    {
        "type": "function",

        "function": {

            "name":
                "get_course_fee",

            "description":
                (
                    "Get the fee in rupees "
                    "for a single course code, "
                    "for example CS101."
                ),

            "parameters": {

                "type": "object",

                "properties": {

                    "course_code": {

                        "type": "string"
                    }
                },

                "required": [
                    "course_code"
                ]
            }
        }
    },


    {
        "type": "function",

        "function": {

            "name":
                "calculator",

            "description":
                (
                    "Evaluate an arithmetic "
                    "expression using "
                    "+ - * / and brackets."
                ),

            "parameters": {

                "type": "object",

                "properties": {

                    "expression": {

                        "type": "string"
                    }
                },

                "required": [
                    "expression"
                ]
            }
        }
    }
]


if __name__ == "__main__":

    print(
        "get_course_fee('ai202') ->",
        get_course_fee("ai202")
    )


    print(
        "calculator("
        "'(12000 + 18000) * 0.9'"
        ") ->",
        calculator(
            "(12000 + 18000) * 0.9"
        )
    )


    print(
        "calculator("
        "'15000 - 12000'"
        ") ->",
        calculator(
            "15000 - 12000"
        )
    )