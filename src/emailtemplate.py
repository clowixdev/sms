import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('send.address.sms@gmail.com', 'send.address.sms.psw')
server.sendmail('send.address.sms@gmail.com', 'clowix2@gmail.com', 'hello')
server.quit()

def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
    except:
        pass