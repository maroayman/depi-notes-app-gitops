let state = {page: 1, limit: 10, search: ""};

const el = (sel) => document.querySelector(sel);
const notesEl = el("#notes");
const errorEl = el("#error");
const contentEl = el("#content");
const searchEl = el("#search");
const limitEl = el("#limit");
const prevEl = el("#prev");
const nextEl = el("#next");
const pageInfoEl = el("#pageinfo");

async function fetchNotes() {
  const params = new URLSearchParams({page: state.page, limit: state.limit});
  if (state.search) params.set("search", state.search);
  const res = await fetch(`/notes?${params.toString()}`);
  const data = await res.json();
  renderNotes(data.items);
  const totalPages = Math.max(1, Math.ceil(data.meta.total / state.limit));
  pageInfoEl.textContent = `Page ${state.page} of ${totalPages} • ${data.meta.total} notes`;
  prevEl.disabled = state.page <= 1;
  nextEl.disabled = state.page >= totalPages;
}

function renderNotes(items) {
  notesEl.innerHTML = "";
  for (const n of items) {
    const li = document.createElement("li");
    li.className = "bg-white rounded-xl shadow p-3";
    li.innerHTML = `
      <div class="flex justify-between items-start gap-2">
        <div class="flex-1">
          <textarea data-id="${n.id}" class="w-full border rounded p-2 note-content">${n.content}</textarea>
          <div class="text-xs text-gray-500 mt-1">${new Date(n.created_at).toLocaleString()}</div>
        </div>
        <div class="flex gap-2">
          <button data-id="${n.id}" class="save px-3 py-1 rounded bg-green-600 text-white">Save</button>
          <button data-id="${n.id}" class="delete px-3 py-1 rounded bg-red-600 text-white">Delete</button>
        </div>
      </div>
    `;
    notesEl.appendChild(li);
  }
}

async function addNote(e) {
  e.preventDefault();
  errorEl.classList.add("hidden");
  const content = contentEl.value.trim();
  if (!content) return;
  const res = await fetch("/notes", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({content})
  });
  if (res.ok) {
    contentEl.value = "";
    await fetchNotes();
  } else {
    const data = await res.json();
    errorEl.textContent = data.error || "Failed to add note";
    errorEl.classList.remove("hidden");
  }
}

async function handleListClick(e) {
  const id = e.target.getAttribute("data-id");
  if (!id) return;
  if (e.target.classList.contains("delete")) {
    if (!confirm("Delete this note?")) return;
    await fetch(`/notes/${id}`, {method: "DELETE"});
    await fetchNotes();
  } else if (e.target.classList.contains("save")) {
    const textarea = e.target.closest("li").querySelector(".note-content");
    const content = textarea.value.trim();
    const res = await fetch(`/notes/${id}`, {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({content})
    });
    if (!res.ok) {
      alert("Failed to update note");
    } else {
      await fetchNotes();
    }
  }
}

function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  el("#add-form").addEventListener("submit", addNote);
  notesEl.addEventListener("click", handleListClick);
  searchEl.addEventListener("input", debounce((e) => {
    state.search = e.target.value.trim();
    state.page = 1;
    fetchNotes();
  }, 300));
  limitEl.addEventListener("change", (e) => {
    state.limit = parseInt(e.target.value, 10);
    state.page = 1;
    fetchNotes();
  });
  prevEl.addEventListener("click", () => { state.page = Math.max(1, state.page - 1); fetchNotes(); });
  nextEl.addEventListener("click", () => { state.page = state.page + 1; fetchNotes(); });
  fetchNotes();
});
