from util import *
import sys

from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
def send_mail(subject, text, from_email, rec_list, html=None):
    """
    Shortcut for sending email.
    """
    msg = EmailMultiAlternatives(subject, text, from_email, rec_list)
    if html:
        msg.attach_alternative(html, "text/html")
    if settings.DEBUG:
        print '---begin---'
        print 'To:', rec_list
        print 'Subject:', subject
        print 'Body:', text
        print '---end---'
    msg.send(fail_silently=True)


def get_subscribed_topic(request, start_num=0, last_num=20):
    data = {
            'total_topic_num': 0,
            'topics': []
        }
    try:
        topics = request.user.subscriptions.all()

        data = {
            'total_topic_num': len(topics),
            'topics': []
        }

        for topic in topics:
            data['topics'].append(topic.as_tapatalk())
    except:
        send_mail("Debugging Forum", sys.exc_info()[0], settings.DEFAULT_FROM_EMAIL, ["sander@androidworld.nl"])

    return data
