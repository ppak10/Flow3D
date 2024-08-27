from setuptools import setup, find_packages

setup(
    name='Flow3D',
    version='0.0.11',
    packages=find_packages(),
    include_package_data=True,
    package_data={"Flow3D": ["data/**/*.txt"]}
)

