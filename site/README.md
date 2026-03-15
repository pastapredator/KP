# Krishnapriya PS — Personal Site

Orange & blue whimsical Jekyll site with blog (tag filters, pinned posts), books shelf (Google Drive viewer), and portfolio. Deployed on GitHub Pages.

---

## 🚀 One-Time Deployment (15 min)

### 1. Create the GitHub repo

```bash
# On github.com → New repository
# Name: krishnapriya  (or your username.github.io for root domain)
# Visibility: Public
# Don't initialise with README
```

### 2. Push this code

```bash
cd this-folder
git init
git add .
git commit -m "Initial site"
git branch -M main
git remote add origin https://github.com/pastapredator/krishnapriya.git
git push -u origin main
```

### 3. Enable GitHub Pages

Go to your repo → **Settings → Pages**
- Source: **GitHub Actions**
- Click Save

Your site will be live at `https://pastapredator.github.io/krishnapriya/` within ~2 min.

---

## ✍️ Writing Blog Posts

### Option A — Google Docs (recommended, easiest)

1. Create a Google Drive folder called **"Blog Posts"**
2. Get its ID from the URL: `drive.google.com/drive/folders/`**`FOLDER_ID`**
3. In GitHub repo → **Settings → Secrets and variables → Actions**, add:
   - `GDOC_FOLDER_ID` = your folder ID
   - `GDRIVE_CREDENTIALS` = base64 of credentials.json (see below)
   - `GDRIVE_TOKEN` = base64 of token.json (see below)

**Getting Google API credentials:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. New project → Enable **Google Docs API** and **Google Drive API**
3. Credentials → Create → OAuth2 → Desktop app → Download `credentials.json`
4. Run locally once: `python scripts/sync_gdocs_to_posts.py`
   - This opens a browser, you log in, it generates `token.json`
5. Encode both files: `base64 -i credentials.json` and `base64 -i token.json`
6. Add the base64 strings as GitHub secrets (see step 3 above)

**Writing a post:**
1. In your "Blog Posts" Drive folder, create a new Google Doc
2. Name it: `2024-03-15 My Post Title`  (date prefix is required)
3. Optionally add metadata at the top of the doc:
   ```
   categories: technology-product, startups
   pinned: false
   read_time: 5
   subtitle: An optional subtitle
   ```
4. Write your post in the doc — bold, italic, headings, links all work
5. The GitHub Action syncs daily at 8am UTC, or trigger manually:
   - Repo → **Actions → Build & Deploy Site → Run workflow**

### Option B — Markdown directly

Create a file in `_posts/` named `YYYY-MM-DD-your-title.md`:

```markdown
---
layout: post
title: "My Post Title"
subtitle: "Optional subtitle"  
date: 2024-03-15 00:00:00 +0000
categories:
  - technology-product
  - startups
pinned: false
read_time: 5
---

Your post content here in **Markdown**.
```

Commit and push — the site rebuilds automatically.

---

## 📚 Adding Books

1. Upload your PDF to Google Drive
2. Share it: **Anyone with the link → Viewer**
3. Get the file ID from the URL: `drive.google.com/file/d/`**`FILE_ID`**`/view`
4. Edit `_books/your-book.md` (or create a new file):

```markdown
---
layout: book
title: "Your Book Title"
author_name: "Krishnapriya PS"
year: 2024
description: "A short description of what the book is about."
cover: "https://link-to-cover-image.jpg"
drive_file_id: "paste_the_file_id_here"
---

Longer description of the book goes here.
```

The book will appear on `/books/` with a **Read now** button that opens an embedded Google Drive viewer. Downloading is disabled.

**Book protection notes:**
- The Google Drive "preview" embed hides the download toolbar
- Right-click is disabled in the reader
- Direct PDF URL is never exposed in the page HTML
- A determined technical user could still extract the URL — this protects against casual copying (95%+ of readers)

---

## 📌 Pinning Posts

To pin up to 3 posts to the top of the blog:

```markdown
---
pinned: true
---
```

Pinned posts appear first with a 📌 badge, regardless of date. Only the first 3 pinned posts are shown pinned (any additional are treated as normal).

---

## 🏷️ Blog Categories

Use these exact strings in `categories:` for the tag filter to work:

| Category | Label shown |
|---|---|
| `technology-product` | 🖥️ Technology & Product |
| `books-reading` | 📚 Books & Reading |
| `design` | 🎨 Design |
| `startups` | 🚀 Startups |
| `personal-humor` | 😄 Personal & Humor |

---

## 🖼️ Profile Photo

Replace `assets/img/profile.jpg` with your photo (square, min 400×400px recommended).

---

## 🎨 Customising the Design

All design tokens are in `assets/css/main.css` under `:root {}`:

```css
--orange:  #E8621A;   /* Main accent — change to any orange you love */
--blue:    #1A5F9E;   /* Secondary accent */
```

---

## 🔧 Maintenance Schedule

Automated: a GitHub Issue is created every **6 months** (Jan 1 & Jul 1) reminding you to:
- Update gems (`bundle update`)  
- Check CDN links (fonts, icons)
- Test the book viewer

**Hard dates for your calendar:**
- **July 1, 2025** — First bi-annual dependency review
- **January 1, 2026** — Second review
- **January 1, 2027** — Full refactor assessment (Jekyll major version, consider Astro/Next if Jekyll EOL)

**Manual backup:** Download a ZIP of your repo from GitHub every 6 months as an offline archive.

---

## 🏃 Running Locally

```bash
# Install Ruby 3.2+ and Bundler first
gem install bundler
bundle install
bundle exec jekyll serve --livereload
# → open http://localhost:4000/krishnapriya/
```

---

## 📁 Site Structure

```
_posts/          ← Blog posts (Markdown)
_books/          ← Book entries
_projects/       ← Project entries  
_layouts/        ← Page templates
_includes/       ← Reusable HTML snippets
assets/
  css/main.css   ← All styles (one file)
  js/main.js     ← All JS (one file)
  img/           ← Images (profile.jpg etc)
scripts/
  sync_gdocs_to_posts.py  ← Google Docs sync script
.github/
  workflows/
    deploy.yml         ← Auto-deploy on push + daily sync
    maintenance.yml    ← Bi-annual dependency reminder
```
