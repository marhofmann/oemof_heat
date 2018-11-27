"""
This script creates time series input for
optimise_district_heating.py

* heat demand time series
* electricity price time series
* 

"""

__copyright__ = "Reiner Lemoine Institut"
__license__ = "GPLv3"
__author__ = "c-moeller, jnnr"


import pandas as pd
import demandlib.bdew as bdew
import matplotlib
import matplotlib.pyplot as plt
import datetime
import os
from workalendar.europe import Germany
import yaml

abs_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))

def prepare_timeseries_temperature(raw_file, output_file):
    """
    convert raw temperature data to appropriate format.
    """
    # load temperature data
    filename = abs_path + '/data_raw/' + raw_file
    temperature = pd.read_csv(filename,
                              skiprows=3,
                              index_col=0,
                              names=['time', 'utc', 'temperature'],
                              usecols=['time', 'temperature'],
                              parse_dates=True)

    temperature.to_csv(output_file)

    return temperature

def prepare_timeseries_demand_heat(year, building_types, temperature, output_file):
    """
    Creates synthetic heat profiles using the BDEW method.
    """
    # get holidays for germany
    cal = Germany()
    holidays = dict(cal.holidays(year))

    # create a DataFrame to hold the timeseries
    demand = pd.DataFrame(
        index=pd.date_range(pd.datetime(year, 1, 1, 0),
                            periods=8760, freq='H'))
    demand = pd.DataFrame(index=temperature.index)

    # Single family house (efh: Einfamilienhaus)
    demand['efh'] = bdew.HeatBuilding(
        demand.index, holidays=holidays, temperature=temperature,
        shlp_type='EFH',
        building_class=1, wind_class=1, annual_heat_demand=232000000,
        name='EFH').get_bdew_profile()

    # Multi family house (mfh: Mehrfamilienhaus)
    demand['mfh'] = bdew.HeatBuilding(
        demand.index, holidays=holidays, temperature=temperature,
        shlp_type='MFH',
        building_class=2, wind_class=0, annual_heat_demand=80000000,
        name='MFH').get_bdew_profile()

    # Industry, trade, service (ghd: Gewerbe, Handel, Dienstleistung)
    demand['ghd'] = bdew.HeatBuilding(
        demand.index, holidays=holidays, temperature=temperature,
        shlp_type='ghd', wind_class=0, annual_heat_demand=140000000,
        name='ghd').get_bdew_profile()

    # save heat demand time series
    demand['efh'].to_csv(output_file)

def prepare_timeseries_price_gas():
    # prepare gas price time series
    ger_day_ahead_prices_2006_2018 = pd.read_csv(abs_path +'/data/opsd-time_series-2018-06-30/time_series_60min_singleindex.csv', index_col='cet_cest_timestamp')['DE_price_day_ahead']
    print(ger_day_ahead_prices_2006_2018)
    ger_day_ahead_prices_2014 = ger_day_ahead_prices_2006_2018.loc['2014-01-01T00:00:00+0100':'2014-12-31T23:00:00+0100']
    ger_day_ahead_prices_2006_2018.to_csv(abs_path+'/data/'+'day_ahead_price_el_2006_2018.csv')
    ger_day_ahead_prices_2014.to_csv(abs_path+'/data/'+'day_ahead_price_el_2014.csv')

def prepare_timeseries_price_electricity():
    # prepare electricity price time series
    pass

def prepare_timeseries(config_path, results_dir):
    # open config
    abs_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    # temperature
    temperature = prepare_timeseries_temperature(
        'ninja_weather/ninja_weather_51.8341_12.2374_uncorrected.csv',
        results_dir + '/data_preprocessed/temperature.csv')

    # heat demand
    prepare_timeseries_demand_heat(2014, None, temperature, os.path.join(results_dir, cfg['timeseries']['timeseries_demand_heat']))

if __name__ == '__main__':
    prepare_timeseries()