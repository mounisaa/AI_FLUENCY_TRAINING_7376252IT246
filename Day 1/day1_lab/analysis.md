# Comparing a Plain Chatbot, Rule-Based Workflow, and AI Agent

## 1. Scenario

The scenario used in this project is a college course-fee assistant. The available course data contains the fees for CS101, AI202, and DS303. The same questions are tested using three different approaches: a plain chatbot, a rule-based workflow, and an AI agent.

The purpose is to understand the difference between an LLM-only chatbot, a predefined rule-based system, and an AI agent that combines an LLM, tools, and a loop.

---

## 2. Plain Chatbot

The plain chatbot uses an LLM to generate answers to the user's questions. It does not use tools and it does not have access to the private college course-fee data.

Because the chatbot does not receive the actual course-fee information, questions that require the private fee data cannot be answered reliably. The model may guess an answer or say that it does not have enough information. This shows the limitation of using an LLM alone for private-data questions.

The welcome-message question does not require the private course data, so the chatbot can generate a suitable response.

---

## 3. Rule-Based Workflow

The rule-based workflow does not use an LLM. It follows predefined rules written in the program.

For example, when the user asks for the AI202 fee, the workflow identifies the question and calls the course-fee function. For calculations, it follows predefined steps and uses the calculator function.

The workflow is reliable for questions that have already been covered by its rules. However, it is rigid. If the user asks a new question that was not included in the predefined rules, the workflow cannot handle it properly.

---

## 4. AI Agent

The AI agent combines an LLM, tools, and a loop.

The LLM first understands the user's question and decides which tool is required. The agent can use the `get_course_fee` tool to obtain private course-fee data and the `calculator` tool to perform arithmetic.

After receiving the tool results, the agent sends the observations back to the LLM. The agent can then decide whether another tool is needed or whether it can provide the final answer.

This makes the agent more flexible for multi-step questions. For example, it can retrieve the fees of two courses and then use the calculator to find their total or difference.

---

## 5. Comparison

| Basis for comparison | Plain chatbot | Rule-based workflow | AI agent |
|---|---|---|---|
| Flexibility | High for general conversation, but limited for private data | Low because it follows predefined rules | High because it can select tools based on the question |
| Decision-making | LLM generates a response | Decisions are predefined in code | LLM decides which tools and steps are needed |
| Tool usage | No tools | Uses predefined functions/rules | Uses tools selected by the LLM |
| Private-data access | No private course-fee access | Yes, through predefined data/functions | Yes, through tools |
| Multi-step task handling | Limited | Only predefined multi-step tasks | Can perform multiple tool calls in a loop |
| Automation | Limited | Good for fixed processes | Good for flexible multi-step processes |
| Reliability | Can produce incorrect or guessed answers | Reliable for predefined cases | Flexible, but tool/model behaviour can be less predictable |

---

## 6. Suitability Analysis

For this college course-fee scenario, the three approaches demonstrate different strengths.

The plain chatbot is useful for general questions that do not require private course data. However, it should not be relied on for exact course fees because it does not have access to the fee information.

The rule-based workflow is suitable when the questions are known in advance and the required steps are fixed. It can provide reliable results for the questions covered by its rules. Its limitation is that it cannot easily handle a new type of question.

The AI agent is suitable for questions that require private data together with multiple steps of reasoning and calculation. It can retrieve course fees using tools, perform calculations, observe the results, and continue until it reaches an answer.

---

## 7. Challenge Question

The challenge question is:

> I can pay Rs. 30,000. Which two courses can I take together within this budget?

The rule-based workflow was not specifically designed with a rule for this question, so it cannot answer it.

The AI agent can retrieve the fees of CS101, AI202, and DS303 and compare possible pairs using calculations.

The course combinations are:

- CS101 + AI202 = Rs. 30,000
- CS101 + DS303 = Rs. 27,000
- AI202 + DS303 = Rs. 33,000

Therefore, the combinations within a budget of Rs. 30,000 are CS101 + AI202 and CS101 + DS303.

This demonstrates the difference between a rigid predefined workflow and a flexible tool-using agent.

---

## 8. Conclusion

A plain chatbot is appropriate when the task mainly requires natural-language responses and does not depend on private or exact data.

A rule-based workflow is appropriate when the process is predictable, the rules are known in advance, and reliability for those predefined cases is important.

An AI agent is appropriate when a task requires an LLM to understand the request, select and use tools, perform multiple steps, observe results, and continue working until the task is completed.

The main lesson from this project is that an AI agent can be described as:

**Agent = LLM + Tools + Loop**

The three systems therefore provide different approaches to solving the same type of problem: the chatbot uses an LLM alone, the workflow uses predefined rules, and the agent combines an LLM with tools and a loop.