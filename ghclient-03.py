"""reposnoop GitHub API client module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import sys
import requests
import urllib.parse as urls
from datetime import datetime
from pprint import pprint
import pandas as pd

API_TFORMAT = "%Y-%m-%dT%H:%M:%SZ"

ENDPOINTS = {
            "api_repo_search": "https://api.github.com/search/repositories?q=",
            "api_repo_commits": "https://api.github.com/repos/OWNER/REPO/"
                                "stats/commit_activity?",
            "api_repo_contrib": "https://api.github.com/repos/OWNER/REPO/"
                                "stats/contributors?"
            }


def prepare_url(endpoint, payload):
    """Prepare URL at <endpoint> with <payload> for request."""
    if endpoint in ENDPOINTS:
        compl_endpoint = ENDPOINTS[endpoint].replace(
                        "OWNER",
                        urls.quote(payload["owner"])).replace(
                        "REPO",
                        urls.quote(payload["repo"]))
        # print("compl_endpoint", compl_endpoint)
        search_string = urls.quote_plus(" ".join(payload["search_kw"]))
        # print("search_string", search_string)
        qualif_str = urls.quote("&".join(
            [f"{str(k)}={str(v)}" for k, v in payload["qualifiers"].items()]),
            safe="/&=")
        # print("qualif_str", qualif_str)
        return compl_endpoint + "&".join(filter(None, [search_string, qualif_str]))
    else:
        raise ValueError("Request for unknown endpoint")


def get_api_data(endpoint, payload):
    """Run search query request and return selected item data as list."""
    # build URL and send out request
    try:
        req_url = prepare_url(endpoint, payload)
        print("Requesting ", req_url)
        search_response = requests.get(req_url)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception occurred while preparing URL string / sending request:")
        print(e, "at line", e_line, type(e))
        return None
    else:
        # parse response with requests json parser
        # this could be divided into separate funcs in future
        try:
            result_json = search_response.json()
        except Exception as e:
            e_line = sys.exc_info()[2].tb_lineno
            print("Exception occurred while parsing API response:")
            print(e, "at line", e_line, type(e))
        else:
            return result_json


def get_search(payload):
    """Perform search request and filter results into list.

    Returns a list of dicts, each corresponding to a repository.
    Keys contained in dicts:
    name|str, full_name|str, description|str, owner|str, topics|list, language|str,
    license|str, private|boolean, visibility|str, created_at|int-epoch-secs,
    pushed_at|int-epoch-secs, updated_at|int-epoch-secs, stargazers_count|int,
    watchers|int, forks|int, open_issues|int
    """
    try:
        result_dict = get_api_data("api_repo_search", payload)
        # pprint(result_dict)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception in get_search() occurred while drawing data from API:")
        print(e, "at line", e_line, type(e))
        return None
    else:
        item_list = []
        # extract relevant data
        for item in result_dict['items']:
            item_list.append({
                "name": str(item['name']),
                "full_name": str(item['full_name']),
                "description": str(item['description']),
                "owner": str(item['owner']['login']),
                "topics": item['topics'],
                "language": str(item['language']),
                "license": str(item['license']),
                "private": item['private'],
                "visibility": str(item['visibility']),
                "created_at": int(datetime.strptime(item['created_at'],
                                                    API_TFORMAT).timestamp()),
                "pushed_at": int(datetime.strptime(item['pushed_at'],
                                                   API_TFORMAT).timestamp()),
                "updated_at": int(datetime.strptime(item['updated_at'],
                                                    API_TFORMAT).timestamp()),
                "stargazers_count": int(item['stargazers_count']),
                "watchers": int(item['watchers']),
                "forks": int(item['forks']),
                "open_issues": int(item['open_issues'])
            })
        return item_list


def get_commits(payload):
    """Request a repos commits and return them as list of week-items.

    Returns a pandas DataFrame, each row has the commit totals of a week.
    The df is indexed by the week's POSIX timestamp.
    example:
    (index)       commits
    1623542400          5
    1624147200          6
    1624752000          3
    1625356800         14
    1625961600         24
    1626566400          4
    """
    try:
        result_list = get_api_data("api_repo_commits", payload)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception in get_commits() occurred while drawing data from API:")
        print(e, "at line", e_line, type(e))
        return None
    else:
        commit_list = []
        week_list = []
        # extract relevant data
        for item in result_list:
            commit_list.append(int(item["total"]))
            week_list.append(int(item["week"]))
        return pd.DataFrame(commit_list, columns=["commits"], index=week_list)


def get_commits_by_rname(name, repo_list):
    """Return commit data for repository from list, select by repo name."""
    my_payload = {
        "owner": repo_list[-1]["owner"],
        "repo": repo_list[-1]["name"],
        "search_kw": [],
        "qualifiers": {}
    }
    
    # search repo owner that belongs to repo name if the latter exists
    if name in [item["name"] for item in repo_list]:
        my_payload["repo"] = name
        my_payload["owner"] = list(filter(lambda item:
                                          item["name"] == my_payload["repo"],
                                          repo_list))[0]["owner"]
    else:
        raise ValueError("Repository name not found in given list.")

    print("Getting commit statistics for:", my_payload)
    try:
        commits = get_commits(my_payload)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception in get_commits_by_rname() occurred while "
              "drawing data from API:")
        print(e, "at line", e_line, type(e))
        return None

    return commits


def github_client_main():
    """Test / present modules class(es)."""
    smpl_pl_search = {
        "owner": "",
        "repo": "",
        "search_kw": [
            "intelligence",
            "twitter",
            "language:python"
        ],
        "qualifiers": {
            "ref": "advsearch",
            "per_page": 25
        }
    }
    
    # testing: ask for search terms.
    ask_sterms = True
    my_sterms = []
    while ask_sterms:
        term = input("Add search term: ")
        if term == "":
            ask_sterms = False
        else:
            my_sterms.append(term)
    smpl_pl_search["search_kw"] = my_sterms if len(
                my_sterms) else smpl_pl_search["search_kw"]
        
    search_list = get_search(smpl_pl_search)
    # sort_key must be made lowercase for string keys
    sort_key = "stargazers_count"
    sorted_search = sorted(search_list,
                           key=lambda item: item[sort_key])
    # print an overview
    for row in sorted_search:
        print(f"repo: {row['name']}, owner: {row['owner']}, "
              f"stars: {row['stargazers_count']}")
        
    # request weekly commit statistics
    ask_repo = True
    while ask_repo:
        repo_name = input("Which repo for commit display? ")
        if repo_name == "":
            ask_repo = False
        elif repo_name.lower() == "r":
            # print the search list again
            for row in sorted_search:
                print(f"repo: {row['name']}, owner: {row['owner']}, "
                      f"stars: {row['stargazers_count']}")

        else:
            try:
                my_commits = get_commits_by_rname(repo_name, sorted_search)
            except ValueError:
                print("Requested repo name does not match search data. Again?")
                continue
            else:
                pprint(my_commits)
                print("Total # commits within the last 52 weeks:",
                      my_commits["commits"].sum())


if __name__ == "__main__":
    github_client_main()
