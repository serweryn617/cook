# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

from cook.build import BuildStep, LocalBuildServer


default_build_server = 'local'
default_project = 'release'


projects = {
    'release': {
        'build_servers': [
            LocalBuildServer(),
        ],

        'build_steps': [
            # pip install --upgrade build twine
            BuildStep(command='rm -rf dist'),
            BuildStep(command='python3 -m build'),
            BuildStep(command='twine upload dist/*'),
        ],
    },
}