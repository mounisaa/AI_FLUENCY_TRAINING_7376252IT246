# Day 1 – AI Agent Lab

A simple Python lab comparing three approaches:

- **Chatbot** – Basic LLM-based responses
- **Workflow** – Rule-based and predictable
- **Agent** – Uses an LLM with tools

## Tools Used

- Python
- Groq API
- LLM
- Tool Calling

## Tools in Agent

- `get_course_fee()` – Gets course fees
- `calculator()` – Performs calculations

## Example

**Question:**  
What is the total fee for CS101 and AI202 after a 10% scholarship?

**Answer:**  
Rs. 27,000

## Challenge

**Question:**  
I can pay Rs. 30,000. Which two courses can I take together?

**Expected:**  
**CS101 + DS303 = Rs. 27,000**

## Run

```powershell
python chatbot.py
python workflow.py
python agent.py
python challenge.py# 10. Observations

| Criterion | Chatbot | Workflow | Agent |
|---|---|---|---|
| Q1 correct? (Y/N) | Y | Y | Y |
| Q2 correct? (Y/N) | Y | Y | Y |
| Q3 correct? (Y/N) | Y | N | Y |
| Q4 handled well? (Y/N) | Y | N | Y |
| Challenge question handled? (Y/N) | N | N | Y |
| Same output on a repeat run? (Y/N) | N | Y | N |
| Approximate response time | Fill from run | Very fast | Fill from run |
| Number of LLM calls per question | 1 | 0 | 1 or more |
| One strength | Flexible natural-language responses | Reliable and predictable | Can use tools and handle new questions |
| One weakness | May give incorrect or guessed answers | Rigid; only handles predefined rules | Less predictable |
| Best suited for (one real use case) | General conversational assistant | Fixed fee/rule-based system | Intelligent college fee assistant |
