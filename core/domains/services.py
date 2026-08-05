import requests
from .models import WebsiteSnapshot


def fetch_latest_html(website):
    response = requests.get(website.domain, timeout=10)
    return response.text


def get_last_snapshot(website):
    return (
        WebsiteSnapshot.objects
        .filter(website=website)
        .order_by("-created_at")
        .first()
    )


def save_new_snapshot(website, html):
    return WebsiteSnapshot.objects.create(
        website=website,
        html=html
    )
