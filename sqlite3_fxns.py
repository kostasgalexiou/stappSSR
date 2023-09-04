#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""
import base64
import sqlite3
import time

timestr = time.strftime("%Y%m%d-%H%M%S")
import streamlit as st
import pandas as pd

conn = sqlite3.connect("species.db", check_same_thread=False)
c = conn.cursor()


def create_and_populate_table(species_name, infile_df, usern):
    c.execute(
        """CREATE TABLE IF NOT EXISTS %s (marker_name TEXT UNIQUE,
        person TEXT,
        uploadDate TIMESTAMP)"""
        % species_name
    )

    column_list = infile_df[0].to_list()
    column_list = [[x.strip()] for x in column_list]

    add_markers(species_name, column_list, usern)


def add_markers(species, inlist, username):
    for elem in inlist:
        with conn:
            c.execute(
                """INSERT INTO %s(marker_name,person,uploadDate) VALUES (?,?,?)"""
                % species,
                (elem[0], username, timestr),
            )
            conn.commit()


def select_all_tables():
    command = "SELECT marker_name FROM sqlite_master WHERE type='table';"
    tables = list(c.execute(command))
    return tables


# View Details
def view_all_data(sel_species):
    c.execute("""SELECT marker_name FROM %s ORDER BY marker_name""" % sel_species)
    data = c.fetchall()
    return data


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
        new_filename = "{}-binary_{}.csv".format(self.filename, timestr)
        st.markdown("#### Download File ###")
        href = f'<a href="data:file/csv;base64,{b64}" download="{new_filename}">Click Here!!</a>'
        st.markdown(href, unsafe_allow_html=True)
