import email
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from domains.models import Website
from chatbot.models import Conversation, Message
from django.http import HttpResponseRedirect
from leads.models import Lead
import requests
from domains.models import WebsiteSnapshot
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from leads.models import Lead
from django.db.models.functions import TruncDate
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from email_blog.views import send_email_manual
from django.core.mail import EmailMessage
from django.contrib.auth import logout
from django.conf import settings


@login_required
def dashboard_home(request):
    websites = Website.objects.filter(user=request.user)

    # ---------- CONVERSATIONS ----------
    conversations = Conversation.objects.filter(
        website__user=request.user
    )

    total_conversations = conversations.count()

    # ---------- CONVERSATIONS THIS WEEK ----------
    today = timezone.now().date()
    last_7_days = today - timedelta(days=6)

    weekly_conversations = (
        conversations
        .filter(created_at__date__gte=last_7_days)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    # Convert to simple dict for charts
    weekly_chart_data = {
        str(item["day"]): item["count"]
        for item in weekly_conversations
    }

    # ---------- RESPONSE TIME ----------
    total_response_seconds = 0
    response_count = 0

    for convo in conversations.prefetch_related("messages"):
        messages = list(convo.messages.all())

        for i in range(len(messages) - 1):
            if messages[i].sender == "user" and messages[i + 1].sender in ["bot", "human"]:
                delta = (messages[i + 1].timestamp - messages[i].timestamp).total_seconds()
                total_response_seconds += delta
                response_count += 1
                break  # only first response per conversation

    avg_response_time = (
        round(total_response_seconds / response_count, 2)
        if response_count > 0 else 0
    )

    # ---------- FIRST RESPONSE RATE ----------
    conversations_with_reply = 0

    for convo in conversations:
        if convo.messages.filter(sender__in=["bot", "human"]).exists():
            conversations_with_reply += 1

    first_response_rate = (
        round((conversations_with_reply / total_conversations) * 100, 2)
        if total_conversations > 0 else 0
    )

    # ---------- CONVERSATION QUALITY (0–10) ----------
    quality_scores = []

    for convo in conversations:
        score = 0
        msg_count = convo.messages.count()

        if msg_count >= 6:
            score += 4
        elif msg_count >= 3:
            score += 2

        if not convo.human_requested:
            score += 3
        else:
            score += 1

        if convo.messages.filter(sender="human").exists():
            score += 3

        quality_scores.append(score)

    conversation_quality = (
        round(sum(quality_scores) / len(quality_scores), 1)
        if quality_scores else 0
    )

    # ---------- LEAD ENGAGEMENT ----------
    total_leads = Lead.objects.count()

    engaged_leads = Lead.objects.filter(
        email__in=conversations.values_list("email", flat=True)
    ).count()

    lead_engagement = (
        round((engaged_leads / total_leads) * 100, 2)
        if total_leads > 0 else 0
    )

    return render(request, "dashboard/index.html", {
        "websites": websites,
        "total_conversations": total_conversations,
        "weekly_chart_data": weekly_chart_data,
        "avg_response_time": avg_response_time,
        "first_response_rate": first_response_rate,
        "conversation_quality": conversation_quality,
        "lead_engagement": lead_engagement,
    })


def test_page(request):
    return render(request, "test.html")


@login_required
def conversations(request):
    conversations = (
        Conversation.objects
        .filter(website__user=request.user)
        .select_related("website")
        .prefetch_related("messages")
    )

    return render(request, "dashboard/conversations.html", {
        "conversations": conversations
    })


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        website__user=request.user
    )

    # 🔒 NO POST HERE
    # Owner replies are sent via WebSocket ONLY

    return render(request, "dashboard/conversation_detail.html", {
        "conversation": conversation
    })


@login_required
def domains(request):
    if request.method == "POST":
        domain = request.POST.get("domain", "").strip()

        if domain:
            website, created = Website.objects.get_or_create(
                user=request.user,
                domain=domain
            )

            if created:
                # 🔹 STEP 1: Fetch website HTML
                try:
                    response = requests.get(domain, timeout=10)
                    html = response.text
                except Exception:
                    html = ""

                # 🔹 STEP 1: Store snapshot
                WebsiteSnapshot.objects.create(
                    website=website,
                    html=html
                )
                send_email_manual(
                    "New Website Created on ISP",
                    f"""
                A new website has been created on ISP.

                User Email: {request.user.email}
                Domain: {website.domain}
                """,
                    settings.ISP_OWNER_EMAIL
            )

                messages.success(request, "Domain added successfully.")
            else:
                messages.warning(request, "This domain already exists.")

        return redirect("dashboard:dashboard_domains")

    websites = Website.objects.filter(user=request.user)
    return render(request, "dashboard/domains.html", {
        "websites": websites
    })
    


@login_required
def settings_view(request):
    return render(request, "dashboard/settings.html")


@login_required
def email_marketing(request):
    website_id = request.session.get("current_website_id")

    if not website_id:
        messages.error(request, "Please select a website first.")
        return redirect("dashboard:dashboard_home")

    leads = Lead.objects.filter(website_id=website_id)

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        content = request.POST.get("content", "").strip()

        if not subject or not content:
            messages.error(request, "Subject and message are required.")
            return redirect("dashboard:email_marketing")

        if not leads.exists():
            messages.error(request, "No leads found for this website.")
            return redirect("dashboard:email_marketing")

        sent_count = 0

        for lead in leads:
            email = EmailMessage(
                subject=subject,
                body=content,
                from_email=settings.DEFAULT_FROM_EMAIL,  # ✅ ISP verified sender
                to=[lead.email],                         # ✅ lead email
                headers={
                    "Reply-To": request.user.email      # ✅ website owner email
                }
            )

            email.send(fail_silently=False)
            sent_count += 1

        messages.success(
            request,
            f"Email sent successfully to {sent_count} leads."
        )

        return redirect("dashboard:email_marketing")

    return render(request, "dashboard/email_marketing.html", {
        "leads_count": leads.count()
    })

@login_required
def leads(request):
    print("SESSION DATA:", dict(request.session))  # 👈 ADD THIS

    website_id = request.session.get("current_website_id")
    print("CURRENT WEBSITE ID:", website_id)       # 👈 ADD THIS

    leads = Lead.objects.none()

    if website_id:
        leads = Lead.objects.filter(
            website_id=website_id
        ).order_by("-created_at")

    return render(request, "dashboard/leads.html", {
        "leads": leads
    })




@login_required
def change_theme(request):
    theme = request.GET.get("theme")

    if theme in ["dark", "light"]:
        request.session["theme"] = theme

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/dashboard/"))


@login_required
def toggle_theme(request):
    theme = request.GET.get("theme")

    if theme in ["light", "dark"]:
        request.session["theme"] = theme

    return redirect(request.META.get("HTTP_REFERER", "/dashboard/"))




@login_required
def reply_to_conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        website__user=request.user
    )

    if request.method == "POST":
        text = request.POST.get("reply", "").strip()
        if text:
            msg = Message.objects.create(
                conversation=conversation,
                sender="owner",
                text=text
            )

            # 🔥 SEND REAL-TIME MESSAGE
            channel_layer = get_channel_layer()
            email = conversation.email.strip().lower()
            group_name = get_chat_group_name(
                conversation.website.widget_id,
                email
            )


            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat_message",
                    "message": msg.text,
                }
            )

    return redirect("dashboard:conversation_detail", conversation_id=conversation.id)


@login_required
def website_dashboard(request, website_id):
    website = get_object_or_404(
        Website,
        id=website_id,
        user=request.user
    )

    websites = Website.objects.filter(user=request.user)

    # 🔒 Filter EVERYTHING by this website
    conversations = Conversation.objects.filter(
        website=website
    )

    total_conversations = conversations.count()

    # ---- weekly conversations (same logic you already fixed)
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    from django.db.models.functions import TruncDate

    today = timezone.now().date()
    last_7_days = today - timedelta(days=6)

    weekly_conversations = (
        conversations
        .filter(created_at__date__gte=last_7_days)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    weekly_chart_data = {
        str(item["day"]): item["count"]
        for item in weekly_conversations
    }

    # ---- leads for THIS website only
    leads = Lead.objects.filter(
        email__in=conversations.values_list("email", flat=True)
    )

    lead_engagement = round(
        (leads.count() / leads.count()) * 100, 2
    ) if leads.exists() else 0

    return render(request, "dashboard/index.html", {
        "websites": websites,
        "current_website": website,   # ⭐ important
        "total_conversations": total_conversations,
        "weekly_chart_data": weekly_chart_data,
        "lead_engagement": lead_engagement,
    })

@login_required
def website_leads(request, website_id):
    website = get_object_or_404(
        Website,
        id=website_id,
        user=request.user
    )

    websites = Website.objects.filter(user=request.user)

    # 🔗 Get conversations for this website
    conversations = Conversation.objects.filter(website=website)

    # 🔗 Get leads ONLY linked to this website
    leads = Lead.objects.filter(
        email__in=conversations.values_list("email", flat=True)
    ).order_by("-created_at")

    return render(request, "dashboard/leads.html", {
        "websites": websites,
        "current_website": website,
        "leads": leads,
    })

def set_current_website(request, website_id):
    website = Website.objects.get(
        id=website_id,
        user=request.user
    )

    request.session["current_website_id"] = website.id
    request.session["current_website_domain"] = website.domain

    return redirect("dashboard:dashboard_home")

@login_required
def update_email(request):
    if request.method == "POST":
        new_email = request.POST.get("email").strip().lower()
        user = request.user

        # 🔒 SAME EMAIL — DO NOTHING
        if new_email == user.email:
            messages.info(request, "This is already your email.")
            return redirect("dashboard:settings")

        # 🔒 CHECK DUPLICATE EMAIL
        if User.objects.filter(username=new_email).exclude(id=user.id).exists():
            messages.error(request, "This email is already in use.")
            return redirect("dashboard:settings")

        # ✅ UPDATE BOTH (CRITICAL)
        user.email = new_email
        user.username = new_email
        user.save()

        messages.success(request, "Email updated successfully.")
        return redirect("dashboard:settings")
    
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted permanently.")
        return redirect("/")
