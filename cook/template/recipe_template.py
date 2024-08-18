TEMPLATE = '''# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

default_build_server = 'local'
# default_project = 'build'

build_servers = [
    'local',
]

projects = {}

projects['clean_build'] = {
    'components': [
        'clean',
        'build',
    ],
}

projects['clean'] = (
    # 'rm -rf build',
    'echo "cleaning build directory"',
)

projects['build'] = (
    # 'mkdir -p build',
    'echo "creating build directory"',

    # ('build', 'cmake ..'),
    # ('build', 'cmake --build .'),
    'echo "running cmake in build directory"',
)
'''
