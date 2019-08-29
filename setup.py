"""Packaging boilerplate for setuptools.

Boilerplate code needed to distribute package and include version in
package.
"""
from setuptools import setup

with open("VERSION", "r") as in_file:
    with open("src/olsen_randerson/__version__.py", "w") as out_file:
        out_file.write("""\"\"\"Version for the package.\"\"\"
VERSION = "{ver:s}"
""".format(ver=in_file.read()))

setup(package_dir={"": "src"})
