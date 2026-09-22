"""System 2: a rule-based workflow. No LLM."""

from tools import get_course_fee, calculator
from config import QUESTIONS, banner


def workflow(question):
    question_lower = question.lower()

    # Q1
    if "fee for ai202" in question_lower:
        fee = get_course_fee("AI202")
        return f"Fee for AI202: Rs. {fee:,}"

    # Q2
    if "total fee" in question_lower and "10%" in question_lower:
        cs_fee = get_course_fee("CS101")
        ai_fee = get_course_fee("AI202")

        total = calculator(f"({cs_fee} + {ai_fee}) * 0.9")

        return f"Total fee: Rs. {int(total):,}"

    # Q3
    if "ds303" in question_lower and "cs101" in question_lower:
        ds_fee = get_course_fee("DS303")
        cs_fee = get_course_fee("CS101")

        difference = calculator(f"{ds_fee} - {cs_fee}")

        return (
            f"Yes. DS303 costs Rs. {ds_fee:,}, "
            f"while CS101 costs Rs. {cs_fee:,}.\n"
            f"Difference: Rs. {int(difference):,} more for DS303."
        )

    # Q4
    if "welcome" in question_lower:
        return "Sorry, I can only answer questions about course fees."

    # Anything else
    return "Sorry, I do not have a rule for this type of question."


if __name__ == "__main__":
    banner("SYSTEM 2: RULE-BASED WORKFLOW")

    for question in QUESTIONS:
        print("Q:", question)
        print("A:", workflow(question))
        print("-" * 70)