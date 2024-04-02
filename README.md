# Cook

Build script aggregator and remote executor.

# Getting started

### Install cook with pipx

Cook is available on PyPI under the name [cook-builder](https://pypi.org/project/cook-builder/).
It can be easily installed with pip, but the recommended method is to use [pipx](https://pipx.pypa.io/stable/).

```sh
pipx install cook-builder
```

### Setup

Create `recipe.py` file which describes how to build Your project locally and on remote build servers.

See the [example project](example).

### Run

Run `cook` command in the terminal and see how the project is being built!

# Development

### Install cook from source

```sh
git clone https://github.com/serweryn617/cook.git
cd cook
pip install -e .
```

<!-- RELEASING
1. Update version in pyproject.toml
2. Build and upload wheels to PyPI:
    python3 -m build
    twine upload dist/*
-->