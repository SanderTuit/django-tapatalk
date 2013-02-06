import xmlrpclib
from util import *


def get_unread_topic(request, start_num, last_num, search_id='', filters=[]):
    return {
        'result': True,
        'total_topic_num': 0,
        'topics': [],
        'forum_id': '',
    }


def get_latest_topic(request, start_num, last_num, search_id='', filters=[]):
    topics = Topic.objects.all()[:2]
    data = {
        'result': True,
        'topics': [],
    }

    for t in topics:
        data['topics'].append(t.as_tapatalk())

    data['total_topic_num'] = len(data['topics'])
    data['total_unread_num'] = 0
    return data


# TODO: Pagination
def get_participated_topic(request, user_name='', start_num=0, last_num=None, search_id='', user_id=''):
    user = request.user
    posts = Post.objects.filter(user=user)

    topics = []
    tmp = []
    for post in posts:
        if post.topic.id not in tmp:
                t = post.topic
                topics.append(t.as_tapatalk())
                tmp.append(t.id)

    return {
        'result': True,
        'search_id': search_id,
        'total_topic_num': len(topics),
        'total_unread_num': 0,  # TODO: make me work
        'topics': topics,
    }


def get_topic(request, forum_id, start_num=0, last_num=0, mode='DATE'):
    topics = Topic.objects.filter(forum_id=forum_id)
    forum = Forum.objects.get(pk=forum_id)

    if mode == 'TOP':
        topics = topics.filter(sticky=True)

    if start_num != 0:
        topics = topics[last_num:start_num]

    data = {
        'total_topic_num': forum.topic_count,
        'forum_id': forum_id,
        'forum_name': xmlrpclib.Binary(forum.name),
        'can_post': True,
        'can_upload': False,
        'require_prefix': False,
        'topics': [],
    }

    subscriptions = request.user.subscriptions.all()

    for topic in topics:
        t = topic.as_tapatalk()
        if request.user.is_authenticated():
            t['can_subscribe'] = True
            if topic in subscriptions:
                t['is_subscribed'] = True

        data['topics'].append(t)

    return data


def new_topic(request, forum_id, subject, text_body, prefix_id='', attachment_id_array=[], group_id=''):
    from djangobb_forum.models import Topic, Post
    t = Topic()
    t.forum_id = forum_id
    t.name = subject
    t.user_id = request.user
    t.save()

    p = Post()
    p.user_id = 1
    p.topic_id = t.id
    p.body = str(text_body)
    p.save()

    return {
        'result': True,
        'topic_id': t.id,
    }
