#!/usr/bin/env python

from contextlib import contextmanager
import pytest
import urban_backscatter as ubs


def test_io_monthly():
    """
    pytest function for io of monthly netcdf file
    """

    # # try with SASS
    # myds = ubs.ncfileio.get_monthly_data("./data", "SASS", verbose=True)
    # sass_months = len(myds["time"])

    # try with ERS
    myds = ubs.ncfileio.get_monthly_data("./data", "ERS", verbose=True)
    ers_months = len(myds["time"])

    # try with QuikSCAT
    myds = ubs.ncfileio.get_monthly_data("./data", "QuikSCAT", verbose=True)
    qscat_months = len(myds["time"])

    # try with ASCAT
    myds = ubs.ncfileio.get_monthly_data("./data", "ASCAT", verbose=True)
    ascat_months = len(myds["time"])

    # assert sass_months == 3
    assert ers_months == 96
    assert qscat_months == 125
    assert ascat_months == 168


def test_io_seasonal_masked():
    """
    pytest function for io of seasonal masked netcdf file
    """

    # # try with SASS
    # myds = ubs.ncfileio.get_seasonal_data(
    #     "./data", "SASS", season="JAS", masked=True, verbose=True
    # )
    # sass_years = len(myds["time"])

    # try with ERS
    myds = ubs.ncfileio.get_seasonal_data(
        "./data", "ERS", season="JAS", masked=True, verbose=True
    )
    ers_years = len(myds["time"])

    # try with QSCAT
    myds = ubs.ncfileio.get_seasonal_data(
        "./data", "QuikSCAT", season="JAS", masked=True, verbose=True
    )
    qscat_years = len(myds["time"])

    # try with ASCAT
    myds = ubs.ncfileio.get_seasonal_data(
        "./data", "ASCAT", season="JAS", masked=True, verbose=True
    )
    ascat_years = len(myds["time"])

    # assert sass_years == 1
    assert ers_years == 8
    assert qscat_years == 11
    assert ascat_years == 14


def test_io_seasonal_unmasked():
    """
    pytest function for io of seasonal unmasked netcdf file
    """

    # try with ERS
    myds = ubs.ncfileio.get_seasonal_data(
        "./data", "ERS", season="JAS", masked=False, verbose=True
    )
    ers_years = len(myds["time"])

    # try with QSCAT
    myds = ubs.ncfileio.get_seasonal_data(
        "./data", "QuikSCAT", season="JAS", masked=False, verbose=True
    )
    qscat_years = len(myds["time"])

    # try with ASCAT
    myds = ubs.ncfileio.get_seasonal_data(
        "./data", "ASCAT", season="JAS", masked=False, verbose=True
    )
    ascat_years = len(myds["time"])

    assert ers_years == 8
    assert qscat_years == 11
    assert ascat_years == 14


def test_bad_season_raises_value_error():
    """
    pytest function for ncfileio of seasonal masked netcdf file
    with a bad season string
    """

    # try with bad season
    with pytest.raises(ValueError):
        ubs.ncfileio.get_seasonal_data(
            "./data", "ERS", season="JOS", masked=False, verbose=True
        )


def test_bad_platform_raises_value_error():
    """
    pytest function for ncfileio of seasonal masked netcdf file
    with a bad season string
    """

    # try with bad platform
    with pytest.raises(ValueError):
        ubs.ncfileio.get_seasonal_data(
            "./data", "XXX", season="JAS", masked=False, verbose=True
        )
