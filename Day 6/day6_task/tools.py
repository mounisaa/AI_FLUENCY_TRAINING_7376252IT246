ALLOWED_SUBJECTS = [
    "Java",
    "Python",
    "SQL",
    "C++",
    "Cloud Computing"
]


def calculate_study_hours(subjects, minutes_per_subject):
    total_minutes = subjects * minutes_per_subject
    total_hours = total_minutes / 60

    return (
        f"{subjects} subjects × {minutes_per_subject} minutes "
        f"= {total_minutes} minutes = {total_hours:.2f} hours."
    )


def check_subject(subject):
    if subject in ALLOWED_SUBJECTS:
        return f"{subject} is in the student's study list."

    return f"{subject} is not in the student's study list."


FUNCTIONS = {
    "calculate_study_hours": calculate_study_hours,
    "check_subject": check_subject
}