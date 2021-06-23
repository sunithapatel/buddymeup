"""
Function for scoring algorithm
•	Scoring numerical/categorical attributes (closed questions in survey)
•	Scoring text attributes (open-ended questions in survey)
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import json
import db_queries as dbq
import attribute_scoring as ats

track = "python"

with open('config.json') as config_file:
    conf_data = json.load(config_file)

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
    weights_dict, topics_list = ats.set_weights(dfa) # setting weights per item

    scores_all = {}
    # N x N array of similarity scores for text-based responses
    scores_objectives = ats.score_text_on_similarity(data["objectives"])
    scores_descr = ats.score_text_on_similarity(data["personal_descr"])

    for pa in range(len(dfa.index)):  # for pa = person a in df
        scores_dict = {}
        # variables where preference matters: gender, timezone, mentor_choice/experience
        # todo: add this to ats.score_item_in_list function
        gender_scores = []
        tz_scores = []
        experience_scores = []
        for pb in range(len(dfa.index)):  # pb = person b
            gender_scores = ats.score_gender(dfa, pa, pb, gender_scores)
            tz_scores = ats.score_timezone(dfa, pa, pb, tz_scores)
            experience_scores = ats.score_experience(dfa, pa, pb, experience_scores)
        scores_dict["gender"] = gender_scores
        scores_dict["timezone"] = tz_scores
        scores_dict["experience"] = experience_scores

        # binary items where similarity matters / items must match
        # ordinal variables where least distance matters
        list_bin = ["relation_pref"]
        list_bin.extend(topics_list)
        list_ord = ["age", "freq_pref"]
        scores_dict = ats.score_item_in_list(scores_dict, list_bin, dfa, pa, type="binary")
        scores_dict = ats.score_item_in_list(scores_dict, list_ord, dfa, pa, type="ordinal")

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
