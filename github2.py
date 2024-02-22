from git import Repo

# Path to the local repository directory
repo_path = '/path/to/our/local/repository'

# Initialize a Repo object with the repository path
repo = Repo(repo_path)

# Iterate through commits and print commit details including timestamp
for commit in repo.iter_commits():
    print("Commit:", commit.hexsha)
    print("Author:", commit.author.name)
    print("Date:", commit.authored_datetime)
    print("Message:", commit.message)
    print()
