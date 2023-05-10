"""
Matthew Fernandez
5/9/2023
Flask API based on the queries from climate_starter.ipynb
"""

# Import the dependencies.
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, render_template, request, abort, jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect the tables
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
# Initial parameters to render index.html 
@app.route("/")
def index():
    return render_template("index.html", err_msg="")

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Perform a query to retrieve the data and precipitation scores
    sql_statement = """
    SELECT date, prcp
    FROM measurement
    ORDER BY date ASC;
    """

    # Save the query results as a Pandas DataFrame.
    df_date_precep = pd.read_sql(sql_statement, engine)

    # Sort the dataframe by date
    df_date_precep.sort_values(by="date", inplace=True)
    df_date_precep['date'].iloc[-1]
    values_int = []
    # extract year month and day from the most recent date value
    for i in df_date_precep['date'].iloc[-1].split('-'):
        values_int.append(int(i))
    yr, month, day = values_int
    # change to pandas datetime to perform operations in query
    query_date = dt.date(yr, month, day) - dt.timedelta(days=365)

    data = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= query_date).all()
    df_12month_precip = pd.DataFrame(data, columns=['date', 'prcp'])
    # define keys and values for dictionary to return 
    keys = df_12month_precip['date']
    values = df_12month_precip['prcp']
    dict_of_12_month_precipitation = {}
    # add key and value to new dictionary
    for i, key in enumerate(keys.tolist()):
        dict_of_12_month_precipitation[key] = values.tolist()[i]
    # close session
    session.close()
    return jsonify(dict_of_12_month_precipitation)

@app.route('/api/v1.0/stations')
def stations():
    # return a list of all stations
    stations_tuple = session.query(Measurement.station).group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).all()
    stations_list = []
    # create list from tuple values
    for val in stations_tuple:
        stations_list.append(val[0])
    # close session
    session.close()
    return jsonify(stations_list)


@app.route('/api/v1.0/tobs')
def tobs():

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    sql_statement = """
    SELECT date, tobs
    FROM measurement
    WHERE station is "USC00519281";
    """

    df_temp = pd.read_sql(sql_statement, engine)

    # Sort the dataframe by date
    df_temp.sort_values(by="date", ascending=False, inplace=True)

    values_int = []
    # extract year month and day from the most recent date value
    for i in df_temp['date'].iloc[0].split('-'):
        values_int.append(int(i))
    yr, month, day = values_int

    # change to pandas datetime to perform operations in query
    query_date = dt.date(yr, month, day) - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.tobs).\
                    where(Measurement.station=='USC00519281').\
                    filter(Measurement.date >= query_date).all()
    df_12month_temp = pd.DataFrame(data, columns=['date', 'tobs'])
    
    # list of values to return
    temperature_observations = df_12month_temp['tobs'].tolist()
    # close session
    session.close()
    return jsonify(temperature_observations)

# FORMAT MMDDYYYY
@app.route('/api/v1.0/<start>')
def start(start):
    # extract month, day, yr from start parameter
    month = int(start[:2])
    day = int(start[2:4])
    yr = int(start[4:])
    # datetime format for query
    query_date = dt.date(yr, month, day)
    temperatures = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.sum(Measurement.tobs)/func.count(Measurement.tobs)).\
                where(Measurement.date >= query_date).all()
    temperatures = [tuple(row) for row in temperatures]
    # close session
    session.close()
    return jsonify(temperatures[0])


@app.route('/api/v1.0/<start>/<end>')
def end_through_start(start, end):
    # extract month, day, yr from start parameter
    month = int(start[:2])
    day = int(start[2:4])
    yr = int(start[4:])
    # datetime format for query
    query_date = dt.date(yr, month, day)

    # extract month, day, yr from start parameter
    month = int(end[:2])
    day = int(end[2:4])
    yr = int(end[4:])
    # datetime format for query
    query_date_2 = dt.date(yr, month, day)
    # run query
    temperatures = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.sum(Measurement.tobs)/func.count(Measurement.tobs)).\
                where(Measurement.date >= query_date).where(Measurement.date <= query_date_2).all()
    # list of values to return
    temperatures = [tuple(row) for row in temperatures]
    # close session
    session.close()
    return jsonify(temperatures[0])

if __name__ == "__main__":
    # run Flask API
    app.run()