import sqlite3
from flask import g, current_app

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    with current_app.app_context():  # Ensures app context is active
        con = get_connection()
        result = con.execute(sql, params)
        con.commit()
        g.last_insert_id = result.lastrowid
        con.close()

def last_insert_id():
    return getattr(g, 'last_insert_id', None)  # Safer access in case `g` is undefined

def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result