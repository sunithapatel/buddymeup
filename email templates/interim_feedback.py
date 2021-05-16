import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from csv import DictReader


def send_email(name, receiver_email):
    sender_email = "<enter email ID>"
    password = "<password>"

    message = MIMEMultipart("alternative")
    message["Subject"] = "WWCode #buddymeup Interim Feedback"
    message["Cc"] = "<enter CC email ID>"
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    html = f""" 
        Hi {name}, <br><br>
        Congratulations! You made it halfway through this round of BuddyMeUp!<br> 
        We hope you are having fun coding with your buddy and stepping up your python skills.<br>
        Please help us improve by completing this feedback form!<br>
        <br>We promise it won’t take more than <b>2 minutes</b> of your time.<br>
        <br>
        <a href='https://forms.gle/Njg9RrpRxFyc8yVW9'>Interim feedback form</a>
        <br><br>
        We look forward to hearing about your experience so far😊<br>
        <br>"""

    html += f"""
        Shermaine and the BuddyMeUp Team<br>
        Happy Coding!<br><br>
        WomenWhoCode Python<br>
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
        send_email(row['name'], row['email'])