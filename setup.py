from setuptools import setup, find_packages

setup(
    name="explainer-engine",
    version="1.0.0",
    description="Deep Codebase Architecture, Compatibility & Per-File Analysis Engine",
    author="Ayush Pal",
    author_email="ayushpalg46@users.noreply.github.com",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "pygments>=2.15.0",
        "httpx>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "explainer=explainer.cli:main",
            "expl=explainer.cli:main",
            "EXPL=explainer.cli:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
