const API_BASE = "http://127.0.0.1:8000";
const CACHE_KEY = "taskflow_tasks";

const form = document.getElementById("task-form");
const titleInput = document.getElementById("title");
const titleError = document.getElementById("title-error");
const priorityInput = document.getElementById("priority");
const dueDateInput = document.getElementById("due-date");
const projectIdInput = document.getElementById("project-id");
const taskList = document.getElementById("task-list");

const quickForm = document.getElementById("quick-add-form");
const descriptionInput = document.getElementById("description");
const quickProjectIdInput = document.getElementById("quick-project-id");
const quickMessage = document.getElementById("quick-add-message");

function cacheTasks(tasks) {
  localStorage.setItem(CACHE_KEY, JSON.stringify(tasks));
}

function readCachedTasks() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function renderTasks(tasks) {
  taskList.replaceChildren();

  if (!tasks.length) {
    const empty = document.createElement("p");
    empty.textContent = "No tasks yet.";
    taskList.appendChild(empty);
    return;
  }

  tasks.forEach((task) => {
    const item = document.createElement("article");
    item.className = "task-item";

    const details = document.createElement("div");

    const title = document.createElement("div");
    title.className = "task-title";
    title.textContent = task.title;

    const meta = document.createElement("div");
    meta.className = "task-meta";
    meta.textContent =
      `Priority: ${task.priority} | Status: ${task.status} | Due: ${task.due_date || "none"}`;

    details.appendChild(title);
    details.appendChild(meta);

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "Edit";
    editButton.addEventListener("click", () => editTask(task));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => deleteTask(task.id));

    actions.appendChild(editButton);
    actions.appendChild(deleteButton);

    item.appendChild(details);
    item.appendChild(actions);
    taskList.appendChild(item);
  });
}

async function loadTasks() {
  const cached = readCachedTasks();
  if (cached.length) {
    renderTasks(cached);
  }

  try {
    const response = await fetch(`${API_BASE}/tasks`);
    if (!response.ok) {
      throw new Error("Could not load tasks");
    }

    const tasks = await response.json();
    cacheTasks(tasks);
    renderTasks(tasks);
  } catch (error) {
    console.error(error);
  }
}

function validateTitle() {
  if (!titleInput.value.trim()) {
    titleError.textContent = "Title is required.";
    return false;
  }

  titleError.textContent = "";
  return true;
}

titleInput.addEventListener("input", validateTitle);

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!validateTitle()) {
    return;
  }

  const payload = {
    title: titleInput.value.trim(),
    priority: priorityInput.value,
    due_date: dueDateInput.value.trim() || null,
    project_id: Number(projectIdInput.value),
  };

  const response = await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });

  if (response.ok) {
  titleInput.value = "";
  dueDateInput.value = "";
  titleError.textContent = "";
  await loadTasks();
}
else {
    const data = await response.json();
    titleError.textContent = data.detail || "Could not create task.";
  }
});

async function editTask(task) {
    const newTitle = window.prompt("New title:", task.title);

    if (newTitle === null) {
        return;
    }

    if (!newTitle.trim()) {
        window.alert("Title cannot be empty.");
        return;
    }

    const response = await fetch(`${API_BASE}/tasks/${task.id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: newTitle.trim()
        })
    });

    if (response.ok) {
        await loadTasks();
    } else {
        const data = await response.json();
        window.alert(data.detail || "Failed to update task.");
    }
}

async function deleteTask(taskId) {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: "DELETE",
  });

  if (response.ok) {
    await loadTasks();
  }
}

quickForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  quickMessage.textContent = "";

  if (!descriptionInput.value.trim()) {
    quickMessage.textContent = "Description is required.";
    return;
  }

  const response = await fetch(`${API_BASE}/tasks/quick-add`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      description: descriptionInput.value,
      project_id: Number(quickProjectIdInput.value),
    }),
  });

  if (response.ok) {
    descriptionInput.value = "";
    quickMessage.textContent = "Task created.";
    await loadTasks();
  } else {
    const data = await response.json();
    quickMessage.textContent = data.detail || "Quick-add failed.";
  }
});

loadTasks();
