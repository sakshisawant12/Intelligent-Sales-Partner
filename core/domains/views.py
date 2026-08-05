from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Website

@login_required
def add_website(request):
    if request.method == "POST":
        name = request.POST.get("name")
        domain = request.POST.get("domain")

        Website.objects.create(
            user=request.user,
            name=name,
            domain=domain
        )

        return redirect("dashboard")

    return render(request, "domains/add_website.html")


@login_required
def website_code(request, website_id):
    website = get_object_or_404(Website, widget_id=website_id, user=request.user)

    script = f"""
<!-- ISP Chatbot Widget -->
<script
  src="http://127.0.0.1:8000/static/widget.js"
  data-widget-id="{website.id}">
</script>
""".strip()

    return render(request, "domains/website_code.html", {
        "website": website,
        "script": script
    })



@login_required
def registered_websites(request):
    websites = Website.objects.filter(user=request.user)
    return render(request, "dashboard/domains.html", {
        "websites": websites
    })
from .services import (
    fetch_latest_html,
    get_last_snapshot,
    save_new_snapshot,
)


def check_website_changes(website):
    latest_html = fetch_latest_html(website)
    last_snapshot = get_last_snapshot(website)

    if not last_snapshot:
        save_new_snapshot(website, latest_html)
        return False

    if latest_html != last_snapshot.html:
        save_new_snapshot(website, latest_html)
        return True

    return False

