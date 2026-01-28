# KDP Writer (local Streamlit app)

A local-only Streamlit app for managing book projects chapter-by-chapter, translating from Russian into a single target language at a time, and generating marketing copy.

## Features
- Folder-based projects stored in `projects/`.
- Chapter editor with RU source and per-language translations.
- Local formatting cleanup tools.
- AI tools (translate, rewrite, description generator) with offline stub or optional OpenAI integration.

## Local setup (macOS)
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `streamlit run app.py`
5. Open `http://localhost:8501`

## Data layout
```
projects/
  <project_slug>/
    config.json
    glossary.json
    chapters.json
    descriptions.json
```

## OpenAI integration (optional)
Set `OPENAI_API_KEY` to enable real model calls:
```
export OPENAI_API_KEY="your-key"
```
If no key is found, the app uses a stub provider so it runs offline.
