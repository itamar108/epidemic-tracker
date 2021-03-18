
import time
import requests
import os
import math
import json

SUBSCRIBERS_DIR = '/Users/itamar/Desktop/epidemic-tracker/Subscribers'

CONFIRMED_CASES_SERVER_URL = "http://localhost:3030/disease-data-source/covid19/cases/confirmed"

NOTIFICATION_FILE_PATH = "Notifications/notifications.json"


class Notificator:
    def __init__(self, notifications_path=NOTIFICATION_FILE_PATH):
        self.notifications_path = notifications_path
        self.notification_data = None


    def notify(self, subscriber,interaction_point):
        new_line = {"notify": subscriber["email"],
                    "date": subscriber["date"],
                   "interactionPoint": interaction_point}
        self.notification_data.append(new_line)



    def check_subscriber(self, subscriber, point):
        for s_point in subscriber["route"]:
            distance = math.dist((s_point["lat"],s_point["long"]), (point["lat"],point["long"]))
            if distance <= 2:
                self.notify(subscriber,s_point)
                return
            else:
                print("-")

    def check_country_for_infections(self, country_subscribers_path, date, route):
        with open(country_subscribers_path, "r") as f:
            country_data = json.load(f)
        print(country_data)
        if date in country_data:
            for point in route["route"]:
                for subscriber in country_data[date]:
                    self.check_subscriber(subscriber, point)


    def check_route(self, route):
        country = route["country"]
        date = route["date"]
        subscribers_from_country_path = f"{SUBSCRIBERS_DIR}/{country}.json"
        if os.path.exists(subscribers_from_country_path):
            self.check_country_for_infections(subscribers_from_country_path, date,route)



    def check_infection(self):
        # opening notification data
        with open(self.notifications_path, "r") as notification_file:
            self.notification_data = json.load(notification_file)

        response = requests.get(CONFIRMED_CASES_SERVER_URL).json()
        for route in response:
            self.check_route(route)

        # writing all in once all the new notifications
        with open(self.notifications_path, "w") as notification_file:
            json.dump(self.notification_data, notification_file)


    def poll_and_notify(self):
        subscribers = dict()
        while True:
            start_time = time.time()
            self.check_infection()
            time.sleep(30 - ((time.time()- start_time)%30)) # making sure we
            # sleep 120 seconds total (exluding execution time of commands before


if __name__ == '__main__':
    n = Notificator()
    n.poll_and_notify()