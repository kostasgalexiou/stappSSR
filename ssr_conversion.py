#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""
import re
import numpy as np
import pandas as pd
from collections import OrderedDict as od


def generate_output(dframe, alleles_list):

    # start building the new dataframe
    dframe_transp = dframe.iloc[:,1:].T
    dframe_transp.columns = dframe[dframe.columns[0]]

    final_column_list = ['Lines']
    final_column_list.extend(alleles_list)
    final_list = [final_column_list]

    alleles_dict = dict(zip(alleles_list, np.arange(len(alleles_list))))
    for col in dframe_transp.columns:
        binary_list = list()
        binary_list.append(col)

        # generate a dictionary where each allele has a number assigned, starting from 0 to the length of
        # the allele list
        new_alleles_list = len(alleles_list)*["-"]
        for i,a in enumerate(alleles_list):
            if a.rsplit('_',1)[0] in dframe.columns[1:]:
                new_alleles_list[i] = '0'

        for i, col_entry in enumerate(dframe_transp[col].to_list()):

            if not isinstance(col_entry, int) and col_entry != '-':
                for c in col_entry.split("/"):
                    new_alleles_list[alleles_dict[dframe_transp.index[i]+'_'+str(c)]] = '1'
            else:
                if col_entry == "-":
                    #     continue
                    #     # # get the allele list indices that correspond to the marker alleles and replace those positions
                    #     # # with "-"
                    for allele in alleles_list:
                        result = re.search(r'%s_[0-9]+'%dframe_transp.index[i], allele)
                        if result:
                            new_alleles_list[alleles_dict[allele]] = '-'
                else:
                    #     # replace 0 with 1 at the corresponding index of the unique_peak_dict, for the col_entry
                    new_alleles_list[alleles_dict[dframe_transp.index[i]+'_'+str(col_entry)]] = '1'
        binary_list.extend(new_alleles_list)

        final_list.append(binary_list)

    new_df = pd.DataFrame(final_list)
    new_df.columns = new_df.iloc[0]
    new_df = new_df.iloc[1:,]

    return new_df

def generate_allele_final_list(dframe, dframe_row, marker_dict):

    numeric_list = list()
    markerset = set()
    marker_list = []
    alleles_per_marker = []

    # loop over alleles and data frame rows, excluding line column header and line names
    for column, row_elem in zip(dframe.columns[1:].tolist(), dframe_row[1:]):
        marker, size = column.rsplit('_', 1)

        if marker not in marker_dict.keys():
            continue

        elif str(row_elem) == '1':
            if marker not in markerset:
                markerset.add(marker)
                marker_list.append(marker)
                alleles_per_marker = list()

            if alleles_per_marker:
                numeric_list.append(alleles_per_marker)

            alleles_per_marker.append(size)

        elif str(row_elem) == '-' or str(row_elem) == '0':
            if marker not in markerset:
                markerset.add(marker)
                marker_list.append(marker)
                alleles_per_marker = list()

            if alleles_per_marker:
                numeric_list.append(alleles_per_marker)

            alleles_per_marker.append('-')

    return numeric_list, marker_list

def dict_marker(alleles_list):
    marker2sizes = od()
    for i in alleles_list:
        marker, size = i.rsplit('_', 1)

        if marker not in marker2sizes.keys():
            size_list = list()

        size_list.append(int(size))
        marker2sizes[marker] = size_list

    return marker2sizes

def generate_output_from_binary(dframe, alleles_list):

    unique_markers = list(od.fromkeys([x.rsplit('_', 1)[0] for x in alleles_list]))

    numeric_marker_list = ['-'] * (len(unique_markers) + 1)  # line entry plus allele size info per marker

    final_list = list()
    final_list.append(unique_markers)

    for i in range(len(dframe)):

        dfrow = dframe.iloc[i].to_list()  # get row

        linename = dfrow[0]
        numeric_marker_list[0] = linename

        mdict = dict_marker(alleles_list=alleles_list)
        nlist, mlist = generate_allele_final_list(dframe=dframe, dframe_row=dfrow, marker_dict=mdict)

        #obtain unique list entries
        x = []
        for f in nlist:
            if f not in x:
                x.append(f)
        #replace numeric_marker_list elements with "-" or allele sizes
        for m, n in zip(mlist, x):
            if set(n) == {'-'}:
                numeric_marker_list[unique_markers.index(m) + 1] = '-'
            else:
                numeric_marker_list[unique_markers.index(m) + 1] = '/'.join(n)

        final_list.append(numeric_marker_list)
        numeric_marker_list = ['-'] * (len(unique_markers) + 1)

    final_list[0].insert(0, 'Lines')

    new_df_sizes = pd.DataFrame(final_list)
    new_df_sizes.columns = new_df_sizes.iloc[0]
    new_df_sizes = new_df_sizes.iloc[1:, ]

    return new_df_sizes