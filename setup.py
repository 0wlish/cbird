from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
    
setup(
    name = 'cbird',
    version = '0.0.1',
    author = 'Victoria Nassikas',
    author_email = 'tortugavpn@gmail.com',
    license = 'GNU GPLv3',
    description = 'CLI for birding data',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/0wlish/cbird',
    py_modules = ['cbird'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        cbird=cbird:cli
    '''
)