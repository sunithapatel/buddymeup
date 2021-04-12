"""
functions to analyze the dataset and evaluate the matched buddies
"""
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import pandas as pd
dt_today = str(dt.datetime.today().strftime("%m_%d_%Y"))


def evaluate_matches(df_matched):
    # plot_score_hist
    scores = pd.concat([df_matched['score_u1'], df_matched['score_u2']], ignore_index=True)
    sns.displot(scores, bins=len(scores), color='red', kde=False)
    plt.title('Scoring distribution', fontsize=18)
    plt.ylabel('Frequency', fontsize=16)
    # scores
    avg_sc = scores.sum() / len(df_matched)
    min_sc = scores.min()
    max_sc = scores.max()
    print("\nthe average score is: ", avg_sc)
    print("\nthe minimum score is: ", min_sc)
    print("\nthe maximum score is: ", max_sc)
    low_scored = df_matched.loc[((df_matched["score_u1"] < 0.70) | (df_matched["score_u2"] < 0.70))]
    print("manually check low scored matches:", low_scored[["email_1", "email_2"]])
    return


# def get_buddies(name1, df_matched):
#     name2 = df_matched.loc[df_matched["person_a"].str.contains(name1), "person_b"].iloc[0]
#     name1 = df_matched.loc[df_matched["person_a"].str.contains(name2), "person_b"].iloc[0]
#
#     buddy_match_df = data.loc[data.name.isin([name1, name2])]
#     return buddy_match_df