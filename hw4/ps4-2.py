import sqlite3
import pandas


def hashstuff():
    conn = sqlite3.connect('movies.db')
    actors = pandas.read_sql_query('SELECT DISTINCT aid FROM Actors', conn)
    cast = pandas.read_sql_query('SELECT aid FROM Cast', conn)
    conn.close()
    actorslist = [[] for x in range(1024)]
    castlist = [[] for x in range(1024)]
    for item in actors.values:
        actorslist[item[0] % 1024].append(item)
    for item in cast.values:
        castlist[item[0] % 1024].append(item)
    maxact = -1
    minact = float("inf")
    totalact = 0
    for item in actorslist:
        totalact += len(item)
        if len(item) > maxact:
            maxact = len(item)
        if len(item) < minact:
            minact = len(item)
    avgact = totalact / 1024
    maxcast = -1
    mincast = 999999999999
    totalcast = 0
    for item in castlist:
        totalcast += len(item)
        if len(item) > maxcast:
            maxcast = len(item)
        if len(item) < mincast:
            mincast = len(item)
    avgcast = totalcast / 1024
    print("Largest Actor bucket: " + str(maxact))
    print("Smallest Actor bucket: " + str(minact))
    print("Average Actor bucket: " + str(avgact))
    print("Largest Cast bucket: " + str(maxcast))
    print("Smallest Cast bucket: " + str(mincast))
    print("Average Cast bucket: " + str(avgcast))
    print("Number of Actor entries: " + str(len(actors)))
    print("Nubmer of Cast entries: " + str(len(cast)))
    print("Cost of query: " + str((avgact)*.5*len(cast)))


hashstuff()
