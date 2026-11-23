const STORAGE_KEY = "tugas";

const form = document.getElementById("form");
const input = document.getElementById("input");
const list = document.getElementById("list");
const summary = document.getElementById("summary");

let tasks = loadTasks();

function loadTasks() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function addTask(text) {
  tasks.push({ id: Date.now(), text, done: false });
  saveTasks();
  render();
}

function toggleTask(id) {
  const task = tasks.find((t) => t.id === id);
  if (task) task.done = !task.done;
  saveTasks();
  render();
}

function deleteTask(id) {
  tasks = tasks.filter((t) => t.id !== id);
  saveTasks();
  render();
}

function updateSummary() {
  const remaining = tasks.filter((t) => !t.done).length;
  summary.textContent = tasks.length
    ? `${remaining} dari ${tasks.length} tugas belum selesai`
    : "Belum ada tugas.";
}

function render() {
  list.innerHTML = "";
  for (const task of tasks) {
    const li = document.createElement("li");
    if (task.done) li.classList.add("done");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.done;
    checkbox.addEventListener("change", () => toggleTask(task.id));

    const label = document.createElement("span");
    label.textContent = task.text;

    const del = document.createElement("button");
    del.textContent = "Hapus";
    del.className = "delete";
    del.addEventListener("click", () => deleteTask(task.id));

    li.append(checkbox, label, del);
    list.appendChild(li);
  }
  updateSummary();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addTask(text);
  input.value = "";
});

render();
