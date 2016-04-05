from setuptools import setup

readme_contents = open("README.rst").read()

# index where the first paragraph starts
parastart = readme_contents.find('=\n') + 3

# first sentence of first paragraph
sentence_end = readme_contents.find('.', parastart)

setup(
    name='cluster',
    version=open('cluster/version.txt').read().strip(),
    author='Michel Albert',
    author_email='michel@albert.lu',
    url='https://github.com/exhuma/python-cluster',
    packages=['cluster', 'cluster.method'],
    license='LGPL',
    description=readme_contents[parastart:sentence_end],
    long_description=readme_contents,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ]
)
