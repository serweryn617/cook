# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

# TODO: split into separate examples
from cook.build import BuildStep, LocalBuildServer, RemoteBuildServer, Responder
from cook.main import settings
from cook.sync import SyncDirectory, SyncExclude, SyncFile

default_build_server = 'argon'  # Build server used when none were explicitly selected. Use 'local' to build locally.
default_project = 'my_project'  # Project to build when none were explicitly selected.


if 'name' in settings.user_args:
    out_file_name = f'output_{settings.user_args["name"]}'
else:
    out_file_name = 'output_latest'


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
            RemoteBuildServer(name='argon', build_path='~'),
        ],

        'build_steps': [
            BuildStep(command='mkdir -p ~/cook_example'),
        ],
    },

    'my_project_build': {
        'build_servers': [
            LocalBuildServer(),
            RemoteBuildServer(name='argon', build_path='~/cook_example'),
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
                responders=[Responder(pattern=r'Execute example script\? \[y/n\]: ', response='y\n')]
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
            RemoteBuildServer(name='argon', build_path='~'),
        ],

        'build_steps': [
            BuildStep(command='rm -rf cook_example'),
        ],
    },
}
