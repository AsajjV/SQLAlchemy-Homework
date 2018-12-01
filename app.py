# 1. import flask
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# Create our session (link) from Python to the DB
session = Session(engine)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#find last date in table
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
print(last_date)

previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365) 

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

@app.route('/')
def welcome():
    return(
        f"Welcome to the Hawaii Trip Planner API!<br/>"
        f"Available routes:<br/>"
        f"Precipitation data: /api/v1.0/precipitation<br/>"
        f"Weather stations: /api/v1.0/stations<br/>"
        f"Last year dates and temperature observations (tobs): /api/v1.0/tobs<br/>"
        f"Minimum, average, and maximum temperature for given start date:  /api/v1.0/<start><br/>"
        f"Minimum, average, and maximum temperature for a given start and end date: /api/v1.0/<start>/<end><br/> "
    )

@app.route('/api/v1.0/precipitation')
#  * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#  * Return the JSON representation of your dictionary.
def precipitation():

    weather_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()

    #convert to dictionary
    prcp_result = {date: prcp for date, prcp in weather_results}
    return jsonify(prcp_result)


@app.route('/api/v1.0/stations')
#  * Return a JSON list of stations from the dataset.
def station_list():
    stations = session.query(Station.name).all()

    #convert to list
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
#  * query for the dates and temperature observations from a year from the last data point.
#  * Return a JSON list of Temperature Observations (tobs) for the previous year.
def temp_obs():
    temp_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= previous_year).all()

    temp_result = {date: tobs for date, tobs in temp_results}
    return jsonify(temp_result)


#  * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range (2 app routes)
@app.route('/api/v1.0/<start>')
#  * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
def w_start(start):

    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    start_date_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
                        func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    # Convert to list
    start_result = list(np.ravel(start_date_results))
    return jsonify(start_result)

@app.route('/api/v1.0/<start>/<end>')
#  * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
def w_start_end(start,end):

    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
                        func.max(Measurement.tobs)).filter(Measurement.date >= start).filter\
                        (Measurement.date <= end).all()
    
    # Convert to list
    start_end_result = list(np.ravel(start_end_results))
    return jsonify(start_end_result)

if __name__ == "__main__":
    app.run(debug=True)