#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
script to extract summer mean backscatter values for each of the
grid cells in a square region (11x11) around a lat-lon location.
Here were using the unmasked netcdf file to match earlier work
and so that different urban built fraction masks can be applied.
For summer means we use JAS in the northern hemisphere and JFM
in the southern hemisphere.
"""

import sys
import os
import argparse
import datetime
import pandas as pd

import urban_backscatter as ubs


def ds_to_df(ds, season, srctag):
    """
    Take a xarray Dataset with yearly mean and stddev sig0 values and
    convert it to a (wide) dataframe with mean and std for each year.
    The srctag parameter should be one of 'ERS', 'QSCAT', 'ASCAT'.
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "create CSV with values for each grid"
            + " cell in a 11x11 rectangular region around"
            + " a lat-lon location."
        )
    )

    # add arguments
    parser.add_argument(
        "-s",
        "--season",
        nargs=1,
        choices=["JFM", "AMJ", "JAS", "OND"],
        help="season/quarter to select",
        default=["JAS"],
    )

    # add command options
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--with-sass",
        help="include SASS data in CSV",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-d",
        "--datadir",
        nargs="?",
        help=("data directory for output and finding netcdf files"),
        const="./",
        default="./",
    )

    # add positional arguments
    parser.add_argument("lat", type=float, help="Latitude of location")

    parser.add_argument("lon", type=float, help="Longitude (-180-180) of location")

    parser.add_argument("locname", help="location name")

    args = parser.parse_args()
    verbose = args.verbose
    season = args.season[0]
    lat = args.lat
    lon = args.lon
    locname = args.locname
    withsass = args.with_sass
    datadir = args.datadir

    if verbose:
        today = datetime.date.today()
        print("date: {}".format(today))
        print("season: {}".format(season))
        print("location: {} {}".format(lon, lat))
        print("name: {}".format(locname))
        print("include SASS: {}".format(withsass))
        print("data directory: {}".format(datadir))

    # get 11x11 box around center location
    lonmin, latmin, lonmax, latmax = ubs.cmgutils.box11(lon, lat, verbose=True)

    if verbose:
        print("Bounding Box:  {} {} {} {}".format(lonmin, latmin, lonmax, latmax))

    if withsass:
        # extract SASS data
        sass_data = ubs.ncfileio.get_seasonal_data(
            datadir, "SASS", season=season, masked=False, verbose=True
        )

        # subset DataSet
        sass_data_subset = sass_data.sel(
            lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
        )
        if verbose:
            print("SASS data size: {}".format(sass_data_subset["sig0"].shape))

        sass_df = ds_to_df(sass_data_subset, season, "SASS")

        if verbose:
            print(sass_df.head())

    # extract ERS1/2 data
    ers_data = ubs.ncfileio.get_seasonal_data(
        datadir, "ERS", season=season, masked=False, verbose=True
    )

    # subset DataSet
    ers_data_subset = ers_data.sel(
        lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
    )
    if verbose:
        print("ERS data size: {}".format(ers_data_subset["sig0"].shape))

    ers_df = ubs.dsutils.ds_to_df(ers_data_subset, season, "ERS")

    if verbose:
        print(ers_df.head())

    # extract QSCAT data
    qscat_data = ubs.ncfileio.get_seasonal_data(
        datadir, "QuikSCAT", season=season, masked=False, verbose=True
    )

    # subset DataSet
    qscat_data_subset = qscat_data.sel(
        lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
    )
    if verbose:
        print("QSCAT data size: {}".format(qscat_data_subset["sig0"].shape))

    qscat_df = ds_to_df(qscat_data_subset, season, "QSCAT")

    if verbose:
        print(qscat_df.head())

    # extract ASCAT data
    ascat_data = ubs.ncfileio.get_seasonal_data(
        datadir, "ASCAT", season=season, masked=False, verbose=True
    )

    # subset DataSet
    ascat_data_subset = ascat_data.sel(
        lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
    )
    if verbose:
        print("ASCAT data size: {}".format(ascat_data_subset["sig0"].shape))

    ascat_df = ds_to_df(ascat_data_subset, season, "ASCAT")

    if verbose:
        print(ascat_df.head())

    # # merge data from all three instruments
    if withsass:
        df = pd.merge(sass_df, ers_df, how="left", on=["latitude", "longitude"])
    else:
        df = ers_df

    df1 = pd.merge(df, qscat_df, how="left", on=["latitude", "longitude"])

    df2 = pd.merge(df1, ascat_df, how="left", on=["latitude", "longitude"])

    if verbose:
        print(df2.head())
        print(df2.columns)

    # write out CSV
    outdir = os.path.join(datadir, "CSV")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    outname = "{}/{}_bs_grid_{}.csv".format(outdir, locname, season)
    # df_combined.to_csv(outname, index=False)
    df2.to_csv(outname, na_rep="-9999.0", index=False)
