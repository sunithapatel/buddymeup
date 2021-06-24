import streamlit as st
from app_load_css import local_css
import app_db_setup as dbs
import prep as p
import db_queries as q
import numpy as np
import pandas as pd
import json
import altair as alt
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
from PIL import Image
import matplotlib.pyplot as plt


with open('config.json') as config_file:
    conf_data = json.load(config_file)

# Load the dataset
def load_data():
    connection = dbs.init_db()
    query = "SELECT * FROM users_rounds;"
    users_rounds_df = pd.read_sql_query(query, connection)
    query = "SELECT * FROM locations;"
    locations_df = pd.read_sql_query(query, connection)
    query = "SELECT * FROM rounds;"
    rounds_df = pd.read_sql_query(query, connection)

    # Merge users_rounds and locations tables to get actual location names
    users_rounds_loc_df = pd.merge(users_rounds_df, locations_df, 
                                    left_on="fk_location_id", right_on="id")
    # Merge users_rounds and rounds tables to get actual dates each user has enrolled for
    users_rounds_loc_df = pd.merge(users_rounds_loc_df, rounds_df,
                                    left_on="fk_round_id", right_on="id")
    return users_rounds_loc_df


# Sidebar for controlling data exploration
def sidebar_explorer(df):
    # st.sidebar.markdown("BuddyMeUp in Pictures")
    explore_field = st.sidebar.radio("Maps, graphs, and words", (
                                        "Buddies around the world",
                                         "Python experience",
                                         "In their own words"))
    if explore_field == "Buddies around the world":
        st.markdown("<h3><strong>Where are buddies located?</strong></h3>", unsafe_allow_html=True)
        st.map(df[["latitude", "longitude"]], zoom = 0)
        st.markdown("""
                    <p><strong>Notes:</strong></p>
                    <ul>
                        <li>For the first and second rounds, we did not require exact location info 
                            during sign-up; so for buddies who did not fill in their city or state, 
                            their location would be marked in the centre of their country on the map.  
                            For example, as seen from the map above, we have German buddies from 
                            Berlin, Munich, and... Hainich National Park?
                            All we can infer from the last one is that this buddy definitely comes from 
                            <em>somewhere</em> in Germany 🌍.</li>
                        <li>For buddies who entered no location at all, we have made the 
                            assumption that they are based in Antarctica 🧊, 
                            statistically the most likely continent given no other geographical info 😉.
                            (This way, we can also claim that buddies come from 
                            all seven continents on Earth!)</li>
                        <li>We have a good spread of buddies from across the globe's timezones.  
                            However, we would love to welcome more buddies from currently 
                            under-represented regions in South America, Africa, the Middle East, 
                            and several parts of Asia and Europe!</li>
                    </ul>
                    """, unsafe_allow_html=True)
        # st.bar_chart(df["timezone"])
    elif explore_field == "Python experience":
        option = st.selectbox(
            "Explore buddies by:",
            ("Age and experience", "Interest topic and experience", "Gender and experience")
        )
        if option == "Age and experience":
            st.markdown("""
                <h3><strong>Age distribution by experience level</strong></h3> 
                <p class="text_slider">Click on the interactive legend to filter by experience levels! 
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    👇👇👇</p><br>
                """, unsafe_allow_html=True)
            # ages grouped by experience
            age_exp_df = pd.DataFrame({
                "No experience": df[df["experience"] == "0 years, getting started"]["age"],
                "0-1 year": df[df["experience"] == "0-1 year"]["age"],
                "1-3 years": df[df["experience"] == "1-3 years"]["age"],
                "3+ years": df[df["experience"] == "3+ years"]["age"]
            })
            selection = alt.selection_multi(fields=['Experience'], bind='legend')
            age_hist = alt.Chart(age_exp_df).transform_fold(
                ["No experience", "0-1 year", "1-3 years", "3+ years"],
                as_ = ["Experience", "Age"]
            ).mark_bar(
                opacity = 0.5
            ).encode(
                alt.X("Age:Q", bin=alt.Bin(extent=[15, max(df["age"])], step=5), 
                        axis=alt.Axis(title="Age")),
                alt.Y(aggregate="count", type="quantitative", stack=None, 
                        axis=alt.Axis(title="Number of buddies")),
                alt.Color("Experience:N"),
                opacity=alt.condition(selection, alt.value(0.8), alt.value(0.05))
            ).configure_legend(
                rowPadding = 12,
                titlePadding = 10,
                labelFontSize = 12,
                titleFontSize = 12
            ).properties(
                width = 600,
                height = 450,
                background = "transparent"
            ).add_selection(
                selection
            )
            st.write(age_hist)
            st.markdown("""
                <p>You can start coding at any age!  We encourage those who are just starting out 
                on their coding journey, those who have been coding for a while, and those 
                who might be looking for a change into a career that involves coding to sign up. 
                In short, we invite anyone who loves to code or would like to start learning!</p>
                <p>BuddyMeUp works best if there are buddies from a diverse range of experiences, ages, and 
                backgrounds so that we can learn from and teach one another!</p>
                """, unsafe_allow_html=True)
        elif option == "Interest topic and experience":
            st.markdown("""
                <h3><strong>Experience level by interest topic</strong></h3>
                <p class="text_slider">Click on the interactive legend to filter by experience levels! 
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    👇👇👇</p><br>
                """, unsafe_allow_html=True)
            # interest topic grouped by experience
            df_topics = encode_topics(df)
            exp_topic_df = pd.DataFrame({
                "data science": df_topics[df_topics["data science"] == 1]["experience"],
                "machine learning": df_topics[df_topics["machine learning"] == 1]["experience"],
                "mobile": df_topics[df_topics["mobile"] == 1]["experience"],
                "backend": df_topics[df_topics["backend"] == 1]["experience"],
                "frontend": df_topics[df_topics["frontend"] == 1]["experience"]
            })
            exp_topic_grouped_df = pd.DataFrame({
                    "experience": ["No experience", "0-1 year", "1-3 years", "3+ years"],
                    "data science": [sum(exp_topic_df["data science"] == "0 years, getting started"),
                                    sum(exp_topic_df["data science"] == "0-1 year"),
                                    sum(exp_topic_df["data science"] == "1-3 years"),
                                    sum(exp_topic_df["data science"] == "3+ years")],
                    "machine learning": [sum(exp_topic_df["machine learning"] == "0 years, getting started"),
                                    sum(exp_topic_df["machine learning"] == "0-1 year"),
                                    sum(exp_topic_df["machine learning"] == "1-3 years"),
                                    sum(exp_topic_df["machine learning"] == "3+ years")],
                    "mobile": [sum(exp_topic_df["mobile"] == "0 years, getting started"),
                                    sum(exp_topic_df["mobile"] == "0-1 year"),
                                    sum(exp_topic_df["mobile"] == "1-3 years"),
                                    sum(exp_topic_df["mobile"] == "3+ years")],
                    "frontend": [sum(exp_topic_df["frontend"] == "0 years, getting started"),
                                    sum(exp_topic_df["frontend"] == "0-1 year"),
                                    sum(exp_topic_df["frontend"] == "1-3 years"),
                                    sum(exp_topic_df["frontend"] == "3+ years")],
                    "backend": [sum(exp_topic_df["backend"] == "0 years, getting started"),
                                    sum(exp_topic_df["backend"] == "0-1 year"),
                                    sum(exp_topic_df["backend"] == "1-3 years"),
                                    sum(exp_topic_df["backend"] == "3+ years")]
            })
            selection = alt.selection_multi(fields=['Interest topic'], bind='legend')
            topic_graph = alt.Chart(exp_topic_grouped_df).transform_fold(
                ["data science", "machine learning", "mobile", "backend", "frontend"],
                as_ = ["Interest topic", "Num_buddies"]
            ).mark_bar(
                opacity = 0.5
            ).encode(
                alt.X("experience:N", 
                        axis=alt.Axis(title="Experience")),
                alt.Y("Num_buddies:Q", stack=None, 
                        axis=alt.Axis(title="Number of buddies")),
                alt.Color("Interest topic:N"),
                opacity=alt.condition(selection, alt.value(0.8), alt.value(0.05))
            ).configure_legend(
                rowPadding = 12,
                titlePadding = 10,
                labelFontSize = 12,
                titleFontSize = 12
            ).properties(
                width = 600,
                height = 450,
                background = "transparent"
            ).add_selection(
                selection
            )
            st.write(topic_graph)
        elif option == "Gender and experience":
            st.markdown("""
                <h3><strong>Gender by experience level</strong></h3> 
                <p class="text_slider">Click on the interactive legend to filter by experience levels! 
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    👇👇👇</p><br>
                """, unsafe_allow_html=True)
            # gender grouped by experience
            gender_exp_df = pd.DataFrame({
                "female": df[df["gender"] == "female"]["experience"],
                "male": df[df["gender"] == "male"]["experience"],
                "non-binary": df[df["gender"] == "non-binary"]["experience"],
                "undisclosed": df[df["gender"] == "do not want to disclose"]["experience"],
            })
            gender_exp_grouped_df = pd.DataFrame({
                    "gender": ["female", "male", "non-binary", "undisclosed"],
                    "No experience": [sum(gender_exp_df["female"] == "0 years, getting started"),
                                    sum(gender_exp_df["male"] == "0 years, getting started"),
                                    sum(gender_exp_df["non-binary"] == "0 years, getting started"),
                                    sum(gender_exp_df["undisclosed"] == "0 years, getting started")],
                    "0-1 year": [sum(gender_exp_df["female"] == "0-1 year"),
                                    sum(gender_exp_df["male"] == "0-1 year"),
                                    sum(gender_exp_df["non-binary"] == "0-1 year"),
                                    sum(gender_exp_df["undisclosed"] == "0-1 year")],
                    "1-3 years": [sum(gender_exp_df["female"] == "1-3 years"),
                                    sum(gender_exp_df["male"] == "1-3 years"),
                                    sum(gender_exp_df["non-binary"] == "1-3 years"),
                                    sum(gender_exp_df["undisclosed"] == "1-3 years")],
                    "3+ years": [sum(gender_exp_df["female"] == "3+ years"),
                                    sum(gender_exp_df["male"] == "3+ years"),
                                    sum(gender_exp_df["non-binary"] == "3+ years"),
                                    sum(gender_exp_df["undisclosed"] == "3+ years")]
            })
            selection = alt.selection_multi(fields=['Experience'], bind='legend')
            gender_graph = alt.Chart(gender_exp_grouped_df).transform_fold(
                ["No experience", "0-1 year", "1-3 years", "3+ years"],
                as_ = ["Experience", "Num_buddies"]
            ).mark_bar(
                opacity = 0.5
            ).encode(
                alt.X("gender:N", axis=alt.Axis(title="Gender")),
                alt.Y("Num_buddies:Q", stack=None, 
                        axis=alt.Axis(title="Number of buddies")),
                alt.Color("Experience:N"),
                opacity=alt.condition(selection, alt.value(0.8), alt.value(0.05))
            ).configure_legend(
                rowPadding = 12,
                titlePadding = 10,
                labelFontSize = 12,
                titleFontSize = 12
            ).properties(
                width = 600,
                height = 450,
                background = "transparent"
            ).add_selection(
                selection
            )
            st.write(gender_graph)
            st.markdown("""
                <p><strong>Notes:</strong></p>
                <ul>
                    <li>We did not have gender options for "non-binary" or "undisclosed" 
                    in the sign-up form for the first two rounds of BuddyMeUp.  They have been 
                    made as options now.</li>
                    <li>Women Who Code and BuddyMeUp aim to provide a safe and 
                    supportive environment to work in for those who identify as female.  However, we 
                    welcome and encourage anyone <strong>regardless of gender identity</strong> to join, 
                    if they feel that they could benefit from or contribute to the mission.</li>
                </ul>
                """, unsafe_allow_html=True)
    elif explore_field == "In their own words":
        st.markdown("""
                    <h3><strong>What are some words buddies used to describe their goals 
                    and themselves?</strong></h3>
                    """, unsafe_allow_html=True)
        generate_wordcloud(df, "objectives")
        generate_wordcloud(df, "personal_descr")


def generate_wordcloud(df, column):
    stopwords = set(STOPWORDS)
    stopwords.add("will")
    stopwords.add("want")
    stopwords.add("useless")

    if column == "objectives":
        st.subheader("Buddies' coding objectives:")
        mask = np.array(Image.open("assets/images/python_mask.png"))
        wordcloud = WordCloud(width=100, height=100, mode='RGB', background_color='#f9f9f9', max_font_size=None, min_font_size=8,
                          max_words=1000, stopwords=stopwords,  
                          mask=mask, contour_width=0.5, random_state=1).generate(" ".join([i for i in df[column]]))
        image_colors = ImageColorGenerator(mask)
        wordcloud.recolor(color_func=image_colors)
    elif column == "personal_descr":
        st.subheader("There is more to buddies than code:")
        mask = np.array(Image.open("assets/images/ice-cream.png"))
        stopwords.add("love")
        stopwords.add("enjoy")
        wordcloud = WordCloud(width=512, height=512, mode='RGB', background_color='#f9f9f9', max_font_size=128, min_font_size=8,
                          max_words=200, stopwords=stopwords, colormap='Dark2',  
                          mask=mask, contour_width=1, random_state=1).generate(" ".join([i for i in df[column]]))

    st.image(wordcloud.to_array(), width=600)


def encode_topics(df):
    """
    Creates a column for each interest topic (data science, machine learning, backend, etc.)
    and encodes each buddy's interest in each topic with 0 or 1
    :return: new df with original topic column dropped, and several new columns - one for each topic
    """
    # string to lowercase
    df = df.apply(lambda x: x.astype(str).str.lower())

    for topic in conf_data["variables"]["topics"]:
        df[topic] = df["topic"].str.contains(topic).astype(int)
    df_formatted = df.drop(["topic"], axis=1)

    return df_formatted
