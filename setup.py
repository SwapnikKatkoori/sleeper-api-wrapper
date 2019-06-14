import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sleeper_wrapper",
    version="0.1.0",
    description="A Python API wrapper for Sleeper Fantasy Football, as well as tools to simplify data recieved.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/SwapnikKatkoori/sleeper_wrapper",
    author="Swapnik Katkoori",
    author_email="katkoor2@msu.edu",
    license="MIT",
    packages=["sleeper_wrapper"],
    include_package_data=True,
    install_requires=["requests==2.22.0", "pytest==4.6.2"]
)