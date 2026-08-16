# Four-Minute Demo Script

Target length: 3:35. English narration. Every claim maps to visible evidence.

## 0:00-0:25 — The personal friction

Show Windows drive measurements: C: 19.97 GB free, E: 927.86 GB free.

Narration: “My system drive was almost full while another drive was nearly
empty. The difficult part was not finding space. It was deciding what an agent
could safely remove—and ensuring a retry could never remove it twice.”

## 0:25-0:50 — Product and architecture

Show the README architecture and live URL.

Narration: “Red Tag is a background disk-pressure agent. A threshold creates an
incident without chat. Five Google ADK specialists reason with Gemini 3.6 Flash,
while deterministic code owns policy, execution, and idempotency.”

## 0:50-1:45 — Real Windows action, unedited

Run `scripts\run_windows_proof.ps1` in the project terminal. Keep the command and
complete JSON result visible.

Call out: 64 MiB threshold crossing, 64 files deleted, zero bytes after,
protected file preserved, unmarked parent blocked, duplicate delivery blocked,
action count one.

## 1:45-2:50 — Live Google Cloud proof, unedited

Open the public Judge Console and press **RUN CLOUD PIPELINE**. Show the five
stages arriving, then expand one evidence payload. End on `PROOF COMPLETE` and
the duplicate replay banner.

Narration: “The public API writes Firestore and dispatches Pub/Sub. An
authenticated private Cloud Run worker runs the live ADK workflow. The same
delivery is replayed deliberately, but Firestore's durable claim leaves the
action count at one.”

## 2:50-3:20 — Safety boundary

Show `managed_cache.py` marker validation and the reliability test names.

Narration: “The model never receives filesystem authority. The adapter requires
an exact marker, rejects links and escaped paths, and only deletes regular files
inside the managed cache child. SEV1 and unknown actions require a human.”

## 3:20-3:35 — Close

Return to the hero and architecture proof chips.

Narration: “Retries may repeat reasoning. Red Tag never repeats the operational
action. That is how an agent earns permission to act.”
