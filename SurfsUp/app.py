# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement= Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
def date_prev_year():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365) 
    session.close()  
    return(first_date) 

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
        f"Climate App API<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
   
    session = Session(engine)

    
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prev_year()).all()
    
                   
    session.close()

    
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

   
    return jsonify(prcp_list)

#Stations
@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    
    station_data = session.query(Station.station).all()

                   
    session.close()


    station_list = list(np.ravel(station_data))

    
    return jsonify(station_list)

#Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= date_prev_year()).all()

                      
    session.close()

    
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    
    return jsonify(tobs_list)

#Start
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    
    session = Session(engine)
    
   
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    
    if end == None: 
        
        start_data = session.query(*sel).\
                            filter(Measurement.date >= start).all()
       
        start_list = list(np.ravel(start_data))

       
        return jsonify(start_list)
    else:
        
        start_end_data = session.query(*sel).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
        
        start_end_list = list(np.ravel(start_end_data))

        
        return jsonify(start_end_list)

                     
    session.close()
    

if __name__ == "__main__":
    app.run(debug = True)