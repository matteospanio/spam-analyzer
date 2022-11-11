from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'spam-detector',
    version = '0.0.1',
    author = 'Matteo Spanio',
    author_email = 'matteo.spanio97@gmail.com',
    license = 'GPLv3',
    description = 'A tool to determine if an email is spam',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'matteospanio/spam-detector',
    py_modules = ['spam-detector', 'app'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires = '>=3.8',
    classifiers = [
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        cooltool=spam-detector:main
    '''
)
