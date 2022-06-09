"""reposnoop GitHub statistics, API client module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import sys
import urllib.parse as urls
from datetime import datetime
from pprint import pprint
import time

import requests
import pandas as pd

API_TFORMAT = "%Y-%m-%dT%H:%M:%SZ"
ENDPOINTS = {
            "api_repo_search": "https://api.github.com/search/repositories?q=",
            "api_repo_commits": "https://api.github.com/repos/OWNER/REPO/"
                                "stats/commit_activity?",
            "api_repo_contrib": "https://api.github.com/repos/OWNER/REPO/"
                                "stats/contributors?"
            }


class GitHubRequest:
    """Manage requests to GitHub API."""
    def __init__(self, endpoint, payload):
        """Initialize instance vars."""
        self.endpoint = endpoint
        self.payload = payload
        self.url = ""
        self.response = None
        self.res_stat = None
        self.res_data = None
        self.errors = {
                      "url": "",
                      "request": "",
                      "json": ""
                      }
    
    def prepare_url(self):
        """Prepare URL str for request."""
        if self.endpoint in ENDPOINTS:
            compl_endpoint = ENDPOINTS[self.endpoint].replace(
                            "OWNER",
                            urls.quote(self.payload["owner"])).replace(
                            "REPO",
                            urls.quote(self.payload["repo"]))
            if "search_kw" in self.payload.keys():
                search_string = urls.quote_plus(" ".join(
                                self.payload["search_kw"]))
            else:
                search_string = None
            if "search_kw" in self.payload.keys():
                qualif_str = urls.quote("&".join(
                    [f"{str(k)}={str(v)}" for k, v in self.payload["qualifiers"].items()]),
                    safe="/&=")
            else:
                qualif_str = None
            self.url = compl_endpoint + "&".join(filter(None,
                                                        [search_string, qualif_str]))
            self.errors["url"] = ""
            return self.url
        else:
            self.errors["url"] = "Request for unknown endpoint"
            raise ValueError("Request for unknown endpoint")

    def get_api_response(self):
        """Run search query request and return selected item data as list."""
        try:
            self.response = requests.get(self.url)
        except Exception as e:
            e_line = sys.exc_info()[2].tb_lineno
            print("Exception occurred while sending request: ")
            errmsg = str(e) + " at line " + str(e_line) + str(type(e))
            print(errmsg)
            self.errors["request"] = errmsg
            raise
        else:
            self.res_stat = str(self.response.status_code)
            self.errors["request"] = ""
            return self.response, self.res_stat

    def decode_json(self):
        """Decode API response as JSON."""
        try:
            self.res_data = self.response.json()
        except Exception as e:
            e_line = sys.exc_info()[2].tb_lineno
            print("Exception occurred while parsing API response; "
                  "JSON decode failure:")
            errmsg = str(e) + " at line " + str(e_line) + str(type(e))
            print(errmsg)
            self.errors["json"] = errmsg
            raise
        else:
            self.errors["json"] = ""
            return self.res_data

    def get_url(self):
        return self.url

    def get_response(self):
        return self.response

    def get_data(self):
        """Get raw data structure from API."""
        self.prepare_url()
        if not self.errors["url"]:
            self.get_api_response()
            if not self.errors["request"]:
                self.decode_json()
                if not self.errors["json"]:
                    return self.res_data
        return False


class RepoSearch:
    """Manage repository search and response items."""
    def __init__(self, keywords, qualifiers={}):
        """Initialize instance vars and fill gaps with default values."""
        self.payload = {
                       "owner": "",
                       "repo": "",
                       "search_kw": keywords,
                       "qualifiers": qualifiers
                       }
        if "ref" not in self.payload["qualifiers"].keys():
            self.payload["qualifiers"]["ref"] = "advsearch"
        if "per_page" not in self.payload["qualifiers"].keys():
            self.payload["qualifiers"]["per_page"] = 7

        self.api_request = GitHubRequest("api_repo_search", self.payload)
        self.response = {}
        self.errors = {
                      "request": "",
                      "data": ""
                      }
        self.items = []

    def pull(self):
        """Perform search request and filter results into list.
    
        self.response_items is a list of dicts, each corresponding
        to a repository. Keys contained in dicts:
        name|str, full_name|str, description|str, owner|str, topics|list,
        language|str, license|str, private|boolean, visibility|str,
        created_at|int-epoch-secs, pushed_at|int-epoch-secs,
        updated_at|int-epoch-secs, stargazers_count|int,
        watchers|int, forks|int, open_issues|int
        """
        # try 3 times because of rate limit
        wait_for_rate = 30
        for i in [1, 2, 3]:
            try:
                self.response = self.api_request.get_data()
            except Exception as e:
                e_line = sys.exc_info()[2].tb_lineno
                print("Search not successful: ")
                errmsg = str(e) + " at line " + str(e_line) + str(type(e))
                print(errmsg)
                self.errors["request"] = errmsg
                raise
            else:
                if self.response:
                    self.errors["request"] = ""
                    break
                else:
                    http_status = str(self.api_request.res_stat)
                    # good, but empty?
                    if http_status == "200":
                        # response was successful, but apparently search did not
                        # find a single item ...
                        self.errors["request"] = ""
                        if len(self.response_items) == 0:
                            # still, no data
                            self.errors["data"] = "empty"
                            return pd.DataFrame([], columns=["commits"])
                        # return self.items
                    # hit the rate limit?
                    elif http_status == "403":
                        if "rate limit exceeded" in self.api_request.get_response().text:
                            print("Retry after 90 secs, rate limit was hit ...")
                            time.sleep(wait_for_rate)
                            # maybe just wait longer next time
                            wait_for_rate *= 3
                            if i > 2:
                                self.api_request.get_response().raise_for_status()
    
        # extract relevant data
        for item in self.response['items']:
            self.items.append({
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
        return self.items

    def get_keywords(self):
        return self.payload["search_kw"]

    def get_qualifiers(self):
        return self.payload["qualifiers"]

    def get_items(self):
        return self.items

    def get_raw_response(self):
        return self.response


class RepoCommits:
    """Manage Repository Commit data."""
    def __init__(self, repo_fullname):
        """Initialize instance vars and fill gaps with default values."""
        self.repo_name = repo_fullname
        self.payload = {}
        if "/" in self.repo_name:
            self.payload["owner"], self.payload["repo"] = self.repo_name.split("/")
        else:
            raise ValueError("Need the 'full_name' of the repository.")
        self.api_request = GitHubRequest("api_repo_commits", self.payload)
        self.response_items = []
        self.commits = None
        self.errors = {
                      "request": "",
                      "data": ""
                      }

    def pull(self):
        """Request commits and return them as pandas df.
    
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
            self.response_items = self.api_request.get_data()
        except Exception as e:
            e_line = sys.exc_info()[2].tb_lineno
            print(f"Pulling commits for {self.payload['owner']}/"
                  f"{self.payload['repo']} not successful: ")
            errmsg = str(e) + " at line " + str(e_line) + str(type(e))
            print(errmsg)
            self.errors["request"] = errmsg
            raise
        else:
            http_status = str(self.api_request.res_stat)
            if http_status == "200":
                # request went fine
                self.errors["request"] = ""
                if len(self.response_items) == 0:
                    # still, no data
                    self.errors["data"] = "empty"
                    self.commits = pd.DataFrame([], columns=["commits"])
                    return self.commits
            else:
                # no exception, but still no valid data or empty frame
                # if len(self.response_items) == 0:
                #     self.errors["data"] = "empty"
                #     return pd.DataFrame([], columns=["commits"])
                print("\nERROR: Got no valid response on commits request.\n")
                self.errors["request"] = (f"HTTP code {http_status} while pulling commits of"
                                          + f"{self.payload['owner']}/{self.payload['repo']}")
                self.commits = pd.DataFrame([], columns=["commits"])
                return self.commits

        # extract relevant data
        commit_list = []
        week_list = []
        for item in self.response_items:
            commit_list.append(int(item["total"]))
            week_list.append(int(item["week"]))
        self.commits = pd.DataFrame(commit_list, columns=["commits"], index=week_list)
        return self.commits

    def get_commits(self):
        return self.commits

    def get_raw_response(self):
        return self.response_items
    
    def get_name(self):
        return self.repo_name


class RepoContribs:
    """Manage repository contributors data."""
    def __init__(self, repo_fullname):
        """Initialize instance vars and fill gaps with default values."""
        self.repo_name = repo_fullname
        self.payload = {}
        if "/" in self.repo_name:
            self.payload["owner"], self.payload["repo"] = self.repo_name.split("/")
        else:
            raise ValueError("Need the 'full_name' of the repository.")
        self.api_request = GitHubRequest("api_repo_contrib", self.payload)
        self.response_items = []
        # the short summary df ...
        self.contributors = None
        self.contrib_fulldata = None
        self.errors = {
                      "request": "",
                      "data": ""
                      }

    def pull(self):
        """Request a repos contributors and return their activity as pd.DataFrame.
    
        Returns a pandas DataFrame, each column corresponds to one contributor,
        each row has the respective commit totals of a week.
        The df is indexed by the week's POSIX timestamp, column names are
        the names of the contributing account owners (=contributors).
        Additionally it creates a pandas DataFrame with the total commits
        of each contributor. This is not used / maintained in the current version.
        """
        try:
            self.response_items = self.api_request.get_data()
        except Exception as e:
            e_line = sys.exc_info()[2].tb_lineno
            print(f"Pulling contributors info for {self.payload['owner']}/"
                  f"{self.payload['repo']} not successful: ")
            errmsg = str(e) + " at line " + str(e_line) + str(type(e))
            print(errmsg)
            self.errors["request"] = errmsg
            raise
        else:
            http_status = str(self.api_request.res_stat)
            if http_status == "200":
                # request went fine
                self.errors["request"] = ""
                if len(self.response_items) == 0:
                    # still, no data
                    self.errors["data"] = "empty"
                    self.contributors = pd.DataFrame([], columns=["total_commits"])
                    return self.contributors
            else:
                # no exception, but still no valid data or empty frame
                print("\nERROR: Got no valid response on contributor data request.\n")
                self.errors["request"] = (f"HTTP code {http_status} while pulling commits of"
                                          + f"{self.payload['owner']}/{self.payload['repo']}")
                return pd.DataFrame([], columns=["total_commits"])
    
        # first building the index (week) and first column ...
        week_list = []
        commit_first_list = []
        for week in self.response_items[0]["weeks"]:
            week_list.append(int(week["w"]))
            commit_first_list.append(int(week["c"]))
    
        # now build the initial dataframe. we're appending only whole columns
        self.contrib_fulldata = pd.DataFrame(commit_first_list,
                                  columns=[self.response_items[0]["author"]["login"]],
                                  index=week_list)
    
        # prepare the summary as nested list
        contrib_summary = [
                          [str(self.response_items[0]["author"]["login"])],
                          [int(self.response_items[0]["total"])]
                          ]
    
        # extract more data by columns
        if len(self.response_items) > 1:
            for contributor in self.response_items[1:]:
                commit_list = []
                for week in contributor["weeks"]:
                    commit_list.append(int(week["c"]))
                contr_name = str(contributor["author"]["login"])
                # append new column to full list pd DataFrame
                self.contrib_fulldata[contr_name] = commit_list
                # append new column to summary lists
                contrib_summary[0].append(contr_name)
                contrib_summary[1].append(int(contributor["total"]))
    
        # finally, convert nested list summary to pd.df
        self.contributors = pd.DataFrame(
                                        contrib_summary[1],
                                        index=contrib_summary[0],
                                        columns=["total_commits"]
                                        )
    
        return self.contributors

    def get_contributors(self):
        return self.contributors

    def get_raw_response(self):
        return self.response_items

    def get_name(self):
        return self.repo_name


def github_client_main():
    """Test / present modules class(es)."""

    # testing: ask for search terms.
    ask_sterms = True
    my_sterms = []
    while ask_sterms:
        term = input("Add search term: ")
        if term == "":
            ask_sterms = False
        else:
            my_sterms.append(term)
    my_sterms = my_sterms if len(my_sterms) else ["osint", "twitter"]

    # pull search items from GitHub API
    my_search = RepoSearch(my_sterms)
    search_list = my_search.pull()

    # sort list by stars (=likes)
    sort_key = "stargazers_count"
    sorted_search = sorted(search_list,
                           key=lambda item: item[sort_key])
    # print an overview
    for row in sorted_search:
        print(f"repo: {row['name']}, owner: {row['owner']}, "
              f"full_name: {row['full_name']}, "
              f"stars: {row['stargazers_count']}"
              f"\n      description: {row['description'][:80]}")

    # request weekly commit statistics
    ask_repo = True
    while ask_repo:
        repo_fname = input("Further info for which repo (full_name)? ")
        if repo_fname == "":
            ask_repo = False
        elif repo_fname.lower() == "r":
            # print the search list again
            for row in sorted_search:
                print(f"repo: {row['name']}, owner: {row['owner']}, "
                      f"full_name: {row['full_name']}, "
                      f"stars: {row['stargazers_count']}"
                      f"\n      description: {row['description'][:80]}")
        else:
            my_commits = RepoCommits(repo_fname)
            my_contribs = RepoContribs(repo_fname)
            try:
                my_commits.pull()
                my_contribs.pull()
            except ValueError:
                print("Requested repo name does not match search data. Again?")
                continue
            except Exception as e:
                print(e, type(e))
                break
            else:
                print("my_commits", type(my_commits))
                print("my_commits.get_commits()", type(my_commits.get_commits()))
                pprint(my_commits.get_commits())
                print("my_contribs", type(my_contribs))
                print("my_contribs.get_contributors()", type(my_contribs.get_contributors()))
                pprint(my_contribs.get_contributors())
                print("\nTotal # commits within the last 52 weeks:",
                      my_commits.get_commits()["commits"].sum())
                print("\nNumber of contributors:",
                      len(my_contribs.get_contributors()["total_commits"]))


if __name__ == "__main__":
    github_client_main()
