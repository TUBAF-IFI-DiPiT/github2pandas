# use pipenv-setup to generate the requirement list
# https://pypi.org/project/pipenv-setup/

from setuptools import setup
from github2pandas import __version__


with open("README.md", "r") as f:
   long_description = f.read()



setup(
   name="github2pandas",
   version=__version__,
   packages=["github2pandas"],
   license="BSD 2",
   description="github2pandas supports the aggregation of project activities in a GitHub repository and makes them available in pandas dataframes",
   long_description = long_description,
   long_description_content_type="text/markdown",
   author="Maximilian Karl & Sebastian Zug",
   url="https://github.com/TUBAF-IFI-DiPiT/github2pandas",
   download_url=f"https://github.com/TUBAF-IFI-DiPiT/github2pandas/archive/github2pandas-{__version__}.tar.gz",
   keywords=["git", "github", "collaborative code development", "git mining"],
   install_requires=[
      "pygit2>=1.9.1",
      "requests>=2.27.1",
      "pygithub>=1.55",
      "git2net>=1.6.0",
      "pysqlite3>=0.4.7",
      "pandas>=1.2.4",
      "human-id>=0.2.0",
      "xlsxwriter>=3.0.3",
   ], 
   classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
   ],
   python_requires=">=3.9"
)
