import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyTransit-Metra',
    version='1.0.0',
    author='Joe Rechenmacher',
    author_email='joe.rechenmacher@gmail.com',
    description='Python Wrapper for Metra\'s GTFS-Static and GTFS-RealTime APIs',
    license='GPU',
    packages=setuptools.find_packages(where='metra',include=["__init__"],exclude=["metra","constants","utils","utils_metra"]),
    install_requires=['requests','pandas','beautifulsoup4'],
)
