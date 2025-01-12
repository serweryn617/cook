# Cook recipe with user specified arguments.
# Run: 'cook -u key=val flag1 flag2'.

from cook.cli import settings

projects = {}

default_project = 'print_user_args'

projects['print_user_args'] = {
    'components': [
        'print_args',
        'print_flags',
    ]
}

projects['print_args'] = [f'echo User arg: {key} = {value}' for key, value in settings.args.items()]

projects['print_flags'] = [f'echo User flag: {flag}' for flag in settings.flags]
