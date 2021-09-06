import sys
import os
import argparse
import datetime
import pandas as pd

import urban_backscatter as ubs


def seasonal_ds_to_df(ds, season, srctag, keep_nodata=False):
    """
    Take a xarray Dataset with seasonal mean and stddev sig0 values and
    convert it to a (wide) dataframe with mean and std for each year.
    The srctag parameter should be one of 'SASS', 'ERS', 'QSCAT', 'ASCAT'.
    """

    # check season
    if season not in ubs.ncfileio.SEASON_LIST:
        errmsg = "season should be one of 'JFM', 'AMJ', 'JAS', 'OND'"
        raise ValueError(errmsg)

    # check srctag which is used in the column headers
    if srctag not in ["SASS", "ERS", "QSCAT", "ASCAT"]:
        errmsg = "instrument should be one of 'SASS', 'ERS', " + "'QSCAT' or 'ASCAT'"
        raise ValueError(errmsg)

    # convert mean sig0 DataArray to dataframe
    da = ds["sig0"]
    df_mean = da.to_dataframe()
    df_mean.dropna(inplace=True)
    df_test = df_mean.reset_index()

    # convert from long to wide format
    df_wide = df_test.pivot(
        index=["lat", "lon"], columns="time", values="sig0"
    ).reset_index()
    column_list = list(df_wide.columns[2:])

    # rename columns to match earthengine outputs
    time_colnames = [
        srctag + str(x.year) + "_{}_mean".format(season) for x in column_list
    ]
    newcolnames = ("latitude", "longitude") + tuple(time_colnames)
    df_wide.columns = newcolnames

    # reduce sigfigs for output
    col_sigfigs = {}
    for col in df_wide.columns:
        if srctag in col:
            col_sigfigs[col] = 3
        else:
            col_sigfigs[col] = 4
    df_mean = df_wide.round(col_sigfigs)

    # repeat for std()
    # convert mean sig0 DataArray to dataframe
    da = ds["sig0std"]
    df_std = da.to_dataframe()
    df_std.dropna(inplace=True)
    df_test = df_std.reset_index()

    # convert from long to wide format
    df_wide = df_test.pivot(
        index=["lat", "lon"], columns="time", values="sig0std"
    ).reset_index()
    column_list = list(df_wide.columns[2:])

    # rename columns to match earthengine outputs
    time_colnames = [
        srctag + str(x.year) + "_{}_std".format(season) for x in column_list
    ]
    newcolnames = ("latitude", "longitude") + tuple(time_colnames)
    df_wide.columns = newcolnames

    # reduce sigfigs for output
    col_sigfigs = {}
    for col in df_wide.columns:
        if srctag in col:
            col_sigfigs[col] = 3
        else:
            col_sigfigs[col] = 4
    df_std = df_wide.round(col_sigfigs)

    # merge two dataframes
    df_season = pd.merge(df_mean, df_std, on=["latitude", "longitude"])

    # reorder columns
    newcols = ["latitude", "longitude"] + sorted(df_season.columns[2:])
    df_season = df_season[newcols]
    df_season.sort_values(
        by=["latitude", "longitude"], ascending=[False, True], inplace=True
    )

    return df_season
