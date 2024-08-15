# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

default_build_server = 'local'

projects = {
    'format': [
        'black .',
        'isort .',
    ],
    'test': [
        'pytest',
    ],
    'release': [
        # pip install --upgrade build twine
        'rm -rf dist',
        'python3 -m build',
        'twine upload dist/*',
    ],
    'docs': [
        'sphinx-build -M html docs/source docs/output',
        'cp -r docs/output/html/* ../cook-docs/',
    ],
}
