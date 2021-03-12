class CommentData(dict):
    """
    Class extends a dict in order to restrict the comment data set to defined keys.

    Attributes
    ----------
    KEYS: list
        List of allowed keys.
    PARENTS: list
        List of possible parents.
        
    Methods
    -------
        __init__(self, parent_name)
            Check parent_name and set all keys to None.
        __setitem__(self, key, val)
            Set Value if Key is in KEYS.
    
    """

    KEYS = [
        "body",
        "created_at",
        "id",
        "author",
        "reactions_count"
    ]
    PARENTS = [
        "issue", 
        "pull_request"
    ]
    
    def __init__(self, parent_name):
        """
        __init__(self, parent_name)

        Check parent_name and set all keys to None.

        Parameters
        ----------
        parent_name: str
            Name of the parent.

        """

        if not parent_name in CommentData.PARENTS:
            raise ValueError
        CommentData.KEYS.append(parent_name + "_id")
        for key in CommentData.KEYS:
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

        if key not in CommentData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)

class EventData(dict):
    """
    Class extends a dict in order to restrict the event data set to defined keys.

    Attributes
    ----------
    KEYS: list
        List of allowed keys.
    PARENTS: list
        List of possible parents.
        
    Methods
    -------
        __init__(self, parent_name)
           Check parent_name and set all keys to None.
        __setitem__(self, key, val)
            Set Value if Key is in KEYS.
    
    """

    KEYS = [
        "author",
        "commit_id",
        "created_at",
        "event",
        "id",
        "label",
        "assignee",
        "assigner",
    ]
    PARENTS = [
        "issue", 
        "pull_request"
    ]

    def __init__(self, parent_name):
        """
        __init__(self, parent_name)

        Check parent_name and set all keys to None.

        Parameters
        ----------
        parent_name: str
            Name of the parent.

        """

        if not parent_name in EventData.PARENTS:
            raise ValueError
        EventData.KEYS.append(parent_name + "_id")
        for key in EventData.KEYS:
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

        if key not in EventData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)

class ReactionData(dict):
    """
    Class extends a dict in order to restrict the reaction data set to defined keys.

    Attributes
    ----------
    KEYS: list
        List of allowed keys.
    PARENTS: list
        List of possible parents.
        
    Methods
    -------
        __init__(self, parent_name)
            Check parent_name and set all keys to None.
        __setitem__(self, key, val)
            Set Value if Key is in KEYS.
    
    """

    KEYS = [
        "content",
        "created_at",
        "id",
        "author"
    ]
    PARENTS = [
        "issue", 
        "comment"
    ]

    def __init__(self, parent_name):
        """
        __init__(self, parent_name)

        Check parent_name and set all keys to None.

        Parameters
        ----------
        parent_name: str
            Name of the parent.

        """

        if not parent_name in ReactionData.PARENTS:
            raise ValueError
        ReactionData.KEYS.append(parent_name + "_id")
        for key in ReactionData.KEYS:
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

        if key not in ReactionData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)
    
class UserData(dict):
    """
    Class extends a dict in order to restrict the user data set to defined keys.

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
        "anonym_uuid",
        "id",
        "name",
        "email",
        "login",
    ]

    def __init__(self):
        """
        __init__(self)

        Set all keys in KEYS to None.

        """
        for key in UserData.KEYS:
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

        if key not in UserData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)