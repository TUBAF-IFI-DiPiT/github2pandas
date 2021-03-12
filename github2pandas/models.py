class CommentData(dict):
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
        if not parent_name in CommentData.PARENTS:
            raise ValueError
        CommentData.KEYS.append(parent_name + "_id")
        for key in CommentData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in CommentData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)

class EventData(dict):
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
        if not parent_name in EventData.PARENTS:
            raise ValueError
        EventData.KEYS.append(parent_name + "_id")
        for key in EventData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in EventData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)

class ReactionData(dict):
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
        if not parent_name in ReactionData.PARENTS:
            raise ValueError
        ReactionData.KEYS.append(parent_name + "_id")
        for key in ReactionData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in ReactionData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)
    
class UserData(dict):
    KEYS = [
        "anonym_uuid",
        "id",
        "name",
        "email",
        "login",
    ]
    def __init__(self):
        for key in UserData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in UserData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)