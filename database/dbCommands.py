import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def getConnection():
  return psycopg2.connect(DATABASE_URL, sslmode='require')

def databaseWrite(query):
  conn = None
  try:
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    return True
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return False
  finally:
    if conn is not None:
      conn.close()

def databaseReadOne(query):
  conn = None
  try:
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(query)
    row = cur.fetchone()
    print(f"databaseRead: Found {row}")
    cur.close()
    return row
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()

def databaseReadMany(query):
  conn = None
  try:
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(query)
    row = cur.fetchone()

    results = []
    while row is not None:
      results.append(row)
      row = cur.fetchone()

    print(f"databaseReadMany: Found {len(results)} results")
    cur.close()
    return results
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    return None
  finally:
    if conn is not None:
      conn.close()