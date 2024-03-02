# Cooking receipe, checkout Cook at https://github.com/serweryn617/cook


# List of remote build servers with directory paths in which to build each project.
build_servers = {
    'argon': {
        # Hostname as defined in SSH config.
        'ssh_name': 'argon',

        # Paths where to build each project
        'project_remote_build_paths': {
            'create_project_dir': '~',
            'build_my_project': '~/cook_example',
        }
    },
}


# List of projects with instructions on how to build them.
projects = {
    # Instructions for 'my_project'.
    # Each part is optional, when it is missing the respective step will be omitted.
    # All paths used locally are relative to 'location' project parameter or to this receipe location if 'location' was not specified.
    # Paths used remotely are relative to 'project_remote_build_paths' for a given project.
    'my_project': {
        'components': [
            'create_project_dir',
            'build_my_project',
            'my_project_post_actions',
        ],
    },

    'create_project_dir': {
        'build_steps': [
            (
                '.',
                'mkdir -p ~/cook_example'
            ),
        ],
    },

    'build_my_project': {
        # Local project location.
        'location': 'my_project',

        # Files from 'location' to send to remote build server.
        'send': [
            'my_script.py',
        ],

        # Files to exclude from previous list.
        'exclude': [
            'build',
        ],

        # Files to get back from remote server after the build.
        'receive': [
            'build',
        ],

        # Steps to build the project. A list of two element tuples consisting of working directory and a command to run.
        'build_steps': [
            (
                '.',
                'mkdir -p build'
            ),
            (
                'build',
                'python3 ../my_script.py'
            ),
        ],

    },

    'my_project_post_actions': {
        'location': 'my_project',

        'build_steps': [
            (
                '.',
                'cp build/output ../output_latest'
            ),
        ],

        'build_server': 'local',
    },

    'clean': {
        'build_steps': [
            (
                '.',
                'rm -r my_project/build'
            ),
            (
                '.',
                'rm output_latest'
            )
        ],

        'build_server': 'local',
    },
}


# Build server used when none were explicitly selected.
# Can be on of 'build_servers' or 'local' to build locally.
default_build_server = 'argon'


# Project to build when none were explicitly selected.
default_project = 'my_project'
