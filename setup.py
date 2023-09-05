import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("src/__version__.py", "r") as fh:
    exec_output = {}
    exec(fh.read(), exec_output)
    __version__ = exec_output["__version__"]

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="election-predictions",
    version=__version__,
    description="A Python tool for analysing zoom-in simulations run with SWIFT.",
    url="https://github.com/edoaltamura/election-predictions",
    author="Edoardo Altamura",
    author_email="edoardo.altamura@outlook.com",
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    include_package_data=True,
)