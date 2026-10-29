# Python

Semantic coding standards for Python. Formatting and linting are handled by `ruff`, type checking by `ty`. See [Code Style & Tooling Guidelines](../code_style_and_tooling_guidelines.md) for the shared setup.

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
