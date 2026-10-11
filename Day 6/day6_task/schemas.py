SCHEMAS = {
    "calculate_study_hours": {
        "type": "object",
        "properties": {
            "subjects": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of subjects to study"
            },
            "minutes_per_subject": {
                "type": "integer",
                "minimum": 1,
                "description": "Study minutes planned for each subject"
            }
        },
        "required": [
            "subjects",
            "minutes_per_subject"
        ],
        "additionalProperties": False
    },

    "check_subject": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "enum": [
                    "Java",
                    "Python",
                    "SQL",
                    "C++",
                    "Cloud Computing"
                ],
                "description": "Subject the student wants to study"
            }
        },
        "required": [
            "subject"
        ],
        "additionalProperties": False
    }
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_study_hours",
            "description": "Calculate the total study time in hours.",
            "parameters": SCHEMAS["calculate_study_hours"],
            "strict": True
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_subject",
            "description": "Check whether a subject is in the student's study list.",
            "parameters": SCHEMAS["check_subject"],
            "strict": True
        }
    }
]