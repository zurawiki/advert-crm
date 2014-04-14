from django.db.models.signals import post_save, pre_save

from django.dispatch import receiver
from account.signals import password_changed
from account.signals import user_sign_up_attempt, user_signed_up
from account.signals import user_login_attempt, user_logged_in
from eventlog.models import log
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from contracts.models import Advertiser, Correspondence, Advert


@receiver(user_logged_in)
def handle_user_logged_in(sender, **kwargs):
    log(
        user=kwargs.get("user"),
        action="USER_LOGGED_IN",
        extra={}
    )


@receiver(password_changed)
def handle_password_changed(sender, **kwargs):
    log(
        user=kwargs.get("user"),
        action="PASSWORD_CHANGED",
        extra={}
    )


@receiver(user_login_attempt)
def handle_user_login_attempt(sender, **kwargs):
    log(
        user=None,
        action="LOGIN_ATTEMPTED",
        extra={
            "username": kwargs.get("username"),
            "result": kwargs.get("result")
        }
    )


@receiver(user_sign_up_attempt)
def handle_user_sign_up_attempt(sender, **kwargs):
    log(
        user=None,
        action="SIGNUP_ATTEMPTED",
        extra={
            "username": kwargs.get("username"),
            "email": kwargs.get("email"),
            "result": kwargs.get("result")
        }
    )


@receiver(user_signed_up)
def handle_user_signed_up(sender, **kwargs):
    log(
        user=kwargs.get("user"),
        action="USER_SIGNED_UP",
        extra={}
    )


def email(to, advertiser, topic, template_data):
    TOPICS = {
        'advertiser_approved': "Your account has been approved",
        'advertiser_created': "The Harvard Lampoon welcomes you!",
        'ad_paid_created': "Your advertising contract needs your attention",
        'ad_paid_updated': "Your advertising contract has been updated"
    }

    from_email = 'The Harvard Lampoon<sales@harvardlampoon.com>'

    subject = TOPICS[topic]
    html_content = render_to_string("mail/%s.html" % topic, template_data)
    text_content = html_content.split('<!--c281b02d33538e511c1c5551f13d71d2-->')[
        1].strip()  # this strips the html, so people will have the text as well.
    text_content = strip_tags(text_content)
    # create the email, and attach the HTML version as well.
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    # log correspondence
    corres = {'advertiser': advertiser, "_from": from_email,
              "_to": to, "text": '\n'.join((topic, text_content))}
    Correspondence(**corres).save();


@receiver(pre_save, sender=Advertiser)
def handle_advertiser_approved(**kwargs):
    new = kwargs.get('instance')
    try:
        old = Advertiser.objects.get(pk=new.pk)
        if not old.approved and new.approved:
            email(new.email, new, 'advertiser_approved', {'advertiser': new})
    except Advertiser.DoesNotExist:
        pass


@receiver(post_save, sender=Advertiser)
def handle_advertiser_created(**kwargs):
    if kwargs.get('created'):
        new = kwargs.get('instance')
        email(new.email, new, 'advertiser_created', {'advertiser': new})


@receiver(post_save, sender=Advert)
def handle_advert_paid(**kwargs):
    ad = kwargs.get('instance')
    if kwargs.get('created') and ad.paid:
        # send link to upload
        email(ad.advertiser.email, ad.advertiser, 'ad_paid_created', {'advertiser': ad.advertiser, 'ad': ad})

    elif ad.paid:
        # ad status has been updated, check page for info
        email(ad.advertiser.email, ad.advertiser, 'ad_paid_updated', {'advertiser': ad.advertiser, 'ad': ad})

