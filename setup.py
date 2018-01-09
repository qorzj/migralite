# coding: utf-8
"""
migralite
~~~~~~~~

Migralite is a simple mysql migration tool.

Setup
-----

.. code-block:: bash

    > pip install migralite

Links
-----
* `README <https://github.com/qorzj/migralite>`_

"""

from setuptools import setup
from os import path
from setuptools.command.install import install
import re
import ast

here = path.abspath(path.dirname(__file__))


class MyInstall(install):
    def run(self):
        print("-- installing... (powered by lesscli) --")
        install.run(self)


_version_re = re.compile(r'__version__\s+=\s+(.*)')
version = str(ast.literal_eval(
    _version_re.search(
        open('migralite/__init__.py').read()
    ).group(1)
))
setup(
        name = 'migralite',
        version=version,
        description='migralite is a simple mysql migration tool (python3 only)',
        long_description=__doc__,
        url='https://github.com/qorzj/migralite',
        author='qorzj',
        author_email='inull@qq.com',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='migralite mysql migrate',
        packages = ['migralite'],
        install_requires=['lesscli', 'mysql-connector==2.1.4'],

        cmdclass={'install': MyInstall},
        entry_points={
            'console_scripts': [
                'migralite = migralite.main:entrypoint',
            ],
        },
    )
