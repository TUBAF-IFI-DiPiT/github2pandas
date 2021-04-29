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
   download_url="https://github.com/user/reponame/archive/v_01.tar.gz",
   keywords=["git", "github", "collaborative code development", "git mining"],
   install_requires=[
      "pygit2==1.5.0",
      "pyyaml==5.4.1",
      "requests==2.25.1",
      "datetime==4.3",
      "pygithub==1.54.1",
      "argparse==1.4.0",
      "pydriller==1.15.2",
      "git2net==1.4.10",
      "pysqlite3==0.4.6",
      "selenium==3.141.0",
      "python-dotenv==0.17.0",
      "pandas==1.2.4",
      "jupyter==1.0.0",
      "sphinx==3.5.4",
      "m2r2==0.2.7",
      "pypiwin32==223; sys_platform == 'win32'",
      "human-id==0.1.0.post3",
      "psutil==5.8.0",
      "sphinx-rtd-theme==0.5.2"
   ], 
   classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
   ],
   python_requires=">=3.8"
)
