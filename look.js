// The site's look and its light/dark switch. Every page loads this in <head>, right after
// <link id="look-css" href="/look.css">, so the choice is made before the first paint.
//
//   LOOK = "board"    the Board Room look (look.css on top of styles.css): light, with a dark switch in the nav
//   LOOK = "classic"  the original paper-and-green look (styles.css alone, no dark mode)
//
// To put the whole site back on the classic look, change LOOK below and deploy. To try the other look
// in your own browser only, open any page with ?look=classic or ?look=board (remembered until you
// open a page with ?look=default).
(function () {
  var LOOK = "board";

  var root = document.documentElement, look = LOOK, theme = null;
  try {
    var asked = new URLSearchParams(location.search).get("look");
    if (asked === "classic" || asked === "board") localStorage.setItem("indica-look", asked);
    else if (asked === "default") localStorage.removeItem("indica-look");
    look = localStorage.getItem("indica-look") || LOOK;
    theme = localStorage.getItem("indica-theme");
  } catch (e) { /* storage blocked: the default look, in light */ }

  if (look === "classic") {
    var css = document.getElementById("look-css");
    if (css) css.media = "not all";
    return;
  }
  if (theme === "dark") root.setAttribute("data-theme", "dark");

  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 019.5 4a8 8 0 1010.5 10.5z"/></svg>';
  function dark() { return root.getAttribute("data-theme") === "dark"; }
  function paint(btn) {
    btn.innerHTML = dark() ? SUN : MOON;
    btn.setAttribute("aria-label", dark() ? "Switch to the light theme" : "Switch to the dark theme");
    btn.title = btn.getAttribute("aria-label");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var nav = document.querySelector(".nav-inner");
    if (nav) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "theme-btn";
      nav.insertBefore(btn, nav.querySelector(".nav-cta, .menu-btn"));
      paint(btn);
      btn.addEventListener("click", function () {
        var next = dark() ? "light" : "dark";
        if (next === "dark") root.setAttribute("data-theme", "dark");
        else root.removeAttribute("data-theme");
        try { localStorage.setItem("indica-theme", next); } catch (e) { /* the switch still works for this visit */ }
        paint(btn);
      });
    }
    // In dark, a soft light follows the pointer across a card.
    document.addEventListener("pointermove", function (e) {
      var card = e.target.closest && e.target.closest(".diag-cell, .offer, .step");
      if (!card) return;
      var r = card.getBoundingClientRect();
      card.style.setProperty("--mx", (e.clientX - r.left) + "px");
      card.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });
})();
