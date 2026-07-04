# DataDash — Premium Cloud Storage Platform

A production-quality cloud storage web application built with Python 3.13 and Django 5.

---

## Quick Start

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY at minimum
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 6. Collect static files (optional in dev)

```bash
python manage.py collectstatic
```

### 7. Start the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** — you'll be redirected to `/accounts/login/`.

---

## Project Structure

```
datadash/
├── datadash/           # Django project config (settings, urls, wsgi)
├── accounts/           # Auth app — User model, login/register/reset
├── storage/            # Core app — files, folders, trash, sharing, search
├── templates/          # HTML templates (Jinja2-style Django templates)
│   ├── base.html       # Main layout with sidebar, topbar, flash messages
│   ├── accounts/       # Auth page templates
│   └── storage/        # Dashboard, files, photos, shared, trash, settings
├── static/
│   ├── css/main.css    # Full design system — dark/light themes
│   └── js/main.js      # Theme switching, drag-drop upload, sidebar, etc.
├── media/              # Uploaded user files (auto-created)
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Features

### Authentication
- Registration, login, logout
- Forgot / reset password via email
- Remember me (persistent sessions)
- Secure sessions + CSRF protection
- Login history tracking

### Dashboard
- Storage usage ring with percentage
- Stats cards (files, photos, shared, trash)
- Recent uploads list
- Quick actions panel

### File Management
- Upload via drag-and-drop or file browser (multi-file)
- Create, rename, delete folders with colour coding
- Rename, delete, download, favourite files
- Grid view and list view toggle
- Sort by name / date / size
- Breadcrumb navigation through folder hierarchy

### Storage
- 3 GB per user (configurable via `MAX_STORAGE_BYTES` in `.env`)
- Real-time usage tracking
- Progress bar + percentage in sidebar
- Upgrade prompt when storage nears limit

### Trash System
- Soft-delete — files moved to Trash, not permanently removed
- Restore individual files / folders
- Permanent delete
- Empty Trash

### Photos
- Auto-detects uploaded images
- Masonry/grid gallery layout
- Lightbox (click to enlarge)
- Search and sort

### Sharing
- View files you've shared
- View files shared with you
- Permission levels (view / edit)
- Public link sharing

### Search
- Global search across files, folders, photos
- Keyboard shortcut: Ctrl/Cmd + K

### Settings
- Edit username, email, bio, avatar
- Dark / Light / System theme selector
- Default file view preference (grid/list)
- Storage breakdown
- Security — change password, login history
- Danger zone — delete account

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | **Required.** Django secret key |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts |
| `EMAIL_BACKEND` | console backend | Use SMTP in production |
| `EMAIL_HOST_USER` | — | Gmail address for password resets |
| `EMAIL_HOST_PASSWORD` | — | Gmail app password |
| `MAX_STORAGE_BYTES` | `3221225472` | 3 GB per user |

---

## Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Configure a real email backend (SMTP)
- [ ] Use PostgreSQL (`DATABASE_URL`)
- [ ] Run `collectstatic`
- [ ] Set up a reverse proxy (nginx/Caddy)
- [ ] Serve media files via nginx or cloud storage
- [ ] Enable HTTPS

---

## Architecture

- **`accounts` app** — Custom `User` model (UUID pk, email as USERNAME_FIELD, theme preference, avatar)
- **`storage` app** — `UserFile`, `Folder`, `SharedFile`, `UserStorageUsage` models
- **Context processor** — `storage_context` injects storage usage into every template
- **Soft deletes** — Files/folders have `is_deleted` + `deleted_at` fields; trash is a filter, not a separate table
- **Utilities** — `utils.py` handles MIME detection and storage quota checks before every upload
- **Design system** — CSS custom properties for full dark/light theming; `Kablammo` font for brand, `Inter` for UI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | Django ORM |
| Auth | Django's built-in auth + custom User model |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Typography | Kablammo (brand) + Inter (UI) |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Static files | WhiteNoise |
| Image handling | Pillow |
