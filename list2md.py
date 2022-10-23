from datetime import datetime
import json
import requests


head = '''# Top Python Web Frameworks
A list of popular github projects related to Python web framework (ranked by stars automatically)
Please update **list.txt** (via Pull Request)

'''
tail = '\n*Last Automatic Update: {}*'

warning = "⚠️ No longer maintained ⚠️  "

deprecated_repos = list()
repos = list()


def main():
    access_token = get_access_token()

    with open('list.txt', 'r') as f:
        for url in f.readlines():
            url = url.strip()
            if url.startswith('https://github.com/'):
                repo_api = 'https://api.github.com/repos/{}'.format(url[19:])
                print(repo_api)

                r = requests.get(repo_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                repo = json.loads(r.content)

                commit_api = 'https://api.github.com/repos/{}/commits/{}'.format(url[19:], repo['default_branch'])
                print(repo_api)

                r = requests.get(commit_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                commit = json.loads(r.content)

                repo['last_commit_date'] = commit['commit']['committer']['date']
                repos.append(repo)

        repos.sort(key=lambda r: r['stargazers_count'], reverse=True)
        save_ranking(repos)


def get_access_token():
    with open('access_token.txt', 'r') as f:
        return f.read().strip()


def save_ranking(repos):
    with open('README.md', 'w') as f:
        f.write(head)
        for repo in repos:
            if is_deprecated(repo['url']):
                repo['description'] = warning + repo['description']
            repo_user_and_name = '/'.join(repo['html_url'].split('/')[-2:])
            f.write(f"- [{repo['name']}]({repo['html_url']}): {repo['description']} ")
            f.write(f"![GitHub stars](https://img.shields.io/github/stars/{repo_user_and_name}.svg?style=social)")
            f.write(f"![GitHub issues](https://img.shields.io/github/issues/{repo_user_and_name}.svg)")
            f.write(f"![GitHub last commit](https://img.shields.io/github/last-commit/{repo_user_and_name})")
            f.write("\n")
        f.write(tail.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')))


def is_deprecated(repo_url):
    return repo_url in deprecated_repos


if __name__ == '__main__':
    main()
