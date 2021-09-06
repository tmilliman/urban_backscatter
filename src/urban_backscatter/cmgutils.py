#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Functions related to the region of the Climate Modelling Grid (CMG)
# used for the urban backscatter data.


LONMIN = -180.0
LATMIN = -60.0
GRDSIZE = 0.05


def box11(lon, lat, verbose=False):

    # function which creates an 11x11 gridcell box around
    # the city center.

    x0 = int((lon - LONMIN) / GRDSIZE)
    y0 = int((lat - LATMIN) / GRDSIZE)

    lon0 = (x0 * GRDSIZE + GRDSIZE / 2.0) + LONMIN
    lat0 = (y0 * GRDSIZE + GRDSIZE / 2.0) + LATMIN
    if verbose:
        print("Center Cell: {:.3f} {:.3f}".format(lon0, lat0))
    latmin = lat0 - 0.275
    latmax = lat0 + 0.275
    lonmin = lon0 - 0.275
    lonmax = lon0 + 0.275
    return lonmin, latmin, lonmax, latmax
