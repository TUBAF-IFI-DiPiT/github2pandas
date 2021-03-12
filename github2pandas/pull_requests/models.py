class PullRequestData(dict):
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
        for key in PullRequestData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in PullRequestData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)

class PullRequestReviewData(dict):
    KEYS = [
        "pull_request_id",
        "id",
        "author",
        "body",
        "state",
        "submitted_at"
    ]
    def __init__(self):
        for key in PullRequestReviewData.KEYS:
            self[key] = None
    def __setitem__(self, key, val):
        if key not in PullRequestReviewData.KEYS:
            raise KeyError
        dict.__setitem__(self, key, val)