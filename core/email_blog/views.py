from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from domains.models import Website

from .models import EmailBlog
from leads.models import Lead
import smtplib
import ssl
from email.message import EmailMessage

def send_email_manual(subject, content, to_email):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = "sohamjadhav1120@gmail.com"
    msg['To'] = to_email

    context = ssl._create_unverified_context()  # 🔥 bypass SSL issue

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login("sohamjadhav1120@gmail.com", "flos prao nusv ijdo")
        server.send_message(msg)


@login_required
def email_marketing(request):
    user = request.user
    website_id = request.session.get("current_website_id")

    campaigns = EmailBlog.objects.filter(user=user).order_by("-created_at")

    if request.method == "POST":
        subject = request.POST.get("subject")
        content = request.POST.get("content")

        if not website_id:
            messages.error(request, "Please select a website first.")
            return redirect("dashboard:dashboard_email_marketing")

        leads = Lead.objects.filter(website_id=website_id)

        if not leads.exists():
            messages.error(request, "No leads found for this website.")
            return redirect("dashboard:dashboard_email_marketing")

        sent_count = 0

        for lead in leads:
            send_email_manual(subject, content, lead.email)
            sent_count += 1
            

        EmailBlog.objects.create(
            user=user,
            subject=subject,
            content=content,
        )

        messages.success(
            request,
            f"Email sent successfully to {sent_count} leads!"
        )

        return redirect("dashboard:dashboard_email_marketing")

    return render(
        request,
        "dashboard/email_marketing.html",
        {"campaigns": campaigns}
    )
