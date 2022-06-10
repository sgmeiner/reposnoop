#!/usr/bin/python
from tkinter import *

class MyApp:
    def __init__(self, parent):
        self.myParent = parent
        self.main_container = Frame(self.myParent)
        self.main_container.grid(row=0, column=0, columnspan=4)

        self.left_frame = Frame(self.main_container)
        self.left_frame.grid(row=0, column=0, columnspan=2)

        self.right_frame = Frame(self.main_container)
        self.right_frame.grid(row=0, column=2, columnspan=2)

        self.checkbox_scrollbar = Scrollbar(self.left_frame)
        self.checkbox_scrollbar.grid(row=0, column=1, sticky='NS')
        self.checkbox_text = Text(self.left_frame, height=30, width=10,
                                 yscrollcommand=self.checkbox_scrollbar.set)
        self.checkbox_text.grid(row=0, column=0)
        self.checkbox_scrollbar.config(command=self.checkbox_text.yview)

        self.databox_scrollbar = Scrollbar(self.right_frame)
        self.databox_scrollbar.grid(row=0, column=1, sticky='NS')
        self.databox_text = Text(self.right_frame, height=30, width=10,
                                yscrollcommand=self.databox_scrollbar.set)
        self.databox_text.grid(row=0, column=0)
        self.databox_scrollbar.config(command=self.databox_text.yview)

        my_dict = {}
        for each_num in range(20):
            my_line = "Line number: " + str(each_num)
            my_dict[my_line] = 0

        for my_key in my_dict:
            my_dict[my_key] = IntVar()
            cb = Checkbutton(text=my_key, variable=my_dict[my_key])
            self.checkbox_text.window_create(END, window=cb)
            self.checkbox_text.insert(END, "\n")

        for each_entry in range(20):
            entry_line = "This is entry number: " + str(each_entry) + "\n"
            self.databox_text.insert(END, entry_line)


root = Tk()
root.title("Checkbox UI Test")
myapp = MyApp(root)
root.mainloop()
