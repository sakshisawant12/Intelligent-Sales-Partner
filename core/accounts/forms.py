from django.contrib.auth.forms import PasswordResetForm
from email_blog.views import send_email_manual  # your function

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        subject = "Reset Your Password"

        reset_link = f"{context['protocol']}://{context['domain']}/accounts/reset/{context['uid']}/{context['token']}/"

        message = f"""
Hi,

Click the link below to reset your password:

{reset_link}

If you didn’t request this, ignore this email.
"""

        send_email_manual(subject, message, to_email)