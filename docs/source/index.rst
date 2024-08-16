==================
Cook Documentation
==================

What is Cook?
=============

Cook is a local and remote shell commands executor written and configured in Python.

Motivation
==========

**Problem**

Building projects from the terminal often requires running multiple, hard to remember commands in sequence.
For example, when building a CMake based C++ project, you might use the following commands: ``mkdir build && cd build``, ``cmake ..``, and ``cmake --build . -j``.
Afterwards, additional commands may be needed for testing or autoformatting the code.
While tools like CMake and Docker offer solutions such as CMake Presets and Docker Compose, they don't completely solve the problem.

**Cook**

With Cook, instead of storing build instructions in a README file, you can place them in a ``recipe.py`` file.
Cook then allows you to easily run a single command or a predefined combination of multiple commands.
Using a Python file for configuration provides the flexibility of a programming language, in contrast to other solutions that rely on JSON or YAML files.

**Extending the functionality**

Sometimes, you may need to use a remote build server to build your project, but it's often more convenient to develop locally.
Cook simplifies this process by offering remote file syncing and remote command execution capabilities.
This allows you to develop locally while still utilizing a remote build server.
Everything can be defined within the same recipe.py file.
You can specify which files to send or receive and to which remote server, while reusing all of your local build steps.

Features
========

* **Local execution**: Easily run single or multiple commands locally from a Python configuration file.
* **Remote file sync and execution**: Sync files and execute commands on remote servers.
* **Composite projects**: Chain multiple projects together into composites for streamlined builds.
* **Interactive selection**: Optionally use interactive prompts to select and run specific tasks.

.. note::
    
    Remote file sync and execution requires ``OpenSSH`` and ``rsync``, which may not be available by default on all systems (e.g., Windows).

Philosophy
==========

* **Pure Python**: The entire project is written and configured purely in Python.
* **Zero dependencies**: Cook uses no dependencies, making it lightweight and easy to install.
* **Simple CLI**: A straightforward command line interface keeps interactions user friendly.
* **Clear recipes**: Recipes are designed to be clear and easy to read, allowing users to quickly understand and modify build instructions.
* **Extendable recipes**: If needed, recipes can be extended with advanced features and leverage the full power of Python.

Contents
========

.. toctree::
   :maxdepth: 2

   quickstart
   recipe
   recipe_advanced
   cli_reference
