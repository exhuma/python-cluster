from distutils.core import setup

readme_contents = open("README").read()

# index where the first paragraph starts
parastart = readme_contents.find('=\n') + 3

# first sentence of first paragraph
sentence_end = readme_contents.find('.', parastart)

setup(
    name='cluster',
    version='1.1.1b3',
    author='Michel Albert',
    author_email='exhuma@users.sourceforge.net',
    url='http://python-cluster.sourceforge.net/',
    py_modules=['cluster'],
    license='LGPL',
    description=readme_contents[parastart:sentence_end],
    long_description=readme_contents)
