"""Packaging boilerplate for setuptools.

Boilerplate code needed to distribute package and include version in
package.
"""
import os.path

from setuptools import setup

try:
    THIS_DIR = os.path.dirname(__file__)
except NameError:
    THIS_DIR = os.getcwd()

with open(os.path.join(THIS_DIR, "VERSION"), "r") as in_file:
    with open(
        os.path.join(
            THIS_DIR, "src", "olsen_randerson", "__version__.py"
        ), "w"
    ) as out_file:
        out_file.write("""\"\"\"Version for the package.\"\"\"
VERSION = "{ver:s}"
""".format(ver=in_file.read()))

setup(package_dir={"": "src"})
