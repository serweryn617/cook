==========
Quickstart
==========

Installation
============

Cook is available on PyPI as ``cook-builder``.
The recommended way is to install it using pipx:

.. code-block:: bash

   pipx install cook-builder

Generating recipe template
==========================

Cook uses ``recipe.py`` files to store project configuration.

To generate a recipe template for your project run:

.. code-block:: bash

   cook -t

You can open the created ``recipe.py`` file and adjust the projects/commands to your needs.

For more information about recipe file format see :doc:`recipe`.

Running Cook
============

Simply use ``cook`` command to run the recipe file.

.. code-block:: bash

   cook

To see all available command line options use ``cook --help``.