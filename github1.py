from github import Github

# GitHub personal access token
ACCESS_TOKEN = 'our_access_token_here'

# Repository owner and name
repository_owner = 'owner_username'
repository_name = 'repository_name'

# Initialize GitHub instance
g = Github(ACCESS_TOKEN)

# Get the repository
repo = g.get_repo(f"{repository_owner}/{repository_name}")

# Get the last push timestamp
last_push = repo.get_commits().reversed[0].commit.committer.date
print("Last push timestamp:", last_push)
