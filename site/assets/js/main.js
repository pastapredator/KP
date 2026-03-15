/* ============================================================
   MAIN.JS — Krishnapriya PS site
   ============================================================ */

// ── NAV MOBILE TOGGLE ──
(function () {
  var toggle = document.getElementById('navToggle');
  var links  = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    links.classList.toggle('open');
    var isOpen = links.classList.contains('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!toggle.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
    }
  });
})();

// ── BOOK MODAL ──
(function () {
  var modal = document.getElementById('bookModal');
  var iframe = document.getElementById('bookIframe');
  var closeBtn = document.getElementById('bookModalClose');
  if (!modal) return;

  // Expose globally so onclick attrs work
  window.openBookModal = function (fileId, title) {
    if (!fileId) return;
    var titleEl = document.getElementById('bookModalTitle');
    if (titleEl) titleEl.textContent = title || 'Book Reader';

    // Build preview-only embed URL (no toolbar, no download button)
    iframe.src = 'https://drive.google.com/file/d/' + fileId + '/preview?usp=sharing';
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  };

  function closeModal() {
    modal.classList.remove('open');
    iframe.src = '';
    document.body.style.overflow = '';
  }

  closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', function (e) {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });

  // Disable right-click inside viewer area
  modal.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    return false;
  });
})();

// ── SCROLL REVEAL ── (lightweight, no library)
(function () {
  var els = document.querySelectorAll('.blog-card, .book-card, .project-card');
  if (!els.length || !window.IntersectionObserver) return;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  els.forEach(function (el, i) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.5s ease ' + (i % 3 * 0.1) + 's, transform 0.5s ease ' + (i % 3 * 0.1) + 's, box-shadow 0.25s ease, border-color 0.25s ease';
    observer.observe(el);
  });
})();

// ── ACTIVE NAV LINK ──
(function () {
  var path = window.location.pathname;
  var links = document.querySelectorAll('.nav__links a');
  links.forEach(function (a) {
    if (a.getAttribute('href') === path || (path !== '/' && path.startsWith(a.getAttribute('href')))) {
      a.classList.add('active');
    }
  });
})();
