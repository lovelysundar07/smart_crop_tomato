// disease.js
// Handles image preview + AJAX call to /api/detect-disease

const leafInput = document.getElementById("leaf_image");
const leafPreview = document.getElementById("leaf-preview");
const analyzeBtn = document.getElementById("analyze-btn");
const resultBox = document.getElementById("result-box");
const spinner = document.getElementById("spinner");

leafInput.addEventListener("change", () => {
    const file = leafInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        leafPreview.src = e.target.result;
        leafPreview.style.display = "block";
    };
    reader.readAsDataURL(file);
});

analyzeBtn.addEventListener("click", async () => {
    const file = leafInput.files[0];
    if (!file) {
        alert("Please choose a leaf photo first / முதலில் ஒரு இலை புகைப்படத்தை தேர்ந்தெடுக்கவும்");
        return;
    }

    const formData = new FormData();
    formData.append("leaf_image", file);

    spinner.style.display = "block";
    resultBox.classList.remove("show", "alert");

    try {
        const res = await fetch("/api/detect-disease", { method: "POST", body: formData });
        const data = await res.json();
        spinner.style.display = "none";

        if (data.error) {
            resultBox.innerHTML = `<p>${data.error}</p>`;
            resultBox.classList.add("show", "alert");
            return;
        }

        resultBox.classList.add("show");
        if (!data.is_healthy) resultBox.classList.add("alert");

        resultBox.innerHTML = `
            <h3>${data.disease_name}</h3>
            <p><strong>${resultBox.dataset.confidenceLabel || "Confidence"}:</strong> ${data.confidence}%</p>
            <p>${data.advice}</p>
            ${data.audio_url ? `<audio controls src="${data.audio_url}"></audio>` : ""}
        `;
    } catch (err) {
        spinner.style.display = "none";
        resultBox.innerHTML = `<p>Something went wrong. Please try again.</p>`;
        resultBox.classList.add("show", "alert");
        console.error(err);
    }
});
