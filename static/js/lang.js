// lang.js
// Handles the EN / TA language toggle button present in the navbar of
// every page. It calls the Flask session endpoint, then reloads the
// page so all server-rendered text updates immediately.

function toggleLanguage() {
    const current = document.documentElement.getAttribute("data-lang") || "en";
    const next = current === "en" ? "ta" : "en";

    fetch(`/set-language/${next}`)
        .then((res) => res.json())
        .then(() => {
            window.location.reload();
        })
        .catch((err) => console.error("Language switch failed:", err));
}
