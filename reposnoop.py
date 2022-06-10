"""reposnoop: Analyze data from GitHub repos (main module).

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import ghclient as gcl
import dataman as dm
# import charts
# import rsgui
from pprint import pprint


def rs_main():
    """Run the module standalone."""
    # testing: ask for search terms.
    ask_sterms = True
    my_sterms = []
    # ask search terms from user
    while ask_sterms:
        term = input("Add search term: ")
        if term == "":
            ask_sterms = False
        else:
            my_sterms.append(term)
    my_sterms = my_sterms if len(my_sterms) else ["osint", "twitter"]

    # pull search items from GitHub API
    my_search = gcl.RepoSearch(my_sterms)
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
            my_commits = gcl.RepoCommits(repo_fname)
            my_contribs = gcl.RepoContribs(repo_fname)
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
                print("my_commits.get_commits()",
                      type(my_commits.get_commits()))
                pprint(my_commits.get_commits())
                print("my_contribs", type(my_contribs))
                print("my_contribs.get_contributors()",
                      type(my_contribs.get_contributors()))
                pprint(my_contribs.get_contributors())
                print("\nTotal # commits within the last 52 weeks:",
                      my_commits.get_commits()["commits"].sum())
                print("\nNumber of contributors:",
                      len(my_contribs.get_contributors()["total_commits"]))


if __name__ == "__main__":
    rs_main()
