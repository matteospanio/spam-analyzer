from setuptools import setup, find_packages
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

setup(
    name = config['name'],
    version = config['version'],
    author = config['author'],
    author_email = config['author_email'],
    license = config['license'],
    description = config['description'],
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = config['url'],
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
