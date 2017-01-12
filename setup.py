#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pypandoc
import setuptools

def main():

    setuptools.setup(
        name             = "python_sentinel",
        version          = "2017.01.12.2329",
        description      = "motion detection and alerts",
        long_description = pypandoc.convert("README.md", "rst"),
        url              = "https://github.com/wdbm/sentinel",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        py_modules       = [
                           "sentinel"
                           ],
        install_requires = [
                           "opencv",
                           "docopt",
                           "propyte",
                           "shijian",
                           "tonescale"
                           ],
        scripts          = [
                           "sentinel.py"
                           ],
        entry_points     = """
            [console_scripts]
            sentinel = sentinel:sentinel
        """
    )

def read(*paths):
    with open(os.path.join(*paths), "r") as filename:
        return filename.read()

if __name__ == "__main__":
    main()
