#!/usr/bin/env python3
"""
GitHub Achievement Unlocker
Unlocks: Quickdraw, YOLO, Pull Shark, Pair Extraordinaire

Usage:
    export GITHUB_TOKEN=your_token_here
    python achievement_unlocker.py
"""

import requests
import time
import json
import os

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    print("Error: Set GITHUB_TOKEN environment variable")
    exit(1)

USERNAME = "vedparkasharya"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

BASE_URL = "https://api.github.com"


def create_repo(repo_name, description="Achievement unlocker repo", private=False):
    """Create a new repository"""
    url = f"{BASE_URL}/user/repos"
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": True,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "has_discussions": True
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f"Created repo: {repo_name}")
        return response.json()
    elif response.status_code == 422:
        print(f"Repo {repo_name} might already exist, trying to get it...")
        return get_repo(repo_name)
    else:
        print(f"Error creating repo: {response.status_code} - {response.text}")
        return None


def get_repo(repo_name):
    """Get existing repository"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None


def create_issue(repo_name, title, body="Test issue for achievement unlocking"):
    """Create an issue"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/issues"
    data = {"title": title, "body": body}
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        issue = response.json()
        print(f"Created issue #{issue['number']}: {title}")
        return issue
    print(f"Error creating issue: {response.status_code}")
    return None


def close_issue(repo_name, issue_number):
    """Close an issue"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/issues/{issue_number}"
    data = {"state": "closed"}
    response = requests.patch(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        print(f"Closed issue #{issue_number}")
        return True
    print(f"Error closing issue: {response.status_code}")
    return False


def get_default_branch_sha(repo_name):
    """Get the SHA of the default branch"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/ref/heads/main"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["object"]["sha"]
    # Try master
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/ref/heads/master"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["object"]["sha"]
    return None


def create_branch(repo_name, branch_name, sha):
    """Create a new branch"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/refs"
    data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f"Created branch: {branch_name}")
        return True
    elif response.status_code == 422:
        print(f"Branch {branch_name} might already exist")
        return True
    print(f"Error creating branch: {response.status_code} - {response.text}")
    return False


def get_file_sha(repo_name, path, branch="main"):
    """Get file SHA for updating"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/contents/{path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["sha"]
    return None


def create_or_update_file(repo_name, path, content, message, branch, file_sha=None):
    """Create or update a file"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/contents/{path}"
    import base64
    content_b64 = base64.b64encode(content.encode()).decode()
    data = {
        "message": message,
        "content": content_b64,
        "branch": branch
    }
    if file_sha:
        data["sha"] = file_sha
    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code in [200, 201]:
        print(f"Created/updated file: {path}")
        return response.json()
    print(f"Error creating file: {response.status_code} - {response.text}")
    return None


def create_pull_request(repo_name, title, head, base="main", body=""):
    """Create a pull request"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/pulls"
    data = {
        "title": title,
        "head": head,
        "base": base,
        "body": body
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        pr = response.json()
        print(f"Created PR #{pr['number']}: {title}")
        return pr
    print(f"Error creating PR: {response.status_code} - {response.text}")
    return None


def merge_pull_request(repo_name, pr_number, commit_message="", merge_method="merge"):
    """Merge a pull request"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/pulls/{pr_number}/merge"
    data = {
        "merge_method": merge_method
    }
    if commit_message:
        data["commit_message"] = commit_message
    response = requests.put(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        print(f"Merged PR #{pr_number}")
        return True
    print(f"Error merging PR: {response.status_code} - {response.text}")
    return False


def close_pull_request(repo_name, pr_number):
    """Close a pull request without merging"""
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/pulls/{pr_number}"
    data = {"state": "closed"}
    response = requests.patch(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        print(f"Closed PR #{pr_number}")
        return True
    return False


def unlock_quickdraw():
    """Unlock Quickdraw achievement - close issue/PR within 5 minutes"""
    print("\n" + "="*50)
    print("UNLOCKING: Quickdraw")
    print("="*50)
    
    repo_name = "quickdraw-achievement"
    repo = create_repo(repo_name, "Quickdraw achievement unlocker")
    if not repo:
        return False
    
    # Method 1: Create and immediately close an issue
    print("\nMethod 1: Quick issue close...")
    issue = create_issue(repo_name, "Quickdraw test issue", "This issue will be closed immediately to unlock Quickdraw!")
    if issue:
        time.sleep(2)
        close_issue(repo_name, issue["number"])
        print("Quickdraw should be unlocked via issue!")
    
    time.sleep(3)
    
    # Method 2: Create and immediately close a PR
    print("\nMethod 2: Quick PR close...")
    sha = get_default_branch_sha(repo_name)
    if sha:
        branch_name = "quickdraw-branch"
        create_branch(repo_name, branch_name, sha)
        
        # Create a quick file change
        file_content = "# Quickdraw\nThis file was created to unlock the Quickdraw achievement!"
        create_or_update_file(repo_name, "QUICKDRAW.md", file_content, 
                            "Quickdraw achievement commit", branch_name)
        
        pr = create_pull_request(repo_name, "Quickdraw PR", branch_name, body="This PR will be closed immediately!")
        if pr:
            time.sleep(2)
            close_pull_request(repo_name, pr["number"])
            print("Quickdraw should be unlocked via PR!")
    
    print("Quickdraw unlocking complete!")
    return True


def unlock_yolo():
    """Unlock YOLO achievement - merge a PR without review"""
    print("\n" + "="*50)
    print("UNLOCKING: YOLO")
    print("="*50)
    
    repo_name = "yolo-achievement"
    repo = create_repo(repo_name, "YOLO achievement unlocker")
    if not repo:
        return False
    
    sha = get_default_branch_sha(repo_name)
    if not sha:
        print("Could not get default branch SHA")
        return False
    
    branch_name = "yolo-feature-branch"
    create_branch(repo_name, branch_name, sha)
    
    # Create a README update
    file_content = """# YOLO Achievement

This repository was created to unlock the YOLO GitHub achievement!

## What is YOLO?
YOLO is earned by merging a pull request without code review.

## Unlocked!
This badge was earned by merging a PR without review - because sometimes you just gotta send it!

```
const life = {
  review: false,
  merge: true,
  yolo: true
};
```

*Merged without review - living dangerously since 2026*
"""
    create_or_update_file(repo_name, "YOLO.md", file_content, 
                        "Add YOLO achievement documentation", branch_name)
    
    pr = create_pull_request(repo_name, "YOLO: Add achievement docs", branch_name, 
                            body="This PR will be merged without review to unlock YOLO badge!")
    if pr:
        time.sleep(3)
        merge_pull_request(repo_name, pr["number"], 
                         commit_message="YOLO! Merging without review to unlock achievement")
        print("YOLO achievement should be unlocked!")
        return True
    return False


def unlock_pull_shark():
    """Unlock Pull Shark achievement - get PRs merged"""
    print("\n" + "="*50)
    print("UNLOCKING: Pull Shark")
    print("="*50)
    
    repo_name = "pull-shark-achievement"
    repo = create_repo(repo_name, "Pull Shark achievement unlocker")
    if not repo:
        return False
    
    sha = get_default_branch_sha(repo_name)
    if not sha:
        return False
    
    # Create multiple PRs and merge them to build up Pull Shark
    pr_data = [
        ("feature/docs", "PULLSHARK.md", "# Pull Shark Achievement\n\nWorking towards Pull Shark badge!"),
        ("feature/readme", "README_UPDATE.md", "# README Update\n\nImproving documentation!"),
        ("feature/config", "CONFIG.md", "# Configuration\n\nAdding project configuration!"),
    ]
    
    merged_count = 0
    for branch, filename, content in pr_data:
        print(f"\nCreating PR from branch: {branch}")
        create_branch(repo_name, branch, sha)
        create_or_update_file(repo_name, filename, content, f"Add {filename}", branch)
        pr = create_pull_request(repo_name, f"Add {filename}", branch, 
                                body=f"Adding {filename} to unlock Pull Shark!")
        if pr:
            time.sleep(3)
            if merge_pull_request(repo_name, pr["number"]):
                merged_count += 1
                print(f"Merged PR #{pr['number']} - Total merged: {merged_count}")
        time.sleep(2)
    
    print(f"\nPull Shark progress: {merged_count} PRs merged!")
    return merged_count > 0


def unlock_pair_extraordinaire():
    """Unlock Pair Extraordinaire - co-authored commit in merged PR"""
    print("\n" + "="*50)
    print("UNLOCKING: Pair Extraordinaire")
    print("="*50)
    
    repo_name = "pair-extraordinaire-achievement"
    repo = create_repo(repo_name, "Pair Extraordinaire achievement unlocker")
    if not repo:
        return False
    
    sha = get_default_branch_sha(repo_name)
    if not sha:
        return False
    
    branch_name = "pair-feature"
    create_branch(repo_name, branch_name, sha)
    
    # Create a file with co-authored-by in the commit
    # Note: We'll use the Git API directly for co-authored commits
    import base64
    
    file_content = """# Pair Extraordinaire Achievement

This repository was created to unlock the Pair Extraordinaire GitHub achievement!

## What is Pair Extraordinaire?
Earned by co-authoring commits on merged pull requests.

## Collaboration is Key
This badge celebrates teamwork and pair programming!

```python
def collaborate():
    return "Better code through teamwork!"
```

*Built with a collaborator - because two minds are better than one!*
"""
    
    # Use Git API to create a commit with co-author
    url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/contents/PAIR.md"
    content_b64 = base64.b64encode(file_content.encode()).decode()
    
    # For co-authored commit, we need to use git data API
    # First, get the current tree and create a new blob
    
    # Create blob
    blob_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/blobs"
    blob_data = {
        "content": file_content,
        "encoding": "utf-8"
    }
    blob_resp = requests.post(blob_url, headers=HEADERS, json=blob_data)
    if blob_resp.status_code != 201:
        print(f"Error creating blob: {blob_resp.status_code}")
        return False
    
    blob_sha = blob_resp.json()["sha"]
    
    # Get the tree SHA from the branch
    ref_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/ref/heads/{branch_name}"
    ref_resp = requests.get(ref_url, headers=HEADERS)
    if ref_resp.status_code != 200:
        print(f"Error getting ref: {ref_resp.status_code}")
        return False
    
    parent_sha = ref_resp.json()["object"]["sha"]
    
    # Get the commit to find tree
    commit_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/commits/{parent_sha}"
    commit_resp = requests.get(commit_url, headers=HEADERS)
    tree_sha = commit_resp.json()["tree"]["sha"]
    
    # Create a new tree
    tree_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/trees"
    tree_data = {
        "base_tree": tree_sha,
        "tree": [{
            "path": "PAIR.md",
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        }]
    }
    tree_resp = requests.post(tree_url, headers=HEADERS, json=tree_data)
    if tree_resp.status_code != 201:
        print(f"Error creating tree: {tree_resp.status_code}")
        return False
    new_tree_sha = tree_resp.json()["sha"]
    
    # Create commit with co-author
    new_commit_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/commits"
    commit_message = """Add Pair Extraordinaire documentation

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>"""
    
    commit_data = {
        "message": commit_message,
        "tree": new_tree_sha,
        "parents": [parent_sha]
    }
    commit_resp = requests.post(new_commit_url, headers=HEADERS, json=commit_data)
    if commit_resp.status_code != 201:
        print(f"Error creating commit: {commit_resp.status_code}")
        return False
    
    new_commit_sha = commit_resp.json()["sha"]
    
    # Update the reference
    update_ref_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/git/refs/heads/{branch_name}"
    ref_data = {"sha": new_commit_sha}
    ref_resp = requests.patch(update_ref_url, headers=HEADERS, json=ref_data)
    if ref_resp.status_code != 200:
        print(f"Error updating ref: {ref_resp.status_code}")
        return False
    
    print("Created commit with co-author!")
    
    # Create PR and merge it
    pr = create_pull_request(repo_name, "Pair Extraordinaire: Add co-authored docs", branch_name,
                            body="This PR contains a co-authored commit to unlock Pair Extraordinaire!")
    if pr:
        time.sleep(3)
        merge_pull_request(repo_name, pr["number"], 
                         commit_message="Merge co-authored PR for Pair Extraordinaire")
        print("Pair Extraordinaire should be unlocked!")
        return True
    return False


def main():
    print("="*50)
    print("GITHUB ACHIEVEMENT UNLOCKER")
    print("="*50)
    print(f"Target User: {USERNAME}")
    print("Achievements to unlock:")
    print("  1. Quickdraw (close issue/PR within 5 min)")
    print("  2. YOLO (merge PR without review)")
    print("  3. Pull Shark (merged PRs)")
    print("  4. Pair Extraordinaire (co-authored commit)")
    print("="*50)
    
    # Unlock achievements
    try:
        unlock_quickdraw()
        time.sleep(5)
        
        unlock_yolo()
        time.sleep(5)
        
        unlock_pull_shark()
        time.sleep(5)
        
        unlock_pair_extraordinaire()
        
        print("\n" + "="*50)
        print("ACHIEVEMENT UNLOCKING COMPLETE!")
        print("="*50)
        print("Check your profile in a few minutes to see the badges!")
        print("Note: Some achievements may take time to appear on your profile.")
        
    except Exception as e:
        print(f"Error during achievement unlocking: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
