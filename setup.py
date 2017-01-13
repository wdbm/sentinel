#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pypandoc
import setuptools

def main():

    setuptools.setup(
        name             = "python_sentinel",
        version          = "2017.01.13.1732",
        description      = "motion detection and alerts",
        long_description = long_description(),
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

def long_description(
    filename = "README.md"
    ):

    try:
        try:
            import pypandoc
            long_description = pypandoc.convert(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    except Exception:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
