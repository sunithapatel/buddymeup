import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from csv import DictReader


def send_email(name, receiver_email, buddy_name):
    sender_email = "<add WWCode sender email ID here>"
    password = "<add password here>"

    message = MIMEMultipart("alternative")
    message["Subject"] = "WWCode #buddymeup Announcement: You are buddy-upped!"
    message["Cc"] = "<add Cc email ID here>"
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    html = f""" 
        Hi {name}!<br><br>
        Have you gotten in touch with your buddy {buddy_name}? 
        If you have not heard back from your buddy, please let us know and we will rematch you this weekend.<br>
        Some of you have reached out and asked about ideas for projects and exercises, so we came up with a small list of possible topics: <br>
        - Take advantage of the slack community and resources  (insert link) and make these a weekly habit: 
        (1) #tech-discussions by @Chethana: fun little activities and brain teasers! 
        (2) #pythonic_mcqs  by @Ramya: to refresh one’s knowledge on python.
        <br>
        - AoC  (insert link)(also fun after advent): little, quite fun coding exercises (they get harder each day)!
        <br>
        - Take part in this Beginner friendly hackathon  (insert link)on February 5 and February 6!
        <br>
        - If you like pets and dirty data for data analysis - We are happy to share a small dataset on petfluencers.
        <br>
        You want to work with your buddy on your own matching algorithm or you have any other ideas related to this program? Awesome – ideas and involvement are very welcome!
        <br>
        If you have other great ideas, please don’t be shy and share your ideas and projects on our #buddymeup slack channel (insert link) – let's get that inspiration rolling!
        <br>"""

    html += f"""
        Shermaine and the BuddyMeUp Team<br>
        WomenWhoCode Python <br>
    
    """

    # Turn these into plain/html MIMEText objects
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


csv_filename = ""

# open file in read mode
# row variable is a list that represents a row in csv
with open(csv_filename, 'r') as read_obj:
    # pass the file object to DictReader() to get the DictReader object
    csv_dict_reader = DictReader(read_obj)
    # iterate over each line as a ordered dictionary
    for row in csv_dict_reader:
        # row variable is a dictionary that represents a row in csv
        print(row)
        send_email(row['name'], row['email'], row['buddy_name'])