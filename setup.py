import os
from setuptools import find_packages, setup

current_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_dir, "./README.md")) as f:
    long_description = f.read()

with open(os.path.join(current_dir, "./requirements.txt")) as f:
    requirements = f.readlines()
    requirements = [x.strip() for x in requirements]

setup(
    name="GeneralAgent",
    version="0.0.3",
    description="General Agent: From LLM to Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CosmosShadow/GeneralAgent",
    author="Chen Li",
    author_email="lichenarthurdata@gmail.com",
    license="Apache 2.0",
    keywords="generalagent agent gpt llm",
    packages=find_packages(),
    platforms="any",
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'GeneralAgent=GeneralAgent.cli:main',
        ],
    },
)