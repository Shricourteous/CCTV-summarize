import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from plyer import notification


def mailAlert(imagelocation, timing):
    email = "shribalaji1243@gmail.com"
    receiver_email = "mubaraqmuba1@gmail.com"
    subject = "Alert!"
    message = f"New person has been detected {timing}"

    # Gmail SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Login credentials
    smtp_username = email
    smtp_password = "ogjpzcjkfowoodke"  # Your Gmail password or app password

    # Create a multipart message container
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the text message
    msg.attach(MIMEText(message, 'plain'))

    # Attach the image
    with open(imagelocation, 'rb') as f:
        img = MIMEImage(f.read())

    img.add_header('Content-Disposition', 'attachment', filename=imagelocation)
    msg.attach(img)

    try:
        # Establish a secure connection with Gmail's SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to your Gmail account
        server.login(smtp_username, smtp_password)

        # Send email
        server.sendmail(email, receiver_email, msg.as_string())
        notification.notify(title="Mail Sent" ,message= "Alert mail has been sent to centralised system successfully." ,timeout= 5)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        server.quit()
