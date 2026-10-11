import json
from schemas import SCHEMAS


def validate_arguments(tool_name, arguments):

    # Check whether the tool exists
    if tool_name not in SCHEMAS:
        return f"Unknown tool '{tool_name}'."


    schema = SCHEMAS[tool_name]

    # -------------------------------------------------
    # 1. Check required arguments
    # -------------------------------------------------

    for required_arg in schema.get("required", []):

        if required_arg not in arguments:
            return (
                f"Validation error: missing required argument "
                f"'{required_arg}'."
            )


    # -------------------------------------------------
    # 2. Check invented extra arguments
    # -------------------------------------------------

    allowed_arguments = set(
        schema.get("properties", {}).keys()
    )

    for argument in arguments:

        if argument not in allowed_arguments:
            return (
                f"Validation error: invented extra argument "
                f"'{argument}'."
            )


    # -------------------------------------------------
    # 3. Check argument types and enum
    # -------------------------------------------------

    properties = schema.get("properties", {})

    for argument, value in arguments.items():

        rules = properties[argument]

        expected_type = rules.get("type")


        # Check string
        if expected_type == "string":

            if not isinstance(value, str):
                return (
                    f"Validation error: '{argument}' "
                    f"must be a string."
                )


        # Check integer
        elif expected_type == "integer":

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                return (
                    f"Validation error: '{argument}' "
                    f"must be an integer."
                )


        # Check enum
        if "enum" in rules:

            if value not in rules["enum"]:

                return (
                    f"Validation error: '{argument}' "
                    f"must be one of: "
                    f"{rules['enum']}."
                )


        # Check minimum
        if "minimum" in rules:

            if value < rules["minimum"]:

                return (
                    f"Validation error: '{argument}' "
                    f"must be at least "
                    f"{rules['minimum']}."
                )


    return None


def parse_arguments(raw_arguments):

    try:

        arguments = json.loads(raw_arguments)

    except json.JSONDecodeError as e:

        return None, f"Invalid JSON arguments: {e}"


    if not isinstance(arguments, dict):

        return None, "Invalid arguments: expected a JSON object."


    return arguments, None


# -------------------------------------------------
# TEST THE VALIDATOR
# -------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("VALIDATOR TESTS")
    print("=" * 70)


    tests = [

        (
            "Valid",
            "check_subject",
            {"subject": "Java"}
        ),

        (
            "Missing required argument",
            "check_subject",
            {}
        ),

        (
            "Invented extra argument",
            "check_subject",
            {
                "subject": "Java",
                "name": "Mounisaa"
            }
        ),

        (
            "Wrong type",
            "calculate_study_hours",
            {
                "subjects": "three",
                "minutes_per_subject": 60
            }
        ),

        (
            "Value outside enum",
            "check_subject",
            {
                "subject": "Biology"
            }
        )
    ]


    for name, tool, args in tests:

        result = validate_arguments(tool, args)

        print()
        print(f"Test: {name}")
        print(f"Arguments: {args}")

        if result is None:

            print("Result: VALID")

        else:

            print(f"Result: {result}")