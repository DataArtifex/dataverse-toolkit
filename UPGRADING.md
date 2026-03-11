# Upgrading Existing Projects

If you have projects based on an older version of this template, follow these steps to bring them up to date with the latest standards (Hatch, uv, Ruff, and GitHub Actions).

## 1. Update Configuration Files

### `pyproject.toml`
The most significant change is the introduction of `[dependency-groups]` and the `[tool.ruff]` section.
- **Merge Dependencies**: Move your `dev` and `docs` dependencies into the new `[dependency-groups]` section.
- **Update Environments**: Switch `tool.hatch.envs.*.dependencies` to `extra-dependencies` or standard `dependencies` as seen in the new template.
- **Add Ruff**: Copy the `[tool.ruff]` section from the template to the end of your file.

### `.gitignore`
Ensure you are ignoring:
- `.hatch/`
- `.ruff_cache/`
- `docs/build/`

## 2. Add Infrastructure Files
Copy these files directly from the template to your project root:
1. **`AGENTS.md`**: Essential for AI-assisted development.
2. **`CLAUDE.md`**: Instructions specifically for Claude/Cursor.
3. **`GEMINI.md`**: Instructions specifically for Gemini.
4. **`.github/copilot-instructions.md`**: Instructions for GitHub Copilot.
5. **`.pre-commit-config.yaml`**: To enforce code quality locally.
6. **`rename.sh`**: Useful if you ever need to clone the project into a new one.

## 3. Update GitHub Actions
Replace the contents of `.github/workflows/` with the new versions:
- **`test.yml`**: Uses `uv` for multi-OS testing and linting.
- **`sphinx.yaml`**: Uses `uv` for documentation builds.

**Note**: If your project has a custom package name (not `cli`), remember to update the `Known-first-party` setting in `pyproject.toml` and the paths in the workflows.

## 4. Update Test Configuration
Ensure `tests/conftest.py` includes the `python-dotenv` loading logic:
```python
from dotenv import load_dotenv
from pathlib import Path
import pytest

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv_path = Path(__file__).parent / "../.env"
    load_dotenv(dotenv_path=dotenv_path)
```

## 5. Refresh Environment
After updating the files, run:
```bash
uv sync
uv run pre-commit install
```

## (Advanced) Git Template Strategy
If you want to keep projects synced with this template moving forward, you can add the template as a remote:
```bash
git remote add template https://github.com/your-username/your-template-repo.git
git fetch template
# Review changes
git diff main template/main pyproject.toml
# Selectively checkout files
git checkout template/main -- .github/workflows/ AGENTS.md .pre-commit-config.yaml
```
