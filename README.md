# Indica Tech Website

A modern, responsive consulting website for Indica Tech software consulting services.

## 🚀 Quick Start

### Option 1: Test Locally

1. Open the `index.html` file directly in your browser
2. Or use a local server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js (npx)
   npx serve
   ```
3. Visit `http://localhost:8000`

---

## Site look: the Board Room look (default) or the classic look

- `styles.css` is the classic look: warm paper, ink and terminal green, IBM Plex.
- `look.css` loads after it on every page and turns it into the Board Room look: navy and brass, Montserrat and Inter (in `fonts/`). It is light by default, and the sun/moon button in the nav switches to dark. The choice is saved in the visitor's browser (`indica-theme`) and the Board Room guided sample reads the same choice.
- `look.js` picks the look before the page paints. **To put every visitor back on the classic look**, change `var LOOK = "board";` to `var LOOK = "classic";` in `look.js` and deploy. Nothing else needs to change.
- To try either look in your own browser only, add `?look=classic` or `?look=board` to any page's address. It is remembered until you open a page with `?look=default`.
- The site as it was before the Board Room look is tagged `classic-look` in git.
- A new page needs these two lines at the end of its `<head>`, with the same relative path as its `styles.css`:

  ```html
  <link rel="stylesheet" href="look.css" id="look-css">
  <script src="look.js"></script>
  ```

- Not covered: the checklists (their own styles, from `checklists/build_checklists.py`), the two guided samples under `work/*/sample/` (their own designs), `index-print.html` and `linkedin-banner.html`. The diagrams at the top of each blog post keep their classic colours.

---

## 📦 Deploying to GitHub Pages (Step-by-Step)

### Step 1: Create a GitHub Account (if you don't have one)

1. Go to [github.com](https://github.com)
2. Click "Sign up" and create an account
3. Verify your email address

### Step 2: Create a New Repository

1. Log into GitHub
2. Click the **+** icon in the top right → **New repository**
3. Repository settings:
   - **Repository name**: `indica-tech` (or any name you prefer)
   - **Description**: "Indica Tech consulting website"
   - **Visibility**: Public (required for free GitHub Pages)
   - **DO NOT** check "Add a README file"
4. Click **Create repository**

### Step 3: Upload Your Files

**Option A: Using GitHub Web Interface (Easiest)**

1. In your new repository, click **"uploading an existing file"** link
2. Drag and drop these files:
   - `index.html`
   - `styles.css`
   - `script.js`
3. Add commit message: "Initial website upload"
4. Click **Commit changes**

**Option B: Using Git Command Line**

```bash
# Navigate to your project folder
cd indica-tech

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial website upload"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/indica-tech.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (tab at the top)
3. In the left sidebar, click **Pages**
4. Under "Source", select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
5. Click **Save**
6. Wait 2-5 minutes for deployment
7. Your site will be live at: `https://YOUR_USERNAME.github.io/indica-tech/`

---

## 🌐 Connecting Your GoDaddy Domain

### Step 5: Add Custom Domain in GitHub

1. In GitHub repo → **Settings** → **Pages**
2. Under "Custom domain", enter: `indica-tech.com`
3. Click **Save**
4. Check "Enforce HTTPS" (after DNS propagates)

---

## 🔧 Making Updates

### To update your website:

**Via GitHub Web:**
1. Go to your repo
2. Click on the file you want to edit (e.g., `index.html`)
3. Click the ✏️ pencil icon
4. Make changes
5. Click **Commit changes**
6. Changes deploy automatically in 1-2 minutes

**Via Git:**
```bash
# Make changes locally
# Then:
git add .
git commit -m "Update description"
git push
```

---

## 📁 Project Structure

```
indica-tech/
├── index.html      # Main HTML file
├── styles.css      # All styling
├── script.js       # JavaScript functionality
├── CNAME           # Custom domain config (create after setup)
└── README.md       # This file
```

---

## ✏️ Customization Guide

### Change Contact Email
In `index.html`, find and replace:
```html
<a href="mailto:hello@indica-tech.com"...>
```

### Update Statistics
Find the `.stat-card` elements and update numbers:
```html
<div class="stat-number">50+</div>
<div class="stat-label">Projects Delivered</div>
```

### Change Colors
In `styles.css`, modify the CSS variables:
```css
:root {
    --primary: #6366f1;        /* Main brand color */
    --primary-dark: #4f46e5;   /* Darker shade */
    --accent: #22d3ee;         /* Accent color */
}
```

### Add New Industry
In `index.html`, add within `.industries-grid`:
```html
<div class="industry-card">
    <div class="industry-icon">🎯</div>
    <h3>New Industry</h3>
    <p>Description here.</p>
</div>
```

---

## 📄 License

© 2025 Indica Tech. All rights reserved.
