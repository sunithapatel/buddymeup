import streamlit as st
import os
import json
from pathlib import Path
import base64
from app_load_css import local_css
import app_explore_data
import app_signup_form

with open('config.json') as config_file:
    conf_data = json.load(config_file)

def get_config_secrets(secret_key):
    if secret_key in os.environ:
        return os.environ[secret_key]
    else:
        with open('config_secrets.json') as config_secrets_file:
            config_secrets = json.load(config_secrets_file)
            return config_secrets[secret_key]


# Convert image to bytes to pass to <img> HTML element
# as browser cannot access static content from folders.
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

# Below are images used on the app

wwc_python_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo logo-wwc-python'>".format(
    img_to_bytes("assets/images/wwc_python_logo.png")
)
phone_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/phone_logo.png")
)
diary_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/diary_logo.png")
)
github_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/github_logo.png")
)
celebrate_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/celebrate_logo.jpg")
)
weightlift_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/weightlift_logo.png")
)
data_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/data_logo.png")
)
webapp_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/webapp_logo.png")
)
clock_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/clock_logo.jpg")
)
jigsaw_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo logo-jigsaw'>".format(
    img_to_bytes("assets/images/jigsaw_logo.png")
)
brick_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/brick_logo.png")
)
clap_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo logo-clap'>".format(
    img_to_bytes("assets/images/clap_logo.png")
)
tools_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo logo-clap'>".format(
    img_to_bytes("assets/images/tools_logo.png")
)
avo_logo_html = "<img src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/avo_logo.jpg")
)
map_img_html = "<img src='data:image/png;base64,{}' class='img-fluid resource-img'>".format(
    img_to_bytes("assets/images/map.jpg")
)
schema_img_html = "<img src='data:image/png;base64,{}' class='img-fluid resource-img'>".format(
    img_to_bytes("assets/images/schema.png")
)
avo_rachel_img_html = "<img src='data:image/png;base64,{}' class='img-fluid resource-img'>".format(
    img_to_bytes("assets/images/avocados_rachel.jpg")
)
avo_isa_img_html = "<img src='data:image/png;base64,{}' class='img-fluid resource-img'>".format(
    img_to_bytes("assets/images/avocado_isa.jpg")
)
emoji_sad_slide_html = "<img id='emoji-rotate' src='data:image/png;base64,{}' class='img-fluid logo'>".format(
    img_to_bytes("assets/images/emoji_sad.png")
)


def make_pages():
  # Register pages
    pages = {
        "What is BuddyMeUp?": page_about,
        "Data in pictures": page_explore,
        "Resources": page_resources,
        "Sign me up, buddy!": page_sign_up
    }
    local_css("app_style.css")  # apply custom styles
    st.sidebar.title("Navigation")
    # Radio buttons for selecting page
    page = st.sidebar.radio("Go to", tuple(pages.keys()))
    # Display the selected page
    pages[page]()

# Intro page
def page_about():
    st.markdown(f"""
        <h1 style='font-size: 1.5em; text-align: center'>
            Welcome to the BuddyMeUp Program!
        </h1>
        <h3 style='text-align: center'>👷‍♀️👩‍👧‍👧👩‍💻</h3>
        <h3 style='text-align: center'>
            Virtual match-making... 
            <br>
            for WomenWhoCode Pythonistas.
        </h3>
        <div style='display: flex; justify-content: center'>
            <div class='wwc-logo-container'>
                {wwc_python_logo_html}
            </div>
        </div>
        <p>
            We will partner you up with one (or two!) python enthusiast(s) based on your respective interests and preferences. You will be able to:
            <ul>
                <li>work on your own coding projects 📊</li>
                <li>practice together on coding exercises 💻</li>
                <li>vent over your latest seemingly unsolvable coding problem 😤</li>
                <li>or just meet up virtually on a regular basis to discuss your coding journey over a coffee ☕ or even cocktail 🍸!</li>
            </ul>
        </p>
        <div class="announce">
            <p style='text-align: center'>
                Next round starts {conf_data['dates']['start_date_html']}. 
            </p>
            <p style='text-align: center; margin-bottom: 0'>
                Sign-ups open <strong>{conf_data['dates']['signup_date_html']}</strong>. 🎉
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.sidebar.title("About")
    st.sidebar.info("This app is maintained by Isabella Hoesch (GER) and Rachel M (NZ) who buddied up to build something fun together. "
                    "A small team of amazing volunteers supports us behind the scenes additionally to make this initiative work!")

# Page for exploring data
def page_explore():
    st.markdown("<h2>🎨 BuddyMeUp in Pictures 🖌</h2>", unsafe_allow_html=True)
    data_df = app_explore_data.load_data()
    app_explore_data.sidebar_explorer(data_df)


# Page for ideas and resources
def page_resources():
    select_resource = st.sidebar.radio("Select:", (
                        "Suggested workflow",
                        "Ideas and inspiration",
                        "Case study: BuddyMeUp project"))
    if select_resource == "Suggested workflow":
        page_workflow()
    elif select_resource == "Ideas and inspiration":
        page_ideas()
    elif select_resource == "Case study: BuddyMeUp project":
        page_buddymeup()

def page_workflow():
    st.header("👩🏿‍🤝‍👩🏻 **You have been matched with a buddy... now what?**")
    st.markdown(f"""
        <ol>
            <div class='list-item-container-big'>
                <li><strong>Set-up</strong>:
                    <ul>
                        <div class='list-item-logo-container'>
                            <div class='list-item-container'>
                                <li>Initiate contact with your buddy using provided contact info;</li>
                                <li>Set up an introductory meeting to get to know each other a bit;</li>
                                <li>Discuss what you would both like to have achieved by the end of this round (10 weeks);</li>
                            </div>
                            <div class='list-logo-container' style='padding: 10px'>
                                {phone_logo_html}
                            </div>
                        </div>
                                <li>Choose an activity/project that would help meet your goals;</li>
                                <li>Decide on how frequently you would like to meet up and 
                                    try to stick to the schedule as much as possible.</li>
                    </ul>
                </li>
            </div>
            <div class='list-item-container-big'>
                <li><strong>Working together</strong>:
                    <ul>
                        <li><span class='highlight-topic highlight-tip'>TOP TIP</span> Start a log or diary to record 
                            your plans and actions &ndash; this could be a shared document 
                            between you and your buddy;</li>
                        <div class='list-item-logo-container'>
                            <div class='list-item-container'>
                                <li>In this diary, record what you have done during the meeting, and 
                                    what your plans are between now and the next meeting 
                                    (in our experience, it is usually not enough to try and do everything within
                                    the meeting itself; a lot of the learning happens when you are reading things 
                                    up on your own, and insights have a habit of clicking in when you are 
                                    waiting for the bus 🚌 or brushing your teeth 🦷);</li>
                            </div>
                            <div class='list-logo-container' style='padding: 10px'>
                                {diary_logo_html}
                            </div>
                        </div>
                        <li>Failures are equally, sometimes more, important than successes, so 
                            absolutely do record what you tried that did not work, contrary to your
                            expectations;</li>
                        <div class='list-item-logo-container'>
                            <div class='list-item-container'>
                                <li>
                                    <span class='highlight-topic highlight-tip'>TOP TIP</span> If you are working on a project together, 
                                    set up one GitHub repository and add your buddy as a collaborator.  
                                    This way, you can stay up-to-date with your buddy's progress without needing to 
                                    <del>poke</del> directly communicate with them all the time.
                                </li>
                            </div>
                            <div class='list-logo-container' style='border-radius: 20px;'>
                                {github_logo_html}
                            </div>
                        </div>
                    </ul>
                </li>
            </div>
            <div class='list-item-container-big'>
                <li><strong>Wrap-up</strong>:
                    <div class='list-item-logo-container'>
                        <div class='list-item-container'>
                            <ul>
                                <li>Meet with your buddy to celebrate your achievements;</li>
                                <li>Fill out the feedback form that will be sent to you;</li>
                                <li>Sign up (hopefully) for another round of BuddyMeUp! 😍</li>
                            </ul>
                        </div>
                        <div class='list-logo-container list-logo-celebrate-container'>
                            {celebrate_logo_html}
                        </div>
                    </div>
                </li>
            </div>
        </ol>
        The above are just recommendations &ndash; feel free to implement working styles 
        that both you and your buddy are comfortable with.
    <p style='margin-top: 2rem'> 
        After your introductory meeting with each other, if you are already brimming with ideas 
        for what you would like to work on together, then fantastic!  Go ahead and get started! 🐣🚀
        <br>
        But if you are seeking inspiration, then click on the <strong>"Ideas and inspiration"</strong> 
        button on the navbar to the left for a few ideas that might help ignite a spark 💡.
    </p>
    """, unsafe_allow_html=True)


def page_ideas():
    st.header("💡 **Ideas and inspiration**")

    st.markdown(f"""
                Below are some Python-related resources.
                If you have suggestions for other resources that you think would be helpful for other
                buddies in this program, please [let us know]({get_config_secrets('updates_comments')})!         
                """)

    st.markdown(f"""
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    If your plan is to brew a cup of tea/coffee and meet your buddy on Zoom 
                    (or in a cafe for those who are able to meet physically) for an hour or so each week 
                    to <span class='highlight-topic'>flex your coding muscles</span>, 
                    then here are some sites that offer self-contained, short-form katas:
                </div>
                <div class='list-logo-container list-logo-weightlift-container'>
                    {weightlift_logo_html}
                </div>
            </div>
            <li><a href='https://www.codewars.com/kata/search/python?q=&'>Codewars</a></li>
            <li><a href='https://exercism.io/tracks/python'>Exercism</a></li>
            <li><a href='https://www.hackerrank.com/domains/python'>HackerRank</a></li>
            On each site, you can filter katas by difficulty levels.
        </div>
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    If you would like to tackle slightly <span class='highlight-topic'>bigger challenges</span>
                    that might take more than an hour a week to solve, then you might like:
                </div>
                <div class='list-logo-container' style='display: flex'>
                    {data_logo_html}
                </div>
            </div>
            <li><a href='https://adventofcode.com/2020/about'>Advent of Code</a>
                <p style='margin-left: 1rem'>
                    Beloved by students, professionals, competitive and hobby coders from all over the world, 
                    this is a series of 25 puzzles (well, each puzzle consists of two parts, so it's more like 
                    50 puzzles) published each year, one puzzle for each of the 25 days preceding Christmas.
                    Luckily, we are not limited to solving the puzzles within the 25-day schedule &ndash; 
                    the puzzles are available year-round for you to try at your and your buddy's leisure!
                    Each puzzle is self-contained, but we recommend that you start at Day 1 &ndash;
                    there is an overarching storyline, and the difficulty level increases gradually as well.
                </p>
            </li>
            <li><a href='https://www.kaggle.com/datasets'>Kaggle datasets</a>
                <p style='margin-left: 1rem'>
                    If you are interested in working with data and 
                    <span class='highlight-topic'>data science</span> in general, then Kaggle
                    has a variety of datasets to analyse to your heart's content.  
                </p>
            </li>
        </div>
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    For those who would like to showcase your 
                    <span class='highlight-topic'>frontend and backend</span> skills, and 
                    perhaps even combine them with data science, then working together to build a 
                    web application could be the way to go!
                </div>
                <div class='list-logo-container list-logo-webapp-container'>
                    {webapp_logo_html}
                </div>
            </div>
            <li><a href='https://www.djangoproject.com/'>Django</a>
                <p style='margin-left: 1rem'>
                    A complete web application framework on which
                    sites such as Instagram, YouTube, and Pinterest are built!  
                    We recommend that you be comfortable with Python before building 
                    your app with Django; that said, 
                    <a href='https://tutorial.djangogirls.org/en/'>Django Girls</a>
                    have a very accessible introduction to the topic.
                </p>
            </li>
            <li><a href='https://flask.palletsprojects.com/'>Flask</a>
                <p style='margin-left: 1rem'>
                    A more light-weight web application framework than Django.
                    The site contains a tutorial on how to create your very own basic 
                    blog application!
                </p>
            </li>
            <li><a href='https://www.streamlit.io/'>streamlit</a>
                <p style='margin-left: 1rem'>
                    Less fuss than Django or Flask &ndash; you can get a basic app up and running 
                    in <a href='https://docs.streamlit.io/en/stable/'>just a few lines of code</a>!<br>
                    <div class='announce'>
                        In fact, this <span class='highlight-topic highlight-buddymeup'>BuddyMeUp</span> 
                        site that you're on right now is built with streamlit!!
                        If you need any more inspiration for your project, then know that 
                        this app itself is the result of a first-round BuddyMeUp 
                        <span style='display: inline-block'>collaboration! 🙌</span><br>
                        If you would like to read more about how this was achieved, click on the 
                        <strong>"Case study: BuddyMeUp project"</strong> button on the navbar to the left.
                    </div>
                </p>
            </li>
        </div>
        """, unsafe_allow_html=True)


def page_buddymeup():
    st.header("🧐 **Case study: BuddyMeUp project**")
    st.markdown(f"""
        This very web application is itself the result of a BuddyMeUp collaboration between 
        Isabella and Rachel during the very first round!  Here, we share an overview of our 
        journey, which we hope you may be able to take as inspiration to start your own 
        collaborative project, or perhaps just have a light-hearted chuckle at reading about 
        our sometimes bumbling (or bumpy?) learning adventure 🚴‍♀️.
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    <p><strong>A bit of history (<em>circa</em> Nov 2020)</strong></p>
                    <p> BuddyMeUp is the brainchild of Isabella, who was sitting down and drinking a 
                        relaxing cup of tea one day when she suddenly realized that she did not want to lose the edge 
                        off her coding skills.
                    </p>
                </div>
                <div class='list-logo-container list-logo-clock-container'>
                    {clock_logo_html}
                </div>
            </div>
            <p> So she put out a call on the WWCPython Slack group for like-minded 
                people who would like to be buddied up together for some regular pair-programming.
                More than a dozen people signed up for this pilot round, and Isabella personally 
                and carefully matched each pair together based on responses on the sign-up forms.  
                It was a success and everyone enjoyed their eight weeks of fun!<br>
                In particular, Isabella matched with Rachel to refine the buddy-matching process 
                in anticipation of the program going viral, which would render manual matching tedious.  
                (Spoiler: the next round of BuddyMeUp attracted nearly 80 buddies from all around 
                the world!!)
            </p>
        </div>
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    <p><strong>Buddy-matching algorithm</strong></p>
                    <p>
                        If you have filled out the BuddyMeUp sign-up form, you may have wondered why 
                        there were sooo many questions to answer.  
                        Well, we are feeding your info (in a non-creepy way) to a custom 
                        algorithm which combines linear programming using Python's 
                        <tt style='font-size: 1.1em'>PuLP</tt> library and some 
                        natural language processing (NLP) using Python's 
                        <tt style='font-size: 1.1em'>scikit-learn</tt> library, 
                        to calculate optimal matches based on your responses.
                    </p>
                </div>
                <div class='list-logo-container list-logo-jigsaw-container'>
                    {jigsaw_logo_html}
                </div>
            </div>
            <p>
                The <span class='highlight-topic highlight-keyword'>NLP</span> 
                part is used to analyse your text-based responses about your objectives and 
                the bit where you describe yourself, and measure your similarity to 
                other participants' responses (for example, based on frequencies of certain words).
            </p>
            <p>
                The <span class='highlight-topic highlight-keyword'>linear programming</span> 
                part considers how similar your stated preferences (for gender, timezone, 
                experience level, etc.) are to each of the other participants', 
                together with how similar your goals and interests are as determined by the NLP score above, 
                and assigns you a score indicating how good a match you are with each of the others.
                This score is calculated by maximizing the overall sum of scores 
                between each possible pairing.<br>
                The person with whom you scored the highest is then assigned as your buddy! 🍒
            </p>
            <p>
                Much like how Amazon recommends you stuff you never knew you needed, or 
                how Google knows what you want to search for almost before you begin typing, 
                the more information we can gather, the better a match we could find for you &ndash; 
                that is why we ask you to try to be as explicit as possible about your objectives 
                and descriptions about yourself.  (But rest assured, we cannot tell what your 
                favourite beverage or who your celebrity crush is based on the info we collect!)
            </p>
        </div>
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    <p><strong>Building a web application</strong></p>
                    <p>
                        After sorting out the matching algorithm, we thought: 
                        "How cool would it be to build a web application where buddies could sign up, 
                        and the info could be stored automatically (instead of having to download and 
                        format CSV files from Google Forms)?" <br>
                        Answer: Very cool!  No practical idea how to go about it, but very cool in theory 😎.
                    </p>
                </div>
                <div class='list-logo-container list-logo-brick-container'>
                    {brick_logo_html}
                </div>
            </div>
            <p>
                We began by looking at different Python 
                <span class='highlight-topic highlight-keyword'>web application frameworks</span> and 
                settled on <tt style="font-size: 1.1em">streamlit</tt>, which is designed for data science 
                applications and thus allowed us to focus more on the data part and less on the 
                web part.  This enabled us to have an app up and running very quickly on 
                our local machines for testing.
            </p>
            <p>
                Data from buddies is the most important part of our application.  Therefore, we spent 
                significant time designing the sign-up form in such a way to collect 
                the necessary information, yet be fun to fill in.  You will need to obtain a BuddyMeUp
                key to unlock the Python-track sign-up form, but here is a glimpse of 
                part of the form where we ask for your location data, and the map underneath your input 
                would try to pinpoint your location and 
                print out your timezone almost in real-time after you've entered the info:<br>
                <div class='resource-img-container'>
                    <figure>
                        {map_img_html}
                    </figure>
                    <figcaption class='resource-img-caption'>
                        Using a map as an auto-location-checker in the BuddyMeUp 
                        <span style='display: inline-block'>Python-track</span> sign-up form.
                    </figcaption>
                </div>
            </p>
            <p>
                Then we needed a <span class='highlight-topic highlight-keyword'>database</span> 
                to store the data securely.  We used a PostgreSQL database 
                for the backend, and started by filling all the info into one giant table.  
                Although it was simple to store the data this way, it was not efficient for retrieval.  
                Also, typically each row in the table represents a unique buddy, so we had 
                to think about the scenario when a buddy signs up for another round &ndash; 
                it would not make sense to create a duplicate row for the same person containing mostly the 
                same info (same name, email, location, etc.), but different starting dates and matched buddy.  
                We iterated through several designs before settling on using five tables to 
                store various aspects of the data:<br>
                <div class='resource-img-container'>
                    <figure>
                        {schema_img_html}
                    </figure>
                    <figcaption class='resource-img-caption'>
                        Database schema for storing buddies' data.
                    </figcpation>
                </div>
            </p>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    <p>
                        Finally, once we have tested the frontend and backend on our local machines, 
                        we were ready to <span class='highlight-topic highlight-keyword'>deploy</span> 
                        the app online!  We chose the Heroku platform 
                        because it supports Python apps built on <tt style='font-size: 1.1em'>streamlit</tt>, 
                        is very simple to set up, 
                        and (importantly) the free tier is sufficient for our needs!  
                        (Of course, there are costs for "free" things &ndash; one being that 
                        you may find the server to be a bit slow to spin up when you first
                        load the app...)
                    </p>
                </div>
                <div class='list-logo-container list-logo-clap-container'>
                    {clap_logo_html}
                </div>
            </div>
        </div>
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    <p><strong>Our toolkit</strong></p>
                    Here are the main tools we used to build the BuddyMeUp application:
                </div>
                <div class='list-logo-container list-logo-tools-container'>
                    {tools_logo_html}
                </div>
            </div>
            <ul>
                <li>Python (of course!); in particular, these libraries:
                    <ul>
                        <li><tt style="font-size: 1.1em">streamlit</tt> for the application framework</li>
                        <li><tt style="font-size: 1.1em">PuLP</tt> for solving the buddy-matching optimization problem</li>
                        <li><tt style="font-size: 1.1em">scikit-learn</tt> for analysing text responses from sign-up forms</li>
                    </ul>
                </li>
                <li>PostgreSQL for database management</li>
                <li>A dash of HTML/CSS to add a bit of style to our site</li>
                <li>GitHub for version control and code-sharing</li>
                <li>Heroku platform for web deployment</li>
            </ul>
            And that's it!  Like the "Häagen-Dazs Five" ice cream range, many good things in life 
            are made from five simple ingredients 🍧.
        </div>
        <div class='list-item-container-big'>
            <div class='list-item-logo-container'>
                <div class='list-item-container'>
                    <p><strong>Coding and... avocados?</strong></p>
                    <p>
                        Isabella and Rachel met at least weekly over several months to 
                        discuss the design and development of this project.  
                        We have both learned a lot from each other and from Stack Overflow, 
                        and are super-proud of this application.  
                        We hope that other buddies would find it both useful and fun to use.
                        But we would like to emphasize that BuddyMeUp is not just about building your 
                        coding and technical skills, it is also about building 
                        <span class="highlight-topic highlight-keyword">friendships</span> !
                    </p>
                </div>
                <div class='list-logo-container list-logo-avo-container'>
                    {avo_logo_html}
                </div>
            </div>
            <p>
                Isabella loves to go hiking in the mountains and surfing in winter(!), and 
                often shares her adventures with Rachel during their Zoom meetings.<br>
                On the other hand, Rachel loves eating avocados and then saving the seeds 
                to grow into plants, which often feature in the background of her Zoom calls.  
                This prompted Isabella to try her hand at growing one herself... with success!
                <div style="display: flex">
                    <div class='resource-img-container'>
                        <figure>
                            {avo_rachel_img_html}
                        </figure>
                        <figcaption class='resource-img-caption'>
                            Rachel's avocado plantlings collection
                        </figcaption>
                    </div>
                    <div class='resource-img-container'>
                        <figure>
                            {avo_isa_img_html}
                        </figure>
                        <figcaption class='resource-img-caption'>
                            Isabella's very first avocado seed putting down roots!
                        </figcaption>
                    </div>
                </div>
                We actually spent quite a bit of time discussing the best conditions for growing 
                avocado plants from seed, and whether our respective plants seem to be happy or not  
                (avocado seeds can be tricky sometimes &ndash; you can give them all the care 
                in the world by keeping them moist and temperature-controlled, but they could appear 
                inactive for months, until just when you've given up hope and are about to discard them, 
                they start to sprout!).
            </p>
            <p>
                Anyway, you are probably here for coding inspiration, not 
                advice about growing avocados... so go ahead and sign up for BuddyMeUp 
                and see what wonderful projects you could work on with your buddy! 🥑🥑🥑
            </p>
        </div>
    
                    
                    
    """, unsafe_allow_html=True)


# # Page for sign-up
# def page_sign_up():
#     select_track = st.sidebar.radio("Track:", (
#                         "Python",
#                         "Cloud"))
#     if select_track == "Python":
#         page_sign_up_python()
#     elif select_track == "Cloud":
#         page_sign_up_cloud()
    

def page_sign_up():
    st.title("Sign Me Up!")
    st.header("I mean, BuddyMeUp! :wink:")

    if conf_data["signup_open"] == "True":
        correct_slack_pw_py = get_config_secrets('wwc_slack_pw_py')
        st.markdown("""
                    <p style='margin-top: 30px; margin-bottom: 30px;'>
                    You can find the key in the WomenWhoCode Python slack community.
                    Having all BuddyMeUp participants join the slack community gives us a place to communicate and interact 
                    and saves us the struggle from spamming your email/junk-folder.
                    </p>
                    """, unsafe_allow_html=True)
        slack_pw_py = st.text_input("🐍 Signup key for Python", "")
        python_button = st.button("Continue to Python Signup")
        st.info(f"""🐍 Join the [Python slack community] ({get_config_secrets('wwc_py_slack_invite')}) 
                    #buddymeup channel to get the key.""")

        if slack_pw_py or python_button:
            if slack_pw_py == correct_slack_pw_py:
                participant_info = app_signup_form.signup()  # returns participant info as a dict
                if st.checkbox("I understand that my data is processed to (1) evaluate matching buddies from the pool of participants and to (2) notify me via email and slack about my buddy."):
                    if st.button("Submit"):
                        app_signup_form.save(participant_info)
            else:
                st.error(f"""Oops, that did not work. Check the #buddymeup channel in the 
                            WWCode Python Slack Community for the right key.""")
    else: # sign-up period is closed
        st.markdown(f"""
            <div class="emoji-wrapper">
                {emoji_sad_slide_html}
            </div>
                """, unsafe_allow_html=True)
        st.info(f"""Oh no! Sign-ups for BuddyMeUp has closed for the current round.
                    Stay tuned on the [Python Slack] ({get_config_secrets('wwc_py_slack_invite')})
                    #buddymeup channel to get notifications of dates for the next round!""")



