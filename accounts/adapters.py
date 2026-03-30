from allauth.account.adapter import DefaultAccountAdapter
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        user = context.get('user')

        if template_prefix == 'account/email/email_confirmation_signup':
            html_content = render_to_string(
                'account/email/email_confirmation_signup.html',
                context
            )
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject=f"Добро пожаловать в Новостной портал, {user.username}!",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            super().send_mail(template_prefix, email, context)