import prep as p
import score as s
import match as m
import analyze_evaluate as ae



track = "python"

print("before __name__ guard")
if __name__ == '__main__':
    print("importing data")
    data, email_ids, fdf, idx_dict = p.prep_data(track=track)
    print("scoring participants")
    df_matrix = s.scoring_alg(fdf, data, idx_dict, track=track)
    print("matching participants")
    df_matched = m.pair_participants(data, df_matrix, email_ids, idx_dict)
    print("analyze matches")
    ae.evaluate_matches(df_matched)
    print("saving matches to db or .csv")
    #m.save_matches(df_matched, track=track)
    print("create and save .csv for email sending")
    m.csv_announcement_email(df_matched)

print("after __name__ guard")

