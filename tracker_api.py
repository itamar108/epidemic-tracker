import flask
import requests

from risk_analyzer import get_trip_risk
from risk_analyzer import get_visit_risk

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Epidemic Tracker</h1><p>This site is an Epidemic Tracker </p>"


@app.route('/epidemic-tracker/hello/<message>', methods=['GET'])
def api_hello(message):
    return "<h1>hello from epidemic tracker, message: " + message + "</h1>"


@app.route('/epidemic_tracker/covid19/infectionRisk', methods=['PUT'])
def api_infectionRisk():
    body = flask.request.json
    visits = tuple(tuple(visit.values()) for visit in body["visited"])
    # risk = get_trip_risk(visits)
    risk = "hello"
    print(get_visit_risk(visits[1]))
    return f"{risk}%"

if __name__ == '__main__':
    app.run()
