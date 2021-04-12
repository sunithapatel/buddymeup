"""
Function for scoring algorithm
•	Scoring numerical/categorical attributes (closed questions in survey)
•	Scoring text attributes (open-ended questions in survey)
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import db_queries as dbq

track = "python"

with open('config.json') as config_file:
    conf_data = json.load(config_file)


def calc_similarity(text_responses):
    """
    Function for scoring the similarity of text responses (objectives and personal interests)
    between each pair of participants.

    :return: N x N scores df (N = no. of participants).
    """
    vect = TfidfVectorizer(min_df=1, stop_words="english")
    tfidf = vect.fit_transform(text_responses)
    # tfidf is a sparse matrix with dimensions (no. of documents) * (no. of distinct words)
    # Get whole matrix:
    tfidf_matrix = tfidf.todense()

    cos_similarity_matrix = np.zeros((tfidf_matrix.shape[0], tfidf_matrix.shape[0]))
    for i in range(tfidf_matrix.shape[0]):
        for j in range(tfidf_matrix.shape[0]):
            cos_similarity_matrix[i][j] = cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])

    # rescale values to a scale of 0-1
    min_max_scaler = MinMaxScaler()
    cos_similarity_scaled = min_max_scaler.fit_transform(cos_similarity_matrix)

    return cos_similarity_scaled


def scoring_alg(fdf, data, idx_dict, track = track):
    """
    Function for scoring algorithm. Logic:
    •	Assign weight to each item
    •	Score each item of other person
    •	Create score for each other person (sum of weights*attribute_scores)
    •	Create matrix of scores (each persons score on each other person)
    todo: question: could this be written with less code by transposing a numpy array?
    :param fdf: pd.df with numeric values from transform_data()
    :return: pd.df with score of each person for each person
    """
    dfa = fdf.copy()
    dfa.apply(pd.to_numeric)

    # setting weights per item
    weights_dict = {
        "gender": 1,
        "timezone": 0.8,
        "experience": 0.9,
        "age": 0.3,
        "freq_pref": 0.5,
        "relation_pref": 0.3,
        "objectives": 0.01,
        "personal_descr": 0.01
    }
    # setting topic weights to 1 for each topic
    weight_topic = 1
    topics_list = dfa.filter(regex="topic", axis=1).columns.tolist()
    weights_topics = {w: weight_topic for w in topics_list}

    weights_dict.update(weights_topics)

    scores_all = {}
    # N x N array of similarity scores for text-based responses
    scores_objectives = calc_similarity(data["objectives"])
    scores_descr = calc_similarity(data["personal_descr"])

    for pa in range(len(dfa.index)):  # for pa = person a in df
        scores_dict = {}

        gender_scores = []
        tz_scores = []
        experience_scores = []
        for pb in range(len(dfa.index)):  # pb = person b
            # variables where preference matters: gender, timzone, mentor_choice/experience
            # gender
            if dfa["gender_pref"].iloc[pa] == dfa["gender"].iloc[pb] and dfa["gender"].iloc[pb] != 3:
                gender_score = 1
            else:
                gender_score = 0.5
            gender_scores.append(gender_score)

            # timezone
            # todo: alter scoring for timezone! "tz 12 is followed by tz 1"
            tz_score_not_norm = abs(int(dfa["timezone"].iloc[pa]) - int(dfa["timezone"].iloc[pb]))
            max = 26 # (dfa["timezone"].max()) - (dfa["timezone"].min()) # total of 26 different timezones
            min = 0
            if dfa["timezone_pref"].iloc[pa] == 0:  # if person a indicated preference for same timezone
                tz_score = round(1 - (tz_score_not_norm - min) / (max - min), 2)
            elif dfa["timezone_pref"].iloc[pa] == 1:  # if person indicated a preference for opposite timezones
                tz_score = round((tz_score_not_norm - min) / (max - min), 2)
            else:# dfa["timezone_pref"].iloc[pa] == 2:  # if person indicated no preference for any timezone
                tz_score = 0.5
            tz_scores.append(tz_score)

            # mentor_choice (mentor or buddy) --> experience matters
            experience_score_not_norm = abs(int(dfa["experience"].iloc[pa]) - int(dfa["experience"].iloc[pb]))
            max = (dfa["experience"].max()) - (dfa["experience"].min())
            min = 0

            if dfa["mentor_choice"].iloc[pa] == 2:  # if person indicated preference for buddy/mentor (2 = No. I prefer to be matched with someone on the same level or with more experience.)
                experience_score = round(1 - (experience_score_not_norm - min) / (max - min), 2)
            elif dfa["mentor_choice"].iloc[pa] == 1:  # if person indicated preference for mentee (1 = Yes. I would mentpr)
                experience_score = round((experience_score_not_norm - min) / (max - min), 2)
            else: # if person indicated no preference for experience level (mentee or buddy)
                experience_score = 0.5
            experience_scores.append(experience_score)

        scores_dict["gender"] = gender_scores
        scores_dict["timezone"] = tz_scores
        scores_dict["experience"] = experience_scores

        # ordinal variables where least distance matters
        list_ord = ["age", "freq_pref"]
        for item in list_ord:
            item_scores = []
            for pb in range(len(dfa.index)):
                item_score_not_norm = abs(int(dfa[item].iloc[pa]) - int(dfa[item].iloc[pb]))
                max = (dfa[item].max()) - (dfa[item].min())
                min = 0
                item_score = round(1 - (item_score_not_norm - min) / (max - min), 2)  # rescale values 0-1
                item_scores.append(item_score)
            scores_dict[item] = item_scores

        # binary items where similarity matters / items must match
        list_bin = ["relation_pref"]
        list_bin.extend(topics_list)

        for item in list_bin:
            item_scores = []
            for pb in range(len(dfa.index)):
                if dfa[item].iloc[pa] == dfa[item].iloc[pb]:
                    item_score = 1
                else:
                    item_score = 0
                item_scores.append(item_score)
            scores_dict[item] = item_scores

        # text-based responses: objectives and self-descriptions
        scores_dict["objectives"] = scores_objectives[pa][:]
        scores_dict["personal_descr"] = scores_descr[pa][:]

        # generate overall score (Person A scores Person B and vice versa for each Person)
        scores_pp = []
        for pb in range(len(dfa.index)):
            overall_score = 0
            for e in list(weights_dict.keys()):
                overall_score += weights_dict[e] * scores_dict[e][pb]  # change this to list comprehension
            scores_pp.append(overall_score)
        scores_all[pa] = scores_pp
    unscaled_df_matrix = pd.DataFrame.from_dict(scores_all)

    # rescale values to a scale of 0-1
    min_max_scaler = MinMaxScaler()
    np_matrix = min_max_scaler.fit_transform(unscaled_df_matrix)
    df_matrix = pd.DataFrame(data=np_matrix)

    # setting score for oneself to 0
    for s in range(len(df_matrix)):
        df_matrix.loc[s,s] = 0

    try: #if a file or with prior rounds exists
        prior_combinations = prior_buddy_check(idx_dict, track)
        for id_1, id_2 in prior_combinations.items():
            idm_1 = idx_dict[id_1]
            idm_2 = idx_dict[id_2]
            df_matrix.loc[idm_1, idm_2] = 0
            print("checked for prior buddies!")

    except:
        pass

    return df_matrix


def prior_buddy_check(idx_dict, track):
    """
    THIS FUNCTION NEEDS TESTING!
    Retrieving prior buddy-combinations in order to set prior combinations to zero.
    This function is run in scoring_alg()
    :return: dictionary with all prior combinations by indeces
    """

    if track == "python":
        connection = dbq.connect()
        df_m = pd.read_sql_query(dbq.prior_part, connection)
        connection.close()
        # df_m = pd.read_csv("datafiles_sens/" + track + "/"+ conf_data["file_name"]["prior_matches"],  usecols=["fk_round_id", "fk_user_1_id", "fk_user_2_id"]) # aka db "matches" table
        # df_m.dropna(how="all", inplace=True)
        # print("retrieving matches for {} from .csv file. Fix db connection (or make sure .csv files are up to date)!".format(track))

    else:
        #read prior matches
        df_m = pd.read_csv("datafiles_sens/" + track + "/"+ conf_data["file_name"]["prior_matches"],  usecols=["fk_round_id", "fk_user_1_id", "fk_user_2_id"]) # aka db "matches" table
        df_m.dropna(how="all", inplace=True)

    # get lists of all participants prior this round, all participants of this round that have been in prior rounds too
    df_prev = df_m[df_m["fk_round_id"] != conf_data["round_num_id"]]
    userid_current = idx_dict.values()
    userid_past = {*list(df_prev["fk_user_1_id"]), *list(df_prev["fk_user_2_id"])}
    userid_repeating = set(list(set(userid_current) & set(userid_past)))

    # get a dictionary with all indices of prior combinations
    prior_combinations = {}
    for p_userid in userid_repeating: # for each of repeating signups get the previous buddy/buddies that have also signed up for this round
        comb1 = set(df_m.loc[(df_m['fk_user_1_id'] == p_userid), "fk_user_2_id"]) & set(userid_repeating)
        comb2 = set(df_m.loc[(df_m['fk_user_2_id'] == p_userid), "fk_user_1_id"]) & set(userid_repeating)
        past_buddies = {*list(comb1), *list(comb2)}
        for pb in past_buddies:
            prior_combinations[pb] = p_userid

    return prior_combinations
