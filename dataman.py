"""reposnoop data management module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import pandas as pd


class StatsCache:
    """Provides caching of statistical data."""
    def __init__(self):
        """Setup main data structures."""
        self.cache = [{"john_doe/project": {"commits": pd.DataFrame([0]*52, column=["commits"]),
                                            "c_total": 0,
                                            "contributors": pd.DataFrame([1, 2, 3],
                                                                         index=["Anna", "Ben", "Christine"],
                                                                         column=["commits"])}}]



def data_manager_main():
    """Test / present modules class(es)."""
    pass
    return None


if __name__ == "__main__":
    data_manager_main()
