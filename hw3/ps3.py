import sqlite3, pandas, datetime, numpy
conn = sqlite3.connect('monkepo.db')
curs = conn.cursor()
curs.execute('CREATE TABLE Monkepo(\
             mid INTEGER PRIMARY KEY AUTOINCREMENT,\
             name TEXT,\
             UNIQUE(name))')
curs.execute('CREATE TABLE Appearance(\
             mid INTEGER,\
             latitude REAL,\
             longitude REAL,\
             datetime DATETIME,\
             PRIMARY KEY(mid, latitude, longitude, datetime),\
             FOREIGN KEY(mid) REFERENCES Monkepo(mid))')
curs.execute('CREATE TABLE Class(\
             mid INTEGER,\
             major BOOLEAN,\
             type TEXT,\
             PRIMARY KEY(mid, major),\
             FOREIGN KEY(mid) REFERENCES Monkepo(mid))')
monkcsv = pandas.read_csv('monkepo.csv')
monk_names = monkcsv.name.drop_duplicates()
monk_names.to_sql('Monkepo', conn, if_exists='append', index=False)


def converttime(row):
    try:
        return datetime.datetime.combine(
            datetime.datetime.strptime(row['date'], '%Y-%m-%d'),
            datetime.datetime.time(datetime.datetime.strptime(row['time'], '%H:%M:%S.%f')))
    except ValueError:
        return datetime.datetime.combine(
            datetime.datetime.strptime(row['date'], '%Y-%m-%d'),
            datetime.datetime.time(datetime.datetime.strptime(row['time'], '%H:%M:%S')))


def monkepotomid(row):
    return pandas.read_sql_query(
        'SELECT mid from Monkepo M WHERE M.name = "'+ row['name'] + '"', conn)['mid'][0]


monkcsv['mid'] = monkcsv.apply(monkepotomid, axis=1)
monk_sightings = monkcsv.drop(['majorclass', 'minorclass', 'date', 'time', 'name'], axis=1)
monk_sightings['datetime'] = monkcsv.apply(converttime, axis=1)
monk_sightings = monk_sightings.drop_duplicates()
monk_sightings.to_sql('Appearance', conn, if_exists='append', index=False,)
monk_class_major = monkcsv.drop(
    ['longitude', 'latitude', 'name', 'date', 'time', 'minorclass'], axis=1)
monk_class_minor = monkcsv.drop(
    ['longitude', 'latitude', 'name', 'date', 'time', 'majorclass'], axis=1)
monk_class_minor = monk_class_minor.drop_duplicates()
monk_class_major = monk_class_major.drop_duplicates()
monk_class_major.rename(columns={'majorclass':'type'}, inplace=True)
monk_class_minor.rename(columns={'minorclass':'type'}, inplace=True)
monk_class_major['major'] = True
monk_class_minor['major'] = False
monk_class = pandas.concat([monk_class_major, monk_class_minor])
monk_class = monk_class[monk_class.type != 'None']
monk_class.to_sql('Class', conn, if_exists='append', index=False)
conn.commit()
conn.close()


def appearancefreqpy(db):
    conn = sqlite3.connect(db)
    monks = pandas.read_sql_query('SELECT M.name\
                                  FROM (Monkepo JOIN Appearance USING(mid)) AS M',
                                  conn)
    conn.close()
    monkviews = {}
    for row in monks.values:
        monkviews[row[0]] = monkviews.get(row[0],0) + 1
    return sorted(monkviews.items(), key=lambda tup: tup[1], reverse=True)


pandas.DataFrame(appearancefreqpy('monkepo.db'), columns=['Name', 'Appearances'])


def appearancefreqsql(db):
    conn = sqlite3.connect(db)
    res = [tuple(tup) for tup in
            pandas.read_sql_query('SELECT M.name, count(M.mid)\
                                 FROM (Monkepo JOIN Appearance USING(mid)) AS M\
                                 GROUP BY(M.mid)\
                                 ORDER BY COUNT(M.mid) DESC',
                                 conn).values]
    conn.close()
    return res


pandas.DataFrame(appearancefreqsql('monkepo.db'), columns=['Name', 'Appearances'])


def maxminclass(db):
    conn = sqlite3.connect(db)
    classes = pandas.read_sql_query('SELECT DISTINCT type FROM Class', conn)
    res = []
    for i in classes['type']:
        maxmonk = pandas.read_sql_query('SELECT name\
                                 FROM (Monkepo JOIN Appearance USING(mid)\
                                       JOIN Class USING(mid)) AS M\
                                 WHERE type = "' + i + '"\
                                 GROUP BY M.mid\
                                 ORDER BY COUNT(M.mid) DESC\
                                 LIMIT 1',
                                 conn)
        minmonk = pandas.read_sql_query('SELECT name\
                                 FROM (Monkepo JOIN Appearance USING(mid)\
                                       JOIN Class USING(mid)) AS M\
                                 WHERE type = "' + i + '"\
                                 GROUP BY M.mid\
                                 ORDER BY COUNT(M.mid) ASC\
                                 LIMIT 1',
                                 conn)
        res.append((i, maxmonk.name[0], minmonk.name[0]))
    conn.close()
    return res


pandas.DataFrame(maxminclass('monkepo.db'), columns=['Class', 'Most Common', 'Least Common'])


conn = sqlite3.connect('monkepo.db')
curs = conn.cursor()
curs.execute('CREATE TABLE SupplyStations(\
             stationID INTEGER PRIMARY KEY,\
             latitude REAL,\
             longitude REAL)')
pandas.read_csv("stations.csv").to_sql('SupplyStations', conn, if_exists='append', index=False)
conn.commit()
conn.close()


def stationpopularity(db):
    appearances = pandas.read_sql_query('SELECT A.latitude, A.longitude\
                                        FROM Appearance A',
                                        sqlite3.connect(db))
    stations = pandas.read_sql_query('SELECT S.stationID, S.latitude, S.longitude\
                                            FROM SupplyStations S',
                                            sqlite3.connect(db))
    stations['count'] = 0
    for applat, applong in appearances.values:
        min_dist = float('inf')
        pos = 0
        station = 0
        for statid, statlat, statlong, count in stations.values:
            dist = numpy.sqrt(numpy.power(applat-statlat, 2)+numpy.power(applong-statlong, 2))
            if dist < min_dist:
                min_dist = dist
                station = pos
            pos += 1
        stations.set_value(station, 'count', stations['count'][station] + 1)
    stations.sort_values('count', axis=0, ascending=False, inplace=True, kind='quicksort')
    res = []
    for statid, statlat, statlong, count in stations.values:
        res.append((statid, statlat, statlong, count))
    return res


pandas.DataFrame(stationpopularity('monkepo.db'),
                 columns = ['Station', 'Longitude', 'Latitude', 'Nearby'])
