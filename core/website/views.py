#from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from leads.models import Lead
from domains.models import Website

def home(request):
    return render(request, "website/home.html")

def get_code(request):
    return render(request, "website/get_code.html")

def embed(request):
    return render(request, "website/embed.html")

def about(request):
    return render(request, "website/about.html")

def features(request):
    return render(request, "website/features.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # 🔥 GET WEBSITE (single-site ISP landing page)
        website = Website.objects.first()
        if not website:
            messages.error(request, "No website configured.")
            return redirect("contact")

        # ---------- CREATE / UPDATE LEAD ----------
        lead, created = Lead.objects.get_or_create(
            website=website,   # ✅ REQUIRED
            email=email,
            defaults={
                "name": name,
                "message": message,
                "source": "contact_form",
                "intent": "contact",
            },
        )

        if not created:
            lead.name = lead.name or name
            lead.message = message
            lead.source = "contact_form"
            lead.intent = "contact"
            lead.save()

        # ---------- EMAIL ----------
        subject = "🚨 New Contact Form Inquiry – ISP"

        full_message = f"""
📩 NEW CONTACT FORM SUBMISSION

━━━━━━━━━━━━━━━━━━━━━━━

👤 Name: {name}
📧 Email: {email}
🌐 Website: {website.domain}

📝 Message:
{message}

━━━━━━━━━━━━━━━━━━━━━━━

🤖 Possible Intent Check:

• This user submitted contact form.
• May need help with ISP setup.
• May be interested in chatbot integration.
• Review message and respond accordingly.

━━━━━━━━━━━━━━━━━━━━━━━

— Intelligent Sales Partner System
        """

        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ISP_OWNER_EMAIL],  # ✅ FIXED OWNER MAIL
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "website/contact.html")
