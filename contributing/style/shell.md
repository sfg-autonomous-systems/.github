# Shell

Semantic coding standards for shell scripts. Formatting is handled by `shfmt`, linting by `shellcheck`. See [Code Style & Tooling Guidelines](../code_style_and_tooling_guidelines.md) for the shared setup.

## General

- Write scripts in Bash. Do not write POSIX `sh` scripts.
- Start every file with `#!/usr/bin/env bash`, including files meant to be sourced.
- If a script grows beyond about 100 lines, or needs data structures or non-trivial argument parsing, write it in Python instead.

## Environment Variables & ROS

- Check required environment variables with `: "${VAR:?}"` before using them.
- Never hardcode the ROS distribution; use `${ROS_DISTRO}`.

## Sourced Files

- Do not call `set` or `exit` in sourced files.

## Naming Conventions

- **Functions:** Use `snake_case`, prefixed with the repository name and two underscores (e.g. `sfg_bash_utils__print_color`).
- **Local Variables:** Use `snake_case`. Declare them with `local`.
- **Constants:** Use `UPPER_SNAKE_CASE`. Declare them with `local -r`.
- **Environment Variables:** Use `UPPER_SNAKE_CASE`. Export them with `local -x` unless the script is meant to set them in the caller's shell.

## Script Structure

- Put all code into functions. Name the entry point function after the script (e.g. `sfg_example__build` in `build`).
- End executable scripts with an entry point block that enables strict mode and calls the entry point function only when the script is executed, not sourced:

  ```bash
  if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
      set -euo pipefail
      sfg_example__build "${@}"
  fi
  ```

- Write error messages to stderr (`>&2`).

### Example

```bash
#!/usr/bin/env bash

sfg_example__log_error() {
    echo "error: ${1}" >&2
}

sfg_example__build() {
    : "${ROS_DISTRO:?}"
    local package_name="${1:?usage: build <package>}"
    local workspace_dir="/workspace"

    if [[ ! -d "${workspace_dir}/src/${package_name}" ]]; then
        sfg_example__log_error "package ${package_name} not found"
        return 1
    fi

    cd "${workspace_dir}"
    colcon build --packages-select "${package_name}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    set -euo pipefail
    sfg_example__build "${@}"
fi
```
