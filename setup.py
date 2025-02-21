"""Setup.py"""
from setuptools import (
    find_packages,
    setup,
)

__version__ = 'v1.1'
__author__ = 'Tyler Bruno'
DESCRIPTION = 'Raising Exceptions From the Dead by Re-raising Them With New Exception \
    Types'
INSTALL_REQUIRES = ()


with open('README.md', 'r', encoding='utf-8') as file:
    README = file.read()

setup(
    name='zombie-py',
    version=__version__,
    author=__author__,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type='text/markdown',
    keywords='python re-raise exceptions',
    url='https://github.com/tybruno/zombie-py',
    license='MIT',
    package_data={'zombie-py': ['py.typed'], '': ['images/zombie-py.png']},
    include_package_data=True,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: ' 'Libraries :: Python Modules',
    ],
    python_requires='>=3.11',
)
