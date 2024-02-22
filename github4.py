from github import Github

# Provide GitHub personal access token 
# Make sure to enable the necessary permissions (e.g., repo) for the token
ACCESS_TOKEN = 'our_access_token'

# Repository information
repository_owner = 'repository_owner_username'
repository_name = 'repository_name'

# Initialize PyGithub client
g = Github(ACCESS_TOKEN)

# Get the repository
repo = g.get_repo(f"{repository_owner}/{repository_name}")

# Specify the path to our database file(s)
database_paths = ['path/to/database/file.sql', 'path/to/another/database/file.sql']

# Fetch commit history for each database file
for database_path in database_paths:
    try:
        commits = repo.get_commits(path=database_path)
        print(f"Commit history for {database_path}:")
        for commit in commits:
            print(f"Date: {commit.commit.author.date}, Message: {commit.commit.message}")
        print("\n")
    except Exception as e:
        print(f"An error occurred while fetching commit history for {database_path}: {str(e)}")
