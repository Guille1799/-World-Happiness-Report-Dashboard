# Contributing

Thanks for helping improve this project.

## How to contribute

1. **Fork** the repository and create a **feature branch** from `main`.
2. Keep changes **focused** — one logical fix or feature per pull request.
3. **Lint and test** before opening a PR:

   ```bash
   cd world-happiness-streamlit
   pip install -r requirements-dev.txt
   python -m ruff check .
   python -m pytest tests/ -q
   ```

   **Coverage (CI enforces this):** `trend_helpers.py` and `insights.py` must stay at **≥ 95%** line coverage together:

   ```bash
   python -m pytest tests/ -q --cov=trend_helpers --cov=insights --cov-report=term-missing --cov-fail-under=95
   ```

4. **Optional — pre-commit** (from the repo root, after `pip install pre-commit`):

   ```bash
   pre-commit install
   pre-commit run --all-files   # or rely on hooks on git commit
   ```

   Hooks run **Ruff** on `world-happiness-streamlit/` and **pytest** when Python files under that path change.

5. Match existing **style**: same naming, imports, and minimal comments unless something is non-obvious.
6. For **UI strings**, add keys to both `en` and `es` in `i18n.py` when possible.

## What we avoid

- Committing `.env`, API tokens, or large binary datasets.
- Drive-by refactors unrelated to the issue.
- New dependencies without a clear need (keep `requirements.txt` lean for Streamlit Cloud).

## Pull requests

- Describe **what** changed and **why** in plain English.
- Link related issues if any.

## Questions

Open a [GitHub issue](https://github.com/Guille1799/-World-Happiness-Report-Dashboard/issues) for bugs or feature ideas.
