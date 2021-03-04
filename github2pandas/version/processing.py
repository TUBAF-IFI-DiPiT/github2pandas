import pandas as pd
from pathlib import Path

from . import aggregation
from .. import utility 

def identify_commits_in_branches(pd_commits_raw):
  pd_commits_raw["in_dev_branches"] = pd_commits_raw.branches.apply(lambda x: True if len(set(x.split(","))- set(["master"])) > 0 else False)
  return pd_commits_raw
