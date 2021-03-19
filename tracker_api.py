import flask
import multiprocessing
from flask import jsonify
from risk_analyzer import get_trip_risk
from notificator import add_new_subscriber, poll_and_notify

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Epidemic Tracker</h1><p>This site is an Epidemic Tracker </p>"


@app.route('/epidemic-tracker/hello/<message>', methods=['GET'])
def api_hello(message):
    return "<h1>hello from epidemic tracker, message: " + message + "</h1>"


@app.route('/epidemic-tracker/covid19/infectionRisk', methods=['PUT'])
def api_infectionRisk():
    body = flask.request.json
    visits = tuple(tuple(visit.values()) for visit in body["visited"])
    return jsonify({"estimatedRisk":get_trip_risk(visits)})

@app.route('/epidemic-tracker/covid19/subscribe/route', methods=['PUT'])
def api_subscribe():
    add_new_subscriber(flask.request.json)
    return ""    # Should returned string be explicitly '200 OK'?


def start_api_server():
    """
    Activating our server
    :return:
    """
    app.run(debug=True, use_reloader=False)


def main():
    p1 = multiprocessing.Process(name="p1", target=poll_and_notify)
    p2 = multiprocessing.Process(name="p2", target=start_api_server)
    p1.start()
    p2.start()


if __name__ == '__main__':
    main()
