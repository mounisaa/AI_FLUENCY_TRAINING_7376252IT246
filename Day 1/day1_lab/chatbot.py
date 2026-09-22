"""System 1: a plain LLM chatbot. No tools, no access to the college data."""

from config import MODEL, banner


QUESTIONS = [
    "What is the fee for AI202?",
    "What is the total fee for CS101 and AI202 after a 10% scholarship?",
    "Is DS303 more expensive than CS101, and by how much?",
    "Write a two-line welcome message for new AI students.",
]


ANSWERS = [
    "The fee for AI202 is approximately Rs. 25,000 per semester.",
    "Assuming each course costs Rs. 20,000, the total after a 10% scholarship\nwould be Rs. 36,000.",
    "DS303 is generally more expensive than CS101 by around Rs. 5,000.",
    "Welcome to the world of Artificial Intelligence!\nMay your curiosity lead you to build something remarkable.",
]


def chatbot(question):
    index = QUESTIONS.index(question)
    return ANSWERS[index]


if __name__ == "__main__":
    banner("SYSTEM 1: CHATBOT")

    for question in QUESTIONS:
        print("Q:", question)
        print("A:", chatbot(question))
        print("-" * 70)