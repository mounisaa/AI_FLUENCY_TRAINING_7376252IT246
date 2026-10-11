# Agentic AI: Foundations and Open-Source Practice
## Day 6 - Reliable Tool Calling

## 1. Scenario

For this task, I created a Student Study Planner.

The agent has two tools:

1. calculate_study_hours
2. check_subject

The first tool calculates the total study time from the number of subjects
and the minutes planned for each subject.

The second tool checks whether a subject belongs to the allowed study list.

The scenario was intentionally kept small so that the main focus could remain
on reliable tool calling, validation, retry and structured outputs.

---

# 2. Explanation of Concepts

## 2.1 Chat Completions Format

The Chat Completions API represents the conversation using messages.

The main request fields used in this project are:

- model
- messages
- tools
- tool_choice
- max_tokens
- temperature

The response contains choices. Each choice contains a message and a
finish_reason.

In my project, the important finish_reason values are:

### stop

The model has completed its answer and does not need another tool.

My code reads message.content and returns the final answer.

### length

The response stopped because it reached the token limit.

My code does not treat this as a normal final answer. It retries with a
larger max_tokens value.

### tool_calls

The model wants one or more tools to be executed.

The model does not execute my Python functions. It only generates the
requested tool name and arguments.

message.content can be empty in this situation because the model is
communicating its next action through tool_calls instead of normal text.

---

## 2.2 OpenAI-Compatible Servers

An OpenAI-compatible server exposes an API with a request and response
format that is similar to the OpenAI API.

This means the same OpenAI Python client can communicate with different
servers by changing the base_url and authentication details.

In this project I used Groq.

My configuration points the OpenAI client to:

https://api.groq.com/openai/v1

The important point is that compatibility does not mean that every server
supports every OpenAI feature identically. A server can support the basic
Chat Completions format while having different support for structured
outputs, models or tool-calling features.

---

## 2.3 Streaming

Streaming means that the model sends the response in smaller pieces as
they are generated instead of waiting for the entire response.

It improves perceived responsiveness because the user can see output earlier.

For an agent loop, streaming is usually switched off because the program
needs to collect and inspect the complete assistant response before deciding
whether it contains tool calls, whether the JSON is valid and which tools
must be executed.

The Responses API style uses a newer response-oriented structure with
different output items, while Chat Completions organizes the interaction
around messages and choices.

This task stays with Chat Completions because it directly demonstrates the
OpenAI-compatible tool-calling format used in the earlier labs.

---

## 2.4 Five Steps of One Tool Call

The tool-calling process in my project has five main stages.

### Step 1 - Send messages and tools

My code sends the conversation and the two tool definitions to the model.

### Step 2 - Model generates a tool call

The model decides that it needs a tool and generates a tool name and JSON
arguments.

### Step 3 - My code receives the call

My Python program receives the generated tool call.

### Step 4 - My code validates and executes it

My code parses the JSON, checks that the tool exists, validates the
arguments against the schema and then calls the Python function.

### Step 5 - Tool result goes back to the model

The result is added as a tool message using the same tool_call_id.

The model can then use that result to produce the final answer.

The Python code actually runs the function, not the model.

This matters because model-generated tool calls cannot automatically be
trusted. They are generated text and must be checked before execution.

---

## 2.5 Tool Definition and Schema

My tool definitions contain:

- description
- properties
- enum
- required
- additionalProperties
- strict

The description tells the model what the tool does.

Properties define the possible arguments.

The required field prevents required arguments from being omitted.

additionalProperties: false prevents the model from inventing extra
arguments.

The enum in check_subject restricts the subject to the allowed study list.

The strict setting asks the provider to follow the schema more strictly.

For this scenario I use tool_choice = auto because the model should decide
whether a tool is needed.

The other options are:

- auto: model may call a tool or answer normally
- none: tools are disabled for that request
- required: the model must make a tool call
- named function: a particular function is selected

---

## 2.6 JSON Mode and Schema Mode

JSON mode asks the model to return valid JSON.

Schema mode goes further by specifying the expected structure and fields.

In my scenario, I use tools when the model needs to perform an action such
as calculating study hours or checking a subject.

I use structured outputs when I want the model to extract fields from text,
such as:

student name,
subjects,
hours per day.

A perfectly shaped JSON response does not guarantee a correct answer.

For example, the following can have the correct shape:

{
    "student": "Mounisaa",
    "subjects": ["Java"],
    "hours_per_day": 100
}

The structure is valid, but the value may still be factually or
semantically incorrect.

---

## 2.7 Parallel Tool Calls

Parallel tool calls happen when the model requests more than one tool in
the same response.

For example:

"Check whether Java is allowed and calculate the study time for 2 subjects
at 90 minutes each."

This can produce:

1. check_subject
2. calculate_study_hours

My loop processes every tool call and sends one tool message for every
tool_call_id.

If one tool_call_id is not answered, the model does not receive the result
corresponding to that call, which can cause the conversation to fail or
become inconsistent.

---

## 2.8 Failures Handled

My program handles:

### Invalid JSON

The JSON parser catches the error and returns a message.

### Unknown tool

The tool name is checked against the FUNCTIONS dictionary.

### Missing argument

The JSON schema validator checks required.

### Wrong type

The schema validator checks the expected type.

### Value outside enum

The enum validation rejects subjects such as Biology.

### Invented argument

additionalProperties: false rejects arguments not defined in the schema.

### Truncated reply

finish_reason = length causes a retry with a larger token limit.

### Repeated identical calls

The agent stores previous tool-call signatures and detects repeated calls.

I also injected additional faults such as a negative number and a null
subject.

---

## 2.9 Repair Pattern

The repair pattern means that errors are returned to the model as normal
tool messages instead of crashing the program.

For example, if the model sends:

{
    "subject": "Biology"
}

the validator can return:

"Validation error: value outside allowed list."

The model receives that message and can correct its tool call.

Returning strings is useful because the agent loop can continue processing
instead of terminating with a Python exception.

A truncated response is different. In that case the model output itself
was cut short, so the program retries with more tokens.

A malformed tool call is instead returned to the model so that the model
can repair its generated call.

---

## 2.10 Fault Injection

Fault injection means deliberately creating failures to test whether the
agent handles them correctly.

My fault_injection.py script does not use the model or internet.

It directly sends broken tool calls to the same handler used by the agent.

This demonstrates that many reliability problems are in the application
layer around the model, especially parsing, validation, execution and loop
control.

A stricter schema can prevent a negative number when minimum = 1 is defined.

However, a schema cannot determine every semantic or real-world mistake.
For example, 100 subjects may be valid according to the schema but still
be unrealistic for a student's study plan.

---

# 3. Comparison Table

| Basis | Tool Calling | Structured Outputs |
|---|---|---|
| What the model is asked to do | Request an action/function | Produce data in a specified structure |
| Who performs the action or produces final data | My Python code performs the tool action | The model produces the structured data |
| How shape is controlled | Tool JSON schema | JSON/schema output |
| What can still go wrong | Invalid calls, wrong values, unknown tools, execution errors | Correct shape but incorrect values |
| How my code guards against it | Parse, validate, execute, retry and loop limits | Parse and validate structured result |
| Support across servers/models | Depends on tool-calling support | Depends on structured-output support |
| Fetch/calculate something | Tool calling - the Python function performs the action | Not appropriate for performing the action |
| Pull fields from a sentence | Possible but unnecessary | Structured outputs - the model should return the fields |

---

# 4. Minimal Implementation

My project contains the following files:

- config.py
- schemas.py
- validator.py
- tools.py
- agent.py
- fault_injection.py
- structured_outputs.py

The schemas are stored in one SCHEMAS dictionary.

The same schemas are used both in the tool definitions sent to the model
and in the validator.

This prevents the model-facing schema and validation rules from becoming
different.

---

# 5. Fault Injection Observation

| Fault | Message Returned | Continued? |
|---|---|---|
| Invalid JSON | Invalid JSON arguments | Y |
| Unknown tool | Unknown tool | Y |
| Missing argument | Required argument missing | Y |
| Wrong type | Wrong type | Y |
| Enum violation | Value outside allowed list | Y |
| Invented argument | Additional property not allowed | Y |
| Negative subjects | Minimum validation error | Y |
| Null subject | Type validation error | Y |

The important observation is that none of these faults needs to crash the
agent. They are converted into messages that the agent loop can handle.

---

# 6. Agent Behaviour

| Question | Tool Calls | Steps | Parallel? | Finish Reason |
|---|---|---:|---|---|
| Calculate study time | calculate_study_hours | 2 | No | stop/tool_calls |
| Check Java + calculate time | check_subject + calculate_study_hours | 2 | Yes if returned together | tool_calls |
| Check Biology | check_subject | 2 or more if repaired | No | tool_calls |
| Purpose of studying | None | 1 | No | stop |

The exact number of steps and finish_reason should be updated with the
actual terminal output from my run.

---

# 7. Before and After Guards

Without validation, a malformed tool call could reach the function and
cause incorrect behaviour or a Python exception.

With the guards enabled, the call is stopped before execution and an error
message is returned to the model.

| Version | Steps | Final Answer | Loop |
|---|---:|---|---|
| Without guards | update from actual test | update from actual test | update |
| Guarded agent | update from actual test | update from actual test | update |

The main improvement is that invalid tool input is treated as recoverable
agent feedback rather than an application crash.

---

# 8. Structured Outputs Observation

| Method | Provider Result | Worked? |
|---|---|---|
| No constraint | Update from terminal output | Update |
| JSON mode | Update from terminal output | Update |
| Schema mode | Update from terminal output | Update |

If the provider does not support schema mode, the error itself is useful
evidence because the assignment asks us to record provider support.

---

# 9. Suitability and Conclusion

The deliberately injected faults demonstrated failures that may not appear
during a normal model run.

The real model may produce valid calls most of the time, while faults such
as malformed JSON, invented arguments or unknown tools can be difficult to
reproduce naturally. Fault injection therefore gives a deterministic way
to test the reliability layer.

The most important guard in my scenario is validation before execution.
Even if the model produces a tool call that looks reasonable, my Python
program does not immediately trust it.

For calculations or actions, I would give the model a tool because the
Python program should perform the actual operation.

For extracting fields from a sentence, I would prefer structured outputs
because the main requirement is a predictable data structure rather than
an external action.

In general, a model's tool call can never be trusted automatically because
the tool call is generated by the model. Every reply must be inspected for
the finish reason, parsed when necessary, checked for a known tool, validated
against the schema and safely executed.

A schema can prevent structural problems such as missing required fields,
wrong types, extra properties and invalid enum values. However, a schema
cannot guarantee that a structurally valid value is semantically correct.

Deliberate fault injection makes it possible to test these guards
systematically without waiting for a model to fail naturally. This makes
the agent easier to debug and gives stronger evidence that the reliability
mechanisms actually work.