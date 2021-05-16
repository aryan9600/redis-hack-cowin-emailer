from typing import List
import requests
import os
def send_email(emails: List[str], subject: str, body: str):
    # Sends a request to my custom mail server. The server sends the actual email.
    response = requests.post(
        url=os.environ['MAIL_URL'],
        headers={"Authorization": os.environ['MAIL_TOKEN']},
        json={
            'to_mails': emails,
            'from_mail': 'contact@ieeevit.org',
            'subject': subject,
            'body': body
        }
    )
    if response.status_code == 200:
        return True
    return False
