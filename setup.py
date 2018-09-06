#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import sys
from glob import glob
from distutils.command.sdist import sdist

from setuptools import (
    setup,
    find_packages,
    Extension
)

from distutils.command.build_ext import build_ext


class NoCython(Exception):
    pass

try:
    import Cython.Compiler.Main as cython_compiler
    have_cython = True
except ImportError:
    have_cython = False


def cythonize(src):
    sys.stderr.write("cythonize: %r\n" % (src,))
    cython_compiler.compile([src], cplus=True)

def ensure_source(src):
    pyx = os.path.splitext(src)[0] + '.pyx'

    if not os.path.exists(src):
        if not have_cython:
            raise NoCython
        cythonize(pyx)
    elif (os.path.exists(pyx) and
          os.stat(src).st_mtime < os.stat(pyx).st_mtime and
          have_cython):
        cythonize(pyx)
    return src


class BuildExt(build_ext):
    def build_extension(self, ext):
        try:
            ext.sources = list(map(ensure_source, ext.sources))
        except NoCython:
            print("WARNING")
            print("Cython is required for building extension from checkout.")
            print("Install Cython >= 0.16")
            return
        try:
            return build_ext.build_extension(self, ext)
        except Exception as e:
            print("WARNING: Failed to compile extension modules.")
            print(e)



# take care of extension modules.
if have_cython:
    class Sdist(sdist):
        def __init__(self, *args, **kwargs):
            for src in glob('rlp/sedes/*.pyx'):
                cythonize(src)
            sdist.__init__(self, *args, **kwargs)
else:
    Sdist = sdist

libraries = []
if sys.platform == 'win32':
    libraries.append('ws2_32')

if sys.byteorder == 'big':
    macros = [('__BIG_ENDIAN__', '1')]
else:
    macros = [('__LITTLE_ENDIAN__', '1')]


ext_modules = []
if not hasattr(sys, 'pypy_version_info'):
    ext_modules.append(Extension('rlp.sedes._sedes',
                                 sources=['rlp/sedes/_sedes.cpp'],
                                 libraries=libraries,
                                 include_dirs=['.'],
                                 define_macros=macros,
                                 ))

del libraries, macros



extras_require = {
    'test': [
        "pytest==3.3.2",
        "tox>=2.9.1,<3",
        "hypothesis==3.56.5",
    ],
    'lint': [
        "flake8==3.4.1",
    ],
    'doc': [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9",
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "pytest-xdist",
        "pytest-watch>=4.1.0,<5",
        "wheel",
        "ipython",
        "twine",
    ],
}


extras_require['dev'] = (
    extras_require['dev'] +
    extras_require['test'] +
    extras_require['lint'] +
    extras_require['doc']
)


setup(
    name='rlp',
    # *IMPORTANT*: Don't manually change the version here. See README for more.
    version='1.0.2',
    description="A package for Recursive Length Prefix encoding and decoding",
    long_description_markdown_filename='README.md',
    cmdclass={'build_ext': BuildExt, 'sdist': Sdist},
    ext_modules=ext_modules,
    author="jnnk",
    author_email='jnnknnj@gmail.com',
    url='https://github.com/Helios-Protocol/py-rlp-cython',
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    setup_requires=['setuptools-markdown'],
    install_requires=[
        "eth-utils>=1.0.2,<2", "cython>=0.16"

    ],
    extras_require=extras_require,
    license="MIT",
    zip_safe=False,
    keywords='rlp ethereum',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
