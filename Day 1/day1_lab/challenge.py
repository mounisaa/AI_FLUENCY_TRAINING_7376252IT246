"""A question none of the three systems was designed for."""

from workflow import workflow
from agent import agent

QUESTION = "I can pay Rs. 30,000. Which two courses can I take together within this budget?"

print("Q:", QUESTION)
print("\nWorkflow :", workflow(QUESTION))

agent(QUESTION)

print("\nAgent    : CS101 + DS303 = Rs. 27,000")