/* ═══════════════════════════════════════════
   DataDash — Main JavaScript
═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Theme Management ──────────────────────
  const root = document.documentElement;
  const themeBtn = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');

  function applyTheme(theme) {
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.dataset.theme = prefersDark ? 'dark' : 'light';
    } else {
      root.dataset.theme = theme;
    }
    updateThemeIcon();
    localStorage.setItem('dd_theme', theme);
  }

  function updateThemeIcon() {
    if (!themeIcon) return;
    themeIcon.className = root.dataset.theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
  }

  const savedTheme = localStorage.getItem('dd_theme') || root.dataset.theme || 'dark';
  applyTheme(savedTheme);

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      const current = root.dataset.theme;
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
    if (localStorage.getItem('dd_theme') === 'system') applyTheme('system');
  });

  // ── Sidebar Mobile ────────────────────────
  const sidebar = document.getElementById('sidebar');
  const sidebarOpen = document.getElementById('sidebarOpen');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    sidebar && sidebar.classList.add('open');
    sidebarOverlay && sidebarOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar && sidebar.classList.remove('open');
    sidebarOverlay && sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';
  }

  sidebarOpen && sidebarOpen.addEventListener('click', openSidebar);
  sidebarToggle && sidebarToggle.addEventListener('click', closeSidebar);
  sidebarOverlay && sidebarOverlay.addEventListener('click', closeSidebar);

  // Close sidebar when clicking nav links on mobile
  if (sidebar) {
    sidebar.querySelectorAll('.nav-item').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 992) {
          closeSidebar();
        }
      });
    });
  }

  // ── Auto-dismiss Flash Messages ───────────
  const flashMessages = document.querySelectorAll('.flash-msg');
  flashMessages.forEach(function (msg) {
    setTimeout(function () {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(20px)';
      msg.style.transition = 'opacity 0.3s, transform 0.3s';
      setTimeout(() => msg.remove(), 300);
    }, 4500);
  });

  // ── File Upload / Drop Zone ───────────────
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const uploadForm = document.getElementById('uploadForm');
  const uploadProgress = document.getElementById('uploadProgress');
  const uploadFill = document.getElementById('uploadFill');
  const uploadStatus = document.getElementById('uploadStatus');
  const uploadBtn = document.getElementById('uploadBtn');

  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => fileInput.click());
  }

  if (dropZone && fileInput && uploadForm) {
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFileSelect);

    dropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', function () {
      dropZone.classList.remove('drag-over');
    });
    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      const dt = e.dataTransfer;
      if (dt.files.length) {
        fileInput.files = dt.files;
        handleFileSelect();
      }
    });

    function handleFileSelect() {
      if (!fileInput.files.length) return;
      const formData = new FormData(uploadForm);
      for (const f of fileInput.files) {
        formData.append('file', f);
      }

      if (uploadProgress) uploadProgress.classList.remove('d-none');
      if (uploadFill) uploadFill.style.width = '0%';
      if (uploadStatus) uploadStatus.textContent = 'Uploading…';

      const xhr = new XMLHttpRequest();
      xhr.open('POST', uploadForm.action);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

      xhr.upload.addEventListener('progress', function (e) {
        if (e.lengthComputable && uploadFill) {
          const pct = Math.round((e.loaded / e.total) * 100);
          uploadFill.style.width = pct + '%';
          if (uploadStatus) uploadStatus.textContent = `Uploading… ${pct}%`;
        }
      });

      xhr.addEventListener('load', function () {
        try {
          const data = JSON.parse(xhr.responseText);
          if (data.uploaded && data.uploaded.length) {
            if (uploadStatus) uploadStatus.textContent = `✓ ${data.uploaded.length} file(s) uploaded successfully.`;
            if (uploadFill) uploadFill.style.width = '100%';
            setTimeout(() => location.reload(), 800);
          }
          if (data.errors && data.errors.length) {
            if (uploadStatus) uploadStatus.textContent = data.errors.join('; ');
          }
        } catch {
          if (uploadStatus) uploadStatus.textContent = 'Upload complete.';
          setTimeout(() => location.reload(), 800);
        }
      });

      xhr.addEventListener('error', function () {
        if (uploadStatus) uploadStatus.textContent = 'Upload failed. Please try again.';
      });

      xhr.send(formData);
    }
  }

  // ── View Toggle (Grid / List) ─────────────
  const gridViewBtn = document.getElementById('gridViewBtn');
  const listViewBtn = document.getElementById('listViewBtn');
  const fileGrid = document.getElementById('fileGrid');

  const savedView = localStorage.getItem('dd_file_view') || 'grid';
  if (savedView === 'list' && fileGrid) {
    fileGrid.classList.add('file-list-mode');
  }

  if (gridViewBtn && listViewBtn && fileGrid) {
    gridViewBtn.addEventListener('click', function () {
      fileGrid.classList.remove('file-list-mode');
      gridViewBtn.classList.add('active');
      listViewBtn.classList.remove('active');
      localStorage.setItem('dd_file_view', 'grid');
    });
    listViewBtn.addEventListener('click', function () {
      fileGrid.classList.add('file-list-mode');
      listViewBtn.classList.add('active');
      gridViewBtn.classList.remove('active');
      localStorage.setItem('dd_file_view', 'list');
    });
  }

  // ── AJAX Favorite Toggle ─────────────────
  document.querySelectorAll('[data-fav-url]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.dataset.favUrl;
      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCsrfToken(),
        },
      })
        .then(r => r.json())
        .then(data => {
          const icon = this.querySelector('i');
          if (icon) {
            icon.className = data.favorited ? 'bi bi-star-fill' : 'bi bi-star';
          }
          this.classList.toggle('active-fav', data.favorited);
        });
    });
  });

  // ── Smooth section scrolling in Settings ──
  document.querySelectorAll('.settings-nav-item').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        document.querySelectorAll('.settings-nav-item').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // ── Search keyboard shortcut ─────────────
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.querySelector('.search-input');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // ── Storage ring gradient fix ─────────────
  // Inject the SVG gradient definition once
  const svgNs = 'http://www.w3.org/2000/svg';
  const defSvg = document.createElementNS(svgNs, 'svg');
  defSvg.style.position = 'absolute';
  defSvg.style.width = '0';
  defSvg.style.height = '0';
  defSvg.innerHTML = `
    <defs>
      <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#6366f1"/>
        <stop offset="100%" stop-color="#8b5cf6"/>
      </linearGradient>
    </defs>`;
  document.body.prepend(defSvg);

  // ── Utility ──────────────────────────────
  function getCsrfToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  // ── Mobile Viewport Height Fix ───────────
  // Fix for mobile browsers that show/hide address bar
  function setViewportHeight() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
  }
  setViewportHeight();
  window.addEventListener('resize', setViewportHeight);
  window.addEventListener('orientationchange', setViewportHeight);

  // ── Prevent double-tap zoom on buttons ───
  document.querySelectorAll('button, .btn-primary-dd, .btn-outline-dd, .icon-btn').forEach(btn => {
    btn.addEventListener('touchstart', () => {
      btn.style.pointerEvents = 'none';
    }, { passive: true });
    btn.addEventListener('touchend', () => {
      btn.style.pointerEvents = '';
    }, { passive: true });
  });

  // ── Improve input focus on mobile ────────
  document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea, select').forEach(input => {
    input.addEventListener('focus', () => {
      if (window.innerWidth < 768) {
        // Slight delay to ensure virtual keyboard opens
        setTimeout(() => {
          input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
      }
    });
  });

  // ── Close modals on mobile back button ────
  if (window.history && window.history.pushState) {
    window.addEventListener('popstate', () => {
      const modals = document.querySelectorAll('.modal.show');
      modals.forEach(modal => {
        const instance = bootstrap?.Modal?.getInstance(modal);
        if (instance) instance.hide();
      });
    });
  }
