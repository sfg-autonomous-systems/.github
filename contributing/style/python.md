# Python

Editor setup and semantic coding standards for Python. Formatting and linting are handled by `ruff`, type checking by `mypy`. See [Code Style & Tooling Guidelines](../code_style_and_tooling_guidelines.md) for the shared setup.

## Tooling

### Required Extensions

| Extension ID                  | Name              | Marketplace                                                                             |
| ----------------------------- | ----------------- | --------------------------------------------------------------------------------------- |
| `charliermarsh.ruff`          | Ruff              | [Link](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)          |
| `ms-python.mypy-type-checker` | Mypy Type Checker | [Link](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker) |
| `ms-python.python`            | Python            | [Link](https://marketplace.visualstudio.com/items?itemName=ms-python.python)            |

### Configuration Files

Copy the following from [`config/`](../config/) into the repository root:

| File                               | Tool   | Purpose                       |
| ---------------------------------- | ------ | ----------------------------- |
| [`ruff.toml`](../config/ruff.toml) | `ruff` | Python formatting and linting |
| [`mypy.ini`](../config/mypy.ini)   | `mypy` | Python type checking          |

In `requirements-dev.txt`, uncomment `ruff` and `mypy`.

> [!warning]
> Configure each tool in exactly one place. Do not additionally add `[tool.ruff]` or `[tool.mypy]` sections to a `pyproject.toml`: `ruff.toml` and `mypy.ini` take precedence and such sections are silently ignored.

### VS Code Settings

Merge the following into your project's `.vscode/settings.json`. This makes the extensions use the tool versions from `requirements-dev.txt`.

```json
{
    "python.languageServer": "Pylance",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": "explicit"
        }
    },
    "mypy-type-checker.importStrategy": "fromEnvironment",
    "mypy-type-checker.cwd": "${nearestConfig}",
    "mypy-type-checker.showNotifications": "onError"
}
```

## Typing

- **Rule:** Add type hints to all class-level attributes.

### Example

```python
class AgentRegistry:
    max_agents: int = 10
```

## Naming Conventions

- **Modules:** Use `snake_case`.
- **Internal/Private Variables and Methods:** Use `snake_case` prefixed with a single underscore `_` to denote that they are class internals.
- **Global Constants:** Use `UPPER_SNAKE_CASE`.
