"""reposnoop data management module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
# import pandas as pd

UPTODATE_TF = 604800  # seconds, == 7 days


class StatsCache:
    """Provides caching of statistical data.

    to do:
    # get_size
    # get_elements_by_commit_total
    # get_elements_by_contrib_count
    # get_elements_by_contrib_name
    # get_old_elements
    # methods for reading from / saving to disk
    """

    def __init__(self):
        """Initialize main data structures."""
        self.__cache = {"""
                       "john_doe/project":
                           {
                           # info on repo as delivered from search
                           "info": {}
                           # weekly commits sum for last 52 weeks
                           "commits": pd.DataFrame([0]*52,
                                                   column=["commits"]),
                           # total commits sum of last 52 weeks
                           "comm_total": 0,
                           # contributors and their commits total
                           "contributors": pd.DataFrame(
                               [1, 2, 3],
                               index=["Anna", "Ben", "Christine"],
                               column=["commits"]
                               ),
                           # number of contributors
                           "contrib_count": 0,
                           # POSIX timestamp of latest update; updating always
                           # all records or none; int|secs
                           "update_ts": 0
                           }
                       """}

    def has(self, rname):
        """Return true if named element is in cache else false."""
        return True if rname in self.__cache.keys() else False

    def get_elm(self, rname):
        """Return named element, None if not exists."""
        return (self.__cache[rname] if rname in self.__cache.keys() else None)

    def update(self, rname, element):
        """Update named element if exists, else create new.

        To date get / update are not implemented as transparently acting
        methods, because API requests do not run safe enough to hide them
        from the accessing higher level scopes (which would relay all error
        handling to the cache object).
        """
        self.__cache[rname] = element
        return None


def data_manager_main():
    """Test / present modules class(es)."""
    pass
    return None


if __name__ == "__main__":
    data_manager_main()
