
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

def set_weights(dfa):
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
    return weights_dict, topics_list


def score_text_on_similarity(text_responses):
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

def score_gender(dfa, pa, pb, gender_scores):
    # preference matters
    if dfa["gender_pref"].iloc[pa] == dfa["gender"].iloc[pb] and dfa["gender"].iloc[pb] != 3:
        gender_score = 1
    else:
        gender_score = 0.5
    gender_scores.append(gender_score)
    return gender_scores


def score_timezone(dfa, pa, pb, tz_scores):
    # preference matters
    # todo: alter scoring for timezone! "tz 12 is followed by tz 1"
    tz_score_not_norm = abs(int(dfa["timezone"].iloc[pa]) - int(dfa["timezone"].iloc[pb]))
    max = 26  # (dfa["timezone"].max()) - (dfa["timezone"].min()) # total of 26 different timezones
    min = 0
    if dfa["timezone_pref"].iloc[pa] == 0:  # if person a indicated preference for same timezone
        tz_score = round(1 - (tz_score_not_norm - min) / (max - min), 2)
    elif dfa["timezone_pref"].iloc[pa] == 1:  # if person indicated a preference for opposite timezones
        tz_score = round((tz_score_not_norm - min) / (max - min), 2)
    else:  # dfa["timezone_pref"].iloc[pa] == 2:  # if person indicated no preference for any timezone
        tz_score = 0.5
    tz_scores.append(tz_score)
    return tz_scores

def score_experience(dfa, pa, pb, experience_scores):
    # mentor_choice (mentor or buddy) --> experience matters
    experience_score_not_norm = abs(int(dfa["experience"].iloc[pa]) - int(dfa["experience"].iloc[pb]))
    max = (dfa["experience"].max()) - (dfa["experience"].min())
    min = 0

    if dfa["mentor_choice"].iloc[
        pa] == 2:  # if person indicated preference for buddy/mentor (2 = No. I prefer to be matched with someone on the same level or with more experience.)
        experience_score = round(1 - (experience_score_not_norm - min) / (max - min), 2)
    elif dfa["mentor_choice"].iloc[pa] == 1:  # if person indicated preference for mentee (1 = Yes. I would mentpr)
        experience_score = round((experience_score_not_norm - min) / (max - min), 2)
    else:  # if person indicated no preference for experience level (mentee or buddy)
        experience_score = 0.5
    experience_scores.append(experience_score)
    return experience_scores


def score_ordinals_on_distance(item, dfa, pa, pb, item_scores):
    # ordinal variables where least distance matters
    item_score_not_norm = abs(int(dfa[item].iloc[pa]) - int(dfa[item].iloc[pb]))
    max = (dfa[item].max()) - (dfa[item].min())
    min = 0
    item_score = round(1 - (item_score_not_norm - min) / (max - min), 2)  # rescale values 0-1
    item_scores.append(item_score)
    return item_scores

def score_binaries_on_equality(item, dfa, pa, pb, item_scores):
    # binary items where similarity matters / items must match
    if dfa[item].iloc[pa] == dfa[item].iloc[pb]:
        item_score = 1
    else:
        item_score = 0
    item_scores.append(item_score)
    return item_scores


def score_item_in_list(scores_dict, attr_list, dfa, pa, type="binary"):
    for item in attr_list:
        item_scores = []
        for pb in range(len(dfa.index)):
            if type == "binary":
                item_scores = score_binaries_on_equality(item, dfa, pa, pb, item_scores)
            elif type == "ordinal":
                item_scores = score_ordinals_on_distance(item, dfa, pa, pb, item_scores)
        scores_dict[item] = item_scores
    return scores_dict



