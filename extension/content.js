// window.location.search is everything after the "?" — e.g. "?v=abc123&t=30s"
// URLSearchParams parses that into a lookup object, so .get("v") pulls out the ID
// without you writing manual string-splitting logic.
function getVideoId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("v");
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

  btn.addEventListener("click", () => {
    console.log("Analyze clicked for video:", getVideoId());
  });

  // prepend = insert as the FIRST child, so it appears above the suggested-videos list
  target.prepend(btn);
}

// Runs once for the very first page load.
injectButton();

// Runs again every time YouTube's internal navigation finishes —
// this is what keeps the button alive across video changes without a reload.
document.addEventListener("yt-navigate-finish", injectButton);