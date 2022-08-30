#!/usr/bin/env python

import os

from setuptools import find_packages, setup

here = os.path.dirname(__file__)

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="sphinxcontrib-openapi",
    description="OpenAPI (fka Swagger) spec renderer for Sphinx",
    long_description=long_description,
    license="BSD",
    url="https://github.com/sphinx-contrib/openapi",
    keywords="sphinx openapi swagger rest api renderer docs",
    author="Ihor Kalnytskyi",
    author_email="ihor@kalnytskyi.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    use_scm_version={"root": here},
    setup_requires=["setuptools_scm >= 1.15"],
    install_requires=[
        "sphinx >= 2.0",
        "sphinxcontrib-httpdomain >= 1.5.0",
        "PyYAML >= 3.12",
        "jsonschema >= 2.5.1",
        "sphinx-mdinclude >= 0.5.2",
        "picobox >= 2.2",
        "deepmerge >= 0.1",
    ],
    project_urls={
        "Documentation": "https://sphinxcontrib-openapi.readthedocs.io/",
        "Source": "https://github.com/sphinx-contrib/openapi",
        "Bugs": "https://github.com/sphinx-contrib/openapi/issues",
    },
    classifiers=[
        "Topic :: Documentation",
        "Topic :: Documentation :: Sphinx",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Framework :: Setuptools Plugin",
        "Framework :: Sphinx",
        "Framework :: Sphinx :: Extension",
    ],
    namespace_packages=["sphinxcontrib"],
    python_requires=">=3.6",
)
