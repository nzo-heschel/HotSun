import datetime
import logging

import pandas as pd
import numpy as np
from config_manager import ConfigGetter
from abc import ABC, abstractmethod

import config_manager


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


class Cost(ABC):
    """
    This class wraps a cost db
    """

    @abstractmethod
    def get_buying_price_by_range_of_date(self, start_date: datetime.datetime,
                                          end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_selling_electricity_price_by_range_of_date(self, start_date: datetime.datetime,
                                                       end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_battery_capex_by_range_of_date(self, start_date: datetime.datetime,
                                           end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_battery_opex_by_range_of_date(self, start_date: datetime.datetime,
                                          end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_solar_panel_capex_by_range_of_date(self, start_date: datetime.datetime,
                                               end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_solar_panel_opex_by_range_of_date(self, start_date: datetime.datetime,
                                              end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass


class HourlyPricesData(Cost):
    # TODO: test if it works
    """
    This class implements ElectricityPrices for month radiation data
    """
    BUYING_INDEX = 2
    SELLING_INDEX = 3
    BATTERY_CAPEX_INDEX = 4
    BATTERY_OPEX_INDEX = 5
    PANEL_CAPEX_INDEX = 6
    PANEL_OPEX_INDEX = 7

    def __init__(self):
        titles = ['Date', "Hour", "BuyingElectricityPrice", "SellingElectricityPrice", "BatteryCapex", "BatteryOpex",
                  "SolarPanelCapex", "SolarPanelOpex"]

        self.df = pd.read_csv("data/ElectricityPrices.csv", header=[0])
        #print(self.df.columns)
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)

    def get_start_and_end_hour(self, start_date: datetime.datetime,
                               end_date: datetime.datetime):
        """
        converts the start and end date to start and end hours
        :return: the simulation start date
        """
        logging.info("df objects [prices] - calculates the start and end hours")
        time_string_format = ConfigGetter["TIME_FORMAT"]
        # reads the start & end date as a datetime object
        simulation_initial_time = datetime.datetime.strptime(ConfigGetter["START_DATE"], time_string_format)
        start_hour = abs(start_date - simulation_initial_time).total_seconds() // 3600
        end_hour = abs(end_date - simulation_initial_time).total_seconds() // 3600
        return start_hour, end_hour

    def get_buying_price_by_range_of_date(self, start_date: datetime.datetime,
                                          end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info("df objects [electricity prices] - converts the csv to hourly buying prices in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[self.BUYING_INDEX] for hour in period]

    def get_selling_electricity_price_by_range_of_date(self, start_date: datetime.datetime,
                                                       end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info("df objects [electricity prices] - converts the csv to hourly selling prices in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[self.SELLING_INDEX] for hour in period]

    def get_battery_capex_by_range_of_date(self, start_date: datetime.datetime,
                                           end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info("df objects [electricity prices] - converts the csv to hourly battery capex in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[self.BATTERY_CAPEX_INDEX] for hour in period]

    def get_battery_opex_by_range_of_date(self, start_date: datetime.datetime,
                                          end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info("df objects [electricity prices] - converts the csv to hourly battery opex in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[self.BATTERY_OPEX_INDEX] for hour in period]

    def get_solar_panel_capex_by_range_of_date(self, start_date: datetime.datetime,
                                               end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info(
            "df objects [electricity prices] - converts the csv to hourly solar panel capex in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[self.PANEL_CAPEX_INDEX] for hour in period]

    def get_solar_panel_opex_by_range_of_date(self, start_date: datetime.datetime,
                                              end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info("df objects [electricity prices] - converts the csv to hourly solar panel opex in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[self.PANEL_OPEX_INDEX] for hour in period]


class Pollution(ABC):
    """
    This class wraps a cost db
    """

    @abstractmethod
    def get_emission_rate_by_range_of_date(self, start_date: datetime.datetime,
                                           end_date: datetime.datetime):
        """
        return the solar radiation (W/m^2) in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass


class HourlyEmmision(Pollution):
    # TODO: test if it works
    """
    This class implements ElectricityPrices for month radiation data
    """

    def __init__(self):
        titles = ["Date", "Pollution Rates"]
        self.df = pd.read_csv("data/PollutionRates.csv", header=[0])
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)

    # def get_start_and_end_hour(self, start_date: datetime.datetime,
    #                            end_date: datetime.datetime):
    #     """
    #     converts the start and end date to start and end hours
    #     :return: the simulation start date
    #     """
    #     logging.info("df objects [pollution] - calculates the start and end hours")
    #     time_string_format = ConfigGetter["TIME_FORMAT"]
    #     # reads the start & end date as a datetime object
    #     simulation_initial_time = datetime.datetime.strptime(ConfigGetter["START_DATE"], time_string_format)
    #     start_hour = abs(start_date - simulation_initial_time).total_seconds() // 3600
    #     end_hour = abs(end_date - simulation_initial_time).total_seconds() // 3600
    #     return start_hour, end_hour

    def get_emission_rate_by_range_of_date(self, start_date: datetime.datetime,
                                           end_date: datetime.datetime):
        """
        return the emission rate in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        logging.info("df objects [emission rate] - converts the csv to hourly buying prices in the given dates")
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)].to_numpy()

        return [hour[-1] for hour in period]  # removes dates


class PeriodsSimulation(ABC):
    """
    This class wraps a period db
    """

    # todo: doc

    @abstractmethod
    def get_new_batteries(self):
        """
        return the new batteries in given range of date (including start_date excluding end_date)
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_all_batteries(self):
        """
        return the total batteries in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_new_solar_panels(self):
        """
        return the total batteries in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_all_solar_panels(self):
        """
        return the total batteries in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_electricity_buying(self):
        """
        return the total batteries in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass

    @abstractmethod
    def get_electricity_sells(self):
        """
        return the total batteries in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the solar radiation at that date range by hour
        """
        pass


class HourlySimulationDataOfPeriod(PeriodsSimulation):
    # TODO: test if it works
    """
    This class implements ElectricityPrices for month radiation data
    """

    def __init__(self, period_index: int):
        titles = ["Date", "Batteries", "Solar", "Buying", "Selling", "Lost", "Storaged", "NewBatteries", "AllBatteries",
                  "NewSolarPanels", "AllSolarPanels"]
        self.df = pd.read_csv(f"simulation output/period{period_index}.csv", header=[0])
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)
        #print("hello")

    # todo: consider change it to numpy arrays
    def get_new_batteries(self):
        return [item for item in self.df["NewBatteries"].to_numpy()]

    def get_all_batteries(self):
        return [item for item in self.df["AllBatteries"].to_numpy()]

    def get_new_solar_panels(self):
        return [item for item in self.df["NewSolarPanels"].to_numpy()]

    def get_all_solar_panels(self):
        return [item for item in self.df["AllSolarPanels"].to_numpy()]

    def get_electricity_buying(self):
        return [item for item in self.df["Buying"].to_numpy()]

    def get_electricity_sells(self):
        return [item for item in self.df["Selling"].to_numpy()]

    def get_start_date(self):
        return self.df["Date"][0].to_pydatetime()

    def get_end_date(self):
        return self.df["Date"].iloc[-1].to_pydatetime()
