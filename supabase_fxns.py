#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""

import streamlit as st
import base64
import time
from supabase import create_client, Client

timestr = time.strftime("%Y-%m-%d")

# Initialize connection.
url: str = st.secrets['connections']['supabase']["SUPABASE_URL"]
key: str = st.secrets['connections']['supabase']["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


# View Details
def view_all_data():
    # get all data from speciesdb table
    info, count = supabase.table("speciesDB").select("*").execute()
    all_data = list(info[1])

    data_list = []
    for d in all_data:
        data_list.append(list(d.values()))

    return data_list


def view_species_data(sel_species):
    info, count = supabase.table("speciesDB").select("*").eq("Species", sel_species).execute()
    all_data = list(info[1])

    mlist = []
    for d in all_data:
        _, m, _, _, _ = list(d.values())
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
        new_filename = "{}_{}.csv".format(self.filename, timestr)

        href = f'<a href="data:file/csv;base64,{b64}" download="{new_filename}">Click Here!!</a>'
        st.markdown(href, unsafe_allow_html=True)
