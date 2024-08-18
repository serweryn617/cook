======
Recipe
======

All project configurations are stored in a ``recipe.py`` file.
This is a standard Python file, allowing you to use all Python features inside, including imports, variables, functions, etc.

Basic recipe reference
======================

Cook can parse a basic version of the recipe without importing any additional Cook modules inside.
For advanced recipe configuration see :doc:`recipe_advanced`.

Recipe variables
----------------

Cook loads the specified `recipe.py` file and imports the following global variables from it:

* **projects: dict**

  Dictionary of project definitions.
  Each entry defines a project, with the key being the project name.
  A basic project definition can be a list of build steps.
  For composite project it has to be a dictionary with ``components`` entry containing a list of project names.

* **default_project: str**

  Project to run by default.
  If ``default_project`` is not defined and project was not selected explicitly from command line, an interactive project selection will be shown.

Build step
----------

Build step can be either a string or a tuple of 2 strings.

* **command: str**

  Shell command to be executed.

* **(workdir: str, command: str)**

  Tuple containing working directory and command. Command will be executed from inside the working directory.

Composite project
-----------------

If a project definition is a dictionary with ``components`` key inside, it is treated as a composite project.
Composite projects do not contain their own build steps, instead they execute a sequence of sub-projects.
Composite projects can also be nested within each other.

See :ref:`Minimal configuration` below for a composite project example.
If ``clean_build`` project is selected, firstly the ``clean`` project and then the ``build`` project will be run:

Special characters
------------------

Escaping special characters in strings must be done manually.
Strings are not quoted automatically so shell features works correctly (e.g. tilde expansion).

Example build step with space in the working directory path:

.. code-block:: python

   ('~/"build dir"', 'echo Building...')

Minimal configuration
=====================

Example ``recipe.py`` for a CMake based project. Recipe template can also be generated using ``cook -t``:

.. code-block:: python

   default_project = 'build'

   projects = {}

   projects['clean_build'] = {
       'components': [
           'clean',
           'build',
       ],
   }

   projects['clean'] = (
       'rm -rf build',
   )

   projects['build'] = (
       'mkdir -p build',
       ('build', 'cmake ..'),
       ('build', 'cmake --build .'),
   )

