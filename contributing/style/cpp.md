# C++

Semantic coding standards for C++. Formatting is handled by `clang-format`. See [Code Style & Tooling Guidelines](../code_style_and_tooling_guidelines.md) for the shared setup.

## Header Management

- Use `#pragma once` at the top of all header files instead of traditional include guards.
- Use **quotes (`" "`)** for our own workspace and local project headers.
- Use **angle brackets (`< >`)** for system standard libraries and third-party dependencies.

### Example

```cpp
#pragma once

#include <string>
#include <rclcpp/rclcpp.hpp>

#include "sfg_agent/agent_discoverer.hpp"
```

## Naming Conventions

- **Classes, Structs, Enums, and Typedefs:** Use `PascalCase`.
- **Functions and Local Variables:** Use `snake_case`.
- **Class Member Variables:** Use `snake_case` prefixed with `m_`.
- **Static Variables:** Use `snake_case` prefixed with `s_`.
- **Macros, and Defines:** Use `UPPER_SNAKE_CASE`.
- **Enum Values:** Use `PascalCase` for modern scoped enums (`enum class`), or `UPPER_SNAKE_CASE` if using legacy enums.

### Example

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

## Class/Struct Declaration Order

- Use each scope exactly once per class/struct.
- Order `public` before `protected`, and `protected` before `private`.
- Within each scope block, elements should appear in the following order:
  1. Types, aliases, or nested declarations (`typedef`, `using`, `enum`, `struct`, ...).
  2. Constructors, assignment operators, and destructors.
  3. Methods (member functions).
  4. Member variables (fields).

## Other Remarks

- Always use namespaces for your code.
- Have no more than one top-level class/struct declaration per file.
- Use `auto` when the type is explicitly clear on the right-hand side of the assignment.
- Do not use the `this` pointer unless required.
- Write comments with `//` only. Do not use `/* */`.
