import psycopg2
from psycopg2.extras import DictCursor
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"


def connect(func):

    def wrapped(*args, **kwargs):
        with psycopg2.connect(DSN) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                args = args + (cursor, )
                result = func(*args, **kwargs)
                return result

    return wrapped


@connect
def get_all(cursor, id_list=None):
    query = """SELECT id, function, interval, step, (image IS NOT NULL) as has_image, error
               FROM models"""

    if id_list:
        query += " WHERE id = ANY(%s)"
        cursor.execute(query, (id_list, ))
    else:
        cursor.execute(query)

    models = cursor.fetchall()
    return models


@connect
def get_image(id_, cursor):
    cursor.execute("""SELECT image
                   FROM models
                   WHERE id=%s""", (id_, ))
    image = cursor.fetchone()['image']
    return image


@connect
def insert(function, interval, step, cursor):
    cursor.execute("""INSERT INTO models (function, interval, step) VALUES(%s, %s, %s)
                   RETURNING id""", (function, interval, step))
    id_ = cursor.fetchone()['id']
    return id_


@connect
def update(id_, cursor, image=None, error=None):
    query = """UPDATE models SET updated=now(), {field_name}=%s WHERE id=%s"""
    if image:
        query = query.format(field_name='image')
        field_value = psycopg2.Binary(image)
    elif error:
        query = query.format(field_name='error')
        field_value = error

    cursor.execute(query, (field_value, id_))


@connect
def create_db(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS models (
                        id SERIAL PRIMARY KEY,
                        function TEXT NOT NULL,
                        interval SMALLINT NOT NULL,
                        step SMALLINT NOT NULL,
                        error TEXT DEFAULT '',
                        image BYTEA,
                        updated TIMESTAMP)""")


if __name__ == '__main__':
    create_db()
