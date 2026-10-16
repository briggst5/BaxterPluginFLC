import os
import requests
from urllib.parse import quote


def main():
    org = os.environ.get("ADO_ORG")
    project_raw = os.environ.get("ADO_PROJECT")
    repo = os.environ.get("ADO_REPO")
    pr_id = os.environ.get("PR_ID", os.environ.get("SYSTEM_PULLREQUEST_PULLREQUESTID", ""))
    token = os.environ["SYSTEM_ACCESSTOKEN"]

    if not org or not project_raw or not repo:
        raise ValueError("ADO_ORG, ADO_PROJECT, and ADO_REPO must be set")
    project = quote(project_raw)
    if not pr_id:
        raise ValueError("PR_ID or SYSTEM_PULLREQUEST_PULLREQUESTID must be set")

    with open("review.md") as f:
        content = f.read()

    print(f"Review content:\n{content[:500]}")
    print(f"Review length: {len(content)} chars")

    url = f"{org}{project}/_apis/git/repositories/{repo}/pullRequests/{pr_id}/threads?api-version=7.1"

    body = {
        "comments": [
            {"parentCommentId": 0, "content": content, "commentType": 1}
        ],
        "status": 1,
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
    )
    print(f"Post comment status: {resp.status_code}")
    print(f"Post comment response: {resp.text}")
    if resp.status_code >= 400:
        raise Exception(f"Failed to post comment: {resp.status_code} {resp.text}")


if __name__ == "__main__":
    main()
