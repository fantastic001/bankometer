from setuptools import setup, find_packages

setup(
    name="bankometer",
    version="1.0.0",
    description="A command-line tool for managing bank transactions with support for multiple banks and filters.",
    author="Stefan Nožinić",
    author_email="stefan@lugons.org",  
    url="https://github.com/fantastic001/bankometer", 
    packages=[
        "bankometer",
        "bankometer"
    ],
    install_requires=[
        "piecash",
        "requests", 
        "pandas",
        "setuptools",
        "orgasm-package", 
        "lxml",
        "tabulate",
        "sqlalchemy"
    ],
    entry_points={
        "console_scripts": [
            "bankometer=bankometer:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
