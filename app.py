# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

measurement = Base.classes.measurement
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/yyyy-mm-dd<br/>"
        f"/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation and date"""
    
    #Query all precipitation and date
    
    results = session.query(measurement.date, measurement.prcp).all()
    
    session.close()
    
    #Convert list of tuples into normal list
    
    all_precipitation = []
    for date, prcp in results:
        precipitation_dictionary = {}
        precipitation_dictionary[date] = prcp
        all_precipitation.append(precipitation_dictionary)
       
    
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    #Create our session (link) from Python to the DB
    
    session = Session(engine)
    
    """Return a list of all stations"""
    
    #Query all stations


    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    #Create a dictionary from the row data and append to a list 
    
    allstation = []
    for station, name,latitude,longitude,elevation in results:
        station_dictionary = {}
        station_dictionary['station'] = station
        station_dictionary['name'] = name
        station_dictionary['latitude'] = latitude
        station_dictionary['longitude'] = longitude
        station_dictionary['elevation'] = elevation
        allstation.append(station_dictionary)

        
    return jsonify(allstation)

@app.route("/api/v1.0/tobs")
def temperatureobserve():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of all temparture observation in the last year"""
    
    #Query all temperature observations
    
    recent_date = session.query(measurement.date).\
            order_by(measurement.date.desc()).first()
    
    #last twelve months data

    last_twelve = (dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365))

    top_station_twelve = session.query(measurement.date,measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date > last_twelve).all()

    temps = list(np.ravel(top_station_twelve))

    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
   
    if not end:
        results = session.query(*sel).\
            filter(measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

  
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
    
    

   
if __name__ == '__main__':
    app.run(debug=True)

        
