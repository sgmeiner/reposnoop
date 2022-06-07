"""reposnoop GitHub API client module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import requests


API_SEARCH = "https://api.github.com/search/repositories?"
API_COMMITS = "https://api.github.com/repos/OWNER/REPO/stats/commit_activity"
API_CONTRIBUTORS = "https://api.github.com/repos/OWNER/REPO/stats/contributors"


def get_repo_search(keywords="", qualifiers=""):
    """Run search query request and return selected item data as list."""
    search_kw = keywords if keywords else ["intelligence", "twitter", "language%3Apython"]
    search_qual = qualifiers if qualifiers else ["ref=advsearch", "per_page=100"]

    # preparing URL
    search_url = "&".join([API_SEARCH,
                           f"q={'+'.join(search_kw)}",
                           *search_qual])
    print("searching for " + search_url)

    # sending out request. URL should still be built better
    search_response = requests.get(search_url)
    print("\nHeaders:", search_response.headers['content-type'])
    print("Encoding:", search_response.encoding)
    print("Status:", search_response.status_code)
    
    # meanwhile we use the requests json parser
    result_json = search_response.json()
    print(f"\nResponse:\n    incomplete results: {result_json['incomplete_results']}")
    print(f"    number of items: {len(result_json['items'])}")
    print(f"    items total_count, should be: {result_json['total_count']}")

    item_list = []
    for item in result_json['items']:
        print(f"\n{'name: ':<20}{str(item['name']):<35}")
        # print(f"{'updated_at: ':<20}{str(item['updated_at']):<35}")
        # print(f"{'stargazers_count: ':<20}{str(item['stargazers_count']):<35}")
        print(f"{'private: ':<20}{str(item['private']):<35}")
        print(f"{'visibility: ':<20}{str(item['visibility']):<35}")
        
        # reconfigure data, shorten for bunch of URLs
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
    repo_list = get_repo_search()
    print("\n\n".join([str(item) for item in repo_list]))
    

if __name__ == "__main__":
    github_client_main()
