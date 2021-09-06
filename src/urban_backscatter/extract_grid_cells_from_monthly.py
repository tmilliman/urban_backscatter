#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
script to extract JAS mean backscatter values for each of the
grid cells in a rectangular region around a lat-lon location.
"""

import sys
import os
import argparse
import datetime
import pandas as pd

import urban_backscatter as ubs


def ds_to_df(sig0_monthly, srctag):
    """
    Take a xarray DataSet with monthly sig0 mean and StdDev values and
    convert it to a (wide) dataframe with mean and std for each time
    period.  The srctag parameter should be one of 'SASS', 'ERS',
    'QuikSCAT', 'ASCAT'.

    """

    # check srctag
    if srctag not in ["SASS", "ERS", "QuikSCAT", "ASCAT"]:
        errmsg = (
            "instrument should be one of 'SASS', "
            + "'ERS', 'QuikSCAT',"
            + " or 'ASCAT'"
        )
        raise ValueError(errmsg)

    # extract sig0 DataArray from dataset
    sig0_monthly_mean = sig0_monthly["sig0"]
    sig0_monthly_std = sig0_monthly["sig0std"]

    # convert DataArray to dataframe
    df = sig0_monthly_mean.to_dataframe()
    df_test = df.reset_index()

    # convert from long to wide format
    df_wide = df_test.pivot(
        index=["lat", "lon"], columns="time", values="sig0"
    ).reset_index()
    column_list = list(df_wide.columns[2:])

    # rename columns to match earthengine outputs
    time_colnames = [
        srctag + str(x.year) + "_" + "{:02d}".format(x.month) + "_mean"
        for x in column_list
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

    # convert DataArray to dataframe
    df = sig0_monthly_std.to_dataframe()
    df_test = df.reset_index()

    # convert from long to wide format
    df_wide = df_test.pivot(
        index=["lat", "lon"], columns="time", values="sig0std"
    ).reset_index()
    column_list = list(df_wide.columns[2:])

    # rename columns to match earthengine outputs
    time_colnames = [
        srctag + str(x.year) + "_" + "{:02d}".format(x.month) + "_std"
        for x in column_list
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
    df = pd.merge(df_mean, df_std, on=["latitude", "longitude"])

    # reorder columns
    newcols = ["latitude", "longitude"] + sorted(df.columns[2:])
    df = df[newcols]
    df.sort_values(by=["latitude", "longitude"], ascending=[False, True], inplace=True)

    return df


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "create CSV with values for each grid"
            + " grid cell in a 11x11 rectangular region around"
            + " a lat-lon location."
        )
    )

    # add command options
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
        default=False,
    )

    # parser.add_argument(
    #     "--with-sass",
    #     help="include SASS data in CSV",
    #     action="store_true",
    #     default=False,
    # )

    parser.add_argument(
        "-d",
        "--datadir",
        nargs="?",
        help=("data directory for output and finding netcdf files"),
        const="./data",
        default="./data",
    )

    # add positional arguments
    parser.add_argument("lat", type=float, help="Latitude of location")

    parser.add_argument("lon", type=float, help="Longitude (-180-180) of location")

    parser.add_argument("locname", help="location name")

    args = parser.parse_args()
    verbose = args.verbose
    lat = args.lat
    lon = args.lon
    locname = args.locname
    # withsass = args.with_sass
    withsass = False
    datadir = args.datadir

    if verbose:
        today = datetime.date.today()
        print("date: {}".format(today))
        print("location: {} {}".format(lon, lat))
        print("name: {}".format(locname))
        # print("include SASS: {}".format(withsass))
        print("data directory: {}".format(datadir))

    # get 11x11 box around center location
    lonmin, latmin, lonmax, latmax = ubs.cmgutils.box11(lon, lat, verbose=True)

    if verbose:
        print("Bounding Box:  {} {} {} {}".format(lonmin, latmin, lonmax, latmax))

    if withsass:
        # extract SeaSAT data
        monthly_sass_ds = ubs.ncfileio.get_monthly_data(datadir, "SASS", verbose=True)

        # subset DataSet
        # get a xarray data slice for box around the city
        sass_start_date = "1978-07-01"
        sass_end_date = "1978-10-01"
        sass_monthly = monthly_sass_ds.sel(
            time=slice(sass_start_date, sass_end_date),
            lon=slice(lonmin, lonmax),
            lat=slice(latmax, latmin),
        )
        if verbose:
            print("SASS data size: {}".format(sass_monthly["sig0"].shape))

        sass_df = ds_to_df(sass_monthly, "SASS")

        if verbose:
            print(sass_df.head())

    # extract ERS1/2 data
    monthly_ers_ds = ubs.ncfileio.get_monthly_data(datadir, "ERS", verbose=True)

    # subset DataSet
    # get a xarray data slice for box around the city
    ers_start_date = "1993-01-01"
    ers_end_date = "2001-01-01"
    ers_monthly = monthly_ers_ds.sel(
        time=slice(ers_start_date, ers_end_date),
        lon=slice(lonmin, lonmax),
        lat=slice(latmax, latmin),
    )
    if verbose:
        print("ERS data size: {}".format(ers_monthly["sig0"].shape))

    ers_df = ds_to_df(ers_monthly, "ERS")

    if verbose:
        print(ers_df.head())

    # extract QSCAT data
    monthly_qscat_ds = ubs.ncfileio.get_monthly_data(datadir, "QuikSCAT", verbose=True)

    # subset DataSet
    # get a xarray data slice for box around the city
    qscat_start_date = "1999-07-01"
    qscat_end_date = "2009-12-01"
    qscat_monthly = monthly_qscat_ds.sel(
        time=slice(qscat_start_date, qscat_end_date),
        lon=slice(lonmin, lonmax),
        lat=slice(latmax, latmin),
    )
    if verbose:
        print("QSCAT data size: {}".format(qscat_monthly["sig0"].shape))

    qscat_df = ds_to_df(qscat_monthly, "QuikSCAT")

    if verbose:
        print(qscat_df.head())

    # extract ASCAT data
    monthly_ascat_ds = ubs.ncfileio.get_monthly_data(datadir, "ASCAT", verbose=True)

    # subset DataSet
    # get a xarray data slice for box around the city
    ascat_start_date = "2007-01-01"
    ascat_end_date = "2020-12-31"
    ascat_monthly = monthly_ascat_ds.sel(
        time=slice(ascat_start_date, ascat_end_date),
        lon=slice(lonmin, lonmax),
        lat=slice(latmax, latmin),
    )
    if verbose:
        print("ASCAT data size: {}".format(ascat_monthly["sig0"].shape))

    ascat_df = ds_to_df(ascat_monthly, "ASCAT")

    if verbose:
        print(ascat_df.head())

    # merge data from all four/three instruments
    if withsass:
        df1 = pd.merge(sass_df, ers_df, how="left", on=["latitude", "longitude"])
    else:
        df1 = ers_df

    df2 = pd.merge(df1, qscat_df, how="left", on=["latitude", "longitude"])
    df3 = pd.merge(df2, ascat_df, how="left", on=["latitude", "longitude"])

    if verbose:
        print(df3.head())
        print(df3.columns)

    # write out CSV
    outdir = os.path.join(datadir, "CSV")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    outname = "{}/{}_bs_grid_monthly.csv".format(outdir, locname)
    df3.to_csv(outname, na_rep="-9999.0", index=False)
