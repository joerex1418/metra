import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pymetra',
    version='0.0.1',
    author='Joe Rechenmacher',
    author_email='joe.rechenmacher@gmail.com',
    description="Python Wrapper for Metra's GTFS-Static and GTFS-RealTime APIs",
    packages=setuptools.find_packages(where='metra',include=["__init__"]),
    install_requires=['requests'],
)
