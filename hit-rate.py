import requests
from datetime import datetime as dt
import time

API_SEARCH = "https://api.github.com/search/repositories?"
API_COMMITS = "https://api.github.com/repos/OWNER/REPO/stats/commit_activity"
API_CONTRIBUTORS = "https://api.github.com/repos/OWNER/REPO/stats/contributors"


def github_client_main():
    """Test / present modules class(es)."""
    for i in range(11):
        search_url = API_SEARCH + str(dt.now().timestamp())
        print("searching for " + search_url)

        # sending out request. URL should still be built better
        search_response = requests.get(search_url)
        print("Status:", search_response.status_code)
        time.sleep(1.5)

    return None


if __name__ == "__main__":
    github_client_main()
