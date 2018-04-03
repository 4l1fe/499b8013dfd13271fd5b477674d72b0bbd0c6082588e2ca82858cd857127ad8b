import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"


def generate_data(function, start, stop, step):
    step = f'{step} hour'
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur: # TODO: funciton substitution
            cur.execute("""SELECT {} as x, t as y
                           FROM (SELECT extract(epoch from generate_series(%s::timestamp, %s, %s)) as t) as timestamps"""
                           .format(function),
                        (start, stop, step))
            data = cur.fetchall()
    return data
