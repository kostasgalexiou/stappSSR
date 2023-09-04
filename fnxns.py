#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""

from sqlite3_fxns import view_all_data

def detect_duplicate_markers(user_marker, species):
    user_marker_list = user_marker.split("\n")
    user_marker_list_for_sql = [
        [x] for x in user_marker_list
    ]  # format for running the sqlite3 command

    data = view_all_data(species)
    data2 = [x[0] for x in data]

    # check whether the provided markers are already present in the species database
    common_marker_list = set(data2).intersection(set(user_marker_list))

    return common_marker_list, user_marker_list, user_marker_list_for_sql