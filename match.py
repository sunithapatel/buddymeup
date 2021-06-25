"""
•	Function for finding the optimal combination within the scoring matrix
source for starting point: https://towardsdatascience.com/how-to-match-two-people-with-python-7583b51ff3f9
"""
from pulp import *
import pandas as pd
import datetime as dt
import db_queries as dbq

track = "python"

with open('config.json') as config_file:
    conf_data = json.load(config_file)

dt_today = str(dt.datetime.today().strftime("%m_%d_%Y"))

def save_matches(df_matched, track=track):
    if track == "python":
        # Connecting to the database
        matches_db = df_matched[['id_user_1', 'id_user_2', 'score_u1', 'score_u2']]
        matches_db.columns = ['fk_user_1_id', 'fk_user_2_id', 'algo_score_u1', 'algo_score_u2']
        matches_db["fk_round_id"] = conf_data["round_num_id"]
        save = "db"
        conn = dbq.connect()
        dbq.m_single_insert(conn, matches_db)
    else:
        save = ".csv"
        to_path = conf_data["filepath"][track] + str(conf_data["dates"]["round_num"]) + "/"+ dt_today + conf_data["file_name"]["buddy_results"]
        df_matched.to_csv(to_path, sep=',', decimal=".", encoding='utf-8', index=False, header=True)
    return print("saved {} to {}".format(track, save))


def pair_participants(data, df_matrix, email_ids, idx_dict):
    """
    Function for finding the optimal combination within the scoring matrix
    retrieved from this article:
    https://towardsdatascience.com/how-to-match-two-people-with-python-7583b51ff3f9
    :return:
    """
    df_matrix_og = df_matrix.copy()

    if len(df_matrix) % 2 != 0:
        even = False
        df_matrix = df_matrix.iloc[:-1,:-1]

    else:
        even = True

    prob = LpProblem("MatchingBuddies", LpMaximize)
    m_a = df_matrix.to_numpy()

    particip = range(len(df_matrix.index))

    # Variables: create y, a decision variable to determine whether or not to match employee i with employee j (1 if paired, 0 otherwise)
    y = LpVariable.dicts("pair", [(i, j) for i in particip for j in particip], cat='Binary')

    # Objective: Maximize the preference scores between participant i and j
    prob += lpSum([(m_a[i][j] + m_a[j][i]) * y[(i, j)] for i in particip for j in particip])

    # Constraints
    for i in particip:
        prob += lpSum(y[(i, j)] for j in particip) <= 1 # participant i is paired with no more than 1 participant j
        prob += lpSum(y[(j, i)] for j in particip) <= 1 # participant j is paired with no more than 1 participant i
        prob += lpSum(y[(i, j)] for j in particip) + lpSum(y[(j, i)] for j in particip) <= 1 # pairing between participant i and j means also pairing between participant j and i
    prob += lpSum(y[(i, j)] for i in particip for j in particip) == len(df_matrix)/2 # there is a total of x (tbd) pairs
    prob.solve()
    print("Finish matching!\n")

    email1 = []#emails and names are added in case df_matched will be used as basis for email notifications (can change later)
    email2 = []
    name1 = []
    name2 = []
    slname1 = []
    slname2 = []
    obj1 = []
    obj2 = []
    pers1 = []
    pers2 = []
    user_ids = pd.Series(idx_dict)
    ids_1 = []
    ids_2 = []
    u1_score_on_u2 = []
    u2_score_on_u1 = []
    overall_score = []
    for i in particip:
        for j in particip:
            if y[(i, j)].varValue == 1:
                print('{} and {} with preference score {} and {}. Total score: {}'
                      .format(email_ids[i], email_ids[j], m_a[i, j], m_a[j, i], m_a[i, j] + m_a[j, i]))

                email1.append(email_ids[i])
                email2.append(email_ids[j])
                name1.append(data["name"][i])
                name2.append(data["name"][j])
                slname1.append(data["slack_name"][i])
                slname2.append(data["slack_name"][j])
                obj1.append(data["objectives"][i])
                obj2.append(data["objectives"][j])
                pers1.append(data["personal_descr"][i])
                pers2.append(data["personal_descr"][j])

                ids_1.append(user_ids[i])
                ids_2.append(user_ids[j])
                u1_score_on_u2.append(m_a[i, j])
                u2_score_on_u1.append(m_a[j, i])
                overall_score.append(m_a[i, j] + m_a[j, i])

    df_matched = pd.DataFrame()
    df_matched["email_1"] = email1
    df_matched["email_2"] = email2
    df_matched["name1"] = name1
    df_matched["name2"] = name2
    df_matched["slname1"] = slname1
    df_matched["slname2"] = slname2
    df_matched["objectives_1"] = obj1
    df_matched["objectives_2"] = obj2
    df_matched["personal_descr_1"] = pers1
    df_matched["personal_descr_2"] = pers2

    df_matched["id_user_1"] = ids_1
    df_matched["id_user_2"] = ids_2
    df_matched["score_u1"] = u1_score_on_u2
    df_matched["score_u2"] = u2_score_on_u1
    df_matched["overall_score"] = overall_score

    if even == False:
        print("number of participants was uneven! after removing: ", email_ids.iloc[-1], ", number of participants is", len(df_matrix))
        df_matched = leftover_match(df_matched, df_matrix_og, data, idx_dict, email_ids)
    else:
        print("number of participants was even! No double buddies")

    df_matched["round"] = conf_data["dates"]["round_num"]
    return df_matched



def leftover_match(df_matched, df_matrix_og, data, idx_dict, email_ids):
    """
    If the number of signups is not even, the last person has not been matched in pair_participants().
    Here: this person (p1) is matched by
    1) looking at who p1 scores highest, and
    2) if this person (p2) has indicated to be fine with more than 1 buddy.
    :return: df_matched with additional row of the leftover user and the matched user
    """
    scores = df_matrix_og.tail(1)#get p1´s scores on everyone
    # get bidx (col-name) associated with highest score (df_matrix)
    score_u1 = scores.max(axis=1).values[0]#p1 highest score given
    nid_user_2 = scores.idxmax(axis=1).values[0] #p2 associated with the highest score (this is NOT the real user_id)
    id_user_2 = idx_dict[nid_user_2]#this is the real user_id

    # loop through max-scores given by p1 until a potential buddy has indicated "sure!" for more than one buddy
    while data.iloc[nid_user_2,:]["amount_buddies"] != "sure!":
        scores.drop(nid_user_2, axis=1, inplace=True)
        score_u1 = scores.max(axis=1).values[0]
        nid_user_2 = scores.idxmax(axis=1).values[0]
        id_user_2 = idx_dict[nid_user_2]

    # for the identified buddy get required information to create row for df_matched
    nid_user_1 = df_matrix_og.tail(1).index[0]
    id_user_1 = idx_dict[nid_user_1]
    email1 = email_ids.iloc[-1]
    email2 = email_ids.iloc[nid_user_2]
    score_u2 = df_matrix_og.loc[nid_user_2, nid_user_1]
    overall_score = score_u1+score_u2

    name1 = data["name"][nid_user_1]
    name2 = data["name"][nid_user_2]

    slname1 = data["slack_name"][nid_user_1]
    slname2 = data["slack_name"][nid_user_2]
    obj1 = data["objectives"][nid_user_1]
    obj2 = data["objectives"][nid_user_2]
    pers1 = data["personal_descr"][nid_user_1]
    pers2 = data["personal_descr"][nid_user_2]

    df2 = pd.DataFrame([[email1, email2, name1, name2, slname1, slname2, obj1, obj2, pers1, pers2, id_user_1, id_user_2, score_u1, score_u2, overall_score]], columns=df_matched.columns)
    df_matched_compl = df_matched.append(df2)
    return df_matched_compl


def csv_announcement_email(df_matched):
    """
    This function returns the df_matched in the format that can be used for the email messaging:
    Announcing buddies to the participants. Use of the email template email_responses.py.
    """
    df_email_og = df_matched.copy()
    df_email_og.drop(["id_user_1", "id_user_2", "score_u1", "score_u2", "overall_score", "round"], axis=1, inplace=True)
    df_email_og.columns = ["email_2", "email_1", "name2", "name1", "slname2", "slname1", "objectives_2", "objectives_1", "personal_descr_2", "personal_descr_1"]
    df_email = df_email_og.append(df_matched)
    df_email.to_csv(conf_data["filepath"][track] + str(conf_data["round_num"]) + "/" + dt_today + "email.csv", sep=',', decimal=".", encoding='utf-8', index=False, header=True)
    return df_email