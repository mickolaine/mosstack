from setuptools import setup, find_packages
# from distutils.core import setup
# from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

setup(
    name='mosstack',
<<<<<<< HEAD
    version='0.6.2',
=======
    version='0.6.1',
>>>>>>> Renaming astrostack to mosstack begun
    author='Mikko Laine',
    author_email='mikko.laine@gmail.com',
    # packages=['mosstack', 'mosstack.Debayer', 'mosstack.Registering', 'mosstack.Stacker'],
    packages=find_packages(),
    scripts=['scripts/mosstack', 'scripts/mosstackgui'],
    include_dirs=[numpy.get_include()],
    #   cmdclass = cmdclass,
    #    ext_modules=ext_modules,
    ext_modules=cythonize(["mosstack/Registering/_step2.pyx",
                           "mosstack/Debayer/_BilinearCython.pyx",
                           "mosstack/Debayer/_VNGCython.pyx",
                           "mosstack/Stacker/_math.pyx"]),
    data_files=[
        ("share/mosstack/", ["data/mosstack.xpm", "doc/LaTeX/manual.pdf"]),
        ("share/applications/", ["data/mosstack.desktop"])
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
