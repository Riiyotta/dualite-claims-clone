/* ==========================================================================
   Dualite Claims — interaction and motion
   GSAP (ScrollTrigger, SplitText, ScrambleText, DrawSVG) drives everything
   tied to scroll; anime.js handles the intro seal, card choreography, the
   story cursor and small physical moments (stamps, shakes).
   ========================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  if (!window.gsap || !window.ScrollTrigger) {
    root.classList.remove('js');
    root.classList.add('no-loader');
    return;
  }

  var A = window.anime || null;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var isDesktop = function () { return window.innerWidth > 980; };

  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin, DrawSVGPlugin, CustomEase);
  CustomEase.create('codex', 'M0,0 C0.16,1 0.3,1 1,1');
  CustomEase.create('wipe', 'M0,0 C0.7,0 0.2,1 1,1');
  ScrollTrigger.config({ ignoreMobileResize: true });
  gsap.defaults({ ease: 'codex' });

  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  ScrollTrigger.clearScrollMemory('manual');

  /* ------------------------------------------------------------------------
     Smooth scroll (Lenis bridged into GSAP's ticker)
     ------------------------------------------------------------------------ */
  var lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ duration: 1.15, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
  function scrollToY(y, dur) {
    if (lenis) lenis.scrollTo(y, { duration: dur || 1.4 });
    else window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
  }
  function scrollToEl(el) {
    if (!el) return;
    if (lenis) lenis.scrollTo(el, { duration: 1.4 });
    else el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href');
    if (id === '#top') { e.preventDefault(); closeMenu(); scrollToY(0); return; }
    var target = id.length > 1 && document.getElementById(id.slice(1));
    if (!target) return;
    e.preventDefault();
    closeMenu();
    scrollToEl(target);
  });

  /* ------------------------------------------------------------------------
     Fixed-artboard scalers (product demo, platform plates, story stage)
     ------------------------------------------------------------------------ */
  function fitScalers() {
    $$('.scaler').forEach(function (sc) {
      var inner = sc.firstElementChild;
      var w = +sc.dataset.scaleW, h = +sc.dataset.scaleH || 0;
      if (sc.dataset.fit === 'contain') {
        var s = Math.min(sc.clientWidth / w, sc.clientHeight / h, 1.12);
        inner.style.transform = 'translate(-50%,-50%) scale(' + s + ')';
      } else {
        inner.style.width = w + 'px';
        var k = Math.min(1, sc.clientWidth / w);
        inner.style.transform = 'scale(' + k + ')';
        sc.style.height = Math.ceil(inner.offsetHeight * k) + 'px';
      }
    });
    var canvas = $('.stage__canvas'), art = $('.art');
    if (canvas && art) {
      var s2 = Math.min(canvas.clientWidth / 600, canvas.clientHeight / 420) * 0.96;
      art.style.setProperty('--art-s', s2.toFixed(4));
    }
  }
  fitScalers();
  if ('ResizeObserver' in window) {
    var ro = new ResizeObserver(function () { fitScalers(); });
    $$('.scaler, .stage__canvas').forEach(function (el) { ro.observe(el); });
  }
  window.addEventListener('resize', fitScalers);

  /* ------------------------------------------------------------------------
     Navigation: hide on scroll down, theme flip over dark sections, active link
     ------------------------------------------------------------------------ */
  var nav = $('#nav');
  var menuOpen = false;
  ScrollTrigger.create({
    start: 0, end: 'max', refreshPriority: -1,
    onUpdate: function (self) {
      var y = self.scroll();
      nav.classList.toggle('is-scrolled', y > 12);
      if (menuOpen) return;
      if (y > 240 && self.direction === 1 && self.getVelocity() > 40) nav.classList.add('is-hidden');
      else if (self.direction === -1 || y < 240) nav.classList.remove('is-hidden');
    }
  });
  var darkActive = 0;
  $$('[data-theme="dark"]').forEach(function (sec) {
    if (sec.id === 'mmenu') return;
    ScrollTrigger.create({
      trigger: sec, start: 'top top+=38', end: 'bottom top+=38', refreshPriority: -1,
      onToggle: function (self) { darkActive += self.isActive ? 1 : -1; nav.classList.toggle('is-dark', darkActive > 0); }
    });
  });
  $$('[data-nav]').forEach(function (link) {
    var sec = document.getElementById(link.dataset.nav);
    if (!sec) return;
    ScrollTrigger.create({
      trigger: sec, start: 'top 45%', end: 'bottom 45%', refreshPriority: -1,
      onToggle: function (self) { if (self.isActive) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current'); }
    });
  });
  gsap.to('.progress span', { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.3, refreshPriority: -1 } });

  /* Mobile menu: a clip-path curtain, links rise in */
  var burger = $('.burger'), mmenu = $('#mmenu');
  var menuTl = gsap.timeline({ paused: true })
    .set(mmenu, { visibility: 'visible' })
    .fromTo(mmenu, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.8, ease: 'wipe' })
    .from('.mmenu__links a', { yPercent: 60, autoAlpha: 0, duration: 0.9, stagger: 0.06 }, 0.3)
    .from('.mmenu__foot', { autoAlpha: 0, y: 20, duration: 0.8 }, 0.5);
  function openMenu() {
    menuOpen = true; root.classList.add('menu-open');
    burger.setAttribute('aria-expanded', 'true'); burger.setAttribute('aria-label', 'Close menu');
    mmenu.setAttribute('aria-hidden', 'false'); nav.classList.remove('is-hidden');
    if (lenis) lenis.stop();
    menuTl.timeScale(1).play();
  }
  function closeMenu() {
    if (!menuOpen) return;
    menuOpen = false; root.classList.remove('menu-open');
    burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-label', 'Open menu');
    mmenu.setAttribute('aria-hidden', 'true');
    if (lenis) lenis.start();
    menuTl.timeScale(1.6).reverse();
  }
  burger.addEventListener('click', function () { menuOpen ? closeMenu() : openMenu(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

  /* ------------------------------------------------------------------------
     Magnetic buttons (fine pointers only)
     ------------------------------------------------------------------------ */
  if (finePointer && !reduce) {
    $$('[data-magnetic]').forEach(function (el) {
      var xTo = gsap.quickTo(el, 'x', { duration: 0.6, ease: 'power3.out' });
      var yTo = gsap.quickTo(el, 'y', { duration: 0.6, ease: 'power3.out' });
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        xTo((e.clientX - r.left - r.width / 2) * 0.22);
        yTo((e.clientY - r.top - r.height / 2) * 0.3);
      });
      el.addEventListener('mouseleave', function () {
        gsap.to(el, { x: 0, y: 0, duration: 0.9, ease: 'elastic.out(1, 0.45)' });
      });
    });
  }

  /* ------------------------------------------------------------------------
     Text helpers
     ------------------------------------------------------------------------ */
  var SCRAMBLE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

  function prepEyebrows() {
    $$('[data-scramble]').forEach(function (el) {
      var idx = $('.eyebrow__idx', el);
      var text = '';
      Array.prototype.slice.call(el.childNodes).forEach(function (n) {
        if (n.nodeType === 3) { text += n.textContent; n.remove(); }
      });
      var span = document.createElement('span');
      span.className = 'eyebrow__txt';
      span.textContent = text.trim();
      el.appendChild(span);
      if (reduce) return;
      var final = span.textContent;
      span.textContent = '';
      if (idx) gsap.set(idx, { autoAlpha: 0 });
      ScrollTrigger.create({
        trigger: el, start: 'top 90%', once: true,
        onEnter: function () {
          if (idx) gsap.to(idx, { autoAlpha: 1, duration: 0.3, ease: 'none', repeat: 3, yoyo: true, repeatDelay: 0.03, onComplete: function () { gsap.set(idx, { autoAlpha: 1 }); } });
          gsap.to(span, { duration: 1.1, scrambleText: { text: final, chars: SCRAMBLE, speed: 0.5, revealDelay: 0.15 }, ease: 'none' });
        }
      });
    });
  }

  function splitHeadings() {
    $$('[data-split]').forEach(function (el) {
      if (reduce) return;
      SplitText.create(el, {
        type: 'lines', mask: 'lines', autoSplit: true,
        onSplit: function (self) {
          return gsap.from(self.lines, {
            yPercent: 112, rotate: 2.5, transformOrigin: '0% 0%', duration: 1.35, stagger: 0.1, ease: 'expo.out',
            scrollTrigger: { trigger: el, start: 'top 88%', once: true }
          });
        }
      });
    });
  }

  function reveals() {
    $$('[data-reveal]').forEach(function (el) {
      if (reduce) { gsap.set(el, { autoAlpha: 1 }); return; }
      var up = el.dataset.reveal === 'up';
      var from = { autoAlpha: 0, y: up ? 70 : 24 };
      if (isDesktop()) from.filter = 'blur(8px)';
      gsap.fromTo(el, from, {
        autoAlpha: 1, y: 0, filter: 'blur(0px)', duration: up ? 1.5 : 1.2, ease: 'expo.out', clearProps: 'filter',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true }
      });
    });
  }

  function scrubWords() {
    $$('[data-scrub-words]').forEach(function (el) {
      var split = SplitText.create(el, { type: 'words', wordsClass: 'w' });
      if (reduce) return;
      gsap.fromTo(split.words, { opacity: 0.13 }, {
        opacity: 1, stagger: 0.1, ease: 'none',
        scrollTrigger: { trigger: el, start: 'top 80%', end: 'bottom 48%', scrub: true }
      });
    });
  }

  function parallax() {
    if (reduce) return;
    $$('[data-parallax]').forEach(function (el) {
      var amt = parseFloat(el.dataset.parallax) || 8;
      var sec = el.closest('section') || el;
      var atTop = sec.offsetTop < 10;
      gsap.fromTo(el, { yPercent: atTop ? 0 : -amt }, {
        yPercent: amt, ease: 'none',
        scrollTrigger: { trigger: sec, start: atTop ? 'top top' : 'top bottom', end: 'bottom top', scrub: true }
      });
    });
  }

  /* ------------------------------------------------------------------------
     Hero
     ------------------------------------------------------------------------ */
  var heroSplit = null;
  function prepHero() {
    var h1 = $('[data-split-hero]');
    if (reduce) { gsap.set('[data-hero]', { autoAlpha: 1 }); return; }
    heroSplit = SplitText.create(h1, { type: 'words', mask: 'words', wordsClass: 'split-word' });
    gsap.set(heroSplit.words, { yPercent: 118, rotate: 3 });
  }

  function heroIntro() {
    if (reduce) return;
    var tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    tl.set('[data-hero]', { autoAlpha: 1 })
      .from('.nav__in > *', { y: -24, autoAlpha: 0, duration: 1.2, stagger: 0.08 }, 0.1)
      .from('.hero__guides i', { scaleY: 0, duration: 1.8, stagger: 0.07, ease: 'expo.inOut' }, 0)
      .from('.hero__eyebrow', { y: 16, autoAlpha: 0, duration: 1 }, 0.2)
      .to(heroSplit.words, { yPercent: 0, rotate: 0, duration: 1.5, stagger: 0.055 }, 0.25)
      .from('.hero__sub', { y: 26, autoAlpha: 0, filter: 'blur(10px)', duration: 1.4, clearProps: 'filter' }, 0.7)
      .from('.hero__ctas > *', { y: 26, autoAlpha: 0, duration: 1.2, stagger: 0.09 }, 0.85)
      .from('.hero__copy > .micro', { autoAlpha: 0, duration: 1 }, 1.1)
      .from('.hero__scene', { y: 60, autoAlpha: 0, scale: 0.96, duration: 2, ease: 'expo.out' }, 0.35)
      .from('.plate__corner', { scale: 0, duration: 0.9, stagger: 0.06, ease: 'back.out(3)' }, 1.0)
      .from('.hero__foot > *', { y: 22, autoAlpha: 0, duration: 1.1, stagger: 0.07 }, 1.0)
      .add(startStatusTicker, 1.6);
    return tl;
  }

  function startStatusTicker() {
    var el = $('[data-status]');
    if (!el || reduce) return;
    var list = ['Reading discharge summary', 'Checking 50+ case rules', 'Collating 14 pages', 'Applying Digistamp', 'Draft saved on RGHS portal'];
    var i = 0;
    setInterval(function () {
      if (document.hidden) return;
      i = (i + 1) % list.length;
      gsap.to(el, { duration: 0.9, scrambleText: { text: list[i], chars: SCRAMBLE.toLowerCase(), speed: 0.6 }, ease: 'none' });
    }, 2800);
  }

  function heroScroll() {
    if (reduce) return;
    gsap.to('.hero__copy', {
      yPercent: -14, autoAlpha: 0.25, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
    });
    var svg = $('.iso-hero-scene');
    if (svg) {
      ScrollTrigger.create({ trigger: '.hero', start: 'top top', end: 'bottom top', onToggle: function (s) { svg.classList.toggle('is-paused', !s.isActive); } });
    }
  }

  /* ------------------------------------------------------------------------
     Proof quote: words resolve in (anime.js)
     ------------------------------------------------------------------------ */
  function proofQuote() {
    var p = $('[data-words]');
    if (!p || reduce || !A) return;
    var split = SplitText.create(p, { type: 'words' });
    A.utils.set(split.words, { opacity: 0.08 });
    ScrollTrigger.create({
      trigger: p, start: 'top 88%', once: true,
      onEnter: function () {
        A.animate(split.words, {
          opacity: [0.08, 1], translateY: ['0.35em', '0em'], filter: ['blur(6px)', 'blur(0px)'],
          duration: 900, delay: A.stagger(55), ease: 'outExpo'
        });
      }
    });
  }

  /* ------------------------------------------------------------------------
     Problem: cost cards (anime.js choreography + GSAP scramble)
     ------------------------------------------------------------------------ */
  function costs() {
    var wrap = $('[data-costs]');
    if (!wrap || reduce) return;
    var cards = $$('.cost', wrap), vals = $$('[data-scramble-v]', wrap);
    var finals = vals.map(function (v) { return v.textContent; });
    if (A) A.utils.set(cards, { opacity: 0, translateY: 70 });
    else gsap.set(cards, { autoAlpha: 0, y: 70 });
    vals.forEach(function (v) { v.style.minHeight = '1em'; v.textContent = ' '; });
    ScrollTrigger.create({
      trigger: wrap, start: 'top 82%', once: true,
      onEnter: function () {
        if (A) A.animate(cards, { opacity: [0, 1], translateY: [70, 0], duration: 1300, delay: A.stagger(120), ease: 'outExpo' });
        else gsap.to(cards, { autoAlpha: 1, y: 0, duration: 1.3, stagger: 0.12 });
        vals.forEach(function (v, i) {
          gsap.to(v, { delay: 0.35 + i * 0.14, duration: 1.1, scrambleText: { text: finals[i], chars: '0123456789#%₹X', speed: 0.45 }, ease: 'none' });
        });
      }
    });
  }

  /* ------------------------------------------------------------------------
     Results: section expands in, odometers roll, arrow draws
     ------------------------------------------------------------------------ */
  function results() {
    var sec = $('.results');
    if (!sec) return;
    if (!reduce) {
      gsap.fromTo(sec, { clipPath: 'inset(6% 3% 0% 3% round 28px)' }, {
        clipPath: 'inset(0% 0% 0% 0% round 0px)', ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top bottom', end: 'top 25%', scrub: true }
      });
    }
    $$('[data-odo]').forEach(function (el) {
      var target = el.dataset.odo, from = el.dataset.from;
      var cols = [];
      target.split('').forEach(function (ch, ci) {
        var d = +ch, seq = [];
        if (from != null) { for (var n = +from; n >= d; n--) seq.push(n); }
        else { var spins = ci + 1; for (var s = 0; s < spins; s++) for (var k = 0; k < 10; k++) seq.push(k); for (var m = 0; m <= d; m++) seq.push(m); }
        var col = document.createElement('span');
        col.className = 'odo__col';
        col.innerHTML = seq.map(function (n) { return '<span>' + n + '</span>'; }).join('');
        el.appendChild(col);
        cols.push({ el: col, len: seq.length });
      });
      el.setAttribute('aria-hidden', 'true');
      if (reduce) { cols.forEach(function (c) { gsap.set(c.el, { yPercent: -100 * (c.len - 1) / c.len }); }); return; }
      ScrollTrigger.create({
        trigger: el, start: 'top 85%', once: true,
        onEnter: function () {
          cols.forEach(function (c, i) {
            gsap.to(c.el, { yPercent: -100 * (c.len - 1) / c.len, duration: from != null ? 1.6 : 2.2 + i * 0.25, ease: 'power4.inOut', delay: 0.15 });
          });
        }
      });
    });
    var arrow = $$('.metric__arrow .draw');
    if (arrow.length && !reduce) {
      gsap.set(arrow, { drawSVG: '0%' });
      gsap.to(arrow, { drawSVG: '100%', duration: 0.9, stagger: 0.25, ease: 'power2.inOut', scrollTrigger: { trigger: '.metrics', start: 'top 85%', once: true } });
    }
  }

  /* ------------------------------------------------------------------------
     How a file moves: pinned, scrubbed story
     ------------------------------------------------------------------------ */
  function movement() {
    var sec = $('.move'), stage = $('[data-stage]');
    if (!sec || !stage) return;
    var q = function (s) { return $(s, stage); }, qa = function (s) { return $$(s, stage); };
    var doc = q('.a-doc'), scan = q('.a-scan'), hls = qa('.a-field__hl'), tags = qa('.a-tag');
    var rules = q('.a-rules'), ruleRows = qa('.a-rule'), pages = qa('.a-page'), index = q('.a-index'), idxRows = qa('.a-index__row');
    var counter = q('.a-counter'), pips = qa('.a-pips i'), stamp = q('.a-stamp'), ink = q('.a-ink'), sealmark = q('.a-sealmark');
    var sign = q('.a-sign__path'), portal = q('.a-portal'), ok = q('.a-portal__ok'), wIn = q('.w-in'), wOut = q('.w-out');
    var fills = qa('[data-fill]');

    var names = ['Watch', 'Read', 'Validate', 'Organise', 'Digistamp', 'Submit'];
    var starts = [0, 1.1, 2.2, 3.3, 4.4, 5.6];
    var secs = [3, 7, 11, 14, 19, 26];
    var logs = [
      'Picked up from /scans/incoming',
      'Read patient, admission and bill data · 14 pages',
      '50+ case rules run · 1 item flagged for review',
      'Collated into one indexed PDF · 14 pages',
      'Seal and signature applied · 9 of 9 pages',
      'Saved on RGHS portal as draft · acknowledgement stored'
    ];
    var pgLabels = ['SCAN · 1 FILE', 'READING · 14 PP', 'CHECKING', '14 PP · INDEXED', 'SEALED 9/9', 'DRAFT ON PORTAL'];
    var TOTAL = 7.0;

    var hudStep = q('[data-stage-step]'), hudClock = q('[data-stage-clock]'), logEl = q('[data-stage-log]');
    var pgEl = q('[data-doc-pg]'), rulesCount = q('[data-rules-count]'), sealCount = q('[data-seal-count]');
    var stepEls = $$('.step', sec), descs = $$('.move__desc p', sec), fill = $('.steps__fill', sec);

    gsap.set(doc, { y: 200, scale: 0.4, autoAlpha: 0, transformOrigin: '50% 100%' });
    gsap.set([wIn, wOut, sign], { drawSVG: '0%' });
    gsap.set(stamp, { y: -40, autoAlpha: 0 });
    gsap.set(descs, { autoAlpha: 0 });
    gsap.set(descs[0], { autoAlpha: 1 });

    var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    // 01 Watch
    tl.to(wIn, { drawSVG: '100%', duration: 0.45, ease: 'power1.inOut' }, 0.05)
      .to(doc, { y: 0, scale: 1, autoAlpha: 1, duration: 0.8 }, 0.2);
    // 02 Read
    var s = starts[1];
    tl.to(wIn, { drawSVG: '100% 100%', duration: 0.4, ease: 'power1.in' }, s)
      .fromTo(scan, { top: '0%', autoAlpha: 0 }, { top: '0%', autoAlpha: 1, duration: 0.08, ease: 'none', immediateRender: false }, s)
      .to(scan, { top: '100%', duration: 0.85, ease: 'none' }, s + 0.05)
      .to(scan, { autoAlpha: 0, duration: 0.08, ease: 'none' }, s + 0.9)
      .to(hls, { autoAlpha: 1, duration: 0.15, stagger: 0.14, ease: 'none' }, s + 0.2)
      .fromTo(tags, { autoAlpha: 0, x: 18 }, { autoAlpha: 1, x: 0, duration: 0.3, stagger: 0.1 }, s + 0.25);
    // 03 Validate
    s = starts[2];
    tl.to(tags, { autoAlpha: 0, x: -12, duration: 0.2, stagger: 0.03, ease: 'power2.in' }, s)
      .to(hls, { autoAlpha: 0, duration: 0.2 }, s)
      .fromTo(rules, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.35 }, s + 0.15)
      .to(ruleRows, { opacity: 1, duration: 0.12, stagger: 0.13, ease: 'none' }, s + 0.3)
      .fromTo(ruleRows[2], { backgroundColor: '#FFFDF8' }, { backgroundColor: '#FBF4E6', duration: 0.2 }, s + 0.55);
    // 04 Organise
    s = starts[3];
    tl.to(rules, { autoAlpha: 0, y: -12, duration: 0.25, ease: 'power2.in' }, s)
      .set(pages, { autoAlpha: 1 }, s + 0.05)
      .to(pages, { x: function (i) { return (i - 2) * 30; }, y: function (i) { return -8 - Math.abs(i - 2) * 6; }, rotate: function (i) { return (i - 2) * 6; }, duration: 0.4, ease: 'power2.out' }, s + 0.05)
      .to(doc, { scale: 0.94, duration: 0.3 }, s + 0.05)
      .to(pages, { x: 0, y: 0, rotate: 0, duration: 0.4, ease: 'power2.inOut', stagger: 0.03 }, s + 0.5)
      .to(doc, { scale: 1, duration: 0.3 }, s + 0.62)
      .set(pages, { autoAlpha: 0 }, s + 0.95)
      .fromTo(index, { autoAlpha: 0, x: 18 }, { autoAlpha: 1, x: 0, duration: 0.35 }, s + 0.4)
      .fromTo(idxRows, { autoAlpha: 0, x: 8 }, { autoAlpha: 1, x: 0, duration: 0.2, stagger: 0.06 }, s + 0.5);
    // 05 Digistamp
    s = starts[4];
    tl.to(index, { autoAlpha: 0, x: -12, duration: 0.25, ease: 'power2.in' }, s)
      .fromTo(counter, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.3 }, s + 0.1)
      .to(stamp, { autoAlpha: 1, duration: 0.1, ease: 'none' }, s + 0.05)
      .to(stamp, { y: 311, duration: 0.42, ease: 'power3.in' }, s + 0.05)
      .to(stamp, { scaleY: 0.93, transformOrigin: '50% 100%', duration: 0.06, ease: 'none' }, s + 0.47)
      .fromTo(sealmark, { autoAlpha: 0, scale: 1.5, rotate: -30 }, { autoAlpha: 1, scale: 1, rotate: -12, duration: 0.2, ease: 'back.out(2)' }, s + 0.49)
      .fromTo(ink, { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1.6, duration: 0.2, ease: 'power2.out' }, s + 0.49)
      .to(ink, { autoAlpha: 0, duration: 0.3 }, s + 0.7)
      .to(stamp, { scaleY: 1, y: 120, duration: 0.35, ease: 'power2.out' }, s + 0.56)
      .to(stamp, { autoAlpha: 0, duration: 0.15 }, s + 0.8)
      .to(sign, { drawSVG: '100%', duration: 0.35, ease: 'power1.inOut' }, s + 0.6)
      .to(pips, { backgroundColor: '#3D5A2A', duration: 0.05, stagger: 0.045, ease: 'none' }, s + 0.5);
    // 06 Submit
    s = starts[5];
    tl.to(counter, { autoAlpha: 0, y: -12, duration: 0.25, ease: 'power2.in' }, s)
      .to(doc, { x: -70, scale: 0.72, duration: 0.55, ease: 'power3.inOut' }, s + 0.05)
      .fromTo(portal, { autoAlpha: 0, x: 26 }, { autoAlpha: 1, x: 0, duration: 0.4 }, s + 0.3)
      .to(wOut, { drawSVG: '100%', duration: 0.35, ease: 'power1.inOut' }, s + 0.45)
      .fromTo(ok, { autoAlpha: 0, y: 6 }, { autoAlpha: 1, y: 0, duration: 0.2 }, s + 1.05)
      .to({}, { duration: TOTAL - (s + 1.25) }, s + 1.25);

    var fillText = fills.map(function (f) { return f.dataset.fill; });
    var current = -1;
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };

    function stateAt(t) {
      var idx = 0;
      for (var i = 0; i < starts.length; i++) if (t >= starts[i] - 0.001) idx = i;
      var next = idx < starts.length - 1 ? starts[idx + 1] : TOTAL;
      var local = gsap.utils.clamp(0, 1, (t - starts[idx]) / (next - starts[idx]));
      var prevSec = idx === 0 ? 0 : secs[idx - 1];
      var elapsed = Math.round(prevSec + (secs[idx] - prevSec) * Math.min(1, local * 1.4));
      hudClock.textContent = '00:' + pad(elapsed);
      pgEl.textContent = pgLabels[idx];
      rulesCount.textContent = (idx > 2 || (idx === 2 && local > 0.55)) ? '1 FOR REVIEW' : 'RUNNING…';
      var sc = idx > 4 ? 9 : idx < 4 ? 0 : Math.round(gsap.utils.clamp(0, 1, (t - starts[4] - 0.5) / 0.4) * 9);
      sealCount.textContent = sc;
      var ft = idx < 5 ? 0 : gsap.utils.clamp(0, 1, (t - starts[5] - 0.55) / 0.5);
      fills.forEach(function (f, i) {
        var txt = fillText[i], n = Math.round(txt.length * gsap.utils.clamp(0, 1, ft * 1.6 - i * 0.3));
        f.textContent = n ? txt.slice(0, n) : ' ';
      });
      if (fill) fill.style.transform = 'scaleY(' + gsap.utils.clamp(0, 1, t / (TOTAL - 0.2)) + ')';
      if (idx !== current) setStep(idx);
    }

    function setStep(idx) {
      var prev = current;
      current = idx;
      hudStep.textContent = 'Step ' + pad(idx + 1) + ' / 06 · ' + names[idx];
      logEl.textContent = '00:' + pad(secs[idx]) + '  ' + logs[idx];
      stepEls.forEach(function (el, i) { el.classList.toggle('is-active', i === idx); el.classList.toggle('is-done', i < idx); });
      if (prev > -1 && descs[prev]) gsap.to(descs[prev], { autoAlpha: 0, y: idx > prev ? -14 : 14, duration: 0.35, ease: 'power2.in', overwrite: true });
      gsap.fromTo(descs[idx], { autoAlpha: 0, y: idx > prev ? 14 : -14 }, { autoAlpha: 1, y: 0, duration: 0.6, delay: prev > -1 ? 0.18 : 0, ease: 'expo.out', overwrite: true });
      if (!reduce) gsap.fromTo(logEl, { autoAlpha: 0.2 }, { autoAlpha: 1, duration: 0.4, ease: 'none' });
    }

    var st = ScrollTrigger.create({
      trigger: sec, pin: '.move__pin', start: 'top top',
      end: function () { return '+=' + Math.round(window.innerHeight * 5.2); },
      scrub: reduce ? true : 0.9, animation: tl, invalidateOnRefresh: true, anticipatePin: 1
    });
    tl.eventCallback('onUpdate', function () { stateAt(tl.time()); });
    stateAt(0);

    stepEls.forEach(function (el, i) {
      el.setAttribute('tabindex', '0');
      el.setAttribute('role', 'button');
      el.setAttribute('aria-label', 'Jump to step ' + (i + 1) + ': ' + names[i]);
      var go = function () { scrollToY(st.start + (st.end - st.start) * ((starts[i] + 0.9) / TOTAL), 1.2); };
      el.addEventListener('click', go);
      el.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    });
  }

  /* ------------------------------------------------------------------------
     Product demo: 3D tilt into place, autoplaying batch walkthrough
     ------------------------------------------------------------------------ */
  function productDemo() {
    if (!reduce) {
      gsap.fromTo('.demo__tilt', { rotateX: 24, scale: 0.88, y: 60 }, {
        rotateX: 0, scale: 1, y: 0, ease: 'none',
        scrollTrigger: { trigger: '.demo__stage', start: 'top 98%', end: 'top 30%', scrub: true }
      });
    }
    var pd = $('#pd');
    if (!pd) return;
    var timer = null, cur = 0, inView = false;
    function show(i) { cur = i; pd.className = 'pd pd-s' + i; }
    function run() { clearInterval(timer); timer = setInterval(function () { show((cur + 1) % 7); }, 3600); }
    $$('[data-go]').forEach(function (b) { b.addEventListener('click', function () { show(+b.dataset.go); if (inView && !reduce) run(); }); });
    if (reduce) return;
    ScrollTrigger.create({
      trigger: pd, start: 'top 75%', end: 'bottom top',
      onToggle: function (s) { inView = s.isActive; if (inView) { show(cur); run(); } else clearInterval(timer); }
    });
  }

  /* ------------------------------------------------------------------------
     Platform tabs: clip-path wipe between plates, timed autoplay
     ------------------------------------------------------------------------ */
  function platform() {
    var tabs = $$('.pf__tab'), panels = $$('.pf__panel');
    if (!tabs.length) return;
    var cur = 0, auto = !reduce, bar = null, inView = false, hovering = false;
    function select(n, user) {
      if (n === cur && !user) return;
      var prev = panels[cur];
      tabs.forEach(function (t, i) { var on = i === n; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; });
      if (n !== cur) {
        panels[n].classList.add('is-active');
        gsap.set(panels[n], { zIndex: 2 }); gsap.set(prev, { zIndex: 1 });
        if (!reduce) {
          gsap.fromTo(panels[n], { clipPath: 'inset(0% 0% 0% 100%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1, ease: 'expo.inOut', onComplete: function () { prev.classList.remove('is-active'); } });
          gsap.fromTo($('.scaler__inner > div', panels[n]), { x: 60, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 1.2, delay: 0.3, ease: 'expo.out' });
          gsap.to($('.scaler__inner > div', prev), { x: -40, duration: 1, ease: 'expo.inOut', onComplete: function () { gsap.set(this.targets(), { x: 0 }); } });
        } else prev.classList.remove('is-active');
      }
      cur = n;
      fitScalers();
      if (user) { auto = false; if (bar) bar.kill(); gsap.set('.pf__bar i', { scaleY: 0 }); gsap.set($('.pf__bar i', tabs[n]), { scaleY: 1 }); }
      else if (auto) startBar();
    }
    function startBar() {
      if (bar) bar.kill();
      gsap.set('.pf__bar i', { scaleY: 0 });
      bar = gsap.to($('.pf__bar i', tabs[cur]), { scaleY: 1, duration: 7, ease: 'none', paused: !inView || hovering, onComplete: function () { select((cur + 1) % tabs.length); } });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i, true); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = null;
        if (k === 'ArrowDown' || k === 'ArrowRight') n = (i + 1) % tabs.length;
        if (k === 'ArrowUp' || k === 'ArrowLeft') n = (i - 1 + tabs.length) % tabs.length;
        if (n !== null) { e.preventDefault(); tabs[n].focus(); select(n, true); }
      });
    });
    var pf = $('.pf');
    pf.addEventListener('mouseenter', function () { hovering = true; if (bar) bar.pause(); });
    pf.addEventListener('mouseleave', function () { hovering = false; if (bar && inView && auto) bar.play(); });
    if (auto) {
      startBar();
      ScrollTrigger.create({ trigger: pf, start: 'top 70%', end: 'bottom 20%', onToggle: function (s) { inView = s.isActive; if (!bar || !auto) return; if (inView && !hovering) bar.play(); else bar.pause(); } });
    } else gsap.set($('.pf__bar i', tabs[0]), { scaleY: 1 });
  }

  /* ------------------------------------------------------------------------
     Trust: plate opens up, guarantee grid draws in
     ------------------------------------------------------------------------ */
  function trust() {
    var frame = $('[data-clip]');
    if (frame && !reduce) {
      gsap.fromTo(frame, { clipPath: 'inset(16% 16% 16% 16%)' }, { clipPath: 'inset(0% 0% 0% 0%)', ease: 'none', scrollTrigger: { trigger: frame, start: 'top 95%', end: 'top 30%', scrub: true } });
      gsap.fromTo($('video', frame), { scale: 1.35 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: frame, start: 'top bottom', end: 'bottom top', scrub: true } });
    }
    var g = $('[data-guarantees]');
    if (!g || reduce) return;
    var items = $$('.g', g), rule = $('.guarantees__rule', g);
    gsap.set(rule, { scaleX: 0 });
    if (A) A.utils.set(items, { opacity: 0, translateY: 30 }); else gsap.set(items, { autoAlpha: 0, y: 30 });
    ScrollTrigger.create({
      trigger: g, start: 'top 85%', once: true,
      onEnter: function () {
        gsap.to(rule, { scaleX: 1, duration: 1.4, ease: 'expo.inOut' });
        if (A) A.animate(items, { opacity: [0, 1], translateY: [30, 0], duration: 1100, delay: A.stagger(110, { start: 250 }), ease: 'outExpo' });
        else gsap.to(items, { autoAlpha: 1, y: 0, duration: 1.1, stagger: 0.11, delay: 0.25 });
      }
    });
    // Autoplay the trust study only while visible
    var vid = frame && $('video', frame);
    if (vid) {
      vid.muted = true;
      if (reduce) vid.pause();
      else ScrollTrigger.create({ trigger: frame, start: 'top bottom', end: 'bottom top', onToggle: function (s) { if (s.isActive) { var p = vid.play(); if (p && p.catch) p.catch(function () {}); } else vid.pause(); } });
    }
  }

  /* ------------------------------------------------------------------------
     Reconciliation: three sources flow into one dashboard
     ------------------------------------------------------------------------ */
  function reconciliation() {
    var board = $('[data-recon]');
    if (!board || reduce) return;
    var srcs = $$('[data-recon-src]', board), dash = $('[data-recon-dash]', board);
    var wires = $$('.recon__wires path', board), rows = $$('.rrow:not(.rrow--head)', board);
    var chips = $$('.rchip', board), counts = $$('[data-count]', board), flag = $('.rrow--flag', board);
    gsap.set(srcs, { autoAlpha: 0, x: -36 });
    gsap.set(wires, { autoAlpha: 0 });
    gsap.set(dash, { autoAlpha: 0, y: 50 });
    gsap.set(rows, { autoAlpha: 0, y: 14 });
    gsap.set(chips, { scale: 0.6, autoAlpha: 0 });
    ScrollTrigger.create({
      trigger: board, start: 'top 78%', once: true,
      onEnter: function () {
        var tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
        tl.to(srcs, { autoAlpha: 1, x: 0, duration: 1.1, stagger: 0.12 }, 0)
          .to(wires, { autoAlpha: 1, duration: 0.8, stagger: 0.1, ease: 'power2.out' }, 0.45)
          .to(dash, { autoAlpha: 1, y: 0, duration: 1.3 }, 0.55)
          .to(rows, { autoAlpha: 1, y: 0, duration: 0.8, stagger: 0.09 }, 1.0)
          .to(chips, { autoAlpha: 1, scale: 1, duration: 0.6, stagger: 0.09, ease: 'back.out(2.2)' }, 1.25);
        counts.forEach(function (el) {
          var end = parseFloat(el.dataset.count), o = { v: 0 };
          tl.to(o, { v: end, duration: 1.6, ease: 'power3.out', onUpdate: function () { el.textContent = o.v.toFixed(1); } }, 0.8);
        });
        if (flag) tl.fromTo(flag, { backgroundColor: '#FDF3EC' }, { backgroundColor: '#F9DCCB', duration: 0.5, repeat: 3, yoyo: true, ease: 'sine.inOut' }, 2.1);
      }
    });
  }

  /* ------------------------------------------------------------------------
     Customer story: a play button that follows the cursor (anime.js)
     ------------------------------------------------------------------------ */
  function story() {
    var box = $('[data-story]');
    if (!box) return;
    var sec = $('.story'), video = $('video', box), btn = $('.story__play', box);
    var follow = null;
    function center() { return { x: box.clientWidth / 2, y: box.clientHeight / 2 }; }
    function place(x, y, instant) {
      if (follow && !instant) { follow.x(x); follow.y(y); }
      else gsap.set(btn, { x: x, y: y });
    }
    if (A && finePointer && !reduce) {
      follow = A.createAnimatable(btn, { x: 700, y: 700, ease: 'out(4)' });
    }
    var c = center(); place(c.x, c.y, true);
    if (follow) { follow.x(c.x, 0); follow.y(c.y, 0); }
    window.addEventListener('resize', function () { if (!sec.classList.contains('is-playing')) { var c2 = center(); place(c2.x, c2.y, true); if (follow) { follow.x(c2.x, 0); follow.y(c2.y, 0); } } });
    if (finePointer) {
      box.addEventListener('mousemove', function (e) { var r = box.getBoundingClientRect(); place(e.clientX - r.left, e.clientY - r.top); });
      box.addEventListener('mouseenter', function () { gsap.to(btn, { scale: 1, duration: 0.5, ease: 'back.out(2)' }); });
      box.addEventListener('mouseleave', function () { var c3 = center(); place(c3.x, c3.y); });
    }
    var label = $('[data-play-label]', btn), bar = $('.story__bar', box), barFill = $('.story__bar i', box), uiTimer = null;
    function setLabel(text, aria) { label.textContent = text; btn.setAttribute('aria-label', aria); }
    function toggle() {
      if (video.paused || video.ended) { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
      else video.pause();
    }
    function flashUI() {
      sec.classList.add('show-ui');
      clearTimeout(uiTimer);
      uiTimer = setTimeout(function () { sec.classList.remove('show-ui'); }, 1400);
    }
    box.addEventListener('click', function (e) {
      if (e.target.closest('.story__bar')) return;
      e.preventDefault();
      toggle();
      if (!finePointer) flashUI();
    });
    btn.style.pointerEvents = 'auto';
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        e.preventDefault();
        video.currentTime = Math.max(0, Math.min(video.duration || 0, video.currentTime + (e.key === 'ArrowRight' ? 5 : -5)));
      }
    });
    bar.addEventListener('click', function (e) {
      e.stopPropagation();
      if (!video.duration) return;
      var r = bar.getBoundingClientRect();
      video.currentTime = video.duration * Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    });
    video.addEventListener('play', function () { sec.classList.add('is-playing', 'has-started'); setLabel('PAUSE', 'Pause the customer story video'); });
    video.addEventListener('pause', function () {
      sec.classList.remove('is-playing');
      if (!video.ended) setLabel('RESUME', 'Resume the customer story video');
    });
    video.addEventListener('ended', function () { sec.classList.remove('is-playing'); setLabel('REPLAY', 'Replay the customer story video'); });
    video.addEventListener('timeupdate', function () {
      if (video.duration) barFill.style.transform = 'scaleX(' + video.currentTime / video.duration + ')';
    });
    if (!reduce) {
      gsap.from(btn, { scale: 0, duration: 1, ease: 'back.out(1.8)', scrollTrigger: { trigger: box, start: 'top 70%', once: true } });
    }
  }

  /* ------------------------------------------------------------------------
     Staggered groups (case study columns, CTA list) via anime.js
     ------------------------------------------------------------------------ */
  function staggers() {
    $$('[data-stagger]').forEach(function (wrap) {
      var kids = Array.prototype.slice.call(wrap.children);
      if (reduce) return;
      if (A) A.utils.set(kids, { opacity: 0, translateY: 50 }); else gsap.set(kids, { autoAlpha: 0, y: 50 });
      ScrollTrigger.create({
        trigger: wrap, start: 'top 85%', once: true,
        onEnter: function () {
          if (A) A.animate(kids, { opacity: [0, 1], translateY: [50, 0], duration: 1200, delay: A.stagger(120), ease: 'outExpo' });
          else gsap.to(kids, { autoAlpha: 1, y: 0, duration: 1.2, stagger: 0.12 });
        }
      });
    });
  }

  /* ------------------------------------------------------------------------
     FAQ accordion
     ------------------------------------------------------------------------ */
  function faq() {
    var items = $$('.qa');
    items.forEach(function (qa, i) {
      var btn = $('.qa__q', qa), ans = $('.qa__a', qa);
      function set(open, instant) {
        btn.setAttribute('aria-expanded', String(open));
        gsap.to(ans, {
          height: open ? 'auto' : 0, duration: instant || reduce ? 0 : open ? 0.7 : 0.5, ease: open ? 'expo.out' : 'expo.inOut',
          onComplete: function () { ScrollTrigger.refresh(); }
        });
        if (open && !instant && !reduce) gsap.fromTo(ans.firstElementChild, { y: 14, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.7, delay: 0.08, ease: 'expo.out' });
      }
      btn.addEventListener('click', function () { set(btn.getAttribute('aria-expanded') !== 'true'); });
      if (i === 0) set(true, true);
    });
  }

  /* ------------------------------------------------------------------------
     Demo form: gentle validation, an inked seal on success (anime.js)
     ------------------------------------------------------------------------ */
  function form() {
    var f = $('#demo-form');
    if (!f) return;
    var openedAt = Date.now();
    var btn = $('button[type="submit"]', f), btnLabel = $('[data-submit-label]', f), errEl = $('.form__error', f);
    var sending = false;

    function utm() {
      try {
        var q = new URLSearchParams(location.search), out = [];
        ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(function (k) { if (q.get(k)) out.push(k.slice(4) + '=' + q.get(k)); });
        return out.join(' · ');
      } catch (e) { return ''; }
    }

    function showDone() {
      var done = $('.form__done', f);
      var parts = $('#cx-name').value.trim().split(/\s+/);
      var greet = /^dr\.?$/i.test(parts[0]) && parts[1] ? 'Dr. ' + parts[1] : parts[0];
      $('[data-done-name]', f).textContent = greet ? ', ' + greet : '';
      gsap.set(done, { visibility: 'visible' });
      gsap.fromTo(done, { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: reduce ? 0 : 0.9, ease: 'wipe' });
      if (A && !reduce) {
        var draws = A.svg.createDrawable($$('.done-draw', done));
        A.createTimeline({ defaults: { ease: 'inOut(3)' } })
          .add(draws, { draw: ['0 0', '0 1'], duration: 900, delay: A.stagger(120) }, 500)
          .add($('.done-text', done), { opacity: [0, 1], duration: 500 }, 1100)
          .add($('svg', done), { scale: [1.25, 0.94, 1], rotate: [-18, -8], duration: 700, ease: 'outBack(2)' }, 1200)
          .add($$('h3, p', done), { opacity: [0, 1], translateY: [16, 0], duration: 800, delay: A.stagger(100), ease: 'outExpo' }, 1300);
      } else gsap.set($('.done-text', done), { opacity: 1 });
    }

    function showError(data) {
      var body = 'Hello Dualite team,\n\nI would like to book a demo of Dualite Claims.\n\n' +
        'Name: ' + data.name + '\nHospital: ' + data.hospital + '\nWork email: ' + data.email +
        '\nMobile: ' + (data.phone || '-') + '\nRole: ' + data.role + '\nClaims per month: ' + data.volume + '\n';
      var href = 'mailto:info@dualite.dev?subject=' + encodeURIComponent('Demo request: ' + data.hospital) + '&body=' + encodeURIComponent(body);
      errEl.innerHTML = 'That didn’t go through. Please try again, or <a href="' + href + '">send it as an email</a>. We’ve written it for you.';
      errEl.hidden = false;
      if (!reduce) gsap.fromTo(errEl, { y: 8, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5, ease: 'expo.out' });
    }

    function setSending(on) {
      sending = on;
      f.classList.toggle('is-sending', on);
      btn.setAttribute('aria-busy', String(on));
      btnLabel.textContent = on ? 'Sending…' : 'Book my demo';
    }

    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (sending) return;
      errEl.hidden = true;
      var bad = $$('[required]', f).filter(function (i) { return !i.value.trim() || (i.type === 'email' && !/^\S+@\S+\.\S+$/.test(i.value)); });
      $$('input', f).forEach(function (i) { i.removeAttribute('aria-invalid'); });
      if (bad.length) {
        bad.forEach(function (i) { i.setAttribute('aria-invalid', 'true'); i.style.borderColor = '#B04A1E'; });
        bad[0].focus();
        if (A && !reduce) A.animate(bad.map(function (i) { return i.parentNode; }), { translateX: [0, -8, 7, -5, 3, 0], duration: 520, ease: 'outQuad', delay: A.stagger(40) });
        return;
      }
      var data = {
        name: $('#cx-name').value.trim(),
        hospital: $('#cx-hospital').value.trim(),
        email: $('#cx-email').value.trim(),
        phone: $('#cx-phone').value.trim(),
        role: $('#cx-role').value,
        volume: $('#cx-volume').value,
        website: f.elements.website ? f.elements.website.value : '',
        elapsed: Date.now() - openedAt,
        page: location.href.split('#')[0],
        referrer: document.referrer,
        utm: utm()
      };
      setSending(true);
      var ctrl = 'AbortController' in window ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
      fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        signal: ctrl ? ctrl.signal : undefined
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok && j.ok, status: r.status, json: j }; }); })
        .then(function (res) {
          clearTimeout(timer);
          setSending(false);
          if (res.ok) { showDone(); return; }
          if (res.status === 422 && res.json.fields) {
            var map = { name: '#cx-name', hospital: '#cx-hospital', email: '#cx-email', phone: '#cx-phone' };
            var first = null;
            res.json.fields.forEach(function (k) { var el = map[k] && $(map[k]); if (el) { el.setAttribute('aria-invalid', 'true'); el.style.borderColor = '#B04A1E'; first = first || el; } });
            errEl.textContent = 'Please check the highlighted fields.';
            errEl.hidden = false;
            if (first) first.focus();
            return;
          }
          showError(data);
        })
        .catch(function () { clearTimeout(timer); setSending(false); showError(data); });
    });
    $$('input', f).forEach(function (i) { i.addEventListener('input', function () { i.style.borderColor = ''; i.removeAttribute('aria-invalid'); }); });
  }

  /* ------------------------------------------------------------------------
     Footer: the sign-off rises letter by letter
     ------------------------------------------------------------------------ */
  function footer() {
    var mark = $('[data-footer-mark]');
    $$('[data-top]').forEach(function (b) { b.addEventListener('click', function () { scrollToY(0, 2); }); });
    if (!mark || reduce) return;
    var split = SplitText.create(mark, { type: 'chars', mask: 'chars' });
    gsap.from(split.chars, { yPercent: 110, duration: 1.4, stagger: 0.04, ease: 'expo.out', scrollTrigger: { trigger: mark, start: 'top 95%', once: true } });
    gsap.from('.footer__top', { y: 60, autoAlpha: 0, duration: 1.4, ease: 'expo.out', scrollTrigger: { trigger: '.footer', start: 'top 85%', once: true } });
  }

  /* ------------------------------------------------------------------------
     Intro loader (anime.js): the seal draws, the count runs, the file is
     stamped, then olive stripes sweep the page open.
     ------------------------------------------------------------------------ */
  function loader(onReveal) {
    var L = $('.loader');
    if (!L || root.classList.contains('no-loader') || !A) {
      if (L) L.style.display = 'none';
      onReveal();
      return;
    }
    window.scrollTo(0, 0);
    if (lenis) { lenis.scrollTo(0, { immediate: true, force: true }); lenis.stop(); }
    var count = $('.loader__count', L), status = $('.loader__status', L), bar = $('.loader__bar span', L);
    var statuses = [[0, 'Opening claim file'], [22, 'Reading 14 pages'], [48, 'Checking 50+ case rules'], [74, 'Applying Digistamp'], [96, 'Ready for review']];
    var draws = A.svg.createDrawable($$('.seal-draw', L));
    var counter = { v: 0 };
    var revealed = false;
    function reveal() {
      if (revealed) return; revealed = true;
      onReveal();
    }
    A.createTimeline({ defaults: { ease: 'inOut(3)' } })
      .add(draws, { draw: ['0 0', '0 1'], duration: 1250, delay: A.stagger(160) }, 0)
      .add(counter, {
        v: 100, duration: 1750, ease: 'inOut(2)',
        onUpdate: function () {
          var v = Math.round(counter.v);
          count.textContent = v < 10 ? '0' + v : String(v);
          bar.style.transform = 'scaleX(' + counter.v / 100 + ')';
          for (var i = statuses.length - 1; i >= 0; i--) if (v >= statuses[i][0]) { if (status.textContent !== statuses[i][1]) status.textContent = statuses[i][1]; break; }
        }
      }, 0)
      .add($('.seal-text', L), { opacity: [0, 1], duration: 600, ease: 'outQuad' }, 850)
      .add($('.loader__seal', L), { scale: [1, 0.9, 1.02, 1], rotate: [0, -8], duration: 520, ease: 'outQuad' }, 1650)
      .add($('.seal-ink', L), { opacity: [0, 0.12], scale: [0.6, 1], duration: 420, ease: 'outQuad' }, 1700)
      .add($$('.loader__panels i', L), { scaleY: [0, 1], duration: 650, delay: A.stagger(55), ease: 'inOut(4)' }, 2050)
      .call(function () {
        $$('.loader__top, .loader__mid, .loader__bot, .loader__bar', L).forEach(function (n) { n.style.visibility = 'hidden'; });
        L.style.background = 'transparent';
        reveal();
      }, 2780)
      .add($$('.loader__panels i', L), { translateY: ['0%', '-101%'], duration: 800, delay: A.stagger(55), ease: 'inOut(4)' }, 2800)
      .call(function () {
        L.style.display = 'none';
        if (lenis) lenis.start();
        try { sessionStorage.setItem('dc-intro', '1'); } catch (e) {}
      }, 3700);
  }

  /* ------------------------------------------------------------------------
     Boot
     ------------------------------------------------------------------------ */
  function fontsReady() {
    if (!document.fonts || !document.fonts.ready) return Promise.resolve();
    return Promise.race([document.fonts.ready, new Promise(function (r) { setTimeout(r, 2500); })]);
  }

  fontsReady().then(function () {
    movement(); // pinned first, so every later trigger measures with its spacer in place
    prepEyebrows();
    prepHero();
    splitHeadings();
    reveals();
    scrubWords();
    parallax();
    heroScroll();
    proofQuote();
    costs();
    results();
    productDemo();
    platform();
    trust();
    reconciliation();
    story();
    staggers();
    faq();
    form();
    footer();
    fitScalers();
    root.classList.add('is-ready');
    ScrollTrigger.refresh();
    loader(function () {
      heroIntro();
      ScrollTrigger.refresh();
    });
  });
})();
