class IssueData(dict):
    """
    Class extends a dict in order to restrict the issue data set to defined keys.

    Attributes
    ----------
    KEYS: list
        List of allowed keys.
        
    Methods
    -------
        __init__(self)
            Set all keys in KEYS to None.
        __setitem__(self, key, val)
            Set Value if Key is in KEYS.
    
    """

    KEYS = [
        "assignees",
        "assignees_count",
        "body",
        "closed_at",
        "closed_by",
        "created_at",
        "id",
        "labels",
        "labels_count",
        "milestone_id",
        "state",
        "title",
        "updated_at",
        "author",
        "comments_count",
        "event_count",
        "reaction_count"
    ]
    
    def __init__(self):
        """
        __init__(self)

        Set all keys in KEYS to None.

        """

        for key in IssueData.KEYS:
            self[key] = None
    
    def __setitem__(self, key, val):
        """
        __setitem__(self, key, val)

        Set Value if Key is in KEYS.

        Parameters
        ----------
        key: str
            Key for dict
        val
            Value for dict
        """

        if key not in IssueData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)