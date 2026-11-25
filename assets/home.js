// Homepage: logo strip pause, video tabs, the searchable prompt library, the prompt drawer
// (each prompt also has its own page at /prompts/<slug>), and the hero's prompt hand-off.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };

  // ---------- dates: a prompt shows up the day its video posts ----------
  const DAY = 864e5, NEW_DAYS = 14;
  const now = new Date(); const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const dateOf = s => { const [y, m, d] = (s || '').split('-').map(Number); return new Date(y, m - 1, d).getTime(); };
  const isLive = s => dateOf(s) <= today;

  // ---------- moving logos: pause button ----------
  const toggle = $('motion-toggle');
  const PAUSE = '<path d="M3 2h2v8H3zM7 2h2v8H7z" fill="currentColor"/>', PLAY = '<path d="M3 1.5v9l7-4.5z" fill="currentColor"/>';
  toggle.addEventListener('click', () => {
    const paused = document.body.classList.toggle('paused');
    toggle.setAttribute('aria-pressed', paused);
    toggle.setAttribute('aria-label', paused ? 'Play the moving logos' : 'Pause the moving logos');
    toggle.firstElementChild.innerHTML = paused ? PLAY : PAUSE;
  });
  if (reduce) toggle.hidden = true;

  // ---------- videos: a still photo instead of motion when motion is reduced ----------
  if (reduce) {
    const call = $('call'); const img = new Image(); img.src = call.poster; img.alt = ''; call.replaceWith(img);
    const film = $('film'); film.removeAttribute('autoplay'); film.pause(); film.controls = true;
  }

  // ---------- copy ----------
  const flash = (btn, text, ms = 1800) => {
    if (!btn.dataset.label) btn.dataset.label = btn.innerHTML;
    btn.textContent = text; btn.classList.add('is-copied');
    clearTimeout(btn._t); btn._t = setTimeout(() => { btn.innerHTML = btn.dataset.label; btn.classList.remove('is-copied'); }, ms);
  };
  const copy = async (text, btn, selectEl) => {
    try { await navigator.clipboard.writeText(text); flash(btn, 'Copied ✓'); }
    catch (e) {
      if (selectEl) { const r = document.createRange(); r.selectNodeContents(selectEl); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }
      flash(btn, selectEl ? 'Selected, copy it now' : 'Open the prompt to copy', 2600);
    }
  };
  $('email-copy').addEventListener('click', e => copy($('email').textContent.trim(), e.currentTarget, $('email')));

  // ---------- video tabs ----------
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const selectTab = tab => tabs.forEach(t => { const on = t === tab; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; $(t.getAttribute('aria-controls')).hidden = !on; });
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', e => { if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return; const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; selectTab(n); n.focus(); });
  });

  // ---------- the prompt library ----------
  const TOPIC_WORDS = { money: 'money finance budget', agents: 'agents automation agent', content: 'content social', career: 'career job work', design: 'design', health: 'health life fitness', skills: 'skills skill' };
  const SYNONYMS = { cv: 'resume', email: 'email|gmail|inbox', mail: 'email|gmail|inbox', workout: 'workout|personal trainer|strength program|running coach', gym: 'personal trainer|workout|strength program', fitness: 'personal trainer|workout|strength program|running coach', run: 'running coach|strava', running: 'running coach|strava', diet: 'nutrition|nutritionist|meal', food: 'nutrition|meal|recipe', video: 'video|vids|motion', movie: 'movie|vids|video', photo: 'photo|image|picture', money: 'money|budget|savings|finance|refund', finance: 'finance|budget|savings|money', job: 'job|career|resume|interview', business: 'business|quote|lead|customer', social: 'social|instagram|tiktok|linkedin|caption|content', website: 'website|site', app: 'app|dashboard|tracker', ai: '' };
  const norm = t => (t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9+#.\s]/g, ' ');
  const grid = $('grid');
  const cards = [...grid.querySelectorAll('.p-card')].filter(c => {
    if (isLive(c.dataset.added)) return true;
    c.remove(); return false; // waiting for its video; its own page already works
  });
  cards.forEach(c => { if (today - dateOf(c.dataset.added) < NEW_DAYS * DAY) c.querySelector('.new').hidden = false; });
  const hay = cards.map(c => norm(c.textContent + ' ' + TOPIC_WORDS[c.dataset.topic] + ' ' + c.dataset.apps + ' ' + c.dataset.format));
  const tokens = q => norm(q).split(/\s+/).filter(w => w && SYNONYMS[w] !== '');
  const matches = (i, toks) => toks.every(w => { const alts = (SYNONYMS[w] || w).split('|'); if (!alts.includes(w)) alts.push(w); return alts.some(a => a && hay[i].includes(a)); });
  const state = { q: '', topic: 'all', app: 'all', all: false };
  const PAGE = matchMedia('(max-width: 640px)').matches ? 5 : 9;
  const filters = $('filters'), q = $('q'), more = $('more'), empty = $('empty'), count = $('count');

  const render = () => {
    const toks = tokens(state.q);
    const hits = cards.filter((c, i) => (state.topic === 'all' || c.dataset.topic === state.topic)
      && (state.app === 'all' || c.dataset.apps.split(' ').includes(state.app))
      && (!toks.length || matches(i, toks)));
    const showAll = state.all || toks.length > 0;
    cards.forEach(c => { c.hidden = true; });
    hits.forEach((c, i) => { c.hidden = !showAll && i >= PAGE; });
    empty.hidden = hits.length > 0;
    if (!hits.length) empty.textContent = toks.length ? `No prompts match “${q.value.trim()}”. Try a simpler word like “budget”, “resume” or “email”.` : 'No prompts here yet. Try another filter.';
    count.textContent = hits.length === cards.length ? `${cards.length} prompts and guides` : `${hits.length} of ${cards.length} prompts`;
    more.hidden = showAll || hits.length <= PAGE;
    more.textContent = `Show all ${hits.length} prompts`;
  };
  filters.addEventListener('click', e => {
    const b = e.target.closest('.chip'); if (!b) return;
    const { group, value } = b.dataset;
    state[group] = (group === 'app' && state.app === value) ? 'all' : value;
    filters.querySelectorAll(`.chip[data-group="${group}"]`).forEach(c => c.setAttribute('aria-pressed', c.dataset.value === state[group]));
    state.all = false; render();
  });
  q.addEventListener('input', () => { state.q = q.value; state.all = false; render(); });
  q.addEventListener('keydown', e => { if (e.key === 'Escape') { q.value = ''; state.q = ''; render(); } });
  more.addEventListener('click', () => { state.all = true; render(); });
  // A link like kylemeetsai.com/?q=budget opens the library already searched.
  const startQ = new URLSearchParams(location.search).get('q');
  if (startQ) { q.value = startQ; state.q = startQ; }
  render();
  if (startQ) requestAnimationFrame(() => $('prompts').scrollIntoView());

  // ---------- the drawer (the URL changes to the prompt's own page, so links and stats work) ----------
  const TOPICS = { money: 'Money', agents: 'Agents', content: 'Content', career: 'Career', design: 'Design', health: 'Health', skills: 'Skills' };
  const APPS = { claude: 'Claude', chatgpt: 'ChatGPT', gemini: 'Gemini' };
  let DATA = null, loading = null;
  const load = () => loading || (loading = fetch('/data/prompts.json').then(r => { if (!r.ok) throw r; return r.json(); })
    .then(d => { DATA = d; return d; }).catch(err => { loading = null; throw err; }));
  const preload = () => load().catch(() => {});
  if ('requestIdleCallback' in window) requestIdleCallback(preload, { timeout: 4000 }); else setTimeout(preload, 2500);

  const drawer = $('drawer'), homeTitle = document.title;
  let current = null, lastFocus = null;
  const fill = p => {
    current = p;
    $('d-topic').textContent = TOPICS[p.topic] || p.topic;
    $('d-title').textContent = p.title; $('d-desc').textContent = p.desc;
    $('d-apps').replaceChildren(...(p.apps.length ? p.apps.map(x => APPS[x] || x) : [p.tool]).filter(Boolean).map(x => el('span', 'app', x)));
    $('d-prompt').textContent = p.prompt;
    const names = p.apps.map(x => APPS[x] || x);
    const list = names.length > 1 ? names.slice(0, -1).join(', ') + ' or ' + names[names.length - 1] : (names[0] || p.tool || 'your AI chat');
    $('d-tip').textContent = p.format === 'skill' ? `See the full steps to set it up in ${list}.` : p.format === 'link' ? `Use these with ${list}. The full page has the steps.` : `Paste it into ${list} and answer its questions.`;
    const c = $('d-copy'); c.textContent = p.copy || 'Copy prompt'; c.dataset.label = c.textContent; c.classList.remove('is-copied');
    $('d-page').href = '/prompts/' + p.slug;
    const w = $('d-watch');
    if (p.tiktok) { w.hidden = false; w.href = `https://www.tiktok.com/@kyle.meets.ai/video/${p.tiktok}`; } else w.hidden = true;
    document.title = `${p.title} · KyleMeetsAI`;
  };
  const show = slug => {
    const p = DATA && DATA.find(x => x.slug === slug); if (!p) return false;
    fill(p);
    if (!drawer.open) { lastFocus = document.activeElement; drawer.showModal(); }
    $('d-prompt').scrollTop = 0; $('d-close').focus();
    return true;
  };
  const openPrompt = slug => load().then(() => {
    if (show(slug)) history.pushState({ drawer: slug }, '', '/prompts/' + slug);
    else location.href = '/prompts/' + slug;
  }).catch(() => { location.href = '/prompts/' + slug; });
  document.addEventListener('click', e => {
    const a = e.target.closest('a[data-drawer]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault(); openPrompt(a.dataset.drawer);
  });
  drawer.addEventListener('close', () => {
    document.title = homeTitle;
    if (history.state && history.state.drawer) history.back();
    if (lastFocus) lastFocus.focus({ preventScroll: true });
  });
  window.addEventListener('popstate', () => {
    const s = history.state;
    if (s && s.drawer) { if (!show(s.drawer)) location.reload(); }
    else if (drawer.open) drawer.close();
  });
  drawer.addEventListener('click', e => { if (e.target === drawer) drawer.close(); });
  $('d-close').addEventListener('click', () => drawer.close());
  $('d-copy').addEventListener('click', e => { if (current) copy(current.prompt, e.currentTarget, $('d-prompt')); });

  // ---------- the hero: Kyle's call tile hands over a new real prompt every few seconds ----------
  const HERO = JSON.parse($('hero-data').textContent);
  const heroBtn = $('hero-copy');
  let heroI = 0;
  heroBtn.addEventListener('click', () => copy(HERO[heroI].prompt, heroBtn, null));
  const showHero = i => {
    const h = HERO[i];
    $('h-text').textContent = h.text; $('h-name').textContent = h.name;
    $('h-link').href = '/prompts/' + h.slug; $('h-link').dataset.drawer = h.slug;
    $('h-apps').replaceChildren(...h.apps.map(a => el('span', 'app', a)));
  };
  if (!reduce) {
    const you = $('you'), card = $('handoff'), stage = document.querySelector('.stage');
    let hold = false;
    stage.addEventListener('pointerenter', () => { hold = true; });
    stage.addEventListener('pointerleave', () => { hold = false; });
    stage.addEventListener('focusin', () => { hold = true; });
    stage.addEventListener('focusout', () => { hold = false; });
    // A press and a ping only: nothing is copied until the visitor clicks for real.
    const press = () => {
      heroBtn.classList.add('is-pressed', 'is-pinged');
      setTimeout(() => heroBtn.classList.remove('is-pressed'), 140);
      setTimeout(() => heroBtn.classList.remove('is-pinged'), 800);
    };
    const cycle = () => {
      if (hold || document.hidden || drawer.open) { setTimeout(cycle, 1500); return; }
      you.classList.remove('is-there'); card.classList.add('is-swapping');
      setTimeout(() => { heroI = (heroI + 1) % HERO.length; showHero(heroI); card.classList.remove('is-swapping'); }, 380);
      setTimeout(() => you.classList.add('is-there'), 950);
      setTimeout(press, 2250);
      setTimeout(cycle, 5600);
    };
    const first = () => {
      setTimeout(() => you.classList.add('is-there'), 500);
      setTimeout(press, 1800);
      setTimeout(cycle, 5200);
    };
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); first(); } }, { threshold: 0.3 });
      io.observe(card);
    } else first();
  }
})();
