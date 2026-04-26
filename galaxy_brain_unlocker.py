#!/usr/bin/env python3
"""
Galaxy Brain Achievement Unlocker
Unlocks: Galaxy Brain - 2 accepted answers in discussions

Usage:
    export GITHUB_TOKEN=your_token_here
    python galaxy_brain_unlocker.py
"""

import requests
import time
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


def create_repo_with_discussions(repo_name, description="Galaxy Brain achievement unlocker"):
    """Create a new repository with discussions enabled"""
    url = f"{BASE_URL}/user/repos"
    data = {
        "name": repo_name,
        "description": description,
        "private": False,
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
        print(f"Repo {repo_name} might already exist, getting it...")
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


def create_discussion(repo_name, category_id, title, body):
    """Create a discussion using GraphQL API"""
    # First get the repository ID
    repo = get_repo(repo_name)
    if not repo:
        return None
    
    repo_id = repo["node_id"]
    
    # GraphQL mutation to create discussion
    graphql_url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # First, let's list discussion categories using REST API
    categories_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/discussions/categories"
    cat_resp = requests.get(categories_url, headers=HEADERS)
    if cat_resp.status_code == 200:
        categories = cat_resp.json()
        if categories:
            category = categories[0]  # Use first available category
            print(f"Using discussion category: {category['name']} (ID: {category['id']})")
            
            # Create discussion using GraphQL
            query = """
            mutation($repositoryId: ID!, $categoryId: ID!, $body: String!, $title: String!) {
              createDiscussion(input: {
                repositoryId: $repositoryId,
                categoryId: $categoryId,
                body: $body,
                title: $title
              }) {
                discussion {
                  id
                  number
                  url
                }
              }
            }
            """
            
            variables = {
                "repositoryId": repo_id,
                "categoryId": category["node_id"],
                "body": body,
                "title": title
            }
            
            response = requests.post(graphql_url, headers=headers, 
                                   json={"query": query, "variables": variables})
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"] and "createDiscussion" in data["data"]:
                    discussion = data["data"]["createDiscussion"]["discussion"]
                    print(f"Created discussion #{discussion['number']}: {title}")
                    return discussion
                elif "errors" in data:
                    print(f"GraphQL errors: {data['errors']}")
            else:
                print(f"GraphQL request failed: {response.status_code}")
    
    # Fallback: Try REST API for discussions (might not work for creation)
    print("Trying alternative method...")
    
    # Create as an issue-like discussion by posting to discussions endpoint
    discussions_url = f"{BASE_URL}/repos/{USERNAME}/{repo_name}/discussions"
    # This endpoint might not support POST directly
    # Let's try the GraphQL approach with different category handling
    
    return None


def answer_discussion(discussion_id, body):
    """Answer a discussion"""
    # Use GraphQL to create a discussion comment
    graphql_url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    query = """
    mutation($discussionId: ID!, $body: String!) {
      addDiscussionComment(input: {
        discussionId: $discussionId,
        body: $body
      }) {
        comment {
          id
          url
        }
      }
    }
    """
    
    variables = {
        "discussionId": discussion_id,
        "body": body
    }
    
    response = requests.post(graphql_url, headers=headers,
                           json={"query": query, "variables": variables})
    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"] and "addDiscussionComment" in data["data"]:
            comment = data["data"]["addDiscussionComment"]["comment"]
            print(f"Added answer comment: {comment['url']}")
            return comment
        elif "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
    else:
        print(f"Error adding comment: {response.status_code}")
    
    return None


def mark_answer_accepted(discussion_id, comment_id):
    """Mark a discussion comment as the accepted answer"""
    graphql_url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    query = """
    mutation($id: ID!) {
      markDiscussionCommentAsAnswer(input: {
        id: $id
      }) {
        discussion {
          id
          url
          answerChosenAt
        }
      }
    }
    """
    
    variables = {
        "id": comment_id
    }
    
    response = requests.post(graphql_url, headers=headers,
                           json={"query": query, "variables": variables})
    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"] and "markDiscussionCommentAsAnswer" in data["data"]:
            result = data["data"]["markDiscussionCommentAsAnswer"]["discussion"]
            print(f"Marked answer as accepted! Discussion: {result['url']}")
            return True
        elif "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
    else:
        print(f"Error marking answer: {response.status_code}")
        print(response.text)
    
    return False


def unlock_galaxy_brain():
    """Unlock Galaxy Brain achievement - 2 accepted answers"""
    print("\n" + "="*50)
    print("UNLOCKING: Galaxy Brain")
    print("="*50)
    print("Galaxy Brain requires 2 accepted answers in discussions.")
    print("Note: You need to mark your own answers as accepted.")
    
    repo_name = "galaxy-brain-achievement"
    repo = create_repo_with_discussions(repo_name)
    if not repo:
        print("Failed to create repository")
        return False
    
    time.sleep(3)
    
    # Create discussions with questions
    discussions_data = [
        {
            "title": "How do I get started with this project?",
            "body": "I'm new to this project and would love some guidance on how to get started. What are the first steps?"
        },
        {
            "title": "Best practices for contributing?",
            "body": "What are the best practices for contributing to this project? Any guidelines I should follow?"
        }
    ]
    
    accepted_count = 0
    
    for i, disc_data in enumerate(discussions_data, 1):
        print(f"\n--- Discussion {i} ---")
        
        # Create the discussion
        discussion = create_discussion(repo_name, None, 
                                     disc_data["title"], disc_data["body"])
        if not discussion:
            print(f"Failed to create discussion {i}, trying next...")
            continue
        
        time.sleep(2)
        
        # Answer the discussion
        answer_body = f"""Great question! Here's a comprehensive answer:

## Solution

1. **First Step**: Start by reading the documentation thoroughly
2. **Second Step**: Set up your development environment  
3. **Third Step**: Join the community and ask questions

## Additional Resources

- Check out the README for setup instructions
- Review existing issues to understand current priorities
- Don't hesitate to ask for help!

Hope this helps! Let me know if you have any other questions.

---
*This answer was crafted to help unlock the Galaxy Brain achievement*"""
        
        comment = answer_discussion(discussion["id"], answer_body)
        if not comment:
            print(f"Failed to add answer to discussion {i}")
            continue
        
        time.sleep(2)
        
        # Mark the answer as accepted
        if mark_answer_accepted(discussion["id"], comment["id"]):
            accepted_count += 1
            print(f"Discussion {i} answer accepted! ({accepted_count}/2)")
        
        time.sleep(3)
    
    print(f"\nGalaxy Brain progress: {accepted_count}/2 answers accepted!")
    if accepted_count >= 2:
        print("Galaxy Brain should be unlocked!")
    
    return accepted_count >= 2


if __name__ == "__main__":
    unlock_galaxy_brain()
