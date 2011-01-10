from distutils.core import setup

setup(
    name='ConvUtils',
    version='1.0',
    author='Christopher D. Lasher',
    author_email='chris.lasher@gmail.com',
    packages=['convutils', 'convutils.test'],
    url='http://pypi.python.org/pypi/ConvUtils/',
    license='LICENSE.txt',
    description=("A collection of convenient utilities and pure "
        "Python data structures"),
    long_description=open('README.txt').read(),
)

