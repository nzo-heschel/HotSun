import datetime
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class DemandHourly(ABC):
    """
        This abstract class wraps the predicted consumption db
    """

    def get_demand_daily_by_date(self, date: datetime.datetime):
        """
        return the predicted consumption in given date
        :param date: the requested time
        :return: arr of the power consumption at that day by hour
        """
        return self.get_demand_hourly_by_range_of_date(date, date + datetime.timedelta(days=1))[0]

    @abstractmethod
    def get_demand_hourly_by_range_of_date(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        return the predicted consumption in given date
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the power consumption at that day by hour
        """
        pass


class DemandHourlyStateData(DemandHourly):
    """
    This class implements DemandHourly (kWh) for state data
    """

    def __init__(self):
        self.df = pd.read_csv("data/hourlyConsumptionPrediction.csv", header=[0])
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)

    def get_demand_hourly_by_range_of_date(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        return the predicted consumption in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the power consumption at that date range by hour
        """

        # TODO: normalize the data that wil fit the city

        # make sure the dates are at the beginning of the day
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] < end_date)].to_numpy()

        return [day[1:] for day in period]  # remove Date col


class SolarRadiationHourly(ABC):
    """
    This class wraps the solar radiation db
    """

    @abstractmethod
    def get_solar_rad_daily_by_range_of_date(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        return the predicted consumption in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the power consumption at that date range by hour
        """
        pass


class SolarRadiationHourlyMonthData(SolarRadiationHourly):
    """
    This class implements SolarRadiationHourly for month radiation data
    """

    def __init__(self):
        titles = ["Month"]
        titles += [i for i in range(0, 24)]
        self.df = pd.read_csv("data/SolarRadiation.csv", names=titles)

    def get_solar_rad_daily_by_range_of_date(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """

        # make sure the dates are at the beginning of the day
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Month'] >= start_date.month) & (self.df['Month'] <= end_date.month)].to_dict()

        curr_date = start_date
        hourly_solar_rad_daily_arr = []
        while curr_date < end_date:
            # TODO: random the solar radiation in every day
            daily_solar_rad = self.df[self.df['Month'] == curr_date.month].to_numpy()[0]
            hourly_solar_rad_daily_arr.append(daily_solar_rad[1:])  # remove the month index
            curr_date += datetime.timedelta(days=1)

        return hourly_solar_rad_daily_arr


def get_town_loc_by_name():
    df = pd.read_csv("data/cities.csv", header=[0])
    df['loc'] = list(zip(df['lat'], df['lng']))
    return list(zip(df['city'], df['loc']))
