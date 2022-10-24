from datetime import datetime
import json
import requests


head = '''# Top Python Web Frameworks
A list of popular github projects related to Python web framework (ranked by stars automatically)
Please update **list.txt** (via Pull Request)

'''
tail = '\n*Last Automatic Update: {}*'

warning = "\n⚠️ No longer maintained ⚠️\n\n"

deprecated_repos = [
    "https://github.com/flask-api/flask-api",
]
repos = list()


def main():
    access_token = get_access_token()

    with open('list.txt', 'r') as f:
        for url in f.readlines():
            url, pypi_name = url.strip().split(' ')
            if url.startswith('https://github.com/'):
                repo_api = 'https://api.github.com/repos/{}'.format(url[19:])

                r = requests.get(repo_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                repo = json.loads(r.content)
                repo["pypi_name"] = pypi_name

                commit_api = 'https://api.github.com/repos/{}/commits/{}'.format(url[19:], repo['default_branch'])

                r = requests.get(commit_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                commit = json.loads(r.content)

                repo['last_commit_date'] = datetime.fromisoformat(commit['commit']['committer']['date'][:-1])
                if repo['stargazers_count'] >= 1_000:
                    repos.append(repo)

        repos.sort(key=lambda r: r['stargazers_count'], reverse=True)
        save_ranking(repos)


def get_access_token():
    with open('access_token.txt', 'r') as f:
        return f.read().strip()


def save_ranking(repos):
    with open('README.md', 'w') as f:
        f.write(head)
        for repo in (r for r in repos if not(is_deprecated(r))):
            f.write(repo_text(repo))
        f.write(warning)
        for repo in (r for r in repos if is_deprecated(r)):
            f.write(repo_text(repo))
        f.write(tail.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')))


def is_deprecated(repo):
    return repo["url"] in deprecated_repos or (datetime.now() - repo['last_commit_date']).days > 365


def repo_text(repo):
    repo_user_and_name = '/'.join(repo['html_url'].split('/')[-2:])
    text = ""
    text += f"- [{repo['name']}]({repo['html_url']}): {repo['description']} \n\n  "
    text += f"[![GitHub stars](https://img.shields.io/github/stars/{repo_user_and_name}.svg?style=social)]({repo['html_url']}) "
    text += f"[![GitHub issues](https://img.shields.io/github/issues/{repo_user_and_name}.svg)]({repo['html_url']}/issues) "
    if repo['pypi_name'] != "-":
        text += f"[![Downloads](https://img.shields.io/pypi/dw/{repo['pypi_name']})](https://pypi.org/project/{repo['pypi_name']}/) "
    text += f"[![GitHub last commit](https://img.shields.io/github/last-commit/{repo_user_and_name})]({repo['html_url']}/commits) "
    text += "\n"
    return text


if __name__ == '__main__':
    main()
