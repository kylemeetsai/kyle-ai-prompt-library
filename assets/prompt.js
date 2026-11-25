// Prompt pages: copy buttons, NEW badges, and related prompts (only ones whose video is out).
(() => {
  const DAY = 864e5, NEW_DAYS = 14;
  const local = new Date(); const today = new Date(local.getFullYear(), local.getMonth(), local.getDate()).getTime();
  const dateOf = s => { const [y, m, d] = (s || '').split('-').map(Number); return new Date(y, m - 1, d).getTime(); };
  const isNew = s => today - dateOf(s) < NEW_DAYS * DAY && dateOf(s) <= today;

  document.querySelectorAll('[data-added]').forEach(el => {
    const badge = el.querySelector('.new'); if (badge && isNew(el.dataset.added)) badge.hidden = false;
  });
  const related = document.getElementById('related');
  if (related) {
    let shown = 0;
    [...related.children].forEach(c => { const ok = dateOf(c.dataset.added) <= today && shown < 3; c.hidden = !ok; if (ok) shown++; });
  }

  // Arriving here from the homepage drawer can leave its history entry behind: Back should go home.
  const here = location.pathname;
  addEventListener('popstate', () => { if (location.pathname !== here) location.reload(); });

  const box = document.getElementById('prompt-text');
  const flash = (btn, text, ms = 1800) => {
    if (!btn.dataset.label) btn.dataset.label = btn.textContent;
    btn.textContent = text; btn.classList.add('is-copied');
    clearTimeout(btn._t); btn._t = setTimeout(() => { btn.textContent = btn.dataset.label; btn.classList.remove('is-copied'); }, ms);
  };
  document.querySelectorAll('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(box.textContent); flash(btn, 'Copied ✓'); }
    catch (e) {
      const r = document.createRange(); r.selectNodeContents(box); const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      flash(btn, 'Selected, copy it now', 2600);
    }
  }));
})();
