class PullRequestData(dict):
    """
    Class extends a dict in order to restrict the pull request data set to defined keys.

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
        "id",
        "assignees",
        "assignees_count",
        "body",
        "title",
        "changed_files",
        "closed_at",
        "created_at",
        "deletions",
        "additions",
        "deletions",
        "labels",
        "labels_count",
        "merged",
        "merged_at",
        "merged_by",
        "milestone_id",
        "state",
        "updated_at",
        "author",
        "comments_count",
        "issue_events_count",
        "reviews_count"
    ]
    
    def __init__(self):
        """
        __init__(self)

        Set all keys in KEYS to None.

        """

        for key in PullRequestData.KEYS:
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

        if key not in PullRequestData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)

class PullRequestReviewData(dict):
    """
    Class extends a dict in order to restrict the pull request review data set to defined keys.

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
        "pull_request_id",
        "id",
        "author",
        "body",
        "state",
        "submitted_at"
    ]
    
    def __init__(self):
        """
        __init__(self)

        Set all keys in KEYS to None.

        """

        for key in PullRequestReviewData.KEYS:
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

        if key not in PullRequestReviewData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)