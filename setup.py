from setuptools import setup, find_packages

setup(
    name='pyAstroStack',
    version='0.0.9dev',
    author='Mikko Laine',
    author_email='mikko.laine@gmail.com',
#    packages=['pyastrostack', 'pyastrostack.Demosaic', 'pyastrostack.Registering', 'pyastrostack.Stacker'],
    packages=find_packages(),
    scripts=['scripts/Testi.py','scripts/AstroStack.py'],
    url='https://bitbucket.org/mikko_laine/pyastrostack/',
    license='LICENSE.txt',
    description='Stacking software for astronomical images',
    long_description=open('README.txt').read(),
    install_requires=[
        "Pillow >= 2.2.1",
        "NumPy >= 1.6.0",
        "pyopencl >= 2013",
        "astropy >= 0.2.4"
    ],
)