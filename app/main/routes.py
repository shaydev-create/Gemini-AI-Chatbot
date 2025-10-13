from flask import render_template, session, redirect, url_for, current_app, flash, request, send_from_directory
from . import main
import os

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat')
def chat():
    return render_template('chat.html')

@main.route('/privacy_policy')
def privacy_policy():
    """Privacy policy - now serving English version by default"""
    return render_template('privacy_policy_en.html')

@main.route('/privacy_policy_es')
def privacy_policy_es():
    """Privacy policy in Spanish (legacy)"""
    return render_template('privacy_policy.html')

@main.route('/privacy_policy_en')
def privacy_policy_en():
    """Privacy policy in English for Chrome Extension compliance"""
    return render_template('privacy_policy_en.html')

@main.route('/sw.js')
def sw():
    return send_from_directory(current_app.static_folder, 'sw.js')