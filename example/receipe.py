# Cooking receipe, checkout Cook at https://github.com/serweryn617/cook


# List of remote build servers with directory paths in which to build each project.
build_servers = {
    'argon': {
        # Hostname as defined in SSH config.
        'ssh_name': 'argon',

        #
        'project_remote_build_paths': {
            'my_project': '~/cook_example',
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

        # Commands to run after the build. These are run on the local machine.
        'post_actions': [
            (
                '.',
                'cp build/output ../output_latest'
            ),
        ],
    },

    'clean': {
        'post_actions': [
            (
                '.',
                'rm -r my_project/build'
            ),
            (
                '.',
                'rm output_latest'
            )
        ]

        # TODO
        # 'default_build_server': 'local'
    },

    # TODO: Composite targets
    # clean -> build -> post actions
}


# Build server used when none were explicitly selected.
# Can be on of 'build_servers' or 'local' to build locally.
# Defaults to 'local' when left unspecified.
default_build_server = 'argon'


# Project to build when none were explicitly selected.
# Defaults to the first project from 'projects' when left unspecified.
default_project = 'my_project'
