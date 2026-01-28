import re


def normalize_quotes(text: str) -> str:
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return text


def normalize_dashes(text: str) -> str:
    return text.replace("—", "-").replace("–", "-")


def collapse_spaces(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def trim_whitespace_lines(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines()).strip()


def formatting_cleanup(text: str) -> str:
    text = normalize_quotes(text)
    text = normalize_dashes(text)
    text = collapse_spaces(text)
    text = trim_whitespace_lines(text)
    return text
