# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

# TODO: split into separate examples
from cook.build import BuildStep, LocalBuildServer, RemoteBuildServer
from cook.cli import settings
from cook.sync import SyncDirectory, SyncExclude, SyncFile

if 'name' in settings.args:
    out_file_name = f'output_{settings.args["name"]}'
else:
    out_file_name = 'output_latest'


default_build_server = 'build'
default_project = 'my_project'


build_servers = [
    'local',
    'build',
]


projects = {
    'my_project': {
        'components': [
            'my_project_create_workdir',
            'my_project_build',
            'my_project_post_actions',
        ],
    },

    'my_project_create_workdir': {
        'build_servers': [
            LocalBuildServer(skip=True),
            RemoteBuildServer(name='build', build_path='~'),
        ],

        'build_steps': [
            BuildStep(command='mkdir -p ~/cook_example'),
        ],
    },

    'my_project_build': {
        'build_servers': [
            LocalBuildServer(),
            RemoteBuildServer(name='build', build_path='~/cook_example'),
        ],

        'send': [
            SyncDirectory(),  # Everything in this directory
        ],

        'build_steps': [
            BuildStep(
                workdir='my_project_source',
                command='mkdir -p build'
            ),
            BuildStep(
                workdir='my_project_source/build',
                command='python3 ../my_script.py',
            ),
        ],

        'receive': [
            SyncFile('my_project_source/build/output'),
        ],
    },

    'my_project_post_actions': {
        'build_servers': [
            LocalBuildServer(override=True),
        ],

        'build_steps': [
            BuildStep(command=f'cp my_project_source/build/output {out_file_name}'),
            BuildStep(command=f'cat {out_file_name}'),
        ],
    },

    'clean': {
        'build_servers': [
            LocalBuildServer(override=True),
        ],

        'build_steps': [
            BuildStep(command='rm -rf my_project_source/build'),
            BuildStep(command=f'rm -f {out_file_name}'),
        ],
    },

    'clean_remote': {
        'build_servers': [
            RemoteBuildServer(name='build', build_path='~'),
        ],

        'build_steps': [
            BuildStep(command='rm -rf cook_example'),
        ],
    },
}
