from django.conf.urls import url

from tapatalk.views import handle_xmlrpc

urlpatterns = [
    url(r'^xmlrpc/$', handle_xmlrpc, name='tapatalk-xmlrpc'),
    url(r'^mobiquo.php$', handle_xmlrpc, name='tapatalk-xmlrpc-php'),
]