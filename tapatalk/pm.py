import traceback
from tapatalk.dispatcher import send_mail
from util import *
from django_messages.models import Message
import datetime


def get_box_info(request):
    boxes = {
        'inbox': Message.objects.inbox_for(request.user.id),
        'sent': Message.objects.outbox_for(request.user.id),
        'trash': Message.objects.trash_for(request.user.id),
    }

    data = {
        'result': True,
        'message_room_count': 12345,
        'list': [],
    }

    for name, box in boxes.items():

        unread = 0
        for msg in box:
            if msg.read_at == None:
                unread += 1

        num = 0
        if name == 'inbox':
            num = 0
        elif name == 'sent':
            num = 1
        else:
            num = 2


        item = {
            'box_id': str(num),
            'box_name': xmlrpclib.Binary(name),
            'msg_count': len(box),
            'unread_count': unread,
            'box_type': name.upper()
        }
        
        data['list'].append(item)
    return data


# TODO: add pager
def get_box(request, box_id='', start_num=0, end_num=0):
    box = []
    if box_id == '0':
        box = Message.objects.inbox_for(request.user.id)
    elif box_id == '1':
        box = Message.objects.outbox_for(request.user.id)
    else:
        box = Message.objects.inbox_for(request.user.id)

    unread = 0
    for msg in box:
        if msg.read_at == None:
            unread += 1

    total_message_count = len(box)
    if (total_message_count == None):
        total_message_count = 0

    data = {
        'result': True,
        'total_message_count': int(total_message_count),
        'total_unread_count': int(unread),
        'list': [],
    }

    for msg in box:
        m = msg.as_tapatalk()
        m.pop("text_body")
        data['list'].append(m)

    return data


def get_message(request, message_id=None, box_id='', return_html=False):
    try:
        msg = Message.objects.get(recipient=request.user.id, pk=message_id)
    except:
        msg = Message.objects.get(sender=request.user.id, pk=message_id)
    now = datetime.datetime.now()
    msg.read_at = now
    msg.save()

    data = msg.as_tapatalk()
    data['result'] = True

    return data

def delete_message(request, message_id=None, box_id=''):
    try:
        msg = Message.objects.get(recipient=request.user.id, pk=message_id)
    except:
        msg = Message.objects.get(sender=request.user.id, pk=message_id)

    try:
        msg.delete()
        data = {
            'result': True
        }
    except:
        data = {
            'result': False
        }

    return data


def create_message(request, usernames=[], subject='', text_body='', action='', pm_id=''):
    try:

        recipients = []
        for username in usernames:
            recipients.append(get_user(username))

        for recipient in recipients:
            msg = Message()
            msg.recipient = recipient
            msg.sender = request.user.id
            msg.subject = subject
            msg.body = text_body
            if action == 'reply':
                msg.parent_msg_id = pm_id
            msg.save()
    except:
        send_mail("Debugging Forum", "Zucht: " + ''.join(traceback.format_stack()), "mailer@androidworld.nl", ["sander@androidworld.nl"])

    return {
        'result': True,
        'msg_id': msg.id,
    }