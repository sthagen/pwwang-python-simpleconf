
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='python-simpleconf',
    version='0.3.1',
    description='Simple configuration management with python.',
    python_requires='==3.*,>=3.6.0',
    project_urls={"homepage": "https://github.com/pwwang/simpleconf", "repository": "https://github.com/pwwang/simpleconf"},
    author='pwwang',
    author_email='pwwang@pwwang.com',
    license='MIT',
    packages=[],
    package_dir={"": "."},
    package_data={},
    install_requires=['diot'],
    extras_require={"dev": ["pytest", "pytest-cov"], "dotenv": ["python-dotenv"], "toml": ["toml"], "yaml": ["pyyaml"]},
)
