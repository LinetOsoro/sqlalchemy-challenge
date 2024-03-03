# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

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
# Define home route
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )


# Define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
    # Calculate the date 12 months ago from the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert results to dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_dict)


# Define stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.station).all()
    
    # Convert results to list
    station_list = [station for station, in results]
    
    return jsonify(station_list)


# Define temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Calculate the date 12 months ago from the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)
    
    # Query temperature observations for the last 12 months from the most active station
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).first()[0]
    
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert results to list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    return jsonify(tobs_list)


# Define start date route
@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    """Return a JSON list of the minimum temperature, average temperature, and maximum temperature for a specified start date."""
    # Query temperature data for dates greater than or equal to start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start_date).all()
    
    # Convert results to list of dictionaries
    temp_stats = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]
    
    return jsonify(temp_stats)


# Define start and end date route
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):
    """Return a JSON list of the minimum temperature, average temperature, and maximum temperature for a specified date range."""
    # Query temperature data for dates between start and end dates (inclusive)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start_date).\
              filter(Measurement.date <= end_date).all()
    
    # Convert results to list of dictionaries
    temp_stats = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
