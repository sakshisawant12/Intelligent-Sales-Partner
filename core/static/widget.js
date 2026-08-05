(function () {
  const scriptTag = document.currentScript;
  const widgetId = scriptTag.getAttribute("data-widget-id");

  // 🔑 GLOBAL CHAT MODE
  window.chatMode = "bot";

  const iframe = document.createElement("iframe");
  iframe.src =
    "http://127.0.0.1:8000/chat/widget/?widget_id=" +
    widgetId +
    "&origin=" +
    encodeURIComponent(window.location.origin);

  iframe.style.position = "fixed";
  iframe.style.bottom = "20px";
  iframe.style.right = "20px";
  iframe.style.width = "380px";
  iframe.style.height = "100vh";
  iframe.style.maxHeight = "650px";

  iframe.style.border = "none";
  iframe.style.zIndex = "999999";

  document.body.appendChild(iframe);

  // ---------- HUMAN MODE LISTENER ----------
  window.addEventListener("message", function (event) {
    if (!event.data) return;

    // 🔍 Detect human intent
    if (event.data.type === "CHECK_HUMAN_MODE") {
      const message = event.data.message || "";

      if (checkForHumanRequest(message)) {
        iframe.contentWindow.postMessage(
          { type: "SHOW_HUMAN_MODE_BUTTON" },
          "*"
        );
      }
    }

    // 🔥 HUMAN MODE CONFIRMED
    if (event.data.type === "HUMAN_MODE_ACTIVE") {
      window.chatMode = "human";
      console.log("🧠 Chat switched to HUMAN mode");
    }
  });
})();

// ---------- HUMAN KEYWORD CHECK ----------
function checkForHumanRequest(message) {
  const keywords = [
    "manager",
    "owner",
    "human",
    "real person",
    "talk to person",
    "talk to owner"
  ];

  return keywords.some(word =>
    message.toLowerCase().includes(word)
  );
}
