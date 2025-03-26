#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""

import streamlit as st
import base64
import time
import sqlite3


# View Details
def view_all_data():

    conn = sqlite3.connect('species.sqlite')
    cursor = conn.cursor()

    # Execute SELECT query to fetch all data from the table
    table_name = 'data'

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,))
    table = cursor.fetchone()

    if table:
        cursor.execute(f"SELECT * FROM data")

        # Fetch all rows
        rows = cursor.fetchall()

        conn.close()

        data_list = []
        for row in rows:
            data_list.append(list(row))

        return data_list

    else:
        return


def view_species_data(sel_species):
    conn = sqlite3.connect("species.sqlite")
    cursor = conn.cursor()

    query = f"SELECT * FROM data WHERE species = ?"
    cursor.execute(query, (sel_species,))
    rows = cursor.fetchall()

    conn.close()

    mlist = []
    for d in rows:
        m, _, _, _ = list(d)
        mlist.append(m)

    return mlist


class FileDownloader(object):
    """docstring for FileDownloader
    >>> download = FileDownloader(data,filename).download()

    """

    def __init__(self, data, filename="myfile"):
        super(FileDownloader, self).__init__()
        self.data = data
        self.filename = filename

    def download(self):
        b64 = base64.b64encode(self.data.encode()).decode()
        timestr = time.strftime("%Y-%m-%d")

        new_filename = "{}_{}.csv".format(self.filename, timestr)

        href = f'<a href="data:file/csv;base64,{b64}" download="{new_filename}">Click Here!!</a>'
        st.markdown(href, unsafe_allow_html=True)
