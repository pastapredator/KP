#!/usr/bin/env python3
"""
sync_gdocs_to_posts.py
======================
Syncs Google Docs from a specific folder to Jekyll _posts/ markdown files.
Runs as a scheduled GitHub Actions workflow OR locally.

SETUP:
1. pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-frontmatter
2. Create a Google Cloud project → enable Drive API + Docs API
3. Create OAuth2 credentials (Desktop app) → download credentials.json
4. Run once locally to generate token.json
5. Add token.json + credentials.json as GitHub Secrets (base64 encoded)

HOW TO USE:
- Create a Google Doc anywhere in Drive
- Name it: YYYY-MM-DD Title of Your Post
  Example: "2024-03-15 Why I Love Building Things"
- Add a "Properties" section at the top of the doc (optional):
  categories: technology-product, startups
  pinned: false
  read_time: 5
- Run this script → it converts the Doc to Markdown and saves to _posts/
"""

import os
import re
import json
import base64
import datetime
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────
POSTS_DIR       = Path(__file__).parent / "_posts"
GDOC_FOLDER_ID  = os.environ.get("GDOC_FOLDER_ID", "")   # Set this in env
CREDENTIALS_B64 = os.environ.get("GDRIVE_CREDENTIALS", "")
TOKEN_B64       = os.environ.get("GDRIVE_TOKEN", "")
# ───────────────────────────────────────────────────────────

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import frontmatter
except ImportError:
    print("Missing dependencies. Run:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-frontmatter")
    exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]


def get_credentials():
    """Authenticate and return Google API credentials."""
    creds = None
    token_path = Path("token.json")
    creds_path = Path("credentials.json")

    # In CI: decode from env vars
    if TOKEN_B64:
        token_path.write_bytes(base64.b64decode(TOKEN_B64))
    if CREDENTIALS_B64:
        creds_path.write_bytes(base64.b64decode(CREDENTIALS_B64))

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    "credentials.json not found. Download from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return creds


def list_docs_in_folder(drive_service, folder_id):
    """List all Google Docs in the specified folder."""
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name, modifiedTime)",
        orderBy="modifiedTime desc"
    ).execute()
    return results.get("files", [])


def doc_to_markdown(docs_service, doc_id):
    """
    Convert a Google Doc to Markdown.
    Handles: headings, bold, italic, links, lists, blockquotes, code.
    """
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get("body", {}).get("content", [])
    lines = []

    for block in content:
        para = block.get("paragraph")
        if not para:
            continue

        style = para.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        elements = para.get("elements", [])

        text = ""
        for el in elements:
            tr = el.get("textRun", {})
            raw = tr.get("content", "")
            ts  = tr.get("textStyle", {})
            link = ts.get("link", {}).get("url", "")

            if ts.get("bold") and ts.get("italic"):
                raw = f"***{raw}***"
            elif ts.get("bold"):
                raw = f"**{raw}**"
            elif ts.get("italic"):
                raw = f"*{raw}*"
            elif ts.get("strikethrough"):
                raw = f"~~{raw}~~"

            if link:
                raw = f"[{raw}]({link})"

            text += raw

        text = text.rstrip("\n")
        if not text.strip():
            lines.append("")
            continue

        heading_map = {
            "HEADING_1": "# ",
            "HEADING_2": "## ",
            "HEADING_3": "### ",
            "HEADING_4": "#### ",
        }

        if style in heading_map:
            lines.append(heading_map[style] + text)
        elif style == "NORMAL_TEXT":
            bullet = para.get("bullet")
            if bullet:
                depth = bullet.get("nestingLevel", 0)
                lines.append("  " * depth + "- " + text)
            elif text.startswith(">"):
                lines.append(text)  # Already a blockquote
            else:
                lines.append(text)
        else:
            lines.append(text)

    return "\n".join(lines)


def parse_doc_metadata(markdown_text):
    """
    Extract optional YAML-like metadata from the first paragraph of the doc.
    Format:
      categories: technology-product, startups
      pinned: true
      read_time: 5
      subtitle: My subtitle here
    """
    meta = {}
    lines = markdown_text.split("\n")
    meta_end = 0

    for i, line in enumerate(lines):
        m = re.match(r"^(categories|pinned|read_time|subtitle|cover|drive_file_id):\s*(.+)$", line.strip())
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key == "categories":
                meta[key] = [c.strip() for c in val.split(",")]
            elif key == "pinned":
                meta[key] = val.lower() in ("true", "yes", "1")
            elif key == "read_time":
                meta[key] = int(val)
            else:
                meta[key] = val
            meta_end = i + 1
        elif i > 10:
            break

    body = "\n".join(lines[meta_end:]).strip()
    return meta, body


def filename_from_doc_name(doc_name):
    """
    Convert doc name like "2024-03-15 My Post Title" to Jekyll filename.
    Falls back to today's date if no date prefix found.
    """
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})\s+(.+)$", doc_name.strip())
    if date_match:
        date_str  = date_match.group(1)
        title_raw = date_match.group(2)
    else:
        date_str  = datetime.date.today().isoformat()
        title_raw = doc_name.strip()

    slug = re.sub(r"[^a-z0-9]+", "-", title_raw.lower()).strip("-")
    return date_str, title_raw, f"{date_str}-{slug}.md"


def build_frontmatter(title, date_str, meta):
    """Build Jekyll front matter dict."""
    fm = {
        "layout": "post",
        "title":  title,
        "date":   f"{date_str} 00:00:00 +0000",
    }
    for key in ("subtitle", "categories", "pinned", "read_time", "cover", "drive_file_id"):
        if key in meta:
            fm[key] = meta[key]
    return fm


def sync():
    if not GDOC_FOLDER_ID:
        print("ERROR: Set GDOC_FOLDER_ID environment variable.")
        print("       In your Google Drive, create a folder called 'Blog Posts'")
        print("       then get its ID from the URL: drive.google.com/drive/folders/FOLDER_ID")
        exit(1)

    print("Authenticating with Google...")
    creds = get_credentials()
    drive_service = build("drive", "v3", credentials=creds)
    docs_service  = build("docs",  "v1", credentials=creds)

    print(f"Listing docs in folder {GDOC_FOLDER_ID}...")
    docs = list_docs_in_folder(drive_service, GDOC_FOLDER_ID)
    print(f"Found {len(docs)} documents.")

    POSTS_DIR.mkdir(exist_ok=True)
    synced = 0

    for doc in docs:
        doc_name = doc["name"]
        doc_id   = doc["id"]

        date_str, title_raw, filename = filename_from_doc_name(doc_name)
        out_path = POSTS_DIR / filename

        print(f"  Syncing: {doc_name} → {filename}")

        raw_md = doc_to_markdown(docs_service, doc_id)
        meta, body = parse_doc_metadata(raw_md)

        fm_data = build_frontmatter(title_raw, date_str, meta)

        post = frontmatter.Post(body, **fm_data)
        out_path.write_text(frontmatter.dumps(post), encoding="utf-8")
        synced += 1

    print(f"\n✅ Synced {synced} posts to {POSTS_DIR}")
    print("Next step: commit and push to GitHub to trigger a Pages rebuild.")


if __name__ == "__main__":
    sync()
