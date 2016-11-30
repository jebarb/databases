import sqlite3
import pandas


def printfilmography(movie):
    conn = sqlite3.connect('movies.db')
    actors = pandas.read_sql_query(
            'SELECT DISTINCT A.aid, A.name \
            FROM Actors A\
            WHERE A.aid IN ( \
                SELECT C.aid \
                FROM Cast C \
                WHERE C.mid IN ( \
                    SELECT M.mid \
                    FROM Movies M \
                    WHERE M.title = "' + movie + '"))', conn)
    for aid, aname in actors.values:
        print(aname + ',')
        for title, release in pandas.read_sql_query(
                'SELECT DISTINCT title, release \
                FROM Movies JOIN \
                    (SELECT C.aid, C.mid \
                    FROM Cast C \
                    WHERE C.aid = "' + str(aid) + '") \
                    USING(mid) \
                WHERE aid = "' + str(aid) + '"', conn).values:
            print('   ' + title + ', ' + release)


printfilmography('Superman')
