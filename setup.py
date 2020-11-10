from setuptools import setup, find_packages
from os import path
import os
import re
import logging


logging.basicConfig(level=logging.INFO)

AUTHOR = "kdevo"
PROJECT = "grapresso"
VERSION = '0.1.1'

REPO_PATH = f"{AUTHOR}/{PROJECT}"
REPO_URL = f"https://github.com/{REPO_PATH}"

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as readme:
    md_description = readme.read()
    files = os.listdir(path.abspath(path.dirname(__file__)))
    logging.debug(f"Repo files: {'|'.join(files)}")

    def replace_rel(matchobj):
        rel_url = matchobj.group(2)
        if rel_url.startswith('/'):
            rel_url = rel_url[1:]
        # If the URL is an image:
        if matchobj.group(0).startswith("!"):
            abs_url = f"https://raw.githubusercontent.com/{REPO_PATH}/master/{rel_url}"
            logging.info(f"Replace image rel URL '{rel_url}' with abs '{abs_url}'.")
        else:
            abs_url = f"{REPO_URL}/tree/master/{rel_url}"
            logging.info(f"Replace regular rel URL '{rel_url}' with abs '{abs_url}'.")
        return f"{matchobj.group(1)}({abs_url})"


    (processed_md_description, num) = re.subn(fr"(!?\[.*\])\((/?({'|'.join(files)}).*?)\)",
                                              replace_rel, md_description,
                                              flags=re.IGNORECASE)
    print(f"Replaced {num} occurrences of relative links from README.md.")

setup(
    name=PROJECT,
    version=VERSION,
    packages=find_packages(exclude=["tests", "tests.*"]),
    url=REPO_URL,
    license='GPL-3.0',
    extras_require={
        'backend-networkx': ["networkx==2.4.0"],
        'test': ["pytest>=5.0.0,<6.0.0"]
    },
    zip_safe=True,
    python_requires=">=3.6",

    # Metadata for PyPI
    author=AUTHOR,
    author_email='https://kdevo.github.io/#contact',
    description='Graph + Espresso = Caffeinated Python graph data structure library!',
    keywords="graph-algorithms graph-theory graph-datastructure storage-format pluggable-backends",
    project_urls={
        "Bug Tracker": "https://github.com/kdevo/grapresso/issues",
        "Documentation": "https://github.com/kdevo/grapresso/blob/master/README.md",
        "Source Code": "https://github.com/kdevo/grapresso",
        "Download ZIP": "https://api.github.com/repos/kdevo/grapresso/zipball"
    },
    long_description=processed_md_description,
    long_description_content_type='text/markdown'
)
