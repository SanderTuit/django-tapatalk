from djangobb_forum.models import *
from django.core.cache import cache
from django_messages.models import Message
import HTMLParser
from django.utils.encoding import smart_unicode
import xmlrpclib
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .lib import html2markdown, replace_tags
from avatar.util import get_primary_avatar


def get_user(username):
    username = u"" + username.__str__()  # TODO: check this
    username = username.replace("\x00", '')  # ugh, something is messing up our strings

    # username = "" + str(username)
    user = User.objects.get(username=username)

    return user


def get_avatar_for_user(user):
    # fix this to correct call from django_bb
    avatar = None
    try:
        avatar_container = get_primary_avatar(user, 72)
        avatar = avatar_container.avatar_url(72)
    except:
        pass

    if avatar == None:
        avatar = ''

    return avatar

def attachment_as_tapatalk(self):
    name = self.name.lower()
    content_type = "other"
    if name.endswith(".png") or name.endswith(".gif") or name.endswith(".jpg") or name.endswith(".jpeg"):
        content_type = "image"
    elif name.endswith(".pdf"):
        content_type = "pdf"

    data = {
        'content_type': content_type.encode('utf-8'),
        'url': 'http://androidworld.nl' + self.get_absolute_url().encode('utf-8'),
    }

    if content_type == "image":
        data['thumbnail_url'] = 'http://androidworld.nl' + self.get_absolute_url().encode('utf-8')
    return data

def topic_as_tapatalk(self):
    try:
        user = self.user
    except:
        user = User.objects.get(username='archive')

    avatar = get_avatar_for_user(user)
    can_post = not self.closed

    data = {
        'forum_id': str(self.forum.id),
        'forum_name': xmlrpclib.Binary(smart_unicode(self.forum.name).encode('utf-8')),
        'topic_id': str(self.id),
        'topic_title': xmlrpclib.Binary(smart_unicode(self.name).encode('utf-8')),
        'prefix': '',
        'icon_url': avatar,
        'reply_number': self.post_count,
        'view_number': str(self.views),
        'can_post': can_post,
        'is_approved': True,
        'topic_author_id': str(user.id),
        'topic_author_name': xmlrpclib.Binary(user.username.encode('utf-8')),
        'closed': self.closed,
    }
    if self.last_post:
        h = HTMLParser.HTMLParser()
        body = h.unescape(replace_tags(self.last_post.body)).encode('utf-8')
        data.update({
            'short_content': xmlrpclib.Binary(body[:100]),
            'last_reply_time': xmlrpclib.DateTime(str(self.last_post.created.isoformat()).replace('-','') + '+01:00'),
            'post_time': xmlrpclib.DateTime(str(self.last_post.created.isoformat()).replace('-','') + '+01:00'),
            'post_author_id': self.last_post.user.id,
            'post_author_name': xmlrpclib.Binary(self.last_post.user.username.encode('utf-8')),
        })

    return data


def post_as_tapatalk(self):
    avatar = get_avatar_for_user(self.user)

    post_attachments = self.attachments.all()
    attachments = []
    for attachment in post_attachments:
        attachment = attachment.as_tapatalk()
        attachments.append(attachment)

    # try to get online status
    online = cache.get('djangobb_user%d' % self.user.id)
    if online == None:
        online = False

    h = HTMLParser.HTMLParser()
    body = h.unescape(replace_tags(self.body)).encode('utf-8')
    # try:
    # body = html2markdown(smart_unicode(self.body_html))
    # except:

    data = {
        'post_id': str(self.id),
        'post_title': xmlrpclib.Binary(''),
        'post_content': xmlrpclib.Binary(body),
        'forum_name': xmlrpclib.Binary(self.topic.forum.name.encode('utf-8')),
        'forum_id': str(self.topic.forum.id),
        'topic_id': str(self.topic.id),
        'topic_title': xmlrpclib.Binary(self.topic.name.encode('utf-8')),
        'post_author_id': str(self.user.id),
        'post_author_name': xmlrpclib.Binary(self.user.username.encode('utf-8')),
        'post_time': xmlrpclib.DateTime(str(self.created.isoformat().replace('-','') + '+01:00')),
        'is_approved': True,
        'icon_url': avatar,
        'attachments': attachments,
        'is_online': online,
        'reply_number': str(self.topic.post_count),
        'view_count': str(self.topic.views),
        # 'short_content': xmlrpclib.Binary(self.body_html[:100]),
    }

    return data


def message_as_tapatalk(self):
    state = 'Unread'
    if self.read_at:
        state = 'Read'
    if self.replied_at:
        state = 'Replied'

    # try to get online status
    online = cache.get('djangobb_user%d' % self.sender.id)
    if online == None:
        online = False

    data = {
        'msg_id': str(self.id),
        'msg_state': state,
        'sent_date': xmlrpclib.DateTime(str(self.sent_at).replace('-','') + '+01:00'),
        'msg_from_id': self.sender.id,
        'msg_from': xmlrpclib.Binary(self.sender.username.encode('utf-8')),
        'icon_url': get_avatar_for_user(self.sender.encode('utf-8')),
        'msg_subject': xmlrpclib.Binary(self.subject.encode('utf-8')),
        'short_content': xmlrpclib.Binary(self.body.encode('utf-8')),
        'is_online': online,
        'text_body': xmlrpclib.Binary(self.body.encode('utf-8')),
        'msg_to': [
            {
                'user_id': self.recipient.id,
                'username': xmlrpclib.Binary(self.recipient.username.encode('utf-8')),
            }
        ],
    }

    return data

# ugh, monkey patching
Topic.as_tapatalk = topic_as_tapatalk
Post.as_tapatalk = post_as_tapatalk
Message.as_tapatalk = message_as_tapatalk
Attachment.as_tapatalk = attachment_as_tapatalk