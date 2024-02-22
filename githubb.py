from github import Github

# Replace 'our_access_token' with the actual GitHub personal access token
access_token = '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'

# Replace 'our_username' with the GitHub username
username = 'SadikSaaho' 

# Replace 'our_repository' with the name of the GitHub repository
repository_name = 'dummydb' 

# Initialize the Github object with the access token
g = Github(access_token)

# Get the specified repository
repo = g.get_user(username).get_repo(repository_name)

# Retrieve commit history
commits = repo.get_commits()

# Print commit details including timestamp
for commit in commits:
    print("Commit ID:", commit.sha)
    print("Author:", commit.commit.author.name)
    print("Date:", commit.commit.author.date)
    print("Message:", commit.commit.message)
    print()
