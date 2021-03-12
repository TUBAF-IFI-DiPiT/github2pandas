class IssueData(dict):
    KEYS = [
        "assignees",
        "assignees_count",
        "body",
        "closed_at",
        "closedBy",
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
        for key in IssueData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in IssueData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)