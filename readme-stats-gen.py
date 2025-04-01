import requests
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})
import time

# Replace with your GitHub username
GITHUB_USERNAME = 'guilhermevbagio'

# GitHub API URL for user repositories
REPOS_URL = f'https://api.github.com/users/{GITHUB_USERNAME}/repos'

mocking = False  # Define `mocking` globally at the start

def check_rate_limit(response):
    global mocking  # Declare global inside function
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response.headers.get('X-RateLimit-Reset', time.time()))

    if remaining == 0:
        wait_time = reset_time - time.time() + 1
        print(f"Rate limit exceeded. Waiting for {wait_time:.2f} seconds.")
        mocking = True  # Set to True when rate limit is exceeded
        return False
    else:
        mocking = False  # Ensure it's False if limit is not exceeded
        return True

# Function to get repositories
def get_repos():
    repos = []
    page = 1
    while True:
        response = requests.get(REPOS_URL, params={'page': page, 'per_page': 100})
        check_rate_limit(response)  # Call without assigning to `mocking`
        
        if response.status_code != 200:
            print(f"Error fetching repos: {response.status_code}")
            break
        repos.extend(response.json())
        if len(response.json()) < 100:
            break
        page += 1
    return repos

# Function to get languages for a repository
def get_languages(repo_name):
    languages_url = f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/languages'
    response = requests.get(languages_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching languages for {repo_name}: {response.status_code}")
        return {}

# Function to aggregate language usage
def aggregate_languages():
    repos = get_repos()
    language_usage = {}
    for repo in repos:
        repo_name = repo['name']
        languages = get_languages(repo_name)
        for lang, bytes in languages.items():
            language_usage[lang] = language_usage.get(lang, 0) + bytes
    return language_usage

# Function to generate the bar chart
def generate_bar_chart(language_usage):
    global mocking  # Ensure the function reads `mocking`

    if mocking:
        languages = ["Java", "Vue", "Python", "Scala", "C++", "JavaScript", "C#"]
        usage = [1, 2, 3, 10, 2, 1, 1]
    else:
        languages = list(language_usage.keys())
        usage = list(language_usage.values())

    sorted_languages = [x for _, x in sorted(zip(usage, languages))]
    sorted_usage = sorted(usage)

    ratio = 1920/370

    fig = plt.figure(figsize=(5, 5))
    fig.set_facecolor('#000000')
    plt.pie(labels=sorted_languages, x=sorted_usage, colors=['#5E1414', '#000000'])
    plt.xticks([])
    ax = plt.gca()
    ax.set_facecolor('#000000')
    ax.tick_params(axis='y', colors='#5E1414')

    plt.tight_layout()

    plt.savefig('languages_usage.png', transparent = True)
    plt.close()
    print("Bar chart saved as 'languages_usage.png'.")

# Main script
if __name__ == '__main__':
    language_usage = aggregate_languages()
    generate_bar_chart(language_usage)
