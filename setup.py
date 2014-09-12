from distutils.core import setup

readme_contents = open("README.rst").read()

# index where the first paragraph starts
parastart = readme_contents.find('=\n') + 3

# first sentence of first paragraph
sentence_end = readme_contents.find('.', parastart)

setup(
    name='cluster',
    version='1.2.1',
    author='Michel Albert',
    author_email='exhuma@users.sourceforge.net',
    url='https://github.com/exhuma/python-cluster',
    packages=['cluster', 'cluster.method'],
    license='LGPL',
    description=readme_contents[parastart:sentence_end],
    long_description=readme_contents)
