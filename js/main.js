/* ------------------------------------------------------------------
   院區開放活動輯 — Demo scrollytelling
   GSAP + ScrollTrigger + Lenis
------------------------------------------------------------------ */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isMobile = window.matchMedia("(max-width: 820px)").matches;
  // smooth scroll (Lenis) is opt-in via ?smooth — native scroll is the default
  var useSmooth = /[?&]smooth\b/.test(location.search);

  /* ---------- hero video: start at 8s, loop 8s -> end ---------- */
  /* ---------- autoplay every <video> (retry + first-gesture fallback) ---------- */
  var vids = Array.prototype.slice.call(document.querySelectorAll("video"));
  function kickAll() {
    vids.forEach(function (v) {
      v.muted = true;
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
    });
  }
  kickAll();
  var tries = 0, iv = setInterval(function () { kickAll(); if (++tries > 12) clearInterval(iv); }, 500);
  ["pointerdown", "touchstart", "keydown", "wheel", "scroll"].forEach(function (ev) {
    window.addEventListener(ev, function once() {
      kickAll();
      window.removeEventListener(ev, once);
    }, { passive: true });
  });

  /* hero.mp4 is already trimmed to begin at 0:08 of the source clip and loops natively */

  /* ---------- smooth scroll ---------- */
  var lenis = null;
  if (typeof Lenis !== "undefined" && !reduceMotion && useSmooth) {
    lenis = new Lenis({ duration: 1.1, smoothWheel: true });
    window.__lenis = lenis;
    lenis.on("scroll", function () { if (window.ScrollTrigger) ScrollTrigger.update(); });
    if (window.gsap) {
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }
  }

  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") return;
  gsap.registerPlugin(ScrollTrigger);

  /* ---------- top progress bar ---------- */
  var bar = document.getElementById("scrollBar");
  ScrollTrigger.create({
    start: 0, end: "max",
    onUpdate: function (self) { bar.style.width = (self.progress * 100).toFixed(2) + "%"; }
  });

  /* ---------- number count-up ---------- */
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-to")) || 0;
    var obj = { v: 0 };
    gsap.to(obj, {
      v: target, duration: 1.4, ease: "power2.out",
      onUpdate: function () { el.textContent = Math.round(obj.v).toLocaleString("en-US"); }
    });
  }

  /* ---------- hero text + parallax ---------- */
  gsap.from(".hero .kicker, .hero h1, .hero .lede, .hero .scroll-cue", {
    y: 40, opacity: 0, duration: 1, ease: "power3.out", stagger: 0.12, delay: 0.2
  });
  gsap.to(".hero-video", {
    yPercent: 16, ease: "none",
    scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true }
  });

  /* ---------- intro ---------- */
  gsap.utils.toArray(".intro-inner p").forEach(function (p) {
    gsap.from(p, { y: 34, opacity: 0, duration: 0.9, ease: "power2.out",
      scrollTrigger: { trigger: p, start: "top 82%" } });
  });

  /* ---------- year sections ---------- */
  var years = gsap.utils.toArray(".year");
  var railItems = gsap.utils.toArray(".rail li");

  function setRail(idx) {
    railItems.forEach(function (li, j) { li.classList.toggle("on", j === idx); });
  }

  years.forEach(function (section, i) {
    var head = section.querySelector(".year-head");
    var bg = section.querySelector(".year-bg");
    var wrap = section.querySelector(".filmstrip-wrap");
    var strip = section.querySelector(".filmstrip");
    var nums = section.querySelectorAll(".stats .num");
    var counted = false;
    function fireCounts() { if (counted) return; counted = true; nums.forEach(countUp); }

    var headKids = head ? Array.prototype.slice.call(head.querySelectorAll(".yr-big, .year-title > *, .year-body > *")) : [];
    var kv = section.querySelector(".year-kv");
    var kvImg = kv ? kv.querySelector("img") : null;
    var figs = strip ? strip.querySelectorAll("figure") : [];
    function stripDist() {
      if (!strip || !wrap) return 0;
      return Math.max(0, strip.scrollWidth - wrap.clientWidth);
    }

    /* rail highlight + count-up — reliable, independent of pin */
    ScrollTrigger.create({
      trigger: section, start: "top 55%", end: "bottom 45%",
      onToggle: function (self) { if (self.isActive) { setRail(i); fireCounts(); } }
    });

    /* ---- MOBILE: no pin, no reveal animations — just count the stats up ---- */
    if (isMobile) {
      ScrollTrigger.create({
        trigger: section, start: "top 78%", once: true, onEnter: fireCounts
      });
      return;
    }

    /* ---- DESKTOP: pinned, scrubbed parallax + filmstrip (text stays put) ---- */
    var endFn = function () { return "+=" + (stripDist() + window.innerHeight * 0.9); };

    var tl = gsap.timeline({
      defaults: { ease: "none", immediateRender: false },
      scrollTrigger: {
        trigger: section, start: "top top", end: endFn,
        pin: true, scrub: true, anticipatePin: 1, invalidateOnRefresh: true,
        onEnter: fireCounts, onEnterBack: fireCounts
      }
    });

    tl.fromTo(bg, { scale: 1.3 }, { scale: 1.12, duration: 1, immediateRender: true }, 0);
    if (kvImg) tl.fromTo(kvImg, { scale: 1.1, yPercent: -3 }, { scale: 1, yPercent: 3, duration: 1, immediateRender: true }, 0);
    tl.fromTo(strip, { x: 0 }, { x: function () { return -stripDist(); }, duration: 1, ease: "none" }, 0.12);
  });

  /* ---------- recap: static layout, just count the number up ---------- */
  ScrollTrigger.create({
    trigger: ".recap-stat", start: "top 82%", once: true,
    onEnter: function () { var n = document.querySelector(".recap-stat .num"); if (n) countUp(n); }
  });

  /* ---------- rail click ---------- */
  railItems.forEach(function (li) {
    li.addEventListener("click", function () {
      var el = document.getElementById(li.getAttribute("data-target"));
      if (!el) return;
      if (lenis) lenis.scrollTo(el, { offset: -1 });
      else el.scrollIntoView({ behavior: "smooth" });
    });
  });

  /* ---------- keep trigger positions correct as assets settle ---------- */
  [120, 400, 1000, 2500].forEach(function (ms) { setTimeout(function () { ScrollTrigger.refresh(); }, ms); });
  window.addEventListener("load", function () { ScrollTrigger.refresh(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
})();

/* ------------------------------------------------------------------
   圖片點擊放大（lightbox）— 點圖放大，圖片下方顯示標題
------------------------------------------------------------------ */
(function () {
  "use strict";

  var imgs = Array.prototype.slice.call(
    document.querySelectorAll(".filmstrip figure img, .year-kv img")
  );
  if (!imgs.length) return;

  var box = document.createElement("div");
  box.className = "lightbox";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.innerHTML =
    '<button class="lightbox-close" type="button" aria-label="關閉">×</button>' +
    '<img alt="">' +
    '<figcaption></figcaption>';
  document.body.appendChild(box);

  var bigImg = box.querySelector("img");
  var cap = box.querySelector("figcaption");
  var closeBtn = box.querySelector(".lightbox-close");
  var lastFocus = null;

  function captionFor(img) {
    var fig = img.closest("figure");
    var fc = fig ? fig.querySelector("figcaption") : null;
    if (fc && fc.textContent.trim()) return fc.textContent.trim();
    return img.getAttribute("alt") || "";
  }

  function open(img) {
    lastFocus = document.activeElement;
    bigImg.src = img.currentSrc || img.src;
    bigImg.alt = img.alt || "";
    var text = captionFor(img);
    cap.textContent = text;
    cap.style.display = text ? "" : "none";
    box.classList.add("open");
    document.documentElement.style.overflow = "hidden";
    document.body.style.overflow = "hidden";
    if (window.__lenis) window.__lenis.stop();
    closeBtn.focus();
  }

  function close() {
    box.classList.remove("open");
    document.documentElement.style.overflow = "";
    document.body.style.overflow = "";
    if (window.__lenis) window.__lenis.start();
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  imgs.forEach(function (img) {
    img.addEventListener("click", function () { open(img); });
  });
  closeBtn.addEventListener("click", close);
  box.addEventListener("click", function (e) { if (e.target === box) close(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && box.classList.contains("open")) close();
  });
})();
