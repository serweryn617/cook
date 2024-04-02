# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook


default_build_server = 'argon'  # Build server used when none were explicitly selected. Use 'local' to build locally.
default_project = 'my_project'  # Project to build when none were explicitly selected.


if 'name' in user_args:
    out_file_name = f'output_{user_args["name"]}'
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
        'build_servers': {
            'local': {  # Local build
                'skip': True,
            },
            'argon': {  # Hostname from SSH config
                'build_path': '~',
            },
        },

        'build_steps': [
            'mkdir -p ~/cook_example',
        ],
    },

    'my_project_build': {
        'build_servers': {
            'local': {
                'build_path': 'my_project_source',
            },
            'argon': {
                'build_path': '~/cook_example',
            },
        },

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
        'build_servers': {
            'local': {
                'override': True,  # Always run locally
                'build_path': 'my_project_source',
            },
        },

        'build_steps': [
            f'cp build/output ../{out_file_name}',
            f'cat ../{out_file_name}',
        ],
    },

    'clean': {
        'build_servers': {
            'local': {
                'override': True,  # Always run locally
                'build_path': 'my_project_source',
            },
        },

        'build_steps': [
            'rm -rf build',
            f'rm -f ../{out_file_name}',
        ],
    },

    'clean_remote': {
        'build_servers': {
            'argon': {
                'build_path': '~/cook_example',
            },
        },

        'build_steps': [
            'rm -rf build',
        ],
    },
}
