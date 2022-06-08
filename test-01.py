import requests
from pprint import pprint

API_SEARCH = "https://api.github.com/search/repositories?"
API_COMMITS = "https://api.github.com/repos/OWNER/REPO/stats/commit_activity"
API_CONTRIBUTORS = "https://api.github.com/repos/OWNER/REPO/stats/contributors"

API_ERRS = [
           "message",
           "errors",
           ]

def github_client_main():
    """Test / present modules class(es)."""
    # search query has to be crafted by user input later
    search_kw = ["intelligence", "twitter"]
    search_url = "&".join([API_SEARCH,
                           f"q={'+'.join(search_kw)}+language%3Apython",
                           "ref=advsearch", "per_page=112"])
    print("searching for " + search_url)

    # sending out request. URL should still be built better
    search_response = requests.get(search_url)
    print("\nHeaders:", search_response.headers['content-type'])
    print("Encoding:", search_response.encoding)
    print("Status:", search_response.status_code)

    # meanwhile we use the requests json parser
    result_json = search_response.json()
    pprint(result_json)
    print(f"\nResponse:\n    incomplete results: "
          f"{result_json['incomplete_results']}")
    print(f"    number of items: {len(result_json['items'])}")
    print(f"    items total_count, should be: {result_json['total_count']}")

    for item in result_json['items']:
        print(f"\n{'name: ':<20}{str(item['name']):<35}")
        print(f"{'updated_at: ':<20}{str(item['updated_at']):<35}")
        print(f"{'stargazers_count: ':<20}{str(item['stargazers_count']):<35}")

    return None


if __name__ == "__main__":
    github_client_main()
