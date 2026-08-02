# Reflection

(placeholder for reflection content moved from midcourse/reflection.md)
# Reflection — Mid-Course Project

For this project I used a mix of AI tools rather than sticking to one. I
started with Cursor's Agent for the early scaffolding, and used GitHub
Copilot when I started to used Visual Studio especially when we added the 
Kanban and to help remove duplicated task cards that were showing up on the 
Kanban board. Once I hit Cursor's free
usage limit partway through, I switched to working with Claude and Copilot
in chat for the rest of the project: implementing the due-dates and
search features, debugging, writing tests, and putting together this
documentation. That switch changed my workflow quite a bit — instead of
an agent editing files directly, I had to manually copy code from chat
into my editor, save it, and verify it myself at every step. It was
slower, but it also meant I understood every change more closely, since
I was the one placing it into the file.

One moment where AI genuinely helped was debugging a confusing `409
Conflict` error that started appearing on almost every test after I added
due-date fields to my models. On the surface it looked like a duplicate-
task problem, but tracing through the actual error and stack trace showed
the real cause: my `TaskResponse` model now required `due_date` and
`is_overdue`, but my storage code wasn't providing them, which caused a
Pydantic `ValidationError`. Because that error type is technically a
subclass of `ValueError`, and my route was catching `ValueError` broadly
to handle duplicates, the real error was getting silently mislabeled as a
409. I would not have found that on my own without going through the
stack trace carefully with AI's help.

On the other side, one moment that slowed me down was a duplicate-route
bug I introduced myself while editing `main.py`. I pasted a new version
of my `GET /tasks` route without realizing it left an old copy of the
same route still in the file, and in the process my `POST /tasks` route
got deleted entirely. This caused confusing `405` and `409` errors for a
while, and it took several rounds of pasting my actual file contents back
into chat before we found the real problem. It was a reminder that even
with AI help, I still need to carefully verify what's actually in my
files rather than assuming an edit landed the way I expected.

The place where my own review mattered most was noticing that I had
around nine terminal windows open at once, several of them likely still
running old `uvicorn` processes in the background. I raised that myself
when we were stuck debugging repeated `409` errors, and it turned out to
be a real contributing factor — multiple Python processes were competing
to read and write the same `data/tasks.json` file. That's a good example
of why I can't just trust AI-generated fixes blindly; sometimes the
answer is something environmental that only I can see, since I'm the one
looking at my actual terminal windows.