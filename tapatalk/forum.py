from util import *
import base64

def get_config(request):
    return {
        'version': 'vb40_3.9.4',
        'api_level': '3',  # level 3 for now
        'is_open': True,
        'guest_okay': True,
        'inbox_stat': '0',  # forum.inbox_stat
        'can_unread': False,
        'get_latest_topic': True,
        'sys_version': '4.2.0',
        # 'support_md5': True,
        'anonymous': True,
        'goto_unread': True,
        'subscribe_forum': False,
        'disable_subscribe_forum': True,
        'get_id_by_url': False,
        'anonymous': True,
        'reg_url': 'register.php',
        'forum_signature': False,
        'get_forum': True,
        'get_participated_forum': True,
        'user_id': True,
        'disable_bbcode': False,
        'get_topic_status': True,
        'get_forum_status': True,
        'report_post': True,
        'disable_bbcode': False,
        'conversation': '0',
        'mark_pm_unread': '0',
        # 'forum_signature': True,
        # 'allow_moderate': True,
        # 'subscribe_topic_mode': '0,1,2,3',
        # 'subscribe_forum_mode': '0,2,3',
    }


def get_forum(request, return_description=False, forum_id=''):
    # get categories
    categories = Category.objects.all()

    # this will hold the result
    data = []

    # loop through categories, and create result
    for category in categories:
        cat = {
            'forum_id': category.id,
            'forum_name': category.name,
            'parent_id': '-1',
            'sub_only': True,
            'child': [],
        }

        # add all child forums to category
        fora = Forum.objects.filter(category=category)
        for forum in fora:
            f = {
                'forum_id': forum.id,
                'forum_name': forum.name,
                'parent_id': category.id,
                'sub_only': False,
                'child': [],
                'can_post': True,
            }

            cat['child'].append(f)

        data.append(cat)
    return data


def search_topic(request, search_string, start_num=0, last_num=None, search_id=''):
    t = Topic.objects.filter(name__icontains=search_string)
    topics = []
    for topic in t:
        topics.append(topic.as_tapatalk())
    return {
        'total_topic_num': len(topics),
        'topics': topics,
    }
