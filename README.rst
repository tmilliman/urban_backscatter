#################
urban_backscatter
#################


A collection of python scripts for interacting with the NetCDF files
produced for the `Seasonal Urban Backscatter (1993 - 2020) dataset <https://www.ciesin.columbia.edu/data/seasonal-urban-backscatter/>`__ submitted to Scientific
Data August 2021.  The data paper only describes the "seasonal" data set but this
repository also includes scripts to work with the monthly data.


Introduction
============

This is a collection of scripts used to extract CSV files from the
seasonal and monthly NetCDF data files.  The scripts have been developed
in a `miniconda <https://docs.conda.io/en/latest/miniconda.html>`__.
environment.  You can recreate the equivalent environment using the
``environment.yml`` file::

  conda env create --file environment.yml
  conda activate urban_backscatter

Once you place the NetCDF data files in the "data" directory you should
be able to run the test scripts by typing ``pytest``.

Description
===========

There are three scripts in the ``src/urban_backscatter`` directory:

``extract_grid_cells_from_seasonal.py``::

    usage: extract_grid_cells_from_seasonal.py [-h] [-s {JFM,AMJ,JAS,OND}] [-v] [-d [DATADIR]]
                                               lat lon locname
    
    create CSV with values for each grid cell in a 11x11 rectangular region around a lat-lon location.
    
    positional arguments:
      lat                   Latitude of location
      lon                   Longitude (-180-180) of location
      locname               location name
    
    optional arguments:
      -h, --help            show this help message and exit
      -s {JFM,AMJ,JAS,OND}, --season {JFM,AMJ,JAS,OND}
                            season/quarter to select
      -v, --verbose         increase output verbosity
      -d [DATADIR], --datadir [DATADIR]
                            data directory for output and finding netcdf files
    
``extract_grid_cells_from_monthly.py``::

    usage: extract_grid_cells_from_monthly.py [-h] [-v] [-d [DATADIR]] lat lon locname
    
    create CSV with values for each grid grid cell in a 11x11 rectangular region around a lat-lon
    location.
    
    positional arguments:
      lat                   Latitude of location
      lon                   Longitude (-180-180) of location
      locname               location name
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         increase output verbosity
      -d [DATADIR], --datadir [DATADIR]
                            data directory for output and finding netcdf files


``plot_seasonal_timeseries.py``::

    usage: plot_seasonal_timeseries.py [-h] [-s {JFM,AMJ,JAS,OND}] [-v] [-d [DATADIR]] lat lon locname
    
    create CSV with values for each grid grid cell in a rectangular region around a lat-lon location.
    
    positional arguments:
      lat                   Latitude of location
      lon                   Longitude (-180-180) of location
      locname               location name
    
    optional arguments:
      -h, --help            show this help message and exit
      -s {JFM,AMJ,JAS,OND}, --season {JFM,AMJ,JAS,OND}
                            season/quarter to select
      -v, --verbose         increase output verbosity
      -d [DATADIR], --datadir [DATADIR]
                            data directory for output and finding netcdf files  
                                
.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.0.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
