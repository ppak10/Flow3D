from setuptools import setup, find_packages

setup(
    name='Flow3D',
    version='0.0.11',
    packages=find_packages(where="."),
    include_package_data=True,
    package_data={
        "flow3d": [
            "data/**/*.txt",
            "data/workspace/*",
        ]
    },
    entry_points={
        "console_scripts": [
            "flow3d-manage=flow3d.manage:main",
        ],
    },
)
