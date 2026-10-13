// window.location.search is everything after the "?" — e.g. "?v=abc123&t=30s"
// URLSearchParams parses that into a lookup object, so .get("v") pulls out the ID
// without you writing manual string-splitting logic.
function getVideoId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("v");
}

async function api(path, method = "GET") {
  return chrome.runtime.sendMessage({ type: "api", path, method });
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function getPanel() {
  let panel = document.getElementById("persolens-panel");

  if (!panel) {
    panel = document.createElement("div");
    panel.id = "persolens-panel";
    panel.className = "pl-panel";
    panel.dataset.theme = currentTheme();
    document.getElementById("persolens-trigger").after(panel);
  }
  return panel;
}

function showStatus(text, isError = false) {
  const panel = getPanel();
  panel.replaceChildren();
  const line = document.createElement("p");
  line.className = isError ? "pl-status pl-error" : "pl-status";
  line.textContent = text;
  panel.append(line);
}

function seekTo(seconds) {
  const video = document.querySelector("video");
  if (!video) return;
  video.currentTime = seconds;
  video.play();
}

// helper function which makes an element, gives it a class and some text
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// 83 seconds -> "1:23"
function formatClock(totalSeconds) {
  const m = Math.floor(totalSeconds / 60);
  const s = Math.floor(totalSeconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

// Collapsible card for a speech pattern
// function speechCard(p, openByDefault) {
//   const card = el("details", "pl-acc");
//   card.open = openByDefault;

//   const summary = el("summary");
//   summary.append(el("span", "pl-acc-name", p.pattern_name), el("span", "pl-chip", "1 moment"));
//   card.append(summary);

//   const body = el("div", "pl-acc-body");
//   body.append(el("p", "pl-desc", p.description));

//   const quote = el("button", "pl-inst");
//   quote.type = "button";
//   quote.append(el("span", "pl-ts", p.timestamp_label), el("span", "pl-q", p.quote_or_evidence));
//   quote.addEventListener("click", () => seekTo(p.timestamp_sec));

//   const jump = el("button", "pl-jump", `▶ Jump to ${p.timestamp_label}`);
//   jump.type = "button";
//   jump.addEventListener("click", () => seekTo(p.timestamp_sec));

//   body.append(quote, jump);
//   card.append(body);
//   return card;
// }

let learnMode = false;

// Switch in panel header
function learnSwitch(panel) {
  const btn = el("button", "pl-switch");
  btn.type = "button";
  btn.setAttribute("role", "switch");
  btn.setAttribute("aria-checked", String(learnMode));
  btn.append(el("span", "", "Learn mode"), el("span", "pl-track"));

  btn.addEventListener("click", () => {
    learnMode = !learnMode;
    btn.setAttribute("aria-checked", String(learnMode));
    panel.classList.toggle("pl-learning", learnMode); // CSS shows or hides the .pl-learn blocks
  });
  return btn;
}

// One row for one moment
function momentRow(m) {
  const row = el("button", "pl-inst");
  row.type = "button";
  row.append(el("span", "pl-ts", "▶ " + m.timestamp_label), el("span", "pl-q", m.quote));

  if (typeof m.match === "number") {
    const percent = Math.round(m.match * 100);
    row.append(el("span", "pl-match", percent + "% of these words found in the transcript"));
  }

  row.addEventListener("click", () => seekTo(m.timestamp_sec));
  return row;
}

// Why it works box
function learnBlock(p) {
  if (!p.why_it_works && !p.try_it) return null;

  const box = el("div", "pl-learn");
  box.append(el("div", "pl-learn-tag", "AI SUGGESTION"));

  if (p.try_it) {
    box.append(el("div", "pl-learn-h", "Try it"), el("p", "pl-learn-t", p.try_it));
  }
  return box;
}

// Collapsible card for speech pattern
function speechCard(p, openByDefault) {
  const card = el("details", "pl-acc");
  card.open = openByDefault;

  const count = p.moments.length;
  const chipText = count === 1 ? "1 moment" : count + " moments";

  const summary = el("summary");
  summary.append(el("span", "pl-acc-name", p.pattern_name), el("span", "pl-chip", chipText));
  card.append(summary);

  const body = el("div", "pl-acc-body");
  body.append(el("p", "pl-desc", p.description));

  p.moments.forEach((m) => body.append(momentRow(m)));

  const learn = learnBlock(p);
  if (learn) body.append(learn);

  card.append(body);
  return card;
}


// One card for a vocal pattern
function vocalCard(p) {
  const card = el("details", "pl-acc pl-voicecard");
  const summary = el("summary");
  summary.append(el("span", "pl-acc-name", p.pattern_name), el("span", "pl-chip", "whole video"));
  card.append(summary);

  const body = el("div", "pl-acc-body");
  body.append(
    el("p", "pl-desc", p.description),
    el("div", "pl-meas", p.quote_or_evidence),
    el("p", "pl-proof", "Computed from the recording")
  );
  card.append(body);
  return card;
}

function renderReport(report) {
  const panel = getPanel();
  panel.replaceChildren();
  panel.classList.toggle("pl-learning", learnMode)

  const speech = report.patterns
  //const vocal = report.patterns.filter((p) => p.channel === "vocal");
  //if (speech.length + vocal.length === 0) return showStatus("No patterns were found in this video.");

  //header
  const head = el("div", "pl-head");
  
  const brand = el("div", "pl-brand");
  brand.append(el("span", "", "PERSOLENS"), learnSwitch(panel));
  head.append(brand, el("div", "pl-title", report.title || "This video"));

  const meta = el("div", "pl-meta");

  const video = document.querySelector("video");
  if (video) {
    if (Number.isFinite(video.duration)) {
      const label = formatClock(video.duration) + " analyzed";
      meta.append(el("span", "", label));
    }
  }

  // Minutes spent talking vs quiet
  const vocalSummary = report.vocal_summary;
  if (vocalSummary && typeof vocalSummary.speech_seconds === "number" && typeof vocalSummary.silent_seconds === "number") {
    const speakingMin = (vocalSummary.speech_seconds / 60).toFixed(1);
    const quietMin = (vocalSummary.silent_seconds / 60).toFixed(1);
    meta.append(el("span", "", speakingMin + " min speaking · " + quietMin + " min quiet"));
  }

  // if (speech.length > 0) {
  //   let word = "quotes";
  //   if (speech.length === 1) {
  //     word = "quote";
  //   }
  //   const text = "✓ " + speech.length + " " + word + " verified";
  //   meta.append(el("span", "pl-verified", text));
  // }

  // Count quotes
  let quoteCount = 0;
  speech.forEach((p) => { quoteCount += p.moments.length; });

  if (quoteCount > 0) {
    let word = "quotes";
    if (quoteCount === 1) {
      word = "quote";
    }
    const text = "✓ " + quoteCount + " " + word + " verified";
    meta.append(el("span", "pl-verified", text));
  }

  head.append(meta);
  panel.append(head);

  const body = el("div", "pl-body");
  panel.append(body);

  if (speech.length > 0) {
    const label = el("div", "pl-section pl-speech", "COMMUNICATION");
    body.append(label);

    for (let i = 0; i < speech.length; i++) {
      const pattern = speech[i];
      let startOpen = false;
      if (i === 0) {
        startOpen = true;
      }
      const card = speechCard(pattern, startOpen);
      body.append(card);
    }
  }

  if (vocal.length) {
    body.append(el("div", "pl-section pl-voice", "VOCAL DELIVERY"));
    vocal.forEach((p) => body.append(vocalCard(p)));
  }
}

// Waiting for background job
async function waitForJob(jobId) {
  const deadline = Date.now() + 20 * 60 * 1000;
  while (Date.now() < deadline) {
    const res = await api(`/jobs/${jobId}`);
    if (!res.ok) throw new Error(`Job check failed (HTTP ${res.status})`);

    const { status, error } = res.data;
    if (status === "SUCCESS") return;
    if (status === "FAILURE") throw new Error(error || "The extraction failed");

    showStatus(
      status === "PENDING"
        ? "Waiting for the worker to pick this up…"
        : "Analyzing the video… this takes 1 to 3 minutes"
    );
    await sleep(2000);
  }
  throw new Error("Timed out after 20 minutes");
}

async function analyze() {
  const videoId = getVideoId();
  if (!videoId) return showStatus("Open a YouTube video first.", true);

  const btn = document.getElementById("persolens-trigger");
  btn.disabled = true;
  try {
    showStatus("Checking for an existing report…");
    const res = await api(`/videos/${videoId}/report`);
    if (res.status === 0) throw new Error("Can't reach the backend. Is dev_app running?");

    if (res.ok && res.data && res.data.patterns) {
      renderReport(res.data);
      return;
    }

    showStatus("New video. Fetching its details…");
    const watchUrl = `https://www.youtube.com/watch?v=${videoId}`;
    let next = await api(`/videos/ingest?youtube_url=${encodeURIComponent(watchUrl)}`, "POST");
    if (!next.ok) throw new Error(`Ingest failed (HTTP ${next.status})`);

    showStatus("Starting the analysis…");
    next = await api(`/videos/${videoId}/extract`, "POST");
    if (!next.ok) throw new Error(`Extract failed (HTTP ${next.status})`);

    if (next.data.status === "cached") {
      renderReport(next.data.result); // someone analyzed this video already
      return;
    }

    await waitForJob(next.data.job_id);

    next = await api(`/videos/${videoId}/report`);
    if (!next.ok) throw new Error(`Couldn't load the finished report (HTTP ${next.status})`);

    renderReport(next.data);
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    btn.disabled = false;
  }

}

function injectButton() {
  // Guard clause: if this button already exists, stop here.
  // Without this, calling injectButton() twice would create two buttons.
  if (document.getElementById("persolens-trigger")) return;

  // YouTube renders this element dynamically — if it's not there yet,
  // querySelector returns null, and this guard exits rather than crashing.
  // #secondary-inner = YouTube's right-hand sidebar container
  const target = document.querySelector("#secondary-inner");
  if (!target) return;

  const btn = document.createElement("button");
  btn.id = "persolens-trigger";
  btn.className = "persolens-btn";
  btn.textContent = "Analyze with PersoLens";

  btn.addEventListener("click", analyze);

  // prepend = insert as the FIRST child, so it appears above the suggested-videos list
  target.prepend(btn);
}

// removes video results of old videos when YouTube switches without a reload
function onNavigate() {
  document.getElementById("persolens-panel")?.remove(); // ?. = do nothing if there is no panel
  injectButton();
}

// Runs once for the very first page load.
injectButton();

// Follow youtube's light/dark theme
function currentTheme() {
  return document.documentElement.hasAttribute("dark") ? "dark" : "light";
}

function applyTheme() {
  const panel = document.getElementById("persolens-panel");
  if (panel) panel.dataset.theme = currentTheme();
}

// If viewer changes Youtube's theme while panel is open, then restyle it
new MutationObserver(applyTheme).observe(document.documentElement, {
  attributes: true,
  attributeFilter: ["dark"], // only care about this one attribute
});

// Runs again every time YouTube's internal navigation finishes —
// this is what keeps the button alive across video changes without a reload.
document.addEventListener("yt-navigate-finish", onNavigate);
