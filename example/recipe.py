# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook


default_build_server = 'argon'  # Build server used when none were explicitly selected. Use 'local' to build locally.
default_project = 'my_project'  # Project to build when none were explicitly selected.


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
            'cp build/output ../output_latest',
            'cat ../output_latest',
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
            'rm -f ../output_latest',
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
