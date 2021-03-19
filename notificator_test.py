from notificator import Notificator, add_new_subscriber
import filecmp

TEST_OUTFILE_PATH = "Tests/task5_test_output.json"
CORRECT_OUTFILE_PATH = "Tests/task5_test_CorrectOutput.json"
APP_URL = "http://127.0.0.1:5000/"

CONFIRMED_ROUTE = [{"route": [{"lat": 23.54545, "lon": 24.44234},],
                         "date": "2021-01-14", "country": "TY"},

                   {"route": [{"lat": 21.12345, "lon": 24.10001}],
                    "date": "2021-01-14", "country": "TY"},

                    {"route": [{"lat": 21.00000, "lon": 24.10000}],
                    "date": "2021-01-14", "country": "TY"}
                   ]


SUBSCRIBE_ROUTE = {"route": [{"lat": 23.54545, "lon": 24.44232},
                             {"lat": 21.12345, "lon": 24.10002}],
                        "dateOfRoute": "2021-01-14",
                        "country": "TY",
                        "email": "subscriber1@notexist.com"}



def add_and_track_infections():
    """Make sure no TY.json nor outfile exists"""
    add_new_subscriber(SUBSCRIBE_ROUTE)
    n = Notificator(TEST_OUTFILE_PATH)
    n.check_infection_from_given_data(CONFIRMED_ROUTE)
    assert(filecmp.cmp(TEST_OUTFILE_PATH, CORRECT_OUTFILE_PATH))



if __name__ == '__main__':
    add_and_track_infections()






