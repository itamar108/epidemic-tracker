
import os.path
from datetime import date, timedelta
import requests
import json


JSON_DATE_END_IDX = 10 # index of last date char in a json date&time string

COUNTRY_STATS_URL = "https://api.covid19api.com/country/"



class CasesCache:
    """Class representing our cache for countries infection data per date,
    as needed in task 3. Will be buily by a folder ('countriesData') that
    will contain a .json file for each country (where each key is a date,
    and values of the form (days_active_amount, day_before_active_amount,
    days_confirmed_amount)"""

    def __init__(self, dirname):
        self.dirname = dirname

    def get_country_stats(self, country, start, end):
        """
        Gets all country stats per period [start, end]
        :param country: country name
        :param start: start date
        :param end: end date
        :return: list of stats per period from cache
        """
        file_path = self.dirname + country + ".json"
        if os.path.isfile(file_path):
            found_in_cache = self.lookup_period_in_cache(start,end, file_path)
            if found_in_cache:
                return found_in_cache

        self.fetch_stats_from_server(country, start, end)
        return self.lookup_period_in_cache(start,end,file_path)

    def lookup_period_in_cache(self, start, end, file_path):
        """
        Searches for period [start,end] stats in country cache.
        :param start: start date
        :param end: end date
        :param file_path: path to specific country cache file
        :return: period stats if found in cache, otherwise None
        """
        period_cases = []
        with open(file_path, "r") as f:
            country_stats = json.load(f)
            cur = start
            while cur <= end and cur.isoformat() in country_stats:
                period_cases.append(country_stats[cur.isoformat()])
                cur = cur + timedelta(1)

        if len(period_cases) - 1 == (end - start).days:
            return period_cases
        return None

    def fetch_stats_from_server(self, country, start, end):
        """
        Gets cases to cache by GET-requesting covid19 server.
        :param country: country name
        :param start: start date
        :param end: end date
        :return: None
        """
        stats_per_period = dict()
        response = requests.get(COUNTRY_STATS_URL + country, params={
            'from': (start - timedelta(1)).isoformat(),
            'to': end.isoformat()}).json()
        mainland_stats = [x for x in response if x['Province'] == ""]
        for i in range(1, len(mainland_stats)):
            new_key = mainland_stats[i]["Date"][:JSON_DATE_END_IDX]
            new_value = (
            mainland_stats[i]["Active"], mainland_stats[i - 1]["Active"],
            mainland_stats[i]["Confirmed"])
            stats_per_period[new_key] = new_value
        self.persist(country, stats_per_period)

    def persist(self, country, stats):
        """
        Writes stats to country's cache
        :param country: countryname
        :param stats: stats to write
        :return: None
        """
        file_path = f"{self.dirname}{country}.json"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump(stats, f)
                return

        with open(file_path, "r") as f:
            data = json.load(f)

        new_data = {**stats, **data}
        with open(file_path, "w") as f:
            json.dump(new_data, f)


cases = CasesCache("CountriesData/")



def estimated_risk_per_day(active_cases, active_cases_yesterday,
                           confirmed_cases):
    """
    Computing estimated risk per given day.

    :param active_cases: number of cases that day
    :param active_cases_yesterday: number of cases day before
    :param confirmed_cases: confirmed cases that day
    :return:  estimated risk (percentage)
    """

    day_new_cases = active_cases - active_cases_yesterday
    sick_population_ratio = (active_cases / confirmed_cases) * 100
    estimated = ((day_new_cases / active_cases) * 100) * sick_population_ratio * 0.5

    return estimated


def get_country_risk(country, start, end):
    """
    return country's summation of risks per priod
    :param country: country name
    :param start: start date (datetime obj)
    :param end: end date (datetime obj)
    :return: country risk per period
    """
    r = 0
    period_stats = cases.get_country_stats(country, start, end)
    for daily_record in period_stats:
        today, yesterday, confirmed = daily_record
        r += estimated_risk_per_day(today, yesterday, confirmed)
    return r


def get_visit_risk(visit):
    """
    Returns risk per visit.
    :param visit: tuple describing visit
    :return: visit's risk
    """
    print(visit)
    country = visit[0].lower()
    arrival = date.fromisoformat(visit[1])
    left_date = arrival + timedelta(visit[2])
    return get_country_risk(country, arrival, left_date)


def get_trip_risk(visits):
    """
    Returns risk per trip.
    :param visits: tuple of visit tuples
    :return: trip's risk
    """
    trip_risk = 0
    for visit in visits:
        trip_risk+=get_visit_risk(visit)
    return trip_risk


