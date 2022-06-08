"""reposnoop GitHub statistics, API client module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import sys
import requests
import urllib.parse as urls
from datetime import datetime
import time
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

API_ERRS = [
           "message",
           "errors",
           ]


def prepare_url(endpoint, payload):
    """Prepare URL str at <endpoint> with <payload> for request."""
    if endpoint in ENDPOINTS:
        compl_endpoint = ENDPOINTS[endpoint].replace(
                        "OWNER",
                        urls.quote(payload["owner"])).replace(
                        "REPO",
                        urls.quote(payload["repo"]))
        search_string = urls.quote_plus(" ".join(payload["search_kw"]))
        qualif_str = urls.quote("&".join(
            [f"{str(k)}={str(v)}" for k, v in payload["qualifiers"].items()]),
            safe="/&=")
        return compl_endpoint + "&".join(filter(None,
                                                [search_string, qualif_str]))
    else:
        raise ValueError("Request for unknown endpoint")


def get_api_response(req_url):
    """Run search query request and return selected item data as list."""
    try:
        response = requests.get(req_url)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception occurred while sending request:")
        print(e, "at line", e_line, type(e))
        raise
        return [[], "0"]
    else:
        return response, str(response.status_code)


def decode_json(response):
    """Decode API response as JSON."""
    try:
        result_struct = response.json()
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception occurred while parsing API response / "
              "JSON decode failure:")
        print(e, "at line", e_line, type(e))
        raise
    else:
        # this still does not work for many cases
        # for key in result_struct.keys():
        #     if key in API_ERRS:
        #         print("API failed to send expected content, but error msg.:")
        #         pprint(result_struct)
        #         raise ValueError("API failed to send expected content;"
        #                          "request failed.")
        #         return None
        return result_struct


def get_search(payload):
    """Perform search request and filter results into list.

    Returns a list of dicts, each corresponding to a repository.
    Keys contained in dicts:
    name|str, full_name|str, description|str, owner|str, topics|list,
    language|str, license|str, private|boolean, visibility|str,
    created_at|int-epoch-secs, pushed_at|int-epoch-secs,
    updated_at|int-epoch-secs, stargazers_count|int,
    watchers|int, forks|int, open_issues|int
    """
    request_url = prepare_url("api_repo_search", payload)
    api_response, http_status = get_api_response(request_url)

    # basic management of rate limit problems
    if http_status == "403":
        if "rate limit exceeded" in api_response.text:
            print("Retry after 90 secs, rate limit was hit ...")
            time.sleep(90)
            api_response, http_status = get_api_response(request_url)

    result_dict = decode_json(api_response)

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
    request_url = prepare_url("api_repo_commits", payload)
    api_response, http_status = get_api_response(request_url)
    if http_status == "200":
        result_list = decode_json(api_response)
    else:
        print("\nERROR: Got no valid response on commits request.\n")
        result_list = []

    # extract relevant data
    commit_list = []
    week_list = []
    for item in result_list:
        commit_list.append(int(item["total"]))
        week_list.append(int(item["week"]))
    return pd.DataFrame(commit_list, columns=["commits"], index=week_list)


def get_contribs(payload):
    """Request a repos contributors and return their activity as pd.DataFrame.

    Returns a pandas DataFrame, each column corresponds to one contributor,
    each row has the respective commit totals of a week.
    The df is indexed by the week's POSIX timestamp, column names are
    the names of the contributing account owners (=contributors).
    Additionally it returns a pandas DataFrame with the total commits
    of each contributor.
    """
    request_url = prepare_url("api_repo_contrib", payload)
    api_response, http_status = get_api_response(request_url)
    if http_status == "200":
        result_list = decode_json(api_response)
    else:
        print("\nERROR: Got no valid response on contributors request.\n")
        result_list = []

    week_list = []
    # first building the index (week) and first column ...
    commit_first_list = []
    for week in result_list[0]["weeks"]:
        week_list.append(int(week["w"]))
        commit_first_list.append(int(week["c"]))

    # now build the initial dataframe. we're appending only whole columns
    contrib_df = pd.DataFrame(commit_first_list,
                              columns=[result_list[0]["author"]["login"]],
                              index=week_list)

    # prepare the summary as nested list
    contrib_summary = [
                      [str(result_list[0]["author"]["login"])],
                      [int(result_list[0]["total"])]
                      ]

    # extract column data
    for contributor in result_list[1:]:
        commit_list = []
        for week in contributor["weeks"]:
            commit_list.append(int(week["c"]))
        contr_name = str(contributor["author"]["login"])
        contrib_df[contr_name] = commit_list

        contrib_summary[0].append(contr_name)
        contrib_summary[1].append(int(contributor["total"]))

    # finally, convert nested list summary to pd.df
    contrib_sum_df = pd.DataFrame(contrib_summary[1],
                                  index=contrib_summary[0],
                                  columns=["total_commits"])

    return contrib_sum_df, contrib_df


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

    try:
        commits = get_commits(my_payload)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception in get_commits_by_rname() occurred while "
              "drawing data from API:")
        print(e, "at line", e_line, type(e))
        return None

    return commits


def get_contribs_by_rname(name, repo_list):
    """Return contributor data for repo from list, select by repo name."""
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

    try:
        contrib_totals, contrib_df = get_contribs(my_payload)
    except Exception as e:
        e_line = sys.exc_info()[2].tb_lineno
        print("Exception in get_commits_by_rname() occurred while "
              "drawing data from API:")
        print(e, "at line", e_line, type(e))
        return None

    return contrib_totals, contrib_df


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
            "per_page": 7
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
              f"stars: {row['stargazers_count']}",
              f"\n      description: {row['description'][:80]}")

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

            contrib_total, contrib_df = get_contribs_by_rname(repo_name,
                                                              sorted_search)
            pprint(contrib_total)
            pprint(contrib_df)


if __name__ == "__main__":
    github_client_main()
