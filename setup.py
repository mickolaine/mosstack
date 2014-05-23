#from setuptools import setup, find_packages
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

setup(
    name='pyAstroStack',
    version='0.4.0',
    author='Mikko Laine',
    author_email='mikko.laine@gmail.com',
    packages=['pyastrostack', 'pyastrostack.Debayer', 'pyastrostack.Registering', 'pyastrostack.Stacker'],
#    packages=find_packages(),
    scripts=['scripts/AstroStack', 'scripts/AstroStackGui'],
    include_dirs=[numpy.get_include()],
#   cmdclass = cmdclass,
#    ext_modules=ext_modules,
    ext_modules = cythonize(["pyastrostack/Registering/_step2.pyx",
                             "pyastrostack/Debayer/_BilinearCython.pyx",
                             "pyastrostack/Debayer/_VNGCython.pyx",
                             "pyastrostack/Stacker/_math.pyx"]),
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