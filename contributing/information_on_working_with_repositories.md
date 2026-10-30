# Information on Working with Repositories

## Clone Using `--recurse-submodule`

Many repositories withing the SFG project are interconnected, i.e. they embed each other as [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) in order to promote reusability. Therefore, **it is essential that whenever you clone a repository you use the option `--recurse-submodule`**:

### Example

```bash
git clone --recurse-submodule git@github.com:sfg-autonomous-systems/<repository>.git
```

### I Forgot to Clone Using `--recurse-submodule`. What Do I Do?

If you already cloned a repository without the flag, you can initialize the submodules at any time by running these commands from inside the repository's root directory:

```bash
git submodule init
git submodule update --recursive
```

## Ensure Added Submodules Have a Relative Path Inside the Parent Repository's `.gitmodules`

### How to Add a Submodule Correctly

Use a relative path when adding a repository into another repository if both of them reside on the same remote. The path should be relative to the parent repository's location on the remote server. For projects in the same organization, this usually equates to `../<submodule>.git`:

```bash
git submodule add ../<submodule>.git path/to/submodule
```

### How to Fix an Existing Submodule

If a submodule was added with an absolute URL, you can fix it by manually editing the `.gitmodules` file. For example, if you have the following erroneous `.gitmodules` file featuring an absolute URL

```yaml
[submodule "path/to/submodule"]
    path = path/to/submodule
    url = git@github.com:sfg-autonomous-systems/<submodule>.git
```

change the absolute to a relative URL like so

```yaml
[submodule "path/to/submodule"]
    path = path/to/submodule
    url = ../<submodule>.git
```

Finally, after editing the file, run `git submodule sync` to apply the change.

### Rationale

Keeping the absolute URL inside `.gitmodules` means that if you added the submodule via SSH, e.g.

- `git submodule add git@github.com:sfg-autonomous-systems/<submodule>.git`

the SSH URL will be stored inside `.gitmodules`. If someone were to clone the parent repository via HTTPS, e.g.

- `git clone --recurse-submodule https://github.com/sfg-autonomous-systems/<repository>.git`

git would still attempt to clone the embedded submodule via SSH **even though the parent repository was cloned via HTTPS**. Consequently, if the user doesn't have an SSH key set on his machine, he will be unable to clone the submodule.

Using relative urls inside `.gitmodules` resolves this issue, i.e. submodules will be cloned via SSH if the parent repository is cloned via SSH, and vice versa.

## Write Commit Messages in the Conventional Commits Format

Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format, `<type>(<scope>)!: <description>`. The specification leaves the following open, which we settle as follows:

- Use one of the types `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style` or `test`. The scope is optional.
- Write the description in the imperative mood, starting with a lowercase letter and without a trailing period.
- Explain in the optional body why the change was made, not how.
- When a pull request is squash-merged, its title becomes the commit message, so it must follow the same format.

### Example

```text
fix(cli): keep comments when updating settings.json

The update command dropped comments above the first setting, so a second run reported differences again.
```
