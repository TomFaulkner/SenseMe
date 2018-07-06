"""Basic Flask module example.

To use this example do the following:

- install senseme
- install flask
- copy the examples/flask_app.py and templates directory somewhere, or clone
the repo
- python3 SenseMe/examples/flask_app.py
- In a browser go to http://localhost:5000

This is intended as an example, it is not feature complete.
I would gladly take contributions to extend this from an example to a proper
interface. My preference, however, would probably be a hug interface.
"""
import flask

from senseme import discover


fan = discover()[0]

app = flask.Flask(__name__)
app.secret_key = "12839-hidf;safng1jjdsgaklgxzcvzxdsfa125asklvnke1pht32532r"


@app.route("/")
def index():
    # return flask.send_from_directory('./static/', 'index.html')
    flask.flash(str((fan.speed, fan.brightness)))
    return flask.render_template("index.html")


# Light Functions
@app.route("/light/toggle")
def toggle_light():
    fan.light_toggle()
    flask.flash("Toggling Light")
    return flask.redirect(flask.url_for("index"))


@app.route("/light/off")
def light_off():
    fan.light_powered_on = False
    flask.flash("Turning Light Off")
    return flask.redirect(flask.url_for("index"))


@app.route("/light/on")
def light_on():
    fan.light_powered_on = True
    flask.flash("Turning light On")
    return flask.redirect(flask.url_for("index"))


@app.route("/light/<int:level>")
def light_level(level):
    fan.brightness = int(level)
    flask.flash("Set light level to {}".format(level))
    return flask.redirect(flask.url_for("index"))


@app.route("/light/increase")
def inc_light():
    fan.inc_brightness()
    flask.flash("Increased Light Level")
    return flask.redirect(flask.url_for("index"))


@app.route("/light/decrease")
def dec_light():
    fan.dec_brightness()
    flask.flash("Decreased Light Level")
    return flask.redirect(flask.url_for("index"))


# Fan Functions
@app.route("/fan/increase")
def inc_speed():
    fan.inc_speed()
    flask.flash("Increased Fan Speed")
    return flask.redirect(flask.url_for("index"))


@app.route("/fan/decrease")
def dec_speed():
    fan.dec_speed()
    flask.flash("Decreased Fan Speed")
    return flask.redirect(flask.url_for("index"))


@app.route("/fan/<int:speed>")
def set_speed(speed):
    fan.speed = int(speed)
    flask.flash("Set fan speed to {}".format(speed))
    return flask.redirect(flask.url_for("index"))


@app.route("/fan/toggle")
def fan_toggle():
    fan.fan_toggle()
    flask.flash("Toggling Fan")
    return flask.redirect(flask.url_for("index"))


@app.route("/fan/off")
def fan_off():
    fan.fan_powered_on = False
    flask.flash("Turning Fan Off")
    return flask.redirect(flask.url_for("index"))


@app.route("/fan/on")
def fan_on():
    fan.fan_powered_on = True
    flask.flash("Turning Fan On")
    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run()
