"""reposnoop tkinter GUI module.

2022 by Stefan Groh, stefan_groh@gmx.de
"""
import tkinter as tk
import tkinter.font as tkFont
import tkinter.scrolledtext as scrolltxt
from tkinter.constants import RIGHT, LEFT, Y, BOTH, END

import ghclient as gcl


class MainWin(tk.Tk):
    """Class to display the main window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.geometry("1200x800")
        self.title("reposnoop - better GitHub repo stats.")

        FONTSTYLE = {
                    "label": tkFont.Font(family="Helvetica",
                                         size=9,
                                         weight="normal",
                                         slant="roman"),
                    "entry": tkFont.Font(family="Arial",
                                         size=9,
                                         weight="normal",
                                         slant="roman"),
                    "button": tkFont.Font(family="Arial",
                                          size=10,
                                          weight="bold",
                                          slant="roman"),
                    "text": tkFont.Font(family="DejaVu Sans Mono",
                                        size=8,
                                        weight="normal",
                                        slant="roman"),
                    "h1": tkFont.Font(family="Arial",
                                      size=16,
                                      weight="bold",
                                      slant="italic"),
                    "h2": tkFont.Font(family="Arial",
                                      size=16,
                                      weight="bold",
                                      slant="roman")
                    }

        self.search_str = tk.StringVar()
        self.search_str.set("")

        # build main ui widgets
        self.searchform = []
        self.searchform.append(tk.Label(self,
                               text="Enter search terms for GitHub "
                                    "repository search:",
                               foreground="#444444",
                               anchor="w"))
        self.searchform.append(tk.Frame(self))
        self.searchform.append(tk.Entry(self.searchform[1],
                                        textvariable=self.search_str,
                                        width=80,
                                        borderwidth=5,
                                        relief=tk.FLAT))
        self.searchform.append(tk.Button(self.searchform[1],
                                         text="Search!",
                                         foreground="#666666",
                                         command=self.run_search))
        self.results = []
        self.results.append(tk.Label(self,
                               text="Search results:",
                               foreground="#444444",
                               anchor="w"))
        # self.results.append(scrolltxt.ScrolledText(self))
        # self.results.append(tk.Frame(self))
        # # , yscrollcommand=self.databox_scrollbar.set
        # self.results.append(tk.Text(self.results[1], height=60, width=60))
        # self.results.append(tk.Scrollbar(self.results[1], orient=VERTICAL,
        #                     command=self.results[2].yview))

        self.searchform[0].configure(font=FONTSTYLE["label"])
        self.searchform[2].configure(font=FONTSTYLE["entry"])
        self.searchform[3].configure(font=FONTSTYLE["button"])

        # place ui widgets with pack() geometry manager
        self.searchform[0].pack(fill=tk.X, padx=20, pady=(15, 0))
        self.searchform[1].pack(fill=tk.X, padx=10, pady=10)
        self.searchform[2].pack(side=tk.LEFT, fill=tk.Y,
                                padx=10, ipadx=5, pady=5, ipady=0)
        self.searchform[3].pack(fill=tk.X, padx=10, pady=5)

        self.results[0].configure(font=FONTSTYLE["label"])
        # self.results[2].configure(yscrollcommand=self.results[3].set)
        self.results[0].pack(fill=tk.X, padx=20, pady=(15, 0))
        # self.results[1].pack(fill=tk.X, padx=10, pady=10)
        # self.results[2].pack(fill=tk.X, padx=10, pady=10)
        # self.results[3].pack(fill=tk.X, padx=20, pady=(15, 0))

        self.stext = scrolltxt.ScrolledText(bg='white',
                                            width=90,
                                            borderwidth=5,
                                            relief=tk.FLAT,
                                            wrap='word')
        self.stext.configure(font=FONTSTYLE["text"])
        # self.stext.insert(END, __doc__)
        self.stext.pack(fill=BOTH, side=LEFT, expand=True)
        self.stext.focus_set()

        # self.searchform[3]["command"] = self.run_no_search

    def run_search(self):
        """Do someth."""
        # pull search items from GitHub API
        print(self.search_str.get().split("/"))
        self.search = gcl.RepoSearch(self.search_str.get().split("/"),
                                     qualifiers={"per_page": 25})
        self.search_list = self.search.pull()

        # sort list by stars (=likes)
        sort_key = "stargazers_count"
        self.sorted_search = sorted(self.search_list,
                                    key=lambda item: item[sort_key],
                                    reverse=True)
        # print an overview
        self.stext.delete("1.0", END)
        line_length = 75
        for row in self.sorted_search:
            desc_list = row["description"][:256].split(" ")
            print("desc_list:", desc_list)
            line_list = []
            line_str = ""
            while len(desc_list) > 0:
                if (len(line_str) + len(desc_list[0])) < line_length:
                    line_str = line_str + " " + desc_list[0]
                    print(line_str)
                    desc_list.pop(0)
                else:
                    line_list.append(line_str)
                    print(line_list)
                    line_str = ""
            line_list.append(line_str)
            # dlin = [description[i:i+n] for i in range(0, len(description), n)]
            dlin = "\n".join(line_list)
            rtext = (f"owner/repo: {row['full_name']:<75}"
                     f"{row['stargazers_count']:>10} stars"
                     f"\ndescription:\n{dlin}")
                     # f"\ndescription:\n{row['description'][:160]}")
            self.stext.insert(END, f"{rtext}\n\n")


def gui_main():
    """Test / present modules class(es)."""
    root = MainWin()
    root.mainloop()
    return None


if __name__ == "__main__":
    gui_main()
