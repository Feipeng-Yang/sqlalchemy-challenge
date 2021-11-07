import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#------------------------------------------------
# Database Setup
#------------------------------------------------
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)



# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


# join the tables 
# sel = [Station.station, EA.genus, EA.species, NA.family, NA.genus, NA.species]
# jointed = session.query(*sel).filter(Station.station == Measurement.sporder).limit(10).all()

#------------------------------------------------
# Flask Setup
#------------------------------------------------
app = Flask(__name__)
#------------------------------------------------
# Flask Routes
#------------------------------------------------

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all precipitations
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Convert list of tuples into dictionary
    all_precipation = dict(results)
    return jsonify(all_precipation)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all station
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["id"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all measurement
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_year = dt.date.fromisoformat(most_recent_date[0]).strftime("%Y")
    most_recent_month = dt.date.fromisoformat(most_recent_date[0]).strftime("%m")
    most_recent_day = dt.date.fromisoformat(most_recent_date[0]).strftime("%d")
    # Calculate the date one year from the last date in data set.
    previous_year = int(most_recent_year)-1
    previous_year_date = dt.date(previous_year, int(most_recent_month), int(most_recent_day))
    most_active  = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()[0][0]

    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= previous_year_date, Measurement.station == most_active).\
        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_measurement = []
    for station, date, tobs in results:
        measurement_dict = {}
        measurement_dict["station"] = station
        measurement_dict["date"] = date
        measurement_dict["tobs"] = tobs
        all_measurement.append(measurement_dict)
    return jsonify(all_measurement)

@app.route("/api/v1.0/<start>")
def calcualte_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    lowest = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    highest = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    average = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    # find the max, min and avg temp greater than the start date
    results = f"For date later than {start}, the loweste temperature is {lowest}\
                the highest temperature is {highest}, and the average temperature is {average}."

    return results

@app.route("/api/v1.0/<start>/<end>")
def calcualte_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    lowest = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    highest = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    average = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    session.close()

    # find the max, min and avg temp greater than the start date
    results = f"For date between {start} and {end}, the loweste temperature is {lowest}\
                the highest temperature is {highest}, and the average temperature is {average}."

    return results

if __name__ == '__main__':
    app.run(debug=True)
