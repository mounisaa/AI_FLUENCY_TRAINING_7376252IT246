import json

from config import client, MODEL, banner


QUESTION = """
Extract the student's information from this sentence:

"Mounisaa studies Java and SQL for 3 hours every day."
"""


SCHEMA = {
    "type": "object",
    "properties": {
        "student": {
            "type": "string"
        },
        "subjects": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "hours_per_day": {
            "type": "number"
        }
    },
    "required": [
        "student",
        "subjects",
        "hours_per_day"
    ],
    "additionalProperties": False
}


def run_case(title, **kwargs):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": QUESTION
                }
            ],
            temperature=0,
            **kwargs
        )

        raw = response.choices[0].message.content

        print("RAW REPLY:")
        print(raw)

        try:

            parsed = json.loads(raw)

            print()
            print("PARSED RESULT:")
            print(parsed)

        except json.JSONDecodeError as e:

            print()
            print("JSON PARSE ERROR:")
            print(e)

    except Exception as e:

        print()
        print("PROVIDER ERROR:")
        print(e)


if __name__ == "__main__":

    banner("STRUCTURED OUTPUTS DEMO")

    # --------------------------------------------------
    # 1. No constraint
    # --------------------------------------------------

    run_case(
        "1. NO CONSTRAINT"
    )

    # --------------------------------------------------
    # 2. JSON mode
    # --------------------------------------------------

    run_case(
        "2. JSON MODE",
        response_format={
            "type": "json_object"
        }
    )

    # --------------------------------------------------
    # 3. Schema mode
    # --------------------------------------------------

    run_case(
        "3. SCHEMA MODE",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "student_information",
                "strict": True,
                "schema": SCHEMA
            }
        }
    )