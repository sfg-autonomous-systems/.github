# Information on Working With Repositories

## Clone Using `--recurse-submodule`

Many repositories withing the SFG project are interconnected, i.e. they embed each other as [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) in order to promote reusability. Therefore, **it is essential that whenever you clone a repository you use the option `--recurse-submodule`**:

### Example

```bash
git clone --recurse-submodule git@github.com:sfg-autonomous-systems/<repository>.git
```

### I forgot to clone using `--recurse-submodule`. What do I do?

If you already cloned a repository without the flag, you can initialize the submodules at any time by running these commands from inside the repository's root directory:

```bash
git submodule init
git submodule update --recursive
```

## Ensure Added Submodules Have a Relative Path Inside the Parent Repository’s `.gitmodules`

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