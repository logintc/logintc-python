from logintc import __version__
from setuptools import setup, find_packages

setup(
    name='logintc',
    version=__version__,
    author='Cyphercor Inc.',
    author_email='support@cyphercor.com',
    url='https://github.com/logintc/logintc-python',
    packages=find_packages(),
    package_data={'': ['*.pem']},
    license='LICENSE',
    description='API client for LoginTC two-factor authentication.',
    keywords=['logintc', 'two-factor', 'authentication', 'security'],
    install_requires=['httplib2 >= 0.7'],
    classifiers=['Topic :: Security',
                 'License :: OSI Approved :: BSD License']
)
