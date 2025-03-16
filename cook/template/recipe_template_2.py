TEMPLATE = '''# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

from cook.build import BuildStep, LocalBuildServer, RemoteBuildServer
from cook.sync import SyncDirectory, SyncExclude, SyncFile


default_build_server = 'remote_server'
default_project = 'my_project'


# Server named 'remote_server' needs to be defined in SSH config (~/.ssh/config).
build_servers = [
    'local',
    'remote_server',
]


projects = {}


projects['my_project'] = {
    'components': [
        'my_project_create_workdir',
        'my_project_build',
        'my_project_post_actions',
    ],
}


projects['my_project_create_workdir'] = {
    'build_servers': [
        LocalBuildServer(skip=True),
        RemoteBuildServer(name='remote_server', build_path='~'),
    ],

    'build_steps': [
        BuildStep(command='mkdir -p ~/cook_example'),
    ],
}


projects['my_project_build'] = {
    'build_servers': [
        LocalBuildServer(),
        RemoteBuildServer(name='remote_server', build_path='~/cook_example'),
    ],

    # 'send': [
    #     SyncDirectory(),
    #     SyncFile('recipe.py'),
    #     SyncExclude('recipe.py'),
    # ],

    'build_steps': [
        BuildStep(
            # workdir='.',
            command='hostname > output',
            # check=True,
            # expected_return_code=0
        ),
    ],

    'receive': [
        SyncFile('output'),
    ],
}


projects['my_project_post_actions'] = {
    'build_servers': [
        LocalBuildServer(override=True),
    ],

    'build_steps': [
        BuildStep(command='cp output output_latest'),
        BuildStep(command='cat output_latest'),
    ],
}


projects['clean'] = {
    'build_servers': [
        LocalBuildServer(override=True),
    ],

    'build_steps': [
        BuildStep(command='rm output_latest'),
    ],
}


projects['clean_remote'] = {
    'build_servers': [
        RemoteBuildServer(name='remote_server', build_path='~'),
    ],

    'build_steps': [
        BuildStep(command='rm -r cook_example'),
    ],
}
'''
