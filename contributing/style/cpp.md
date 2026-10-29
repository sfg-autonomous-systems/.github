# C++

Editor setup and semantic coding standards for C++ and CMake. Formatting is handled by `clang-format`. See [Code Style & Tooling Guidelines](../code_style_and_tooling_guidelines.md) for the shared setup.

## Tooling

### Required Extensions

| Extension ID                           | Name                   | Marketplace                                                                                      |
| -------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------ |
| `josetr.cmake-language-support-vscode` | CMake Language Support | [Link](https://marketplace.visualstudio.com/items?itemName=josetr.cmake-language-support-vscode) |
| `ms-vscode.cpptools`                   | C/C++                  | [Link](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)                   |

### Configuration Files

Copy the following from [`config/`](../config/) into the repository root:

| File                                       | Tool           | Purpose        |
| ------------------------------------------ | -------------- | -------------- |
| [`.clang-format`](../config/.clang-format) | `clang-format` | C++ formatting |

In `requirements-dev.txt`, uncomment `clang-format`.

### VS Code Settings

Merge the following into your project's `.vscode/settings.json`:

```json
{
    "[cpp]": {
        "editor.defaultFormatter": "ms-vscode.cpptools"
    },
    "[cmake]": {
        "editor.defaultFormatter": "josetr.cmake-language-support-vscode"
    }
}
```

## C++

### Header Management

- Use `#pragma once` at the top of all header files instead of traditional include guards.
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

## CMakeLists.txt

### Architecture

- **Rule:** Strictly employ **Target-Based CMake**. Use `target_link_libraries`, `target_include_directories`, and `target_compile_definitions`. Never use directory-wide commands like `include_directories` or `link_directories()`.

### Dependency Management

- **Rule:** Use modern `find_package(Library REQUIRED)` to locate and incorporate dependencies, passing the imported targets to `target_link_libraries`. Avoid manually specifying include paths for external libraries.
