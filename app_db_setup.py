"""
database for signup variable-input:
year (from config), email, name, slack_name,
city, state, country, latitude, longitude, timezone,
age, gender, topic, experience, relation_pref, mentor_choice, freq_pref, gender_pref,
timezone_pref, amount_buddies, objectives, personal_descr, comments
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import streamlit as st


with open('config.json') as config_file:
    conf_data = json.load(config_file)

def init_db():
    """ Connect to PostgreSQL server and create relevant tables needed for user sign-up."""
    connection = None
    if "DATABASE_URL" in os.environ:
        DATABASE_URL = os.environ["DATABASE_URL"]
    else:
        db = conf_data["db"]
        DATABASE_URL = f"postgresql://{db['user']}@{db['host']}/{db['db_name']}"
    try:
        # connect to the PostgreSQL server
        connection = psycopg2.connect(DATABASE_URL)
        connection.autocommit = False
        cur = connection.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS rounds (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        year INTEGER NOT NULL,
                        round_num INTEGER NOT NULL,
                        start_date DATE UNIQUE NOT NULL,
                        end_date DATE UNIQUE NOT NULL,
                        CONSTRAINT year_round UNIQUE (year, round_num));""")
        cur.execute("""CREATE TABLE IF NOT EXISTS users_all (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
                        email VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        slack_name VARCHAR(320) NOT NULL);""")
        cur.execute("""CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        city TEXT NOT NULL,
                        state TEXT,
                        country TEXT NOT NULL,
                        latitude NUMERIC(6, 3) NOT NULL,
                        longitude NUMERIC(6, 3) NOT NULL,
                        timezone NUMERIC(3, 1) NOT NULL,
                        CONSTRAINT lat_long UNIQUE (latitude, longitude));""")
        cur.execute("""CREATE TABLE IF NOT EXISTS matches (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        fk_round_id INTEGER NOT NULL REFERENCES rounds(id),
                        fk_user_1_id INTEGER NOT NULL REFERENCES users_all(id),
                        fk_user_2_id INTEGER NOT NULL REFERENCES users_all(id),
                        algo_score_u1 REAL,
                        algo_score_u2 REAL,
                        feedback_score_u1 INTEGER,
                        feedback_score_u2 INTEGER,
                        feedback_comments_u1 TEXT,
                        feedback_comments_u2 TEXT,
                        CONSTRAINT round_u1_u2 UNIQUE (fk_round_id, fk_user_1_id, fk_user_2_id));""")
        cur.execute("""CREATE TABLE IF NOT EXISTS users_rounds (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        fk_user_id INTEGER NOT NULL REFERENCES users_all(id),
                        fk_location_id INTEGER NOT NULL REFERENCES locations(id),
                        gender TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        topic TEXT NOT NULL CHECK (length(topic) > 0),
                        experience TEXT NOT NULL,
                        mentor_choice TEXT NOT NULL,
                        relation_pref TEXT NOT NULL,
                        freq_pref TEXT NOT NULL,
                        gender_pref TEXT NOT NULL,
                        timezone_pref TEXT NOT NULL,
                        amount_buddies TEXT NOT NULL,
                        objectives TEXT NOT NULL CHECK (length(objectives) >= 100),
                        personal_descr TEXT NOT NULL CHECK (length(personal_descr) >= 100),
                        comments TEXT,
                        fk_round_id INTEGER NOT NULL REFERENCES rounds(id),
                        fk_match_id INTEGER REFERENCES matches(id),
                        CONSTRAINT user_match UNIQUE (fk_user_id, fk_match_id));""")
        # Constrain (fk_user_id, fk_round_id, fk_match_id) to be unique combination in users_rounds table
        cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS user_round_match_not_null 
	                    ON users_rounds (fk_user_id, fk_round_id, fk_match_id)
	                    WHERE fk_match_id IS NOT NULL;""")
        cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS user_round_match_null
	                    ON users_rounds (fk_user_id, fk_round_id)
	                    WHERE fk_match_id IS NULL;""")
        connection.commit()
        return connection
    except psycopg2.DatabaseError as e:
        print(e)
        connection.rollback()

def save(connection, response):
    cur = connection.cursor()
    insert_dates = """INSERT INTO rounds (year, round_num, start_date, end_date)
                        VALUES (%s, %s, %s, %s) ON CONFLICT ON CONSTRAINT year_round DO NOTHING;"""
    insert_users_all = """INSERT INTO users_all (email, name, slack_name)
                            VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING;"""
    insert_locations = """INSERT INTO locations (city, state, country, latitude, longitude, timezone)
                            VALUES (%s, %s, %s, %s, %s, %s) 
                            ON CONFLICT ON CONSTRAINT lat_long DO NOTHING;"""
    insert_users_rounds = """INSERT INTO users_rounds (timestamp, fk_user_id, fk_location_id, 
                                gender, age, topic, experience, mentor_choice, 
                                relation_pref, freq_pref, gender_pref, timezone_pref, 
                                amount_buddies, objectives, personal_descr, comments, fk_round_id) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT ON CONSTRAINT user_match DO NOTHING;"""

    try:
        dates = conf_data["dates"]
        cur.execute(insert_dates, [dates["year"], dates["round_num"], 
                        dates["start_date"], dates["end_date"]])
        cur.execute(insert_users_all, [response["email"], response["name"], 
                        response["Slack name"]])
        cur.execute(insert_locations, [response["city"], response["state"], response["country"],
                        response["latitude"], response["longitude"], response["timezone"]])
        cur.execute("SELECT id FROM users_all WHERE email = %s;", [response["email"]])
        user_id = cur.fetchone()
        cur.execute("SELECT id FROM locations WHERE latitude = %s AND longitude = %s;",
                        [response["latitude"], response["longitude"]])
        loc_id = cur.fetchone()
        cur.execute("SELECT id FROM rounds WHERE year = %s AND round_num = %s;",
                        [dates["year"], dates["round_num"]])
        round_id = cur.fetchone()
        cur.execute(insert_users_rounds, [response["timestamp"], user_id, loc_id, 
                        response["gender"], response["age"], response["topic"], 
                        response["experience"], response["mentor_choice"], 
                        response["relation_pref"], response["freq_pref"], response["gender_pref"], 
                        response["timezone_pref"], response["amount_buddies"], response["objectives"], 
                        response["personal_descr"], response["comments"], round_id])
    except psycopg2.IntegrityError as e:
        if str(e).startswith("duplicate key value violates unique constraint \"user_round_match_null\""):
            st.error(f"""It looks like you have previously signed up for this round! 😍  
                        \nIf unsure, please email <{conf_data["contact"]["email"]}> or
                        message ``{conf_data["contact"]["slack"]}`` on the WWCodePython 
                        #buddymeup Slack channel and we'll check for you.""")
        elif str(e).startswith("new row for relation \"locations\" violates check constraint \"locations_details_check\""):
            st.error(f"""It looks like there is a problem with your input for location 😅; 
                     please go back and check that the map correctly pinpoints your location.""")
        else:
            print(e)
            st.error(f"""Signup unsuccessful 😱.  But don't worry: check that  
                        - all questions have been answered (except last one on comments, which is optional);  
                        - your second-to-last and third-to-last responses contain at least 100 characters;  
                        then submit again.  
                        If still unsuccessful, email <{conf_data["contact"]["email"]}> or
                        message ``{conf_data["contact"]["slack"]}`` on the WWCodePython 
                        #buddymeup slack channel 🆘.""")
        print(e)
        connection.rollback()
    except KeyError as e:
        e = str(e)[1:-1]  # strip quote marks around string
        description = key_lookup(e)
        st.error(f"""It looks like there is a problem with the input for {description} 😅; 
                     please go back and check that your value is valid.""")
        print(e)
        connection.rollback()
    else:
        connection.commit()
        st.success(f"""Thanks for signing up!
                    You will be notified about your buddy on {conf_data['dates']['start_date_html']}.""")
        st.balloons()
    finally:
        connection.close()


# Look up more descriptive field name for given KeyError e
def key_lookup(e):
  key_dict = {
      'email': 'your email',
      'name': 'your name',
      'Slack name': 'your Slack name',
      'city': 'your location',
      'country': 'your location',
      'age': 'your age',
      'gender': 'your gender',
      'topic': 'the areas of Python you\'re focusing on',
      'experience': 'your level of experience',
      'mentor_choice': 'whether you\'d like to be a mentor',
      'relation_pref': 'your preferred relationship with your buddy - casual or structured',
      'gender_pref': 'your preference for your buddy\'s gender',
      'timezone_pref': 'your preference for your buddy\'s timezone',
      'freq_pref': 'your preference for how often you\'d like to meet with your buddy',
      'amount_buddies': 'whether you\'d like one or two buddies',
      'objectives': 'your coding objectives',
      'personal_descr': 'your personal description'
  }
  return key_dict[e]





