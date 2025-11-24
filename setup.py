"""Setup configuration for Expense Predictor."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="expense-predictor",
    version="1.20.1",
    author="Manoj Bhaskaran",
    author_email="",
    description="A machine learning-based expense prediction system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manoj-bhaskaran/expense-predictor",
    py_modules=[
        "model_runner",
        "helpers",
        "security",
        "config",
        "constants",
        "exceptions",
        "python_logging_framework",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy==1.26.4",
        "pandas==2.2.0",
        "scikit-learn==1.5.0",
        "xlrd==2.0.2",
        "openpyxl==3.1.2",
        "pyyaml==6.0.1",
        "python-dotenv==1.0.0",
        "pydantic==2.10.3",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.0",
            "pytest-cov==4.1.0",
            "pytest-mock==3.11.1",
            "openpyxl==3.1.2",
            "flake8==6.1.0",
            "pylint==2.17.0",
            "black==24.3.0",
            "isort==5.12.0",
            "bandit==1.7.5",
            "mypy==1.5.0",
            "types-python-dateutil==2.8.19",
            "sphinx==7.1.0",
            "sphinx-rtd-theme==1.3.0",
            "ipython==8.14.0",
            "jupyter==1.0.0",
            "notebook==7.2.2",
            "coverage==7.3.0",
            "pre-commit==3.4.0",
            "ipdb==0.13.13",
            "memory-profiler==0.61.0",
            "line-profiler==4.1.3",
            "matplotlib==3.8.0",
            "seaborn==0.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "expense-predictor=model_runner:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/manoj-bhaskaran/expense-predictor/issues",
        "Source": "https://github.com/manoj-bhaskaran/expense-predictor",
        "Documentation": "https://github.com/manoj-bhaskaran/expense-predictor#readme",
    },
)
