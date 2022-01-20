import os
from typing import Iterable
import pandas as pd
import sys

def progress_bar(iterable:Iterable, prefix="", size:int=60, file=sys.stdout):
    """
    progress_bar(iterable, prefix="", size=60, file=sys.stdout)

    Prints our a progress bar.

    Parameters
    ----------
    iterable : Iterable
        A iterable as input. 
    prefix : str, default=""
        String infront of the progress bar.
    size : int
        Size of the progress bar.
    file : Any , default=sys.stdout
        File to print out the progress bar.

    """
    count = len(iterable)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(iterable):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

def copy_valid_params(base_dict,input_params):
    params = base_dict
    for param in input_params:
        if param in params:
            params[param] = input_params[param]
    return params

def file_error_handling(func, path, exc_info):
    """
    handleError(func, path, exc_info)

    Error handler function which will try to change file permission and call the calling function again.

    Parameters
    ----------
    func : Function
        Calling function.
    path : str
        Path of the file which causes the Error.
    exc_info : str
        Execution information.
    
    """
    
    print('Handling Error for file ' , path)
    print(exc_info)
    # Check if file access issue
    if not os.access(path, os.W_OK):
        # Try to change the permision of file
        os.chmod(path, stat.S_IWUSR)
        # call the calling function again
        func(path)

def apply_datetime_format(pd_table, source_column, destination_column=None):
        """
        apply_datetime_format(pd_table, source_column, destination_column=None)

        Provide equal date formate for all timestamps

        Parameters
        ----------
        pd_table : pandas Dataframe
            List of NamedUser
        source_column : str
            Source column name.
        destination_column : str, default=None
            Destination column name. Saves to Source if None.

        Returns
        -------
        str
            String which contains all assignees.
        
        """
        if not destination_column:
            destination_column = source_column
        pd_table[destination_column] = pd.to_datetime(pd_table[source_column], format="%Y-%m-%d %H:%M:%S")

        return pd_table