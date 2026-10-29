# CMake

Semantic coding standards for CMake. See [Code Style & Tooling Guidelines](../code_style_and_tooling_guidelines.md) for the shared setup.

## Architecture

- **Rule:** Strictly employ **Target-Based CMake**. Use `target_link_libraries`, `target_include_directories`, and `target_compile_definitions`. Never use directory-wide commands like `include_directories` or `link_directories()`.

## Dependency Management

- **Rule:** Use modern `find_package(Library REQUIRED)` to locate and incorporate dependencies, passing the imported targets to `target_link_libraries`. Avoid manually specifying include paths for external libraries.
