import setuptools

with open('README.md') as readme:
    long_description = readme.read()

setuptools.setup(
    name='delimitedfile',
    version='0.0.1',
    author='Karl Semich', # feel free to change to 'Community' or whatever you want, same below
    author_email='0xloem@gmail.com',
    description='interpret a file as a delimited MutableSequence',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Community-Maintenance/python-delimitedfile',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Public Domain',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
