# Simple Cook recipe for a CMake based project.

# Simply running 'cook' will use the default project which is 'build' in this case.
default_project = 'build'

# Global 'projects' dictionary is required in recipe.
projects = {}

# To run a specific project use 'cook --project clean'.
projects['clean'] = (
    'rm -rf build',
)

projects['build'] = (
    'mkdir -p build_dir',
    ('build_dir', 'cmake ..'),
    ('build_dir', 'cmake --build .'),
)

# Running 'cook -p clean_build' will run all of the components specified below.
projects['clean_build'] = {
    'components': [
        'clean',
        'build',
    ],
}
