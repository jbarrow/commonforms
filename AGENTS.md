# Repository Guidelines

## Project Structure & Module Organization
- `commonforms/`: Python package and CLI entry (`__main__.py`). Key modules: `inference.py` (YOLO model + HF download), `form_creator.py` (PDF form writing), `utils.py`, `exceptions.py`.
- `tests/`: Pytest suite (`*_test.py`) with PDF fixtures in `tests/resources/`.
- `dataset/`: Dataset preprocessing scripts.
- `assets/`: Images used in the README.
- `.github/workflows/`: CI using `uv` + `pytest`.
- `pyproject.toml`: Dependencies and script entry (`commonforms`).

## Build, Test, and Development Commands
- Setup environment (uv): `uv sync --dev`
- Run tests: `uv run -m pytest`
- Lint/format (ruff): `uv run ruff check --fix && uv run ruff format`
- Run CLI locally: `uv run commonforms tests/resources/input.pdf out.pdf`

## Coding Style & Naming Conventions
- Python ≥ 3.10, 4‑space indent, type hints throughout.
- Style and formatting via Ruff; prefer auto‑fix over manual edits.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_CASE`.
- Keep functions small, with clear docstrings on public APIs.

## Testing Guidelines
- Place tests under `tests/` and name files `*_test.py`.
- Use `tmp_path` for outputs; keep fixtures under `tests/resources/`.
- Tests should be hermetic; first run may download models (HF cache is reused).

## Commit & Pull Request Guidelines
- Commits: concise, imperative subject; reference issues/PRs when relevant (e.g., `add multiline support (#22)`).
- PRs: clear description, reproduction or CLI example, screenshots when visual; link issues. Ensure `ruff` passes and tests run locally/CI.

## Security & Configuration Tips
- Models download via Hugging Face; set `HF_HOME` to control cache location.
- Do not commit large binaries or secrets; ignore generated PDFs and local data.
- Take always in account rules in ./rules folder and subfolder.

