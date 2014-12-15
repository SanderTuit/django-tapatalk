from django_xmlrpc.dispatcher import DjangoXMLRPCDispatcher
from tapatalk import settings


# If we need to debug, now we know
DEBUG = hasattr(settings, 'XMLRPC_DEBUG') and settings.XMLRPC_DEBUG

from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
def send_mail(subject, text, from_email, rec_list, html=None):
    """
    Shortcut for sending email.
    """
    msg = EmailMultiAlternatives(subject, text, from_email, rec_list)
    if html:
        msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=True)

class TapatalkXMLRPCDispatcher(DjangoXMLRPCDispatcher):
    def _marshaled_dispatch(self, request, django_args, django_kwargs):
        def dispatch_method(method, params):
            try:
                try:
                    func = self.funcs[method]
                except KeyError:
                    raise Exception('method "%s" is not supported' % method)

                kwargs = {}
                if django_args:
                    kwargs['django_args'] = django_args
                if django_kwargs:
                    kwargs['django_kwargs'] = django_kwargs
                return func(request, *params, **kwargs)
            except:
                send_mail("Debugging Forum", str(method) + " " + str(params), "mailer@androidworld.nl", ["sander@androidworld.nl"])
                return func(request, *params, **kwargs)

        # Tapatalk sends out bad formatted booleans... *sigh*
        body = request.raw_post_data.replace('<boolean>true</boolean>', '<boolean>1</boolean>')

        return DjangoXMLRPCDispatcher._marshaled_dispatch(self, body, dispatch_method)
