import flask
import threading
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
    app.run(host= "0.0.0.0", port=5001, debug=True, use_reloader=False)


def main():
    p1 = threading.Thread(target=poll_and_notify)
    p2 = threading.Thread(target=start_api_server)
    p1.start()
    p2.start()



if __name__ == '__main__':
    main()
