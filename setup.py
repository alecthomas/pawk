try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='pawk',
    url='http://github.com/alecthomas/pawk',
    download_url='http://github.com/alecthomas/pawk',
    version='0.4',
    description='A Python line-processor (like awk) based on pyline.',
    license='PSF',
    platforms=['any'],
    author='Alec Thomas',
    author_email='alec@swapoff.org',
    py_modules=['pawk'],
    scripts=['pawk'],
    )
