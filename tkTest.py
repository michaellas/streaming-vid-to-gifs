#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as tk #import modułu biblioteki Tkinter -- okienka

root = tk.Tk()
root.title("Filters") #utworzenie okienka

#obsługa checkbox'a
check1=tk.IntVar()
checkbox1 = tk.Checkbutton(root, text="Filter 1", variable=check1)
checkbox1.pack()

root.mainloop()