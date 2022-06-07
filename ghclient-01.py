"""reposnoop GitHub API client module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import requests

API_SEARCH = "https://api.github.com/search/repositories?"
API_COMMITS = "https://api.github.com/repos/OWNER/REPO/stats/commit_activity"
API_CONTRIBUTORS = "https://api.github.com/repos/OWNER/REPO/stats/contributors"


def github_client_main():
    """Test / present modules class(es)."""
    # search query has to be crafted by user input later
    # search_kw = ["multi", "agent", "genetic"]
    # search_kw = ["insurance", "data", "analysis"]
    search_kw = ["intelligence"]  # , "twitter"
    search_url = "&".join([API_SEARCH, f"q={'+'.join(search_kw)}+language%3Apython",
                           "ref=advsearch", "per_page=100"])    # , "sort=stars"
    print("searching for " + search_url)
    
    # sending out request. URL should still be built better
    search_response =  requests.get(search_url)
    print("\nHeaders:", search_response.headers['content-type'])
    print("Encoding:", search_response.encoding)
    print("Status:", search_response.status_code)

    # meanwhile we use the requests json parser
    result_json = search_response.json()
    print(f"\n\nResponse:\n    incomplete results: {result_json['incomplete_results']}")
    print(f"    number of items: {len(result_json['items'])}")
    print(f"    items total_count, should be: {result_json['total_count']}\n\n")

    for item in result_json['items']:
        print(f"{'name: ':<20}{str(item['name']):<35}")
        # print(f"{'description: ':<20}{str(item['description']):<35}")
        # print(f"{'owner: ':<20}{str(item['owner']['login']):<35}")
        # print(f"{'updated_at: ':<20}{str(item['updated_at']):<35}")
        print(f"{'stargazers_count: ':<20}{str(item['stargazers_count']):<35}")
        # print(f"{'watchers: ':<20}{str(item['watchers']):<35}")
        # print(f"{'forks: ':<20}{str(item['forks']):<35}")
        # print(f"{'open_issues: ':<20}{str(item['open_issues']):<35}\n\n")
        if ((item['watchers'] != item['watchers_count'])
            or (item['open_issues'] != item['open_issues_count'])
            or (item['forks'] != item['forks_count'])):
            print("########################################")

    return None


if __name__ == "__main__":
    github_client_main()

    # print(f"{'full_name: ':<20}{str(item['full_name']):<35}")
    # print(f"{'topics: ':<20}{str(item['topics']):<35}")
    # print(f"{'language: ':<20}{str(item['language']):<35}")
    # print(f"{'license: ':<20}{str(item['license']):<35}")
    # print(f"{'private: ':<20}{str(item['private']):<35}")
    # print(f"{'visibility: ':<20}{str(item['visibility']):<35}")
    # print(f"{'created_at: ':<20}{str(item['created_at']):<35}")
    # print(f"{'pushed_at: ':<20}{str(item['pushed_at']):<35}")
    # print(f"{'forks_count: ':<20}{str(item['forks_count']):<35}")
    # print(f"{'open_issues_count: ':<20}{str(item['open_issues_count']):<35}")
    # print(f"{'watchers_count: ':<20}{str(item['watchers_count']):<35>}\n\n")
