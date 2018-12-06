#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

def main():
    setuptools.setup(
        name             = "python_sentinel",
        version          = "2018.12.06.0117",
        description      = "motion detection and alerts",
        long_description = long_description(),
        url              = "https://github.com/wdbm/sentinel",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        packages         = setuptools.find_packages(),
        install_requires = [
                           "docopt",
                           "pathlib2",
                           "propyte",
                           "psutil",
                           "pyprel",
                           "scalar",
                           "shijian",
                           "technicolor",
                           "tonescale"
                           ],
        entry_points     = {
                           "console_scripts": ("sentinel = sentinel.__init__:main")
                           },
        zip_safe         = False
    )

def long_description(
    filename = "README.md"
    ):
    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
