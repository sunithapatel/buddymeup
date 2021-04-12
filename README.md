# BuddyMeUp: a pair-programming initiative 
BuddyMeUp is an initiative started by WomenWhoCode members who buddied up to connect like-minded wo:men throughout the globe for social coding. 
The purpose of this repo is to share what´s behind the the initiative "BuddyMeUp" and to exemplify what buddies could be working on together.
Pull requests are very welcome!

# Project-code 
This repo contains the code for the BuddyMeUp web app, for users to browse statistics about the program, 
find resources for pair-programming, and sign up for the BuddyMeUp program.

It also contains the matching algorithm used to try to optimally match participants into pairs based on 
their preferences.

Check it out [here](http://www.buddymeup.net)!


## Application framework and libraries
- Built with Python's `streamlit` application framework
- Matching algorithm uses [PuLP](https://coin-or.github.io/pulp/) and [scikit-learn](https://scikit-learn.org/stable/) libraries

## Project structure
- all scripts related to running the app are named `app_*.py`; start server with `streamlit run app.py`
(after installing [streamlit](https://docs.streamlit.io/en/stable/troubleshooting/clean-install.html))
- the scripts related to running the matching algorithm are called with `python main.py`

## Contributions
- all scripts
