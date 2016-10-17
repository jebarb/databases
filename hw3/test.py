import pandas
import datetime
import sqlite3

conn = sqlite3.connect('monkepo.db')
curs = conn.cursor()
monkcsv = pandas.read_csv('monkepo.csv')

def combinetwo(row):
    try:
        return datetime.datetime.combine(datetime.datetime.strptime(row['date'], '%Y-%m-%d'), datetime.datetime.time(datetime.datetime.strptime(row['time'], '%H:%M:%S.%f')))
    except ValueError:
        return datetime.datetime.combine(datetime.datetime.strptime(row['date'], '%Y-%m-%d'), datetime.datetime.time(datetime.datetime.strptime(row['time'], '%H:%M:%S')))

monk_sightings = monkcsv.drop(['majorclass', 'minorclass', 'date', 'time'], axis=1)
monk_sightings['datetime'] = monkcsv.apply(combinetwo, axis=1)
print(monk_sightings.head())

