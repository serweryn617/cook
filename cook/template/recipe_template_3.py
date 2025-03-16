TEMPLATE = '''# Cooking recipe, checkout Cook at https://github.com/serweryn617/cook

# Recipe with user specified arguments.
# Run: 'cook -u flag1 key=val flag2'.

from cook.cli import settings

default_project = 'print_user_args'

projects = {}

projects['print_user_args'] = {
    'components': [
        'print_flags',
        'print_args',
    ]
}

projects['print_flags'] = [f'echo User flag: {flag}' for flag in settings.flags]
projects['print_args'] = [f'echo User argument: {key} = {value}' for key, value in settings.args.items()]
'''
