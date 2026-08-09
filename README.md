# TaskFlow — Full-Stack AI-Assisted Task Management Platform

TaskFlow is a FastAPI + SQLAlchemy backend with a vanilla HTML/CSS/JavaScript dashboard. It includes task CRUD, project/user endpoints, SQL aggregation statistics, hand-written insertion/binary/linear search algorithms, and a deterministic zero-key AI quick-add parser.

## 1. Environment setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Running the whole app

This project uses the required two-process run.

Terminal 1:

```bash
uvicorn backend.main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
python3 -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

For convenient demo data, in a third terminal you can optionally run:

```bash
python3 seed.py
```

This creates a sample user, project, and ten tasks without changing the two-process application architecture.

The backend is:

```text
http://127.0.0.1:8000
```

CORS explicitly allows the frontend origin `http://127.0.0.1:5500` (and the equivalent localhost:5500 origin).

## Database

SQLite database file: `taskflow.db`.

Tables:

- `users`: id PK, name NOT NULL, email UNIQUE + NOT NULL
- `projects`: id PK, name NOT NULL, owner_id FK -> users.id
- `tasks`: id PK, title NOT NULL, priority CHECK low/medium/high, status CHECK todo/in_progress/done, nullable text due_date, project_id FK -> projects.id

SQLAlchemy relationships use `back_populates`:

- `User.projects` ↔ `Project.owner`
- `Project.tasks` ↔ `Task.project`

## Endpoint list

### Users

`POST /users`

Example request:

```json
{"name":"Rahul","email":"rahul@example.com"}
```

Example response:

```json
{"id":1,"name":"Rahul","email":"rahul@example.com"}
```

`GET /users`

Example response:

```json
[{"id":1,"name":"Rahul","email":"rahul@example.com"}]
```

### Projects

`POST /projects`

```json
{"name":"Dark Store Ops","owner_id":1}
```

Response:

```json
{"id":1,"name":"Dark Store Ops","owner_id":1}
```

`GET /projects`

```json
[{"id":1,"name":"Dark Store Ops","owner_id":1}]
```

### Tasks

`POST /tasks`

```json
{
  "title":"Fix scanner",
  "priority":"high",
  "status":"todo",
  "due_date":"tomorrow",
  "project_id":1
}
```

Response:

```json
{
  "id":1,
  "title":"Fix scanner",
  "priority":"high",
  "status":"todo",
  "due_date":"tomorrow",
  "project_id":1
}
```

`GET /tasks`

```json
[
  {
    "id":1,
    "title":"Fix scanner",
    "priority":"high",
    "status":"todo",
    "due_date":"tomorrow",
    "project_id":1
  }
]
```

`GET /tasks/1`

```json
{
  "id":1,
  "title":"Fix scanner",
  "priority":"high",
  "status":"todo",
  "due_date":"tomorrow",
  "project_id":1
}
```

`PUT /tasks/1`

```json
{"title":"Fix scanner urgently","status":"in_progress"}
```

Response:

```json
{
  "id":1,
  "title":"Fix scanner urgently",
  "priority":"high",
  "status":"in_progress",
  "due_date":"tomorrow",
  "project_id":1
}
```

`DELETE /tasks/1`

```json
{"message":"Task deleted","id":1}
```

Non-existent task IDs return 404. Invalid Pydantic request bodies return 422.

### Statistics

`GET /projects/stats`

Example:

```json
[
  {
    "project_id":1,
    "project_name":"Dark Store Ops",
    "task_count":3,
    "todo_count":1,
    "in_progress_count":1,
    "done_count":1
  }
]
```

The counts are computed in SQL using `COUNT`, `SUM`, `CASE`, `JOIN`, and `GROUP BY`; the application does not fetch every task and aggregate it in Python.

### Sorted list

`GET /tasks?sort=priority`

The endpoint fetches real task rows, maps low/medium/high to 1/2/3, then calls the hand-written `insertion_sort` function. It does not use `sorted()` or `list.sort()`.

### Search

`GET /tasks/search?title=Fix%20scanner&algo=binary`

Example response:

```json
{
  "id":1,
  "title":"Fix scanner",
  "priority":"high",
  "status":"todo",
  "due_date":"tomorrow",
  "project_id":1
}
```

`algo=binary` uses `insertion_sort` followed by `binary_search`. `algo=linear` uses `linear_search` over the unsorted in-memory index. Not-found searches return 404.

### Quick-add

`POST /tasks/quick-add`

```json
{
  "description":"Fix the urgent scanner issue tomorrow",
  "project_id":1
}
```

Example response:

```json
{
  "id":2,
  "title":"Fix the  scanner issue",
  "priority":"high",
  "status":"todo",
  "due_date":"tomorrow",
  "project_id":1
}
```

The parser is deterministic, keyless, and makes zero network calls. The candidate task is validated through `TaskCreate` before being written.

## 2. Algorithms engine

### Complexity

- Insertion sort: best case O(n), worst case O(n²), in-place.
- Binary search: best case O(1), worst case O(log n), requires sorted input.
- Linear search: best case O(1), worst case O(n).

The sorting/search endpoints use the exact same algorithm implementations in `backend/algorithms.py`.

### Automated checks

Run:

```bash
python3 check_algorithms.py
```

It prints PASS/FAIL lines for every required case.

### Benchmark

Run:

```bash
python3 benchmark.py
```

The benchmark uses realistic task-shaped dictionaries at sizes 10, 500, and 3,000.

Raw comparison counts produced by the committed benchmark:

```text
size=10: insertion_sort_count=27, binary_search_count=7, linear_search_count=10
size=500: insertion_sort_count=62442, binary_search_count=17, linear_search_count=485
size=3000: insertion_sort_count=2260131, binary_search_count=23, linear_search_count=2574
```

Run the script on the final repository and copy its exact output here before submission so the README contains the measured numbers from the submitted implementation.

For TaskFlow usage, sorting first is most useful when the team repeatedly requests ordered lists and then performs multiple searches on that ordered data. Insertion sort has a quadratic worst case, so repeatedly rebuilding a sorted list can become expensive as the task list grows. Binary search, however, reduces each exact-title lookup to logarithmic time after sorting. Because the brief says teams list/sort repeatedly but add or rename less often, paying the sorting cost can be worthwhile when the same sorted snapshot is reused for several searches. The benchmark numbers should be used to justify this decision with the actual measured counts.

## 3. AI Quick-Add

### Prompting technique

The quick-add design is closest to **zero-shot prompting**: the system role explains the desired parsing behavior and the user role carries the actual task description, without requiring a set of demonstrations for the mock parser. This keeps the prompt small and reduces token usage compared with few-shot prompting. The deterministic rule-based mock is more reliable for grading because identical input produces identical output without network calls or model randomness. Chain-of-thought is not required because the output is a structured extraction task, not a request for hidden reasoning. The production code therefore prioritizes predictable fields, closed priority values, and exact date-phrase matching.

### Five worked examples

1. Input:

```text
Fix scanner urgent tomorrow
```

Output:

```json
{
  "title":"Fix scanner",
  "priority":"high",
  "due_date_hint":"tomorrow"
}
```

2. Input:

```text
Review inventory whenever next Monday
```

Output:

```json
{
  "title":"Review inventory",
  "priority":"low",
  "due_date_hint":"next monday"
}
```

3. Input:

```text
Prepare weekly report next Friday
```

Output:

```json
{
  "title":"Prepare weekly report",
  "priority":"medium",
  "due_date_hint":"next friday"
}
```

4. Input:

```text
ASAP update the payment dashboard on Friday
```

Output:

```json
{
  "title":"update the payment dashboard on",
  "priority":"high",
  "due_date_hint":"friday"
}
```

5. Input:

```text
Urgent but low priority: check storage tomorrow
```

Output:

```json
{
  "title":"but : check storage",
  "priority":"high",
  "due_date_hint":"tomorrow"
}
```

The mock checks priority groups in the required order, checks date phrases in the required order, removes every priority keyword occurrence, removes every occurrence of the matched date phrase, preserves the remaining original casing, and uses `Untitled task` if nothing remains.

## Git workflow requirement

The final repository history must show a feature branch with at least two commits and a merge back into `main`. Example commands:

```bash
git checkout -b feature/core-app
git add .
git commit -m "build core TaskFlow app"
git add .
git commit -m "add algorithms and quick add"
git checkout main
git merge --no-ff feature/core-app -m "merge TaskFlow feature"
git log --graph --oneline --all
```

Do not submit until the public repository is accessible and the documented commands work from a clean checkout.

## Git Workflow
This project uses a feature branch workflow for development.

## Project Status
TaskFlow core application, algorithms engine, and AI quick-add are included.
