import time
import requests
import os
import json
from math import cos, asin, sqrt, pi


SUBSCRIBERS_DATA_DIR_PATH = "Subscribers"

CONFIRMED_CASES_SERVER_URL = "http://localhost:3030/disease-data-source/covid19/cases/confirmed"

NOTIFICATION_FILE_PATH = "Notifications/notifications.json"




def update_country_with_subscriber(country_subscribers, date, email, subscriber_route):
    """
    updating subscriber route in suitable place in his country's data.
    :param country_subscribers: dict of subscribers from certain country
    :param date:  date of the subscriber's route
    :param email: email of subscriber
    :param subscriber_route: subscriber
    :return:
    """

    if date in country_subscribers:
        if email in country_subscribers[date]:
            country_subscribers[date][email].append(subscriber_route)
        else:
            country_subscribers[date][email] = [subscriber_route]
    else:
        country_subscribers[date] = {email: [subscriber_route]}


def add_new_subscriber(subscriber_route):
    """
        Adds a new subcriber to subscriber data (will be added to it's
        country's file, if one exists, otherwise will be created)
        :param subscriber_route: subscriber data
        :return: None
        """
    country = subscriber_route["country"]
    date = subscriber_route["dateOfRoute"]
    email = subscriber_route["email"]
    country_filepath = f"{SUBSCRIBERS_DATA_DIR_PATH}/{country}.json"

    if not os.path.exists(country_filepath):
        user_pair = {email: [subscriber_route]}
        with open(country_filepath, "w") as f:
            json.dump({date:user_pair}, f)
    else:
        with open(country_filepath, "r") as f:
            data = json.load(f)
        update_country_with_subscriber(data, date, email, subscriber_route)
        with open(country_filepath,"w") as f:
            json.dump(data,f)


class Notificator:

    def __init__(self, notifications_path=NOTIFICATION_FILE_PATH):
        self.notifications_path = notifications_path
        self.notification_data = None

        if not os.path.exists(self.notifications_path):
            with open(self.notifications_path, "w") as notification_file:
                json.dump(list(), notification_file)

    def notify(self, subscriber_route, interaction_point):
        """
        Notifying subscriber (adding line to notification.json)that was found
        to be potentially infected.
        :param subscriber_route: subscriber problematic route
        :param interaction_point: infection interaction point
        :return:
        """
        new_line = {"notify": subscriber_route["email"],
                    "date": subscriber_route["dateOfRoute"],
                   "interactionPoint": interaction_point}
        self.notification_data.append(new_line)


    def get_distance_between_points(self, lat1, lon1,lat2, lon2):
        """
        Calculates ditance between two GCS points (lat1,lon1), (lat2,lon2).
        :param lat1: latitude of first point
        :param lon1: longitude of first point
        :param lat2: latitude of second point
        :param lon2: longitude of first point
        :return: distance between points
        """
        p = pi / 180
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(
            lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a))


    def check_subscriber(self, subscriber_routes, point):
        """
        Checking subscriber's infection against given point in confirmed
        person's route.
        :param subscriber_routes: routes made by subscriber on the
        problematic date.
        :param point: point in confiremd person's route.
        :return:
        """
        for route in subscriber_routes:
            for s_point in route["route"]:
                distance = self.get_distance_between_points(s_point["lat"],s_point["lon"], point["lat"],point["lon"])
                if distance <= 2:
                    self.notify(route,s_point)
                    return

    def check_country_for_infections(self, country_subscribers_path, date, confirmed_route):
        """
        Checking if subscribers from country were infected by confirmed case.
        :param country_subscribers_path: pathe to country's subscribers file
        :param date: date of confirmed person's route
        :param confirmed_route: confirmed person's route
        :return: None
        """
        with open(country_subscribers_path, "r") as f:
            country_data = json.load(f)

        if date in country_data:
            for point in confirmed_route["route"]:
                for subscriber in country_data[date]:
                    subscriber_routes = country_data[date][subscriber]
                    self.check_subscriber(subscriber_routes, point)


    def check_confirmed_route(self, route):
        """
        checking route of a confirmed case for subscribers infection.
        :param route: confiremd case route
        :return: None
        """
        country = route["country"]
        date = route["date"]
        subscribers_from_country_path = f"{SUBSCRIBERS_DATA_DIR_PATH}/{country}.json"
        if os.path.exists(subscribers_from_country_path):
            self.check_country_for_infections(subscribers_from_country_path, date,route)



    def fetch_and_check_infection(self):
        """
        Requsting server, and checking for infection accordingly.
        :return:
        """
        # bringing notification data
        with open(self.notifications_path, "r") as notification_file:
            self.notification_data = json.load(notification_file)

        response = requests.get(CONFIRMED_CASES_SERVER_URL).json()

        for route in response:
            self.check_confirmed_route(route)

        # writing all new notifications in once
        with open(self.notifications_path, "w") as notification_file:
            json.dump(self.notification_data, notification_file)


    def check_infection_from_given_data(self, data):
        """
        checking subcribers against a given data, not from server (used for
        testing purposes in notificator_test.py)
        :param data:
        :return:
        """
        with open(self.notifications_path, "r") as notification_file:
            self.notification_data = json.load(notification_file)

        for route in data:
            self.check_confirmed_route(route)
        with open(self.notifications_path, "w") as notification_file:
            json.dump(self.notification_data, notification_file)


def poll_and_notify():
    """
    This function runs consistently, polling server and notifies infected
    subscribers.
    :return: None
    """
    n = Notificator()

    while True:
        start_time = time.time()
        n.fetch_and_check_infection()
        time.sleep(120 - ((time.time()- start_time)%120))
        # sleep 120 seconds total (including execution of command before)
