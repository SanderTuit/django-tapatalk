from djangobb_forum.models import *
import xmlrpclib
from django.db.models import F
from django.utils.encoding import smart_unicode
from django.contrib import auth

def get_thread(request, topic_id, start_num=None, last_num=None, return_html=True):
    Topic.objects.filter(pk=topic_id).update(views=F('views') + 1)
    topic = Topic.objects.get(pk=topic_id)
    if request.user.is_authenticated():
        topic.update_read(request.user)

    data = {
        'total_post_num': max(0,topic.post_count),
        'forum_id': str(topic.forum.id),
        'forum_title': xmlrpclib.Binary(smart_unicode(topic.forum.name).encode("utf-8")),
        'topic_id': str(topic.id),
        'topic_title': xmlrpclib.Binary(smart_unicode(topic.name).encode("utf-8")),
        'can_reply': True,
        'posts': [],
        'is_approved': True,
        'can_upload': True,
        'prefix': '',
        'can_subscribe': False,
        'is_closed': topic.closed,
    }

    posts = Post.objects.filter(topic=topic).filter(deleted=False)

    if start_num == None and last_num == None:
        start_num = 0
        last_num = 19

    if start_num != last_num:
        if last_num - start_num > 50:
            posts = posts[start_num:start_num + 50]
        else: 
            posts = posts[start_num:last_num + 1]
    else:
        posts = posts[start_num]

    for post in posts:
        post.last_post = None
        p = post.as_tapatalk()

        if post.user.id == request.user.id:
            p['can_edit'] = True

        data['posts'].append(p)

    return data


def reply_post(request, forum_id, topic_id, subject='', text_body='', attachments=[], group_id='', return_html=False):
    p = Post()
    t = Topic.objects.get(pk=topic_id)
    if t.closed:
        return {
            'result': False,
            'post_id': str(p.id),
        }

    p.user_id = request.user.id
    p.body = str(text_body)
    p.topic = t
    p.save()

    return {
        'result': True,
        'post_id': str(p.id),
    }


def get_raw_post(request, post_id):
    p = Post.objects.get(pk=post_id)
    return p.as_tapatalk()


def save_raw_post(request, post_id, post_title='', post_content='', return_html=False, prefix_id=''):
    p = Post.objects.get(pk=post_id, user=auth.get_user(request))
    p.updated = datetime.now()
    p.updated_reason = "Bewerkt via Tapatalk/Androidworld Reader"
    p.body = str(post_content)
    p.save()

    return {
        'result': True,
    }
