import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


def generate_data(params):
    dsn = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    print(dsn)
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur: #todo funciton substitution
            cur.execute("""SELECT {} as x, t as y
                           FROM (SELECT extract(epoch from generate_series(%s::timestamp, %s, %s)) as t) as timestamps"""
                           .format(params['function']),
                        (params['start'], params['stop'], params['step']))
            result = cur.fetchall()
    return result
