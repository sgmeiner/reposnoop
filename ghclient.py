"""reposnoop GitHub API client module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import requests
import urllib.parse as urls


API_SEARCH = "https://api.github.com/search/repositories?q="
API_COMMITS = "https://api.github.com/repos/OWNER/REPO/stats/commit_activity"
API_CONTRIBUTORS = "https://api.github.com/repos/OWNER/REPO/stats/contributors"

endpoints = {
            "API_SEARCH": "https://api.github.com/search/repositories?q=",
            "API_COMMITS": "https://api.github.com/repos/OWNER/REPO/"
                           "stats/commit_activity?",
            "API_CONTRIBUTORS": "https://api.github.com/repos/OWNER/REPO/"
                                "stats/contributors?"
            }


def prepare_url(endpoint, payload):
    """Prepare URL at <endpoint> with <payload> for request."""
    if endpoint in endpoints:
        complete_endpoint = endpoint.replace(
                        "OWNER",
                        urls.quote(payload["owner"])).replace(
                        "REPO",
                        urls.quote(payload["repo"]))
        search_string = urls.quote_plus("+".join(payload["search_kw"]))
        qualifiers = urls.quote()

        # ---------------- !!! ---------------------
    else:
        print("Request for unknown endpoint: ", endpoint)
        raise ValueError
        return None

    return new_url


def get_repo_search(keywords="", qualifiers=""):
    """Run search query request and return selected item data as list."""
    search_kw = keywords if keywords else ["intelligence",
                                           "twitter",
                                           "language%3Apython"]
    search_qual = qualifiers if qualifiers else ["ref=advsearch",
                                                 "per_page=100"]

    # preparing URL
    search_url = "&".join([API_SEARCH,
                           f"{'+'.join(search_kw)}",
                           *search_qual])

    # sending out request. URL should still be built better
    search_response = requests.get(search_url)

    # parse response with requests json parser
    result_json = search_response.json()

    item_list = []
    # restructure data, shorten for the whole bunch of URLs
    for item in result_json['items']:
        item_list.append({
            "name": str(item['name']),
            "description": str(item['description']),
            "owner": str(item['owner']['login']),
            "topics": item['topics'],
            "language": str(item['language']),
            "license": str(item['license']),
            "private": str(item['private']),
            "visibility": str(item['visibility']),
            "created_at": str(item['created_at']),
            "pushed_at": str(item['pushed_at']),
            "updated_at": str(item['updated_at']),
            "stargazers_count": int(item['stargazers_count']),
            "watchers": int(item['watchers']),
            "forks": int(item['forks']),
            "open_issues": int(item['open_issues'])
        })

    return item_list


def github_client_main():
    """Test / present modules class(es)."""
    repo_list = get_repo_search(keywords=["insurance", "data", "analysis"],
                                qualifiers=["ref=advsearch", "per_page=5"])
    print("\n\n".join([str(item) for item in repo_list]))


if __name__ == "__main__":
    github_client_main()
