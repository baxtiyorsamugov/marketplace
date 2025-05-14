from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_seller_approval_email(profile):
    subject = 'Ваша заявка продавца одобрена'
    context = {
        'username': profile.user.username,
        'company': profile.company_name,
        'login_url': settings.SITE_URL + '/accounts/login/',
    }
    message = render_to_string('emails/seller_approved.txt', context)
    html_message = render_to_string('emails/seller_approved.html', context)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
              [profile.user.email], html_message=html_message)
