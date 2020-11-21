# add dependencies
import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np


from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.ext.automap import automap_base

from sqlalchemy import Column, Integer, String, Float, and_, Date, desc, func

from flask import Flask, jsonify

# Database Setup    
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Create our session (link) from Python to the DB
session = Session(engine)

# Save references 
Station = Base.classes.station
Measurement = Base.classes.measurement

# Flask Setup

app = Flask(__name__)

@app.route("/")
def welcome():

     return (
         f"Available Routes:<br/>"
         f"/api/v1.0/precipitation"
         f"- Dates and temperature observations from the last year<br/>"

         f"/api/v1.0/stations"
         f"- List of stations<br/>"

         f"/api/v1.0/tobs"
         f"- Temperature Observations from the past year<br/>"

         f"/api/v1.0/<start>"
         f"- Minimum temperature, the average temperature, and the max temperature for a given start day<br/>"

         f"/api/v1.0/<start>/<end>"
         f"- Minimum temperature, the average temperature, and the max temperature for a given start-end range<br/>"
     )

@app.route("/api/v1.0/precipitation")
def pcrp():
    # create the date range, use today as the api here does not take a start/end date
    latestdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestdate = list(np.ravel(latestdate))[0]
    latestdate = dt.datetime.strptime(latestdate, '%Y-%m-%d')
    latestYear = int(dt.datetime.strftime(latestdate, '%Y'))
    latestMonth = int(dt.datetime.strftime(latestdate, '%m'))
    latestDay = int(dt.datetime.strftime(latestdate, '%d')) 
    yearbefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)
    yearbefore
    raindata = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date >= yearbefore)
                  .order_by(Measurement.date.asc())
                  .all())

    return jsonify(raindata)

@app.route("/api/v1.0/stations")
def station_list():
    station_counts = session.query(Station.station).all()

    all_stations= list(np.ravel(station_counts))
    

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temp_year():
    high_temps_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    high_temps_station
    high_temps_station= high_temps_station[0]
    high_temps_station

    active_stations_temps = session.query(Measurement.tobs).\
                        filter(Measurement.date>= "2016-08-23").\
                        filter(Measurement.station == "USC00519281").all()

    return jsonify(active_stations_temps)

@app.route("/api/v1.0/<start>")
def start_temp(start="2016-08-23"):

     
    temp_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
   
    temp_stats = []
    
    for Tmin, Tmax, Tavg in temp_data:
        temp_stats_dict = {}
        temp_stats_dict["Minimum Temp"] = Tmin
        temp_stats_dict["Maximum Temp"] = Tmax
        temp_stats_dict["Average Temp"] = Tavg
        temp_stats.append(temp_stats_dict)
    
    return jsonify(temp_stats)
      
    

@app.route("/api/v1.0/<start>/<end>")
def range_temp(start= "2016-08-23", end= "2017-08-23"):

    session = Session(engine)  

    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start, Measurement.date <= end).all() 
    
    session.close()

    return jsonify(temp_data)          



if __name__ == "__main__":
    app.run(debug=True)

