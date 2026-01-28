import json
from datetime import datetime
from typing import Dict, List

import streamlit as st

import ai_provider
import storage
from text_tools import formatting_cleanup

TARGET_LANGS = ["en", "es", "fr", "de", "it", "pt"]


def load_or_create_project(project_slug: str) -> Dict:
    storage.ensure_project_files(project_slug)
    return storage.load_project(project_slug)


def get_chapter_by_id(chapters: List[Dict], chapter_id: int) -> Dict:
    for chapter in chapters:
        if chapter.get("id") == chapter_id:
            return chapter
    return chapters[0]


def save_current_chapter(project_slug: str, chapter: Dict) -> None:
    storage.update_chapter(project_slug, chapter["id"], chapter)


st.set_page_config(page_title="KDP Writer", layout="wide")

st.sidebar.header("Projects")
projects = storage.list_projects()
selected_project = st.sidebar.selectbox("Select project", options=projects or ["(none)"])

with st.sidebar.expander("Create new project"):
    new_project_name = st.text_input("Project name")
    new_project_title = st.text_input("Book title")
    new_project_author = st.text_input("Author")
    if st.button("Create project"):
        project_slug = storage.slugify(new_project_name)
        storage.ensure_project_files(project_slug, title=new_project_title, author=new_project_author)
        st.success(f"Created {project_slug}")
        st.rerun()

if selected_project == "(none)":
    st.info("Create a project to begin.")
    st.stop()

project_slug = selected_project
project_data = load_or_create_project(project_slug)
config = project_data["config"]
glossary = project_data["glossary"]
chapters_data = project_data["chapters"]
descriptions_data = project_data["descriptions"]

chapters = chapters_data.get("chapters", [])
chapter_ids = [chapter["id"] for chapter in chapters]
selected_chapter_id = st.sidebar.selectbox("Chapter", options=chapter_ids)

if st.sidebar.button("Add chapter"):
    storage.add_chapter(project_slug)
    st.rerun()

selected_lang = st.sidebar.selectbox("Target language", options=TARGET_LANGS)

current_chapter = get_chapter_by_id(chapters, selected_chapter_id)

st.title(config.get("title") or f"Project: {project_slug}")

source_col, target_col = st.columns(2)

with source_col:
    st.subheader("Russian source")
    ru_text = st.text_area("RU", value=current_chapter.get("ru", ""), height=400)

with target_col:
    st.subheader(f"Translation ({selected_lang})")
    translations = current_chapter.get("translations", {})
    target_text = st.text_area(
        f"{selected_lang.upper()} translation",
        value=translations.get(selected_lang, ""),
        height=400,
    )

button_col1, button_col2, button_col3, button_col4 = st.columns(4)

with button_col1:
    if st.button("Save"):
        current_chapter["ru"] = ru_text
        current_chapter.setdefault("translations", {})[selected_lang] = target_text
        save_current_chapter(project_slug, current_chapter)
        st.success("Saved")

with button_col2:
    if st.button("Translate RU → target"):
        translated = ai_provider.translate(
            ru_text,
            selected_lang,
            glossary,
            style=config.get("tone", ""),
        )
        current_chapter.setdefault("translations", {})[selected_lang] = translated
        save_current_chapter(project_slug, current_chapter)
        st.success("Translation complete")
        st.rerun()

with button_col3:
    rewrite_target = st.selectbox("Rewrite target", options=["Target translation", "Russian source"])
    rewrite_instruction = st.selectbox(
        "Rewrite tool",
        options=["Polish", "Shorten", "Make more emotional", "Simplify"],
    )
    if st.button("Apply rewrite"):
        if rewrite_target == "Russian source":
            rewritten = ai_provider.rewrite(ru_text, rewrite_instruction)
            current_chapter["ru"] = rewritten
        else:
            rewritten = ai_provider.rewrite(target_text, rewrite_instruction)
            current_chapter.setdefault("translations", {})[selected_lang] = rewritten
        save_current_chapter(project_slug, current_chapter)
        st.success("Rewrite applied")
        st.rerun()

with button_col4:
    cleanup_target = st.selectbox("Cleanup target", options=["Target translation", "Russian source"])
    if st.button("Run cleanup"):
        if cleanup_target == "Russian source":
            cleaned = formatting_cleanup(ru_text)
            current_chapter["ru"] = cleaned
        else:
            cleaned = formatting_cleanup(target_text)
            current_chapter.setdefault("translations", {})[selected_lang] = cleaned
        save_current_chapter(project_slug, current_chapter)
        st.success("Formatting cleanup done")
        st.rerun()

st.divider()

tab_main, tab_description = st.tabs(["Chapter", "Description"])

with tab_main:
    st.write("Use the editors above to work chapter-by-chapter.")

with tab_description:
    st.subheader("Amazon Description")
    with st.form("description_form"):
        genre = st.text_input("Genre", value=config.get("genre", ""))
        tone = st.text_input("Tone", value=config.get("tone", ""))
        audience = st.text_input("Audience", value=config.get("audience", ""))
        keywords = st.text_input(
            "Keywords (comma-separated)",
            value=", ".join(config.get("keywords", [])),
        )
        source_choice = st.selectbox(
            "Source content",
            options=["Russian", f"Translation ({selected_lang})"],
        )
        if st.form_submit_button("Generate description"):
            content_text = ru_text if source_choice == "Russian" else target_text
            payload = {
                "title": config.get("title", ""),
                "author": config.get("author", ""),
                "genre": genre,
                "tone": tone,
                "audience": audience,
                "keywords": [item.strip() for item in keywords.split(",") if item.strip()],
                "chapter_excerpt": content_text[:4000],
            }
            result = ai_provider.generate_description(payload)
            descriptions_data.update(result)
            descriptions_data["updated_at"] = datetime.utcnow().isoformat()
            storage.save_project_section(project_slug, "descriptions.json", descriptions_data)
            st.success("Generated description")

    st.text_input("Tagline", value=descriptions_data.get("tagline", ""), key="tagline")
    st.text_area(
        "Short blurb",
        value=descriptions_data.get("short_blurb", ""),
        height=150,
        key="short_blurb",
    )
    st.text_area(
        "Long description",
        value=descriptions_data.get("long_description", ""),
        height=250,
        key="long_description",
    )
    st.text_input(
        "Keyword phrases (comma-separated)",
        value=", ".join(descriptions_data.get("keywords", [])),
        key="keyword_phrases",
    )

    if st.button("Save description edits"):
        descriptions_data["tagline"] = st.session_state.get("tagline", "")
        descriptions_data["short_blurb"] = st.session_state.get(
            "short_blurb", descriptions_data.get("short_blurb", "")
        )
        descriptions_data["long_description"] = st.session_state.get(
            "long_description", descriptions_data.get("long_description", "")
        )
        keyword_value = st.session_state.get(
            "keyword_phrases", ", ".join(descriptions_data.get("keywords", []))
        )
        descriptions_data["keywords"] = [item.strip() for item in keyword_value.split(",") if item.strip()]
        descriptions_data["updated_at"] = datetime.utcnow().isoformat()
        storage.save_project_section(project_slug, "descriptions.json", descriptions_data)
        st.success("Description saved")

with st.expander("Project settings"):
    st.json(config)
    if st.button("Refresh project data"):
        st.rerun()
