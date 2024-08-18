# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Cook'
copyright = '2024, Seweryn Rusecki'
author = 'Seweryn Rusecki'
release = 'v0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# -- Alabaster theme customization options -----------------------------------
# https://alabaster.readthedocs.io/en/latest/customization.html

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    "description": "Local and remote shell commands executor written and configured in Python",
    "github_repo": "cook",
    "github_user": "serweryn617",
    "github_button": False,
    "github_banner": True,
    "page_width": "70%",
    "body_max_width": "auto",
    "pre_bg": "#e9e9ed",
}
