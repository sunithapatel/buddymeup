"""
Module configuring the signup sheet for data input
"""

import streamlit as st
import streamlit.components.v1 as components
import app_db_setup as dbs
import string
import re
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from datetime import timezone as dt_timezone
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
import geopandas
import matplotlib.pyplot as plt


def signup():
    """
    email, name, slack_name,
    city, state, country, timezone,
    age, gender, topic, experience, mentor_choice,
    relation_pref, freq_pref, gender_pref, timezone_pref, amount_buddies, 
    objectives, personal_descr, comments
    :return: dictionary containing participant information 
    """

    st.header("Please fill in the following:")

    participant_info = {}

    email, check = st.beta_columns(2)
    email = email.text_input("Email")
    if re.match(r'^.+@.+\..{2,3}$', email.strip()):
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["email"] = email
    else:  # invalid email
        check.error(f"Please input your email")
    
    labels = ["name", "Slack name"]
    for label in labels:
        field, check = st.beta_columns(2)
        field = field.text_input(string.capwords(label))
        if len(field.strip()) < 2:  # should contain at least 2 chars
            check.error(f"Please input your {label}")
        else:
            check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
            participant_info[label] = field

    city, state, country = st.beta_columns(3)
    city = string.capwords(city.text_input("Your city"))
    state = state.text_input("Your state/province (if applicable)")
    country = country.text_input("Your country")
    participant_info = {
        "city": city,
        "state": state,
        "country": country
    }

    # Get latitude and longitude of participant's location
    location_valid, latitude, longitude = get_lat_long(city, state, country)
    offset = utc_offset(location_valid, latitude, longitude)
    if location_valid:
        print_timezone(offset)
    
    draw_map(location_valid, latitude, longitude)  # will draw default map if location not valid

    participant_info = {
        "timezone": offset,
        "latitude": latitude,
        "longitude": longitude
    }

    participant_info = {}

    age, check = st.beta_columns(2)
    age = age.number_input("Age", min_value=0, max_value=100)
    if age < 16:
        check.error(f"Please input your age (at least 16)")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["age"] = age

    gender, check = st.beta_columns(2)
    gender = gender.selectbox("Your gender",["-", "female", "male", "non-binary", "do not want to disclose"])
    if gender == "-":
        check.error(f"Please input your gender")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["gender"] = gender

    topic, check = st.beta_columns(2)
    topic = topic.multiselect("What area(s) of Python are you focusing on?",
                                ("Data Science", "Machine Learning", "Mobile", "Backend", "Frontend"))
    if not topic:
        check.error(f"Please input your focus topics")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["topic"] = topic

    experience, check = st.beta_columns(2)
    experience = experience.selectbox("Your level of experience",
                                ["-", "0 years, getting started", "0-1 year", "1-3 years", "3+ years"])
    if experience == "-":
        check.error(f"Please input your experience level")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["experience"] = experience

    gender_pref, check = st.beta_columns(2)
    gender_pref = gender_pref.selectbox("You'd prefer a buddy of gender",
                                ["-", "female", "male", "non-binary", "gender doesn't matter to you"])
    if gender_pref == "-":
        check.error(f"Please indicate your preferred buddy gender")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["gender_pref"] = gender_pref

    timezone_pref, check = st.beta_columns(2)
    timezone_pref = timezone_pref.selectbox("You'd prefer a buddy in",
                                ["-", "same timezone", "different timezone / nationality", 
                                "timezone doesn't matter"])
    if timezone_pref == "-":
        check.error(f"Please indicate your preferred buddy timezone")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["timezone_pref"] = timezone_pref

    freq_pref, check = st.beta_columns(2)
    freq_pref = freq_pref.selectbox("How often would you like to meet?", 
                                ["-", "daily", "weekly", "bi-weekly", "monthly"])
    if freq_pref == "-":
        check.error(f"Please indicate your preferred meeting frequency")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["freq_pref"] = freq_pref

    amount_buddies, check = st.beta_columns(2)
    amount_buddies = amount_buddies.selectbox("You'd be happy to be matched with two buddies",
                                ["-", "sure!", "I'd rather start with one!"])
    if amount_buddies == "-":
        check.error(f"Please indicate your preferred number of buddies")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["amount_buddies"] = amount_buddies

    mentor_choice, check = st.beta_columns(2)
    mentor_choice = mentor_choice.selectbox("You want to be a mentor to someone with less experience", 
                                ["-",
                                 "Yes", 
                                 "No - I prefer to be matched with someone on the same level or with more experience", 
                                 "Either would be great"])
    if mentor_choice == "-":
        check.error(f"Please indicate whether you would like to be a mentor")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["mentor_choice"] = mentor_choice

    relation_pref, check = st.beta_columns(2)
    relation_pref = relation_pref.selectbox("Relationship type", 
                                ["-", 
                                 "More casual - we will contact each other when we want to talk",
                                 "More structured - set schedule"])
    if relation_pref == "-":
        check.error(f"Please indicate your preferred meeting structure")
    else:
        check.markdown("<p style='margin-top: 40px'>&#10003</p>", unsafe_allow_html=True)
        participant_info["relation_pref"] = relation_pref
    
    objectives = st.text_area("Your coding objectives", "")
    if len(objectives.strip()) < 100:
        st.error("""Please write at least 100 characters; 
                    the more descriptive, the better we could match you!""")
    else:
        participant_info["objectives"] = objectives

    personal_descr = st.text_area("""Please give a little description about yourself 
                                        so that we can get to know you better""", "")
    if len(personal_descr.strip()) < 100:
        st.error("""Please write at least 100 characters; 
                    the more descriptive, the better we could match you!""")
    else:
        participant_info["personal_descr"] = personal_descr

    comments = st.text_area("Comments", "")
    participant_info["comments"] = comments

    timestamp = datetime.now(tz=dt_timezone.utc)
    participant_info["timestamp"]: timestamp.strftime("%Y/%m/%d %H:%M:%S")

    # Turn "topic" from array to string
    if "topic" in participant_info:
        participant_info["topic"] = ",".join(participant_info["topic"])

    return participant_info
    

def get_lat_long(city, state, country):
    if not (city and country):  # require values for both city and country
        st.error(f"""📌 Your location should be marked below; if not, 
                         please check that the details entered above are correct.""")
        location_valid = False
        latitude = 0.0
        longitude = 0.0
        return location_valid, latitude, longitude
    location_query = "city=%s&state=%s&country=%s" % (city, state, country)
    url = "https://nominatim.openstreetmap.org/search/?" + location_query + "&format=json"
    response = requests.get(url).json()
    if response:
        location_valid = True
        latitude = round(float(response[0]["lat"]), 3)
        longitude = round(float(response[0]["lon"]), 3)
    else:
        if city or country:
            st.error(f"""📌 Your location should be marked below; if not, 
                         please check that the details entered above are correct.""")
        location_valid = False
        latitude = 0.0
        longitude = 0.0
    return location_valid, latitude, longitude


def utc_offset(location_valid, lat, lng):
    """
    Returns a location's UTC offset in hours.
    Arguments:
    location_valid -- whether lat and lng have been determined by get_lat_long
    lat -- location's latitude
    lng -- location's longitude
    """
    if not location_valid:
        return 0
    today = datetime.now()
    tf = TimezoneFinder(in_memory=True)
    tz_target = timezone(tf.certain_timezone_at(lng=lng, lat=lat))
    if tz_target is None:
        return 0
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds() / 3600


def draw_map(location_valid, latitude, longitude):
    fig, ax = plt.subplots()
    ax.axis('off')
    fig.patch.set_facecolor('None')
    fig.patch.set_edgecolor('#A8B3CC')
    fig.patch.set_linewidth('2')

    world_df = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world_plot = world_df.plot(figsize=(10, 10), ax=ax, alpha=0.3, color='#01852a', edgecolor='#0b5e24')
    
    point_df = pd.DataFrame({'Latitude': [latitude], 'Longitude': [longitude]})
    geo_point_df = geopandas.GeoDataFrame(
        point_df, geometry=geopandas.points_from_xy(point_df['Longitude'], point_df['Latitude']))

    # Plot point given by (latitude, longitude) on world map
    if location_valid:
        geo_point_df.plot(ax=world_plot, marker='*', markersize=300, color='#db0909')
    else:
        pass  # no location point to plot

    st.pyplot(fig)


def print_timezone(offset):
    if offset < 0:
        st.info(f"It looks like you are in time zone UTC{offset} 🤠.")
    else:
        st.info(f"It looks like you are in time zone UTC+{offset} 🤠.")


def save(response):
    # Initialize database
    connection = dbs.init_db()
    #save inputs to db
    dbs.save(connection, response)
