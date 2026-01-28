import os
from typing import Any, Dict, List


class StubProvider:
    def translate(self, text_ru: str, target_lang: str, glossary: Dict[str, Any], style: str) -> str:
        glossary_terms = ", ".join(glossary.get("do_not_translate", [])) or "(none)"
        return (
            f"[STUB TRANSLATION -> {target_lang}]\n"
            f"Style: {style or 'default'}\n"
            f"Glossary terms: {glossary_terms}\n\n"
            f"{text_ru.strip()}"
        )

    def rewrite(self, text: str, instruction: str) -> str:
        return f"[STUB REWRITE: {instruction}]\n\n{text.strip()}"

    def generate_description(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tagline": "[STUB TAGLINE]",
            "short_blurb": "[STUB SHORT BLURB]",
            "long_description": "[STUB LONG DESCRIPTION]",
            "keywords": ["[STUB KEYWORD 1]", "[STUB KEYWORD 2]"],
        }


class OpenAIProvider:
    def __init__(self, api_key: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)

    def _chat(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content or ""

    def translate(self, text_ru: str, target_lang: str, glossary: Dict[str, Any], style: str) -> str:
        system = "You translate from Russian into the requested language."
        glossary_terms = ", ".join(glossary.get("do_not_translate", []))
        notes = glossary.get("notes", "")
        user = (
            f"Target language: {target_lang}\n"
            f"Style/tone: {style or 'default'}\n"
            f"Do not translate: {glossary_terms}\n"
            f"Glossary notes: {notes}\n\n"
            f"Russian text:\n{text_ru}"
        )
        return self._chat(system, user)

    def rewrite(self, text: str, instruction: str) -> str:
        system = "You rewrite text based on the instruction."
        user = f"Instruction: {instruction}\n\nText:\n{text}"
        return self._chat(system, user)

    def generate_description(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        system = "You write book marketing copy for Amazon."
        user = (
            "Create a tagline, short blurb (<=150 words), long description (300-600 words), "
            "and 7 keyword phrases.\n\n"
            f"Payload:\n{payload}"
        )
        content = self._chat(system, user)
        return {
            "tagline": content,
            "short_blurb": "",
            "long_description": "",
            "keywords": [],
        }


def get_provider() -> Any:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return OpenAIProvider(api_key)
    return StubProvider()


def translate(text_ru: str, target_lang: str, glossary: Dict[str, Any], style: str = "") -> str:
    return get_provider().translate(text_ru, target_lang, glossary, style)


def rewrite(text: str, instruction: str) -> str:
    return get_provider().rewrite(text, instruction)


def generate_description(payload: Dict[str, Any]) -> Dict[str, Any]:
    return get_provider().generate_description(payload)
