import json
import os
import shutil
import tempfile
from datetime import datetime
from typing import Any, Dict, List

PROJECTS_ROOT = os.path.join(os.path.dirname(__file__), "projects")


def ensure_projects_root() -> None:
    os.makedirs(PROJECTS_ROOT, exist_ok=True)


def list_projects() -> List[str]:
    ensure_projects_root()
    return sorted(
        [name for name in os.listdir(PROJECTS_ROOT) if os.path.isdir(os.path.join(PROJECTS_ROOT, name))]
    )


def slugify(name: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in name.strip())
    cleaned = "-".join(filter(None, cleaned.split("-")))
    return cleaned or "project"


def project_path(project_slug: str) -> str:
    return os.path.join(PROJECTS_ROOT, project_slug)


def safe_write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        shutil.move(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def default_config(title: str = "", author: str = "") -> Dict[str, Any]:
    return {
        "title": title,
        "author": author,
        "genre": "",
        "tone": "",
        "audience": "",
        "keywords": [],
    }


def default_glossary() -> Dict[str, Any]:
    return {
        "do_not_translate": [],
        "notes": "",
    }


def default_chapters() -> Dict[str, Any]:
    return {
        "chapters": [
            {
                "id": 1,
                "title": "Chapter 1",
                "ru": "",
                "translations": {
                    "en": "",
                    "es": "",
                    "fr": "",
                    "de": "",
                    "it": "",
                    "pt": "",
                },
                "notes": "",
            }
        ],
        "updated_at": datetime.utcnow().isoformat(),
    }


def default_descriptions() -> Dict[str, Any]:
    return {
        "tagline": "",
        "short_blurb": "",
        "long_description": "",
        "keywords": [],
        "updated_at": "",
    }


def ensure_project_files(project_slug: str, title: str = "", author: str = "") -> None:
    base = project_path(project_slug)
    os.makedirs(base, exist_ok=True)

    config_path = os.path.join(base, "config.json")
    glossary_path = os.path.join(base, "glossary.json")
    chapters_path = os.path.join(base, "chapters.json")
    descriptions_path = os.path.join(base, "descriptions.json")

    if not os.path.exists(config_path):
        safe_write_json(config_path, default_config(title=title, author=author))
    if not os.path.exists(glossary_path):
        safe_write_json(glossary_path, default_glossary())
    if not os.path.exists(chapters_path):
        safe_write_json(chapters_path, default_chapters())
    if not os.path.exists(descriptions_path):
        safe_write_json(descriptions_path, default_descriptions())


def load_json(path: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def load_project(project_slug: str) -> Dict[str, Any]:
    ensure_project_files(project_slug)
    base = project_path(project_slug)
    config = load_json(os.path.join(base, "config.json"), default_config())
    glossary = load_json(os.path.join(base, "glossary.json"), default_glossary())
    chapters = load_json(os.path.join(base, "chapters.json"), default_chapters())
    descriptions = load_json(os.path.join(base, "descriptions.json"), default_descriptions())
    return {
        "config": config,
        "glossary": glossary,
        "chapters": chapters,
        "descriptions": descriptions,
    }


def save_project_section(project_slug: str, filename: str, data: Dict[str, Any]) -> None:
    base = project_path(project_slug)
    path = os.path.join(base, filename)
    safe_write_json(path, data)


def add_chapter(project_slug: str) -> Dict[str, Any]:
    project = load_project(project_slug)
    chapters_data = project["chapters"]
    chapters = chapters_data.get("chapters", [])
    next_id = 1 + max((chapter.get("id", 0) for chapter in chapters), default=0)
    chapters.append(
        {
            "id": next_id,
            "title": f"Chapter {next_id}",
            "ru": "",
            "translations": {
                "en": "",
                "es": "",
                "fr": "",
                "de": "",
                "it": "",
                "pt": "",
            },
            "notes": "",
        }
    )
    chapters_data["chapters"] = chapters
    chapters_data["updated_at"] = datetime.utcnow().isoformat()
    save_project_section(project_slug, "chapters.json", chapters_data)
    return chapters_data


def update_chapter(project_slug: str, chapter_id: int, updated: Dict[str, Any]) -> Dict[str, Any]:
    project = load_project(project_slug)
    chapters_data = project["chapters"]
    chapters = chapters_data.get("chapters", [])
    for idx, chapter in enumerate(chapters):
        if chapter.get("id") == chapter_id:
            chapters[idx] = updated
            break
    chapters_data["chapters"] = chapters
    chapters_data["updated_at"] = datetime.utcnow().isoformat()
    save_project_section(project_slug, "chapters.json", chapters_data)
    return chapters_data
