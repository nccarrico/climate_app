import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        "Welcome to the Climate App homepage!<br>"
        "Here are the available routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/(start date: yyyy-mm-dd)<br>"
        "/api/v1.0/(start date: yyyy-mm-dd)/(end date: yyyy-mm-dd)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitaion' page...")
    session = Session(engine)

    last_day = session.query( \
                    func.max(Measurement.date) \
                    ).scalar()

    last_day_dt = dt.strptime(last_day, '%Y-%m-%d')

    twelve_m_ago = dt.date(last_day_dt) - timedelta(days=365)

    year_prcp = session.query(Measurement.date, Measurement.prcp)\
                    .filter(Measurement.date >= twelve_m_ago)\
                    .all()

    all_prcp = []
    for date, prcp in year_prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    session = Session(engine)

    stations = session.query(Station.station).all()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Tobs' page...")
    session = Session(engine)

    last_day = session.query( \
                    func.max(Measurement.date) \
                    ).scalar()

    last_day_dt = dt.strptime(last_day, '%Y-%m-%d')
    
    twelve_m_ago = dt.date(last_day_dt) - timedelta(days=365)
    
    tobs = session.query(Measurement.tobs) \
                .filter(Measurement.date >= twelve_m_ago) \
                .all()

    return jsonify(tobs)

@app.route("/api/v1.0/<start>", defaults={"end": None})
@app.route("/api/v1.0/<start>/<end>")
def temps(start, end):
    print("Server received request for 'Temps(start and end)' page...")
    session = Session(engine)
    if end is None:
        temps = session.query(
                        func.min(Measurement.tobs), \
                        func.avg(Measurement.tobs), \
                        func.max(Measurement.tobs)
                        ) \
                    .filter(Measurement.date >= start) \
                    .all() 
        return jsonify(temps)
    else:
        temps = session.query(
                            func.min(Measurement.tobs), \
                            func.avg(Measurement.tobs), \
                            func.max(Measurement.tobs)
                            ) \
                        .filter(Measurement.date >= start) \
                        .filter(Measurement.date <= end) \
                        .all()
        return jsonify(temps)
    
if __name__ == "__main__":
    app.run(debug=True)
