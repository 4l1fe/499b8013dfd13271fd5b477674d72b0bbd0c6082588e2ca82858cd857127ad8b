import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


DSN = f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"


def insert(function, interval, step):
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO modeling (function, interval, step) VALUES(%s, %s, %s)
                           RETURNING id""",
                        (function, interval, step))
            id_ = cur.fetchone()[0]
    return id_


def update(id_, image=None, error=None):
    if image:
        query = """UPDATE modeling SET image=%s WHERE id=%s"""
        field = psycopg2.Binary(image)
    elif error:
        query = """UPDATE modeling SET error=%s WHERE id=%s"""
        field = error

    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (field, id_))


def create_db():
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS modeling (
                                id SERIAL PRIMARY KEY,
                                function TEXT NOT NULL,
                                interval SMALLINT NOT NULL,
                                step SMALLINT NOT NULL,
                                error TEXT,
                                image BYTEA)
                        """)


if __name__ == '__main__':
    create_db()
