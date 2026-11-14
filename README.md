# SE 239 — Phase 2

**The Socket Scientists — Simple Ticket Booking System**

Team: Hamza Emad Ahmed (representative), Zackaria Muthana, Haroon Habash, Mohammad Bilal.
Names are reproduced as written in the proposal.

## Requirements
Python 3 with the standard library; no pip dependencies. Use four terminals for the manual Week 8 demonstration. All programs use localhost, so run them on the same computer.

## Week 6
Run `python week6/server.py`, then `python week6/client.py` in a second terminal. The client sends a greeting and the server sends a reply. The Week 6 server handles one connection and then exits.

## Week 8
Run `python week8/server.py`. In three separate terminals run `python week8/client.py`; enter a different client ID in each. Keep all clients open. Use `status` to show three connected members. Try `ping hello`, `list`, `book A1`, `my`, and `quit`.

The server starts a thread per connection. JOIN registers a unique active client ID; it is a classroom join step, not password authentication. Requests and replies are one JSON object per newline. Commands: JOIN, PING, STATUS, LIST, BOOK, MY_BOOKING. A shared lock protects members and the atomic booking check/update. One seat per ID is allowed; repeating the same successful request returns already_booked. A taken seat returns already_taken. Bookings last until the server stops; disconnecting releases the active ID but keeps its reservation.

## Reproduce the evidence
Stop any existing servers using ports 5006 or 5008, then run `python demo.py`. It starts the actual servers, exchanges the Week 6 message, joins three persistent TCP clients, tests simultaneous booking requests, checks errors, writes evidence logs, and opens a live evidence viewer. Closing the viewer stops its server. The named clients are test IDs; they do not prove the people themselves performed the run.

Evidence files contain actual run output, not a claim that milestones were completed on earlier dates. `evidence/live-demo.jpg` is a screenshot of the live evidence viewer when available.

## Submission steps still required
1. Repository: https://github.com/mobilal1209-commits/se239-socket-scientists
2. Have the team leader make a genuine commit using their own account. Do not invent contributions or backdate commits. Invite teammates so the repository is shared.
3. Ensure the instructor can access the repository. Review and understand the code as a team.
4. Submit the repository URL, evidence report, and all four names on Moodle. Follow your course's AI-assistance disclosure rules.

The screenshots supplied with the task require both milestones in Git, Week 6 message exchange, Week 8 three concurrent clients with basic join, evidence with short explanations, repository URL and team names. They do not specify a required report template or file format.

