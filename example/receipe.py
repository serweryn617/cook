# Cooking receipe, checkout Cook at https://github.com/serweryn617/cook


build_servers = {
    'argon': {
        'ssh_name': 'argon',  # Hostname from SSH config

        'project_remote_build_paths': {
            'my_project_create_workdir': '~',
            'my_project_build': '~/cook_example',
            'my_project_clean_remote': '~/cook_example',
        }
    },
}


projects = {
    'my_project': {
        'components': [
            'my_project_create_workdir',
            'my_project_build',
            'my_project_post_actions',
        ],
    },

    'my_project_create_workdir': {
        'build_steps': [
            'mkdir -p ~/cook_example',
        ],
    },

    'my_project_build': {
        'location': 'my_project_source',

        'send': [
            '*',
        ],

        'exclude': [
            'build',
        ],

        'build_steps': [
            'mkdir -p build',
            ('build', 'python3 ../my_script.py'),
        ],

        'receive': [
            'build',
        ],
    },

    'my_project_post_actions': {
        'location': 'my_project_source',
        'build_server': 'local',  # Always run locally

        'build_steps': [
            'cp build/output ../output_latest',
            'cat ../output_latest',
        ],
    },

    'clean': {
        'location': 'my_project_source',
        'build_server': 'local',  # Always run locally

        'build_steps': [
            'rm -rf build',
            'rm -f ../output_latest',
        ],
    },

    'my_project_clean_remote': {
        'build_steps': [
            'rm -rf build',
        ],
    },
}


default_build_server = 'argon'  # Build server used when none were explicitly selected. Use 'local' to build locally.
default_project = 'my_project'  # Project to build when none were explicitly selected.
