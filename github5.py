from github import Github

# Provide our GitHub personal access token
ACCESS_TOKEN = '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'

# Repository information
repository_owner = 'SadikSaaho'
repository_name = 'dummydb'

# Path to the database file
database_file_path = 'path/to/database/file.sql'

# Initialize PyGithub client
g = Github(ACCESS_TOKEN)

# Get the repository
repo = g.get_repo(f"{repository_owner}/{repository_name}")

try:
    # Get commits for the specified database file
    commits = repo.get_commits(path=database_file_path)
    
    # Print commit date and time
    print(f"Commit history for {database_file_path}:")
    for commit in commits:
        commit_date = commit.commit.author.date
        print(f"Commit Date: {commit_date}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
