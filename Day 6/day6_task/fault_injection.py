from types import SimpleNamespace

from validator import parse_arguments, validate_arguments
from agent import execute_tool_call


def make_call(tool_name, arguments):
    return SimpleNamespace(
        id="fault-test",
        type="function",
        function=SimpleNamespace(
            name=tool_name,
            arguments=arguments
        )
    )


faults = [

    # 1. Invalid JSON
    (
        "Invalid JSON",
        make_call(
            "check_subject",
            '{"subject":"Java"'
        )
    ),

    # 2. Unknown tool
    (
        "Unknown tool",
        make_call(
            "check_temperature",
            '{"city":"Chennai"}'
        )
    ),

    # 3. Missing argument
    (
        "Missing required argument",
        make_call(
            "check_subject",
            '{}'
        )
    ),

    # 4. Wrong type
    (
        "Wrong type",
        make_call(
            "calculate_study_hours",
            '{"subjects":"three","minutes_per_subject":60}'
        )
    ),

    # 5. Enum violation
    (
        "Value outside enum",
        make_call(
            "check_subject",
            '{"subject":"Biology"}'
        )
    ),

    # 6. Invented argument
    (
        "Invented argument",
        make_call(
            "check_subject",
            '{"subject":"Java","student_name":"Mounisaa"}'
        )
    ),

    # 7. Own fault - negative subjects
    (
        "Own fault: negative subjects",
        make_call(
            "calculate_study_hours",
            '{"subjects":-2,"minutes_per_subject":60}'
        )
    ),

    # 8. Own fault - null argument
    (
        "Own fault: null subject",
        make_call(
            "check_subject",
            '{"subject":null}'
        )
    )
]


if __name__ == "__main__":

    print("=" * 70)
    print("FAULT INJECTION")
    print("=" * 70)

    for number, (name, call) in enumerate(faults, start=1):

        print()
        print(f"FAULT {number}: {name}")

        result = execute_tool_call(call)

        print(f"Returned message: {result}")

        print("Run continued: Y")