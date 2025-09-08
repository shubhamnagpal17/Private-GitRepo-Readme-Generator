import os
import secrets
from datetime import timedelta
from flask import Flask, request, render_template, redirect, session, url_for
from APIS.gemini import generate_readme_material
from APIS.gitapi import fetch_repo_metadata, extract_owner_repo
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(32))

# Session lifetime = 10 minutes
app.permanent_session_lifetime = timedelta(minutes=10)

# GitHub OAuth credentials
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

# Home page
@app.route("/")
def index():
    logged_in = "access_token" in session
    return render_template("index.html", logged_in=logged_in)

# GitHub login
@app.route("/login")
def login():
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=repo&state={state}"
    )
    return redirect(github_auth_url)

# GitHub OAuth callback
@app.route("/callback")
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if state != session.get('oauth_state'):
        return "State mismatch. Possible CSRF attack.", 400

    try:
        token_url = "https://github.com/login/oauth/access_token"
        response = requests.post(token_url, data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "state": state
        }, headers={"Accept": "application/json"})
        response.raise_for_status()
        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            return "Failed to fetch access token.", 400

        session.permanent = True
        session['access_token'] = access_token
        return redirect(url_for("index"))
    except requests.RequestException as e:
        return f"Error during token exchange: {e}", 500

# Revoke GitHub token at logout
def revoke_github_token(token):
    try:
        url = f"https://api.github.com/applications/{CLIENT_ID}/token"
        response = requests.delete(
            url,
            auth=(CLIENT_ID, CLIENT_SECRET),
            json={"access_token": token}
        )
        if response.status_code != 204:
            app.logger.warning(f"Token revoke failed: {response.status_code}, {response.text}")
        return response.status_code == 204
    except requests.RequestException as e:
        app.logger.error(f"Revoke request exception: {e}")
        return False

# Logout
@app.route("/logout")
def logout():
    token = session.get("access_token")
    if token:
        revoked = revoke_github_token(token)
        if not revoked:
            app.logger.warning("Failed to revoke GitHub token during logout.")
    session.pop("access_token", None)
    return redirect(url_for("index"))

# Generate README
@app.route("/generate_readme", methods=['POST'])
def generate_readme():
    repo_url = request.form['repo_url']
    try:
        owner, repo = extract_owner_repo(repo_url)
        token = session.get('access_token')
        metadata = fetch_repo_metadata(owner, repo, token)
        genai_response = generate_readme_material(
            metadata['repo_name'],
            metadata['repo_url'],
            metadata['repo_description'],
            metadata['language'],
            metadata['topics'],
            metadata['stars'],
            metadata['license_name'],
            metadata['files']
        )
        return render_template("readme.html", readme=genai_response)
    except Exception as e:
        app.logger.error(f"Error generating README: {e}")
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))