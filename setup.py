#from setuptools import setup, find_packages
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

'''
try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

cmdclass = { }
ext_modules = [ ]

if use_cython:
    ext_modules += [
        Extension("pyastrostack.Registering._step2", ["pyastrostack/Registering/_step2.pyx"]),
    ]
    cmdclass.update({ 'build_ext': build_ext })
else:
    ext_modules += [
        Extension("pyastrostack.Registering._step2", ["pyastrostack/Registering/_step2.c"]),
    ]
'''
setup(
    name='pyAstroStack',
    version='0.1.0',
    author='Mikko Laine',
    author_email='mikko.laine@gmail.com',
    packages=['pyastrostack', 'pyastrostack.Demosaic', 'pyastrostack.Registering', 'pyastrostack.Stacker'],
#    packages=find_packages(),
    scripts=['scripts/AstroStack.py'],
    include_dirs=[numpy.get_include()],
#   cmdclass = cmdclass,
#    ext_modules=ext_modules,
    ext_modules = cythonize("pyastrostack/Registering/_step2.pyx"),
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