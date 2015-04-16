from setuptools import setup, find_packages

import logintc

setup(
    name='logintc',
    version='.'.join(logintc.__version_info__),
    author='Cyphercor Inc.',
    author_email='support@cyphercor.com',
    url='https://github.com/logintc/logintc-python',
    packages=find_packages(),
    package_data={'': ['*.pem']},
    license='LICENSE',
    description='API client for LoginTC two-factor authentication.',
    long_description=open('README.rst', 'rt').read(),
    keywords=['logintc', 'two-factor', 'authentication', 'security'],
    install_requires=['httplib2 >= 0.7'],
    classifiers=['Topic :: Security',
                 'License :: OSI Approved :: BSD License']
)
