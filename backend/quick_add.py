import re


SYSTEM_PROMPT = (
    "Parse the user's task description into a title, priority, and due-date hint. "
    "Priority must be low, medium, or high. Remove recognized priority and date phrases "
    "from the title while preserving the original casing of the remaining text."
)


def build_prompt(description: str):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": description},
    ]


def parse_quick_add(description: str):
    # Lower-case copy is used only for matching.
    working = description.lower()

    high_keywords = ["urgent", "asap"]
    low_keywords = ["whenever", "low priority"]

    if any(keyword in working for keyword in high_keywords):
        priority = "high"
    elif any(keyword in working for keyword in low_keywords):
        priority = "low"
    else:
        priority = "medium"

    date_phrases = [
        "today",
        "tomorrow",
        "next week",
        "next monday",
        "next tuesday",
        "next wednesday",
        "next thursday",
        "next friday",
        "next saturday",
        "next sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    due_date_hint = None
    matched_date = None

    for phrase in date_phrases:
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", working):
            due_date_hint = phrase
            matched_date = phrase
            break

    # Remove every occurrence of every priority keyword from the original-cased text.
    title = description
    for phrase in high_keywords + low_keywords:
        title = re.sub(
            r"(?i)(?<!\w)" + re.escape(phrase) + r"(?!\w)",
            "",
            title,
        )

    # Remove every occurrence of the matched date phrase.
    if matched_date:
        title = re.sub(
            r"(?i)(?<!\w)" + re.escape(matched_date) + r"(?!\w)",
            "",
            title,
        )

    title = title.strip()
    if not title:
        title = "Untitled task"

    return {
        "title": title,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }
