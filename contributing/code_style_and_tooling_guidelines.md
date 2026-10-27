# Code Style & Tooling Guidelines

This document outlines the required tooling, editor configuration, and semantic coding standards for our C++, Python, and CMake development.

> **Note on Formatting:** Aesthetic formatting (indentation, line length, braces, quotes, auto-sorting of imports) is strictly enforced via `clang-format` and `ruff`. This guide focuses on configuring your editor to handle this automatically, followed by code semantics, naming conventions, and language idioms. Technical design choices (e.g. memory management, rule of 5, smart pointers) are outside the scope of this style guide.

## Tooling & Editor Configuration

We use **[Visual Studio Code](https://code.visualstudio.com/)** as our primary IDE. To ensure everyone's code is formatted identically and automatically upon saving, you must install the required extensions and apply the workspace settings below.

### Required Extensions

**For C++ and CMake:**

| Extension ID                           | Name                   | Marketplace                                                                                      |
| -------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------ |
| `josetr.cmake-language-support-vscode` | CMake Language Support | [Link](https://marketplace.visualstudio.com/items?itemName=josetr.cmake-language-support-vscode) |
| `ms-vscode.cpptools`                   | C/C++                  | [Link](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)                   |

**For Python:**

| Extension ID                  | Name              | Marketplace                                                                             |
| ----------------------------- | ----------------- | --------------------------------------------------------------------------------------- |
| `charliermarsh.ruff`          | Ruff              | [Link](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)          |
| `ms-python.mypy-type-checker` | Mypy Type Checker | [Link](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker) |
| `ms-python.python`            | Python            | [Link](https://marketplace.visualstudio.com/items?itemName=ms-python.python)            |

### Configuration Files

The formatter, linter, and type checker configurations are maintained in [`config/`](config/). Copy the files that apply to your repository into its **root directory**, keeping their names:

| File                                                  | Tool           | Purpose                       |
| ----------------------------------------------------- | -------------- | ----------------------------- |
| [`.clang-format`](config/.clang-format)               | `clang-format` | C++ formatting                |
| [`ruff.toml`](config/ruff.toml)                       | `ruff`         | Python formatting and linting |
| [`mypy.ini`](config/mypy.ini)                         | `mypy`         | Python type checking          |
| [`requirements-dev.txt`](config/requirements-dev.txt) | `pip`          | Tool versions (see below)     |

> [!warning]
> Configure each tool in exactly one place. Do not additionally add `[tool.ruff]` or `[tool.mypy]` sections to a `pyproject.toml`: `ruff.toml` and `mypy.ini` take precedence and such sections are silently ignored.

### Tool Versions

- **New repositories:** copy [`config/requirements-dev.txt`](config/requirements-dev.txt) to the repository root and remove the lines for tools the repository does not use.
- **Working on a repository:** install the pinned tools with `pip install -r requirements-dev.txt`.

### VS Code Workspace Settings

Add the following to your project's `.vscode/settings.json`. This enables format-on-save across all languages, maps the correct formatters to each language, and makes the extensions use the tool versions from `requirements-dev.txt`.

```json
{
    "editor.formatOnSave": true,
    // C++ settings.
    "[cpp]": {
        "editor.defaultFormatter": "ms-vscode.cpptools"
    },
    "[cmake]": {
        "editor.defaultFormatter": "josetr.cmake-language-support-vscode"
    },
    // Python settings.
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

Additionally, set `C_Cpp.clang_format_path` to the absolute path of the `clang-format` installed from `requirements-dev.txt` (find it with `which clang-format`).

## C++ Guidelines

### Header Management

- Use `#pragma once` at the top of all header files instead of traditional include guards.
- `#include` directives are automatically sorted by our formatters, so the order is enforced.
- Use **quotes (`" "`)** for our own workspace and local project headers.
- Use **angle brackets (`< >`)** for system standard libraries and third-party dependencies.

#### Example

```cpp
#pragma once

#include <string>
#include <rclcpp/rclcpp.hpp>

#include "sfg_agent/agent_discoverer.hpp"
```

### Naming Conventions

- **Classes, Structs, Enums, and Typedefs:** Use `PascalCase`.
- **Functions and Local Variables:** Use `snake_case`.
- **Class Member Variables:** Use `snake_case` prefixed with `m_`.
- **Static Variables:** Use `snake_case` prefixed with `s_`.
- **Macros, and Defines:** Use `UPPER_SNAKE_CASE`.
- **Enum Values:** Use `PascalCase` for modern scoped enums (`enum class`), or `UPPER_SNAKE_CASE` if using legacy enums.

#### Example

```cpp
constexpr int max_buffer_size = 1024;

enum class OperationMode 
{
    IdleMode,
    ActiveMode
};

class AgentController 
{
public:
    void start_process();

private:
    static int s_active_controllers;
    int m_target_velocity;
};
```

### Class/Struct Declaration Order

- Use each scope exactly once per class/struct.
- Order `public` before `protected`, and `protected` before `private`.
- Within each scope block, elements should appear in the following order:
  1. Types, aliases, or nested declarations (`typedef`, `using`, `enum`, `struct`, ...).
  2. Constructors, assignment operators, and destructors.
  3. Methods (member functions).
  4. Member variables (fields).

### Other Remarks

- Always use namespaces for your code.
- Have no more than one top-level class/struct declaration per file. 
- Use `auto` when the type is explicitly clear on the right-hand side of the assignment.
- Do not use the `this` pointer unless required.

## CMakeLists.txt Guidelines

### Architecture

- **Rule:** Strictly employ **Target-Based CMake**. Use `target_link_libraries`, `target_include_directories`, and `target_compile_definitions`. Never use directory-wide commands like `include_directories` or `link_directories()`.

### Dependency Management

- **Rule:** Use modern `find_package(Library REQUIRED)` to locate and incorporate dependencies, passing the imported targets to `target_link_libraries`. Avoid manually specifying include paths for external libraries.

## Python Guidelines

### Typing

- **Rule:** Enforce strict type hinting on all function signatures and class-level attributes.
- **Rule:** Use modern standard syntax (`list[str]`, `str | None`). Import `annotations` from `__future__` at the top of the file to support cleaner forward referencing.

#### Example

```python
from __future__ import annotations

def get_active_agents(config: dict[str, str | None]) -> list[str]:
    pass
```

### Naming Conventions

- **Classes:** Use `PascalCase`.
- **Modules, Functions, and Public Variables:** Use `snake_case`.
- **Internal/Private Variables and Methods:** Use `snake_case` prefixed with a single underscore `_` to denote that they are class internals.
- **Global Constants:** Use `UPPER_SNAKE_CASE`.