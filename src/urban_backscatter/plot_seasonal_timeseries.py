#!/usr/bin/env python

"""
script to extract seasonal mean backscatter values for each of the
grid cells in a square region (11x11) around a lat-lon location
and make a timeseries plot. For the plot the mean over the 11x11
region is used.

Here were using the unmasked netcdf file to match earlier work
and so that different urban built fraction masks can be applied.
For summer means we use JAS in the northern hemisphere and JFM
in the southern hemisphere.
"""

import sys
import argparse
import datetime
import pandas as pd
import matplotlib.pyplot as plt

import urban_backscatter as ubs


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "create CSV with values for each grid"
            + " grid cell in a rectangular region around"
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
    datadir = args.datadir

    if verbose:
        today = datetime.date.today()
        print("date: {}".format(today))
        print("season: {}".format(season))
        print("location: {} {}".format(lon, lat))
        print("name: {}".format(locname))
        print("data directory: {}".format(datadir))

    # get 11x11 box around center location
    lonmin, latmin, lonmax, latmax = ubs.cmgutils.box11(lon, lat, verbose=True)

    if verbose:
        print("Bounding Box:  {} {} {} {}".format(lonmin, latmin, lonmax, latmax))

    # extract ERS1/2 data
    ers_data = ubs.ncfileio.get_seasonal_data(
        datadir, "ERS", season=season, masked=False, verbose=True
    )

    # subset ERS DataSet
    ers_data_subset = ers_data.sel(
        lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
    )
    ers_ts = ers_data_subset.mean(dim=["lon", "lat"], skipna=True)
    edf = ers_ts.to_dataframe()
    edf = edf.drop(axis=1, columns=["spatial_ref"])
    edf["instr"] = "ERS"
    if verbose:
        print(edf.head())

    # extract QSCAT data
    qscat_data = ubs.ncfileio.get_seasonal_data(
        datadir, "QuikSCAT", season=season, masked=False, verbose=True
    )
    qscat_data_subset = qscat_data.sel(
        lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
    )
    qscat_ts = qscat_data_subset.mean(dim=["lon", "lat"], skipna=True)
    qdf = qscat_ts.to_dataframe()
    qdf = qdf.drop(axis=1, columns=["spatial_ref"])
    qdf["instr"] = "QuikSCAT"
    if verbose:
        print(qdf.head())

    # extract ASCAT data
    ascat_data = ubs.ncfileio.get_seasonal_data(
        datadir, "ASCAT", season=season, masked=False, verbose=True
    )
    ascat_data_subset = ascat_data.sel(
        lon=slice(lonmin, lonmax), lat=slice(latmax, latmin),
    )
    ascat_ts = ascat_data_subset.mean(dim=["lon", "lat"], skipna=True)
    adf = ascat_ts.to_dataframe()
    adf = adf.drop(axis=1, columns=["spatial_ref"])
    adf["instr"] = "ASCAT"
    if verbose:
        print(adf.head())

    # combine the data frames
    df = pd.concat([edf, qdf, adf])

    # for plotting switch to power ratio (PR)
    prdf = df
    prdf["pr"] = 10.0 ** (prdf["sig0"] / 10.0)

    # standard deviations are trickier since we're in dB space.
    # so just calculate PR values for upper and lower values
    prdf["pr_high"] = 10.0 ** ((prdf["sig0"] + prdf["sig0std"]) / 10.0)
    prdf["pr_low"] = 10.0 ** ((prdf["sig0"] - prdf["sig0std"]) / 10.0)

    # for plotting split back out into separate data frames
    # for each instrument and reset index
    ers_prdf = prdf[prdf["instr"] == "ERS"].reset_index()
    qscat_prdf = prdf[prdf["instr"] == "QuikSCAT"].reset_index()
    ascat_prdf = prdf[prdf["instr"] == "ASCAT"].reset_index()

    # make plot
    fig = plt.figure(figsize=(10, 6))
    plt.plot(ers_prdf["time"], ers_prdf["pr"], marker="o")
    plt.fill_between(
        x=ers_prdf["time"], y1=ers_prdf["pr_low"], y2=ers_prdf["pr_high"], alpha=0.5
    )
    plt.plot(qscat_prdf["time"], qscat_prdf["pr"], marker="o")
    plt.fill_between(
        x=qscat_prdf["time"],
        y1=qscat_prdf["pr_low"],
        y2=qscat_prdf["pr_high"],
        alpha=0.5,
    )

    plt.plot(ascat_prdf["time"], ascat_prdf["pr"], marker="o")
    plt.fill_between(
        x=ascat_prdf["time"],
        y1=ascat_prdf["pr_low"],
        y2=ascat_prdf["pr_high"],
        alpha=0.5,
    )

    # add some anotations
    plt.title("{} (lat:{:.4f} lon:{:.4f})".format(locname, lat, lon))
    plt.ylabel("Mean {} Backscatter Power Ratio (PR)".format(season))
    plt.xlabel("Year")

    # save to file
    outfile = "{}_{}_timeseries_plot.pdf".format(locname, season)
    plt.savefig(outfile)
