# Import Dependenices 
from flask import Flask, jsonify
import numpy as np
import sqlalchemy 
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd

#Create engine
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# # Create our session (link) from Python to the DB
# session = Session(engine)

# Create an app
app = Flask(__name__)

# home page
@app.route("/")
def home():
    return("/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/2017-01-01<br/>")

@app.route("/api/v1.0/precipitation")
def precipitation ():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    initialdate = dt.date(2017,8,23)-dt.timedelta(days=365)
    measurement_df = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=initialdate).order_by(Measurement.date).all()
    df = pd.DataFrame(measurement_df, columns = ["date", "precipitation"])
    session.close()


    return {row["date"]: row["precipitation"] for _, row in df.iterrows()}

@app.route("/api/v1.0/stations")
def stations():
    
    #return a list of stations
    session = Session(engine)
    results = session.query(Station.station).all()

    session.close()

    #Get results into a ID array and convert them into a list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temperature():
    #return the temperature (tobs) for previous years.
     session = Session(engine)
     initialdate = dt.date(2017,8,23)-dt.timedelta(days=365)
     results2 = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()
     session.close()

     temperature = list(np.ravel(results2))

     return jsonify(temperature)


@app.route("/api/v1.0/<start>")
def start(start, end=""):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    session = Session(engine)
    # Perform a query to calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.else:
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                            .filter(Measurement.date >= start).all()
    # Create a dictionary from the row data and append to a list of all_stations
    all_temps = []
    for temperature in results:
        temperature_dict = {}
        temperature_dict["TEMPMIN"] = temperature[0]
        temperature_dict["TEMPAVG"] = temperature[1]
        temperature_dict["TEMPMAX"] = temperature[2]
        all_temps.append(temperature_dict)

    return jsonify(all_temps)


@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                            .filter(Measurement.date >= start)\
                            .filter(Measurement.date <= end).all()

    all_temps = []
    for temperature in results:
        temperature_dict = {}
        temperature_dict["TEMPMIN"] = temperature[0]
        temperature_dict["TEMPAVG"] = temperature[1]
        temperature_dict["TEMPMAX"] = temperature[2]
        all_temps.append(temperature_dict)

    return jsonify(all_temps)



if __name__ == '__main__':
    app.run(debug=True)



