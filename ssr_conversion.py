#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Dec  3 08:26:27 2013

@author: kalexiou
"""
import re
import numpy as np
import pandas as pd
import streamlit as st


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
        new_alleles_list = len(alleles_list)*["?"]
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
                    #     # # with "?"
                    for allele in alleles_list:
                        result = re.search(r'%s_[0-9]+'%dframe_transp.index[i], allele)
                        if result:
                            new_alleles_list[alleles_dict[allele]] = '?'
                else:
                    #     # replace 0 with 1 at the corresponding index of the unique_peak_dict, for the col_entry
                    new_alleles_list[alleles_dict[dframe_transp.index[i]+'_'+str(col_entry)]] = '1'
        binary_list.extend(new_alleles_list)

        final_list.append(binary_list)

    new_df = pd.DataFrame(final_list)
    new_df.columns = new_df.iloc[0]
    new_df = new_df.iloc[1:,]

    return new_df
