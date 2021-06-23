"""
First step in participant matching.

• Reading raw data from:
•• buddymeup-python database (python-track)
•• from .csv-files: generated from google forms for cloud-track (or for python-track as backup)
• Making all (non-string) data numeric

Next step: feed data (pd.df) into score.py for participant scoring
"""

import pandas as pd
import json
import db_queries as dbq
import app_signup_form as asf
import requests

track = "python"

with open('config.json') as config_file:
    conf_data = json.load(config_file)


def prep_csv_data(track = "cloud"):
    """
    Function that reads raw google-forms-csv-data. For cloud signups!
    :param file_path: file_path to .csv file: signups
    :return: pd.df, ready to be transformed (transform_data)
    """

    # for csv data # for cloud track or for python backup
    file_path = conf_data["filepath"][track] + str(conf_data["dates"]["year"]) + "/" +  \
                str(conf_data["dates"]["round_num"]) + conf_data["file_name"]["signups"]
    # read google forms csv into pd.df
    try:
        df_timezone = pd.read_csv(file_path, usecols=["city", "state", "country"])
        df_timezone.dropna(how="all", inplace=True)

        # get timezone from lat and long
        timezone_list = []
        for index, row in df_timezone.iterrows():
            [city, state, country] = row["city"], row["state"], row["country"]
            location_query = "city=%s&state=%s&country=%s" % (city, state, country)
            url = "https://nominatim.openstreetmap.org/search/?" + location_query + "&format=json"
            response = requests.get(url).json()
            if response:
                location_valid = True
                latitude = float(response[0]["lat"])
                longitude = float(response[0]["lon"])
            else:
                location_valid = False
                latitude = 0.0
                longitude = 0.0

            offset = asf.utc_offset(location_valid, latitude, longitude)
            timezone_list.append(offset)

        cols = dbq.var.copy()
        cols.remove("timezone")
        df_og = pd.read_csv(file_path, usecols=cols)
        df_og.dropna(how="all", inplace=True)
        df_og["timezone"] = timezone_list

    except:
        print("check whether the names of the columns match the ones defined in dbq.signup_info!")
    return make_df(df_og)


def prep_db_data(track="python"):
    """
    Function that reads data stored in db
    :return: pd.df, ready to be transformed (transform_data)
    """
    conn = dbq.connect()
    df_raw = pd.read_sql_query(dbq.signup_info, conn)
    conn.close()
    if df_raw.shape[0] == 0:
        print("no data in local db, referring to .csv instead")
        file_path = conf_data["filepath"][track] + str(conf_data["dates"]["year"]) + "/" + \
                    str(conf_data["dates"]["round_num"]) + conf_data["file_name"]["signups"]
        df_raw = pd.read_csv(file_path, usecols=dbq.var)

    return make_df(df_raw)
  

def make_df(df_raw):
    """
    Function that takes raw df parsed from csv or db.
    Creates columns for multiple choice topic selections.
    :return: pd.df, ready to be transformed (transform_data)
    """
    # string to lowercase
    df = df_raw.apply(lambda x: x.astype(str).str.lower())

    # #set index to user_id
    # df.set_index("id", inplace=True)

    # create columns for multiple choice topic selections.
    topics_list = list(set(';'.join(df_raw["topic"].unique()).replace(',',';').lower().split(";")))
    for topic in topics_list:
        df["topic_"+topic] = df["topic"].str.contains(topic).astype(int)
    df_formatted = df.drop(["topic"], axis=1)
    return df_formatted


def transform_data(df):
    """
    Function that takes pd.df containing raw/string data (either real or fake).
    Encodes all data - except name - to numeric only.
    :param filename: pd.df generated from create_data() or prepare_csv_data()
    :return: pd.df with only numeric values - except name (needed for later)
    """
    # dropping text data:
    string = ['slack_name', 'objectives', 'personal_descr', 'name']
    df = df[df.columns.difference(string)]

    # encoding categorical data (where assignment matters)
    df.loc[:, "timezone_pref"] = df["timezone_pref"].map(
        {"different timezone / nationality": 1, "same timezone": 0, "timezone doesn´t matter": 2})
    df.loc[:, "relation_pref"] = df["relation_pref"].map(
        {'more structured - set schedule': 1, 'more casual - we will contact each other when we want to talk': 0})

    df.loc[:, "gender"] = df["gender"].map(
        {"female": 1, "male": 0, "non-binary": 2, "do not want to disclose": 3})
    df.loc[:, "gender_pref"] = df["gender_pref"].map(
        {"female": 1, "male": 0, "non-binary": 2, 'gender doesn´t matter to you': 3})
    df.loc[:, "amount_buddies"] = df["amount_buddies"].map(
        {"i´d rather start with one!": 1, "sure!": 2})
    df.loc[:, "freq_pref"] = df["freq_pref"].map(
        {"daily": 0, "weekly": 1, "bi-weekly": 2, "monthly": 3})
    df.loc[:, "experience"] = df["experience"].map(
        {"0 years, getting started": 1,
         "0-1 year": 2,
         "1-3 years": 3,
         "3+ years": 4})
    df.loc[:, "mentor_choice"] = df["mentor_choice"].map(
        {"Yes": 1,
         "No - I prefer to be matched with someone on the same level or with more experience": 2,
         "Either would be great": 0})

    # formatting numerical data
    df.loc[:,"timezone"] = df["timezone"].apply(lambda x: float(x))
    df.loc[:,"age"] = df["age"].apply(lambda x: (int(float(x))))

    # df with encoded columns and users_round_info_id
    email_ids = df["email"] # keep this to be able to manually check later

    idx_reset = [int(x) for x in email_ids.index.tolist()] # these are the index of matrix dataframe
    idx_user_id = [int(x) for x in df["id"].tolist()] # these are the user_ids as saved in db
    idx_dict = dict(zip(idx_reset, idx_user_id)) #dictionary of both as reference

    df_enc = df.drop(["email", "id"], axis=1)

    return email_ids, df_enc, idx_dict


def prep_data(track="python"):
    """
    combining functions to prep data
    """
    if track == "python":
        data = prep_db_data(track=track)
    elif track == "cloud":
        data = prep_csv_data(track=track)
    email_ids, fdf, idx_dict = transform_data(data)
    print("data is prepped for track: {}".format(track))
    return data, email_ids, fdf, idx_dict