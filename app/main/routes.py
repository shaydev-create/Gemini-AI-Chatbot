
from flask import current_app, render_template, send_from_directory

from . import main


@main.route("/")
def index() -> None:
    return render_template("index.html")


@main.route("/chat")
def chat() -> None:
    return render_template("chat.html")


@main.route("/privacy_policy")
def privacy_policy() -> None:
    """Privacy policy - now serving English version by default"""
    return render_template("privacy_policy_en.html")


@main.route("/privacy_policy_es")
def privacy_policy_es() -> None:
    """Privacy policy in Spanish (legacy)"""
    return render_template("privacy_policy.html")


@main.route("/privacy_policy_en")
def privacy_policy_en() -> None:
    """Privacy policy in English for Chrome Extension compliance"""
    return render_template("privacy_policy_en.html")


@main.route("/sw.js")
def sw() -> None:
    return send_from_directory(current_app.static_folder, "sw.js")


@main.route("/favicon.ico")
def favicon() -> None:
    """Serve the favicon.ico file from the static directory."""
    return send_from_directory(current_app.static_folder, "favicon.ico")
