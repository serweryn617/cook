# Cook

Local and remote shell commands executor written and configured in Python

## Quickstart

### Installation

Cook is available on PyPI as [cook-builder](https://pypi.org/project/cook-builder/).
The recommended way is to install it using [pipx](https://pipx.pypa.io/stable/):

```bash
pipx install cook-builder
```

### Recipe Reference

Cook uses `recipe.py` files to store project configuration.

Check out the [Examples](examples/) for a reference on `recipe.py` format and features.

For a dry run use: `cook --dry`.

To select project and/or build server interactively run: `cook -i`.

### Generating Recipe Template

To generate a recipe template for your project, run:

```bash
cook -t
```

You can open the created `recipe.py` file and adjust the projects/commands to your needs.

### Running Cook

Simply use the `cook` command to run the recipe file:

```bash
cook
```

To see all available command-line options, use:

```bash
cook --help
```
