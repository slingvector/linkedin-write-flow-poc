from setuptools import setup, find_packages

setup(
    name="linkedin-write-flow",
    version="1.0.1",
    description="A robust, SOLID Python package for publishing content on LinkedIn via OAuth 2.0.",
    author="Your Name",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "requests>=2.30.0",
        "tenacity>=8.3.0",
        "python-dotenv>=1.2.0",
        "python-json-logger>=2.0.7"
    ],
    python_requires=">=3.8",
)
