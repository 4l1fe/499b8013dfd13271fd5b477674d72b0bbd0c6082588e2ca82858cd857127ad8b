import psycopg2
from datetime import datetime
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"


def generate_data(function, interval, step):
    now = datetime.now()
    interval = f'{interval} days'
    step = f'{step} hour'
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT t, %(function)s
                           FROM (SELECT extract(epoch from generate_series(%(now)s - interval %(interval)s , %(now)s, %(step)s)) as t)
                                as timestamps""",
                        {'function': function, 'now': now, 'interval': interval, 'step': step})
            data = cur.fetchall()
    return data
