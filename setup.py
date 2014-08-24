#from setuptools import setup, find_packages
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

setup(
    name='mosstack',
    version='0.5',
    author='Mikko Laine',
    author_email='mikko.laine@gmail.com',
    packages=['astrostack', 'astrostack.Debayer', 'astrostack.Registering', 'astrostack.Stacker'],
#    packages=find_packages(),
    scripts=['scripts/mosstack', 'scripts/mosstackgui'],
    include_dirs=[numpy.get_include()],
#   cmdclass = cmdclass,
#    ext_modules=ext_modules,
    ext_modules = cythonize(["astrostack/Registering/_step2.pyx",
                             "astrostack/Debayer/_BilinearCython.pyx",
                             "astrostack/Debayer/_VNGCython.pyx",
                             "astrostack/Stacker/_math.pyx"]),
    data_files=[
        ("share/mosstack/", ["data/mosstack.xpm"]),
#        ("share/astrostack/", ["data/astrostack_icon64.png"]),
#        ("share/astrostack/", ["data/astrostack_icon128.png"]),
        ("share/applications/", ["data/mosstack.desktop"])
    ],
    url='https://bitbucket.org/mikko_laine/pyastrostack/',
    license='LICENSE.txt',
    description='Stacking software for astronomical images',
    long_description=open('README.txt').read(),
#    install_requires=[
#        "Pillow >= 2.2.1",
#        "NumPy >= 1.6.0",
#        "pyopencl >= 2013",
#        "astropy >= 0.2.4",
#    ],
)
