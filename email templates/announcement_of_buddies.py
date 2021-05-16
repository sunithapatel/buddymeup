import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from csv import DictReader


def send_email(name, receiver_email, slack_name, buddy_name, buddy_slack_name, buddy_objectives, buddy_personal_descr, buddy_email):
    sender_email = "<add WWCode sender email ID here>"
    password = "<add password here>"

    message = MIMEMultipart("alternative")
    message["Subject"] = "WWCode #buddymeup Announcement: You are buddy-upped!"
    message["Cc"] = "<add Cc email ID here>"
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    html = f""" 
        Hi {name}, <br><br>
        WomenWhoCodePython is happy to announce your <b>#buddymeup match!</b><br> 
        Your buddy for the next 10 weeks is <b>{buddy_name}</b> <br>
        <br>"""

    if buddy_slack_name != 'nan' and slack_name != 'nan':
        html += f"""Please reach out to your match via  
        <a href='https://join.slack.com/t/wwcodepython/shared_invite/zt-kp9jr2ht-zGyDmQD7YxICdVvlpfhGBw'>slack</a> 
        (slack name: {buddy_slack_name}) and introduce yourself.<br><br>"""
    else:
        html += f"""Please reach out to your match via email ({buddy_email}) and introduce yourself. <br><br>"""

    html += f"""
        <b>About your buddy:</b> <br>
        \"{buddy_personal_descr}\" <br>
         <br>
        <b>Her/his coding objectives are:</b><br>
        \"{buddy_objectives}\"<br>
         <br>
        <b>Please note</b>: your buddy is NOT your mentor! Your buddy is looking forward to your support just as much as you are to his/her support. 
        The secret formula for getting the most out of this program: be proactive and take initiative - we promise, it will come back to you!:)
        <br><br>
        We recommend to set up a chat with your buddy this week to:<br>
        (1) Introduce yourself and get to know each other.<br>
        (2) Share your coding experiences and motivation.<br>
        (3) Discuss coding objectives and projects you are working on or would like to work on together.<br>
        (4) Agree on your “buddy-style” (how frequent you will meet, structure, content, time, ….)<br>
        (5) Find a date and time for your next chat.<br>
        (6) Define your goals for the upcoming 10 weeks<br>
        <br>
        After 10 weeks we will be having another round of #buddymeup for you to connect with and learn from another buddy.<br>
        <br>
        Don’t hesitate to reply to this email if you are unable to connect with your buddy or have any other questions - we are happy to help!<br>
        <br>        
        Happy Coding! <br>
        Happy connecting! <br>
        <br>
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
        send_email(row['name'], row['email'], row['slack_name'], row['buddy_name'], row['buddy_slack_name'],
                   row['buddy_objectives'], row['buddy_personal_descr'], row['buddy_email'])