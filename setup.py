from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy

modules = cythonize(["mosstack/Registering/_step2.pyx",
                         "mosstack/Debayer/_BilinearCython.pyx",
                         "mosstack/Debayer/_VNGCython.pyx",
                         "mosstack/Stacker/_math.pyx"])

modules.append(Extension("mosstack.Debayer.debayer",
                         sources=["mosstack/Debayer/debayermodule.c"],
                         libraries=["cfitsio", "m"],
                         define_macros=[('MAJOR_VERSION', '0'), ('MINOR_VERSION', '7'),],
                         extra_compile_args=["-O3"])
              )

setup(
    name='mosstack',
    version='0.7.dev1',
    author='Mikko Laine',
    author_email='mikko.laine@gmail.com',
    packages=find_packages(),
    scripts=['scripts/mosstack', 'scripts/mosstackgui', 'scripts/mosstack_new'],
    include_dirs=[numpy.get_include()],
    ext_modules=modules,
    data_files=[
        ("share/mosstack/", ["data/mosstack.xpm", "doc/LaTeX/manual.pdf"]),
        ("share/applications/", ["data/mosstack.desktop"]),
    ],
    url='https://sites.google.com/site/mosstack',
    license='LICENSE.txt',
    description='Stacking software for astronomical images',
    long_description=open('README.txt').read(),
    install_requires=[
        "Pillow >= 2.2.1",
        "NumPy >= 1.6.0",
        "pyopencl >= 2013",
        "astropy >= 0.2.4",
        "Cython >= 0.19",
    ],
)
