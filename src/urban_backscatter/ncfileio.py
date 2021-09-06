#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xarray as xr

PLATFORMS = ["SASS", "ERS", "QuikSCAT", "ASCAT"]

SEASON_LIST = ["JFM", "AMJ", "JAS", "OND"]

SEASON_SEL = {"JFM": 2, "AMJ": 5, "JAS": 8, "OND": 11}


def get_monthly_data(datadir, instrument, verbose=False):
    """
    function to read in netcdf files for a single instrument and
    return an xarray dataset with sig0 mean and stddev.  It is
    assumed that the netcdf files are in a directory, <datadir>.
    """

    if instrument not in ["SASS", "ERS", "QuikSCAT", "ASCAT"]:
        errmsg = "instrument should be one of 'SASS' " + "'ERS', 'QuikSCAT' or 'ASCAT'"
        raise ValueError(errmsg)

    # set up filepath for sig0 means
    infile = "{}_monthly_land_sig0_mean.nc".format(instrument)
    inpath = os.path.join(datadir, infile)
    if verbose:
        print("input file path: {}".format(inpath))

    # Open up the data
    with xr.open_dataset(inpath) as file_nc:
        monthly_mean_xr = file_nc

    # repeat for sig0std
    infile = "{}_monthly_land_sig0_StdDev.nc".format(instrument)
    inpath = os.path.join(datadir, infile)
    if verbose:
        print("input file path: {}".format(inpath))

    # Open up the data
    with xr.open_dataset(inpath) as file_nc:
        monthly_std_xr = file_nc

    # merge two datasets
    monthly_xr = monthly_mean_xr.merge(monthly_std_xr["sig0std"], join="exact")
    return monthly_xr


def get_seasonal_data(datadir, instrument, season="JAS", masked=False, verbose=False):
    """
    function to read in netcdf file for a single instrument and return
    an xarray dataset.  It is assumed that the netcdf files are in a
    directory, <datadir>.
    """

    if instrument not in ["SASS", "ERS", "QuikSCAT", "ASCAT"]:
        errmsg = "instrument should be one of 'SASS' " + "'ERS', 'QuikSCAT' or 'ASCAT'"
        raise ValueError(errmsg)

    if season not in SEASON_LIST:
        errmsg = "season should be one of 'JFM', 'AMJ', 'JAS' or 'OND'"
        raise ValueError(errmsg)

    if masked:
        maskname = "urban"
    else:
        maskname = "land"

    # set up filepath for sig0 means
    infile = "{}_seasonal_{}_sig0_mean.nc".format(instrument, maskname)
    inpath = os.path.join(datadir, infile)
    if verbose:
        print("input file path for mean: {}".format(inpath))

    # Open up the data
    with xr.open_dataset(inpath) as file_nc:
        seasonal_xr = file_nc

    # select season
    month = SEASON_SEL[season]
    season_mean_xr = seasonal_xr.sel(time=seasonal_xr.time.dt.month == month)

    # repeat for StdDev
    infile = "{}_seasonal_{}_sig0_StdDev.nc".format(instrument, maskname)
    inpath = os.path.join(datadir, infile)
    if verbose:
        print("input file path for StdDev: {}".format(inpath))

    # Open up the data
    with xr.open_dataset(inpath) as file_nc:
        seasonal_std_xr = file_nc

    # select season
    month = SEASON_SEL[season]
    season_std_xr = seasonal_std_xr.sel(time=seasonal_xr.time.dt.month == month)

    # combine mean and standard deviation
    season_xr = season_mean_xr.merge(season_std_xr.sig0std, join="exact")
    return season_xr
