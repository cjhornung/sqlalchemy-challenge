# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation :Returns the JSON representation of your precipitation dictionary<br/>"
        f"/api/v1.0/stations :Returns a JSON list of stations from the dataset.<br/>"
        f"/api/v1.0/tobs :Returns a JSON list of temperature observations for the previous year<br/>"
        f"/api/v1.0/[start] :Returns a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start (format: [yyyy-mm-dd]). <br/>"
        f"/api/v1.0/[start]/[end]    :Returns a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range (format: [yyyy-mm-dd]). <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns the JSON representation of your precipitation dictionary"""
    # Converts the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    #Get most recent date
    last_row = session.query(Measurement).order_by(Measurement.date.desc()).first()
    most_recent_date= dt.datetime.strptime(last_row.__dict__['date'],'%Y-%m-%d')
    end_date=dt.date(most_recent_date.year -1, most_recent_date.month, most_recent_date.day)
    #get filtered data for everything more recent than end date
    data = [Measurement.date,Measurement.prcp]
    filtered_data = session.query(*data).filter(Measurement.date >= end_date).all()
    #populate dictionary for json
    filtered_data_dict=[]
    for data in filtered_data:
        data_dict = {}
        data_dict[data[0]] = data[1]
        filtered_data_dict.append(data_dict)
    return jsonify(filtered_data_dict)
    session.close()

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns a JSON list of stations from the dataset"""    
    stations=session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation)
    #populate dictionary for json
    json_stations_dict=[]
    for station, name, lat,lon,elevation in stations:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = elevation
        json_stations_dict.append(station_dict)
    return jsonify(json_stations_dict)
    session.close()
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns a JSON list of temperature observations for the previous year"""   
    #Get most recent date
    last_row = session.query(Measurement).order_by(Measurement.date.desc()).first()
    most_recent_date= dt.datetime.strptime(last_row.__dict__['date'],'%Y-%m-%d')
    end_date=dt.date(most_recent_date.year -1, most_recent_date.month, most_recent_date.day)
    #Get most active station by data count
    count_by_stations=session.query(Measurement.station.distinct(), func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station=count_by_stations[0][0]
    #populate dictionary for json
    data = [Measurement.date,Measurement.tobs]
    filtered_data = session.query(*data).filter(Measurement.date >= end_date,Measurement.station == most_active_station).all()
    filtered_data_dict=[]
    for data in filtered_data:
        data_dict = {}
        data_dict[data[0]] = data[1]
        filtered_data_dict.append(data_dict)
    return jsonify(filtered_data_dict)
    session.close()
    
@app.route("/api/v1.0/<start>")
def startjson(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Returns a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start (format: [yyyy-mm-dd])"""
    start_date= dt.datetime.strptime(start,'%Y-%m-%d')
    results=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    data_dict = {}
    data_dict["min"] = results[0][0]
    data_dict["max"] = results[0][1]
    data_dict["avg"] = results[0][2]
    return jsonify(data_dict)
    session.close()
    
@app.route("/api/v1.0/<start>/<end>")
def startendjson(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Returns a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range (format: [yyyy-mm-dd])"""
    start_date= dt.datetime.strptime(start,'%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    results=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date,Measurement.date <= end_date).all()
    data_dict = {}
    data_dict["min"] = results[0][0]
    data_dict["max"] = results[0][1]
    data_dict["avg"] = results[0][2]
    return jsonify(data_dict)
    session.close()    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)
