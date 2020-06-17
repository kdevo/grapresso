from setuptools import setup, find_packages
from os import path

REPO_URL = "https://github.com/kdevo/grapresso"

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as readme:
    markdown_description = readme.read()
    # TODO(kdevo): Auto-replace relative links

setup(
    name='grapresso',
    version='0.0.1b0',
    packages=find_packages(exclude=["tests", "tests.*"]),
    url=REPO_URL,
    license='GPL-3.0',
    # setup_requires=[],
    # install_requires=[],
    tests_require=["pytest>=5.0.0,<6.0.0"],
    zip_safe=True,
    python_requires=">=3.5",

    # Metadata for PyPI
    author='kdevo',
    author_email='',
    description='Graph + Espresso = Caffeinated Python graph data structure library!',
    keywords="graph-algorithms graph-theory graph-datastructure storage-format pluggable-backends",
    project_urls={
        "Bug Tracker": "https://github.com/kdevo/grapresso/issues",
        "Documentation": "https://github.com/kdevo/grapresso/blob/master/README.md",
        "Source Code": "https://github.com/kdevo/grapresso",
        "Download ZIP": "https://api.github.com/repos/kdevo/grapresso/zipball"
    },
    long_description=markdown_description,
    long_description_content_type='text/markdown'
)
