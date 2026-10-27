# Code Style & Tooling Guidelines

This document outlines the shared tooling and editor configuration for our development, and links to the per-language guidelines.

## Tooling & Editor Configuration

We use **[Visual Studio Code](https://code.visualstudio.com/)** as our primary IDE. To ensure everyone's code is formatted identically and automatically upon saving, you must apply the settings below.

### Tool Versions

- **New repositories:** copy [`config/requirements-dev.txt`](config/requirements-dev.txt) to the repository root and uncomment the tools listed in the [language guidelines](#language-guidelines) for each language the repository uses.
- **Working on a repository:** install the pinned tools with `pip install -r requirements-dev.txt`.

### VS Code Workspace Settings

Add the following to your project's `.vscode/settings.json` to enable format-on-save, then merge in the settings from each language guideline:

```json
{
    "editor.formatOnSave": true
}
```

## Language Guidelines

Language-specific guidelines:

- [C++](style/cpp.md)
- [Python](style/python.md)
