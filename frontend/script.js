const API_BASE = "http://127.0.0.1:8000/api";

const resultBox = document.querySelector("#resultBox");

function show(data) {
  resultBox.textContent = JSON.stringify(data, null, 2);
}

async function validatePaste() {
  const language = document.querySelector("#language").value;
  const code = document.querySelector("#code").value;

  const response = await fetch(`${API_BASE}/validate/paste`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, code }),
  });
  show(await response.json());
}

async function validateUpload() {
  const file = document.querySelector("#file").files[0];
  if (!file) {
    show({ error: "Choose a .py or .java file first." });
    return;
  }

  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${API_BASE}/validate/upload`, {
    method: "POST",
    body: form,
  });
  show(await response.json());
}

async function searchKb() {
  const query = encodeURIComponent(document.querySelector("#query").value);
  const response = await fetch(`${API_BASE}/knowledge/search?query=${query}&limit=3`);
  show(await response.json());
}

document.querySelector("#validatePaste").addEventListener("click", validatePaste);
document.querySelector("#validateUpload").addEventListener("click", validateUpload);
document.querySelector("#searchKb").addEventListener("click", searchKb);
