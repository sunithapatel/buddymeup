import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from csv import DictReader


def send_email(receiver_email):
    sender_email = "<enter email ID>"
    password = "<password>"

    message = MIMEMultipart("alternative")
    message["Subject"] = "WWCode #buddymeup Interim Feedback"
    message["Cc"] = "<enter CC email ID>"
    message["From"] = sender_email
    message["To"] = receiver_email
    # Create the plain-text and HTML version of your message
    html = f""" 
        Hello python coder!! <br><br>
        Congratulations on successfully completing this #buddymeup round 3! <br>
        I hope you had fun participating and working with your buddy. <br><br>

        We have a 2-minutes final feedback form to help us improve your experience going forward. 
        <br>Also, feel free to share what you worked on with your buddy in the form.<br><br>

        <a href='https://forms.gle/kMqGamsr8TvRv5ai7'>Final feedback form</a><br><br>

        Excitingly, we will be starting the sign-ups for #buddymeup round 4 ...!!<br>
        Some important announcements about the next round:<br><br> 

        We look forward to hearing about your experience so far!<br><br>

        Thank you so much for your time! Feel free to contact us if you need any help :)<br><br>
    """
    html += f"""
        Regards,<br>
        Shermaine and the BuddyMeUp Team<br>
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
        send_email(row['email'])