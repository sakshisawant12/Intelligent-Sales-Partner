from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
import re
import json
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
from django.core.mail import send_mail
from requests import request
from django.urls import reverse
from domains.models import Website

USE_GROQ = True

# ---------- AI SETUP ----------
if USE_GROQ:
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
else:
    from transformers import pipeline
    generator = pipeline("text-generation", model="distilgpt2")


# ---------- AI FUNCTION ----------
def get_ai_reply(message, website, products):

    if USE_GROQ:

        product_text = ""

        if products:
            product_text = "Available products:\n"
            for p in products:
                product_text += (
                    f"- {p.get('name')} "
                    f"({p.get('category')}) – ₹{p.get('price')} | "
                    f"Description: {p.get('description')} | "
                    f"Keywords: {', '.join(p.get('keywords', []))} | "
                    f"Tags: {', '.join(p.get('tags', []))}\n"
                )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are ONLY the AI assistant of the website named '{website.name}'. "
                        f"The official website name is EXACTLY: {website.name}. "
                        "You must NEVER change, invent, or replace the website name. "
                        "If user asks for website name, respond exactly with the official name only.\n\n"
                        f"{product_text}\n"
                        "If user asks about products, list the available products above. "
                        "If user mentions shirt, overshirt, or top, refer to matching product. "
                        "If user mentions pants or trousers, refer to matching product. "
                        "If user asks about trending items, suggest products tagged as trending. "
                        "If user asks about price, respond with exact price provided above. "
                        "Never invent products. "
                        "Never say you don't know pricing if product is listed above. "
                        "Respond in a friendly tone."
                    )
                },
                {"role": "user", "content": message}
            ],
            max_tokens=400
        )

        return completion.choices[0].message.content.strip()


# ---------- NORMAL CHAT PAGE ----------
def chat(request):
    reply = ""

    if request.method == "POST":
        msg = request.POST.get("message", "").strip()

        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", msg)
        if email_match:
            from leads.models import Lead

            email = email_match.group()
            website = Website.objects.first()

            if website:
                Lead.objects.get_or_create(
                    website=website,
                    email=email,
                    defaults={"source": "chatbot"}
                )

            reply = "Thanks! We’ve received your email."

        elif msg.lower() in ["hi", "hello", "hey", "hii"]:
            reply = "Hello! How can I help you today?"
        else:
            reply = get_ai_reply(msg, Website.objects.first(), [])

    return render(request, "chatbot/chat.html", {"reply": reply})


# ---------- EMBED PAGE ----------
def embed(request):
    widget_id = request.GET.get("widget_id")
    return render(request, "chatbot/embed.html", {"widget_id": widget_id})


# ---------- CHAT WIDGET ----------
def chat_widget(request):
    widget_id = request.GET.get("widget_id")
    origin = request.GET.get("origin")

    try:
        website = Website.objects.get(widget_id=widget_id)
    except Website.DoesNotExist:
        return HttpResponseForbidden("Invalid or deleted widget")

    request.session["current_website_id"] = website.id

    if origin:
        parsed_origin = urlparse(origin)
        parsed_allowed = urlparse(website.domain)

        if parsed_origin.hostname != parsed_allowed.hostname:
            return HttpResponseForbidden("Widget not allowed for this domain")

    return render(request, "chatbot/widget.html", {"widget_id": widget_id})


# ---------- CHAT API ----------
@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    message = data.get("message", "").strip()
    widget_id = data.get("widget_id")
    frontend_origin = data.get("origin")
    products = data.get("products", [])

    if not message or not widget_id:
        return JsonResponse({"error": "Missing data"}, status=400)

    from chatbot.models import Conversation, Message
    from leads.models import Lead

    try:
        website = Website.objects.get(widget_id=widget_id)
    except Website.DoesNotExist:
        return JsonResponse({"error": "Unauthorized widget"}, status=403)

    request.session["current_website_id"] = website.id

    if frontend_origin:
        frontend = urlparse(frontend_origin)
        allowed = urlparse(website.domain)
        if frontend.hostname != allowed.hostname:
            return JsonResponse({"error": "Unauthorized domain"}, status=403)

    # ---------- EMAIL DETECTION ----------
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", message)

    if email_match:
        email = email_match.group()

        conversation, _ = Conversation.objects.get_or_create(
            website=website,
            email=email
        )

        Lead.objects.get_or_create(
            website=website,
            email=email,
            defaults={"source": "chatbot", "message": message},
        )

        # ✅ FIXED EMAIL (NO CRASH)
        try:
            send_mail(
                "🚨 New Lead from Chatbot – ISP",
                f"Email: {email}\nWebsite: {website.domain}\nMessage: {message}",
                settings.DEFAULT_FROM_EMAIL,
                [website.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("EMAIL ERROR:", e)

        reply = "✅ Thanks! You're connected. How can I help you?"

        Message.objects.create(conversation=conversation, sender="bot", text=reply)

        return JsonResponse({"reply": reply})

    # ---------- GET LAST CONVERSATION ----------
    conversation = Conversation.objects.filter(
        website=website
    ).order_by("-updated_at").first()

    if not conversation:
       conversation = Conversation.objects.create(
          website=website,
          email="unknown@user.com"
    )

    if not conversation:
        return JsonResponse({"reply": "📧 Please enter your email to continue."})

    # ---------- HUMAN REQUEST ----------
    if message == "__HUMAN_REQUEST__":
        conversation.human_requested = True
        conversation.save()

        conversation_url = request.build_absolute_uri(
            reverse("dashboard:conversation_detail", args=[conversation.id])
        )

        # ✅ FIXED EMAIL
        try:
            send_mail(
                "🚨 Human Requested via Chatbot – ISP",
                f"Email: {conversation.email}\nView: {conversation_url}",
                settings.DEFAULT_FROM_EMAIL,
                [website.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("EMAIL ERROR:", e)

        Message.objects.create(
            conversation=conversation,
            sender="bot",
            text="📨 User requested to talk with owner."
        )

        return JsonResponse({
            "reply": "👤 The website owner has been notified. AI assistance is paused."
        })

    # ---------- NORMAL FLOW ----------
    Message.objects.create(conversation=conversation, sender="user", text=message)

    reply = get_ai_reply(message, website, products)

    Message.objects.create(conversation=conversation, sender="bot", text=reply)

    return JsonResponse({"reply": reply})