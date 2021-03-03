#!/usr/bin/python

import os
from pathlib import Path
import pandas as pd

def replace_dublicates(pd_table, column_name, dublicates):

    for name in dublicates:
        pd_table[column_name].replace(name[0], name[1],
                                        inplace=True)

    return pd_table


def apply_python_date_format(pd_table, source_colum, destination_column):

    pd_table[destination_column] = pd.to_datetime(pd_table[source_colum], format="%Y-%m-%d %H:%M:%S")

    return pd_table
