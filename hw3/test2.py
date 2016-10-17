import pandas
import datetime
import sqlite3

conn = sqlite3.connect('monkepo.db')
curs = conn.cursor()
monkcsv = pandas.read_csv('monkepo.csv')

monkcsv['datetime'] = datetime
monkcsv['datetime'] = datetime
for i in range(0, len(monkcsv)):
    monkcsv.loc[i]['datetime'] = monkcsv.iloc[i]['date'] + " " + monkcsv.iloc[i]['time']
print(monkcsv.head())

