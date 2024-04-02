# Cook

Build script aggregator and remote executor.

# Getting started

### Install cook with pip

```sh
pip install cook-builder
```

### Install cook from source

```sh
git clone https://github.com/serweryn617/cook.git
cd cook
pip install .
```

### Setup

Create `recipe.py` file which describes how to build Your project and lists the available remote build servers.

See the [example project](example).

### Run

Run `cook` command in the directory where the `recipe.py` file is located and see how the project is being built!