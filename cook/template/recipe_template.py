TEMPLATE = '''# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

default_build_server = 'local'
default_project = 'build'

build_servers = [
    'local',
]

projects = {}

projects['run_all'] = {
    'components': [
        'clean',
        'build',
    ],
}

projects['clean'] = (
    # 'rm -rf build',
    'echo "running: rm -rf build"',
)

projects['build'] = (
    # 'mkdir -p build',
    'echo "running: mkdir -p build"',
    # ('build', 'cmake ..'),
    # ('build', 'cmake --build .'),
    'echo "running cmake in build directory"',
)
'''