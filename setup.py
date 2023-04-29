from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llmscript",
    version="0.1.0",
    author="Bradley Steinfeld",
    author_email="bradley@steinfeld.ca",
    description="A short description of your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bsteinfeld/llmscript",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=[
        "openai",
        "langchain",
        "pytest",
        "python-dotenv",
    ],
)
