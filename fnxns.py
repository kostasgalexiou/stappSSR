#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""

from supabase_fxns import *


def detect_duplicate_markers(user_marker, species):
    user_marker_list = user_marker.split("\n")

    marker_data = view_species_data(species)
    # data2 = [x[0] for x in data]

    # check whether the provided markers are already present in the species database
    common_marker_list = list(set(marker_data).intersection(set(user_marker_list)))

    return common_marker_list, user_marker_list


def add_markers(species, inlist, username):
    list_w_data_to_insert = []
    for i in inlist:
        list_w_data_to_insert.append({'Marker_name': i, 'Species': species, 'Person': username, 'Date': timestr})

    for m in list_w_data_to_insert:
        supabase.table("speciesDB").insert(m).execute()

    return
