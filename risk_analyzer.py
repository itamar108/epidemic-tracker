
import os.path
from datetime import date, timedelta
import requests
import json

COUNTRY_STATS_URL = "https://api.covid19api.com/country/"



class CasesCache:
    def __init__(self, dirname):
        self.dirname = dirname

    def get_country_cases(self, country, start, end):
        file_path = self.dirname + country + ".json"
        if os.path.isfile(file_path):
            found_in_cache = self.lookup_period_in_cache(start,end, file_path)
            if found_in_cache:
                return found_in_cache

        self.fetch_cases_from_server(country, start, end)
        return self.lookup_period_in_cache(start,end,file_path)

    def lookup_period_in_cache(self, start, end, file_path):
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

    def fetch_cases_from_server(self, country, start, end):
        cases_per_period = dict()
        response = requests.get(COUNTRY_STATS_URL + country, params={
            'from': (start - timedelta(1)).isoformat(),
            'to': end.isoformat()}).json()
        mainland_cases = [x for x in response if x['Province'] == ""]
        for i in range(1, len(mainland_cases)):
            new_key = mainland_cases[i]["Date"][:10]
            new_value = (
            mainland_cases[i]["Active"], mainland_cases[i - 1]["Active"],
            mainland_cases[i]["Confirmed"])
            cases_per_period[new_key] = new_value
        self.persist(country, cases_per_period)

    def persist(self, country, cases):
        """save the cache state.
        """
        file_path = f"{self.dirname}{country}.json"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump(cases, f)
                return

        with open(file_path, "r") as f:
            data = json.load(f)

        new_data = {**cases, **data}
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
    period_cases = cases.get_country_cases(country, start, end)
    for daily_record in period_cases:
        today, yesterday, confirmed = daily_record
        r += estimated_risk_per_day(today, yesterday, confirmed)
    return r


def get_visit_risk(visit):
    country = visit[0].lower()
    arrival = date.fromisoformat(visit[1])
    left_date = arrival + timedelta(visit[2])
    return get_country_risk(country, arrival, left_date)


def get_trip_risk(visits):
    trip_risk = 0
    for visit in visits:
        trip_risk+=get_visit_risk(visit)
    return trip_risk

