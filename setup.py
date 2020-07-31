from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ["astunparse", "vyper~=0.2"]

dev_requires = ["ipdb", "ipython"]
docs_requires = ["Sphinx"]
tests_requires = [
    "black",
    "coverage",
    "flake8",
    "flake8-import-order",
    "pep8-naming",
    "pytest-cov",
    "pytest-vyper @ git+https://github.com/sbellem/pytest-vyper.git",
]

extras_require = {
    "dev": dev_requires + docs_requires + tests_requires,
    "docs": docs_requires,
    "tests": tests_requires,
}
setup(
    name="ratl",
    version="0.0.1.dev0",
    author="Sylvain Bellemare",
    description="Experiment.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    license="MIT license",
    packages=find_packages(),
    extras_require=extras_require,
    install_requires=install_requires,
    python_requires=">=3.7",
)
