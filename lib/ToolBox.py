import requests


def int_all(x):
    if x == '':
        return 0
    else:
        return int(x)


# class Mail:
#     def __init__(self):


def send_simple_message(to, subject='CanadaBizTransfer', body='', html='', ):
    from BizTransfer import app
    MAIL_API_KEY = app.config['MAIL_API_KEY']
    return requests.post(
        "https://api.mailgun.net/v3/canadabiztransfer.ca/messages",
        auth=("api", MAIL_API_KEY),
        data={"from": "CanadaBizTransfer <info@canadabiztransfer.ca>",
              "to": [to],
              "subject": subject,
              "text": body,
              "html": html,
              "o:tag": ["Accounts management"]})
