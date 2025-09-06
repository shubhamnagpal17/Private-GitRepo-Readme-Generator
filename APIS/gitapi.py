import requests

def extract_owner_repo(url):
    """
    GitHub repo URL se owner aur repo extraction
    Supports URLs with or without .git
    Example URL:
        https://github.com/username/repo.git
        https://github.com/username/repo
    Returns:
        owner (str), repo_name (str)
    """
    url_part = url.rstrip('/').split("/")
    if len(url_part) < 2:
        raise ValueError("Invalid GitHub repository URL")
    
    owner = url_part[-2]   # second last part
    repo_name = url_part[-1]  # last part
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]  # remove .git if present
    return owner, repo_name


def fetch_repo_metadata(owner, repo, token=None):
    '''
    Fetches metadata of public/private repos and returns as dictionary
    dict contains reponame, repo_url, desc, language, topic,
    stars, license, files name as string

    Returns:
        metadata (dict)
    '''
    # headers for API request
    headers = {"Accept": "application/vnd.github.mercy-preview+json"}  # for topics
    if token:
        headers["Authorization"] = f"token {token}"  # add token for private repos

    # Fetch repo metadata
    repo_data_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(repo_data_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repo: {response.status_code} - {response.text}")
    repo_data = response.json()

    # Fetch file contents
    content_file_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    cont_response = requests.get(content_file_url, headers=headers)
    files_list = []
    if cont_response.status_code == 200:
        for f in cont_response.json():
            files_list.append(f["name"])

    # Prepare metadata dictionary
    metadata = {
        "repo_name": repo_data.get('name'),
        "repo_url": repo_data.get("html_url"),
        "repo_description": repo_data.get("description"),
        "language": repo_data.get("language"),
        "topics": ", ".join(repo_data.get("topics", [])),
        "stars": repo_data.get("stargazers_count", 0),
        "license_name": repo_data.get("license", {}).get("name") if repo_data.get("license") else "Not specified",
        "files": ", ".join(files_list)
    }

    return metadata
