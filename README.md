# PurgeAtOnce

A small Python script that deletes **your own** messages from a single Discord DM channel, one at a time, up to a number you choose. It only touches messages where the author ID matches your account — the other person's messages are never touched.

---

## Requirements

- Linux (tested on Arch)
- Python 3.10+
- A Discord account and the DM channel you want to clean up

---

## Setup

From the project directory:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

That's it. The venv is needed because Arch's system Python is PEP 668 protected (you can't `pip install` directly into it).

---

## What you need before running

You need two pieces of info: your **Discord token** and the **DM channel ID**.

### 1. Discord token

> ⚠️ Treat this exactly like your password. Anyone who has it can fully control your account. **Never paste it into chats, screenshots, Discord messages, or commit it to git.**

1. Open https://discord.com/app in **Firefox or Chrome** (the native desktop client locks DevTools)
2. Press **F12** to open DevTools → click the **Network** tab
3. In the filter box, type `api`
4. In Discord, click any channel or send a message — this triggers traffic
5. In the request list, click any row (e.g. `messages?limit=10`)
6. On the right panel, click the **Headers** sub-tab
7. Scroll down to the **Request Headers** section
8. Find the line `Authorization: ...` — the value (three segments separated by dots) is your token
9. Right-click the value → **Copy**
10. Paste it straight into the script when prompted. Do not put it anywhere else.

### 2. DM channel ID

1. In Discord: **User Settings (gear) → Advanced → enable Developer Mode**
2. Close settings
3. Right-click the DM you want to clean up (in the sidebar) → **Copy Channel ID**
4. You'll get a number like `1411762391687106730`

You can also find it in the URL when the DM is open: `https://discord.com/channels/@me/<this-number-here>`.

---

## Running the script

From the project directory:

```bash
.venv/bin/python delete_messages.py
```

It will ask, in order:

| Prompt | What to enter |
|---|---|
| `Discord token:` | Paste the token (input is hidden — nothing appears as you type, that's normal). Press Enter. |
| `DM channel ID:` | Paste the 18–19 digit channel ID. Press Enter. |
| `How many of your messages to delete:` | A number, e.g. `10` for a test run, `500` for a bigger purge. Press Enter. |

It will start deleting and print progress for each one:

```
authenticated as user id 128850719601905...
deleted 1/10: 'whatever'
deleted 2/10: 'that's the truth'
...
done. deleted 10 message(s).
```

Stops automatically when it either hits your target number or runs out of messages from you in that channel.

---

## How it works

- Authenticates against `/users/@me` to confirm the token works and grab your user ID
- Pages backward through the channel, 100 messages per request
- Skips messages where `author.id` is not yours
- Sends a `DELETE` per matching message with a ~400 ms gap between deletes
- If Discord returns HTTP 429 (rate limit), it sleeps for the requested `retry_after` and retries

---

## Recovering if you leak your token

If you ever paste your token somewhere it doesn't belong (chat, screenshot, public repo, etc.):

1. Discord → **User Settings → My Account → Change Password**
2. That action invalidates every existing token tied to your account.
3. Log back into Discord, repeat the token-grab steps for a fresh one.
4. While you're there, turn on **Two-Factor Authentication**.

---

## Caveats

- **Discord's Terms of Service** technically prohibit automating user accounts (a.k.a. "selfbots"). Action against your account is unlikely for slow personal cleanup but is non-zero. The default 400 ms delay between deletes is intentionally conservative — don't crank it down.
- This script only deletes from **one DM channel per run**. There's no "purge every DM" mode by design — that's an easy way to nuke things you'd rather keep.
- Messages over a certain age can still be deleted via this endpoint (unlike bulk delete, which only works on messages under 14 days old).
- If your token expires or you change your password, you'll need to grab a fresh token before running again.

---

## Files

- `delete_messages.py` — the script
- `requirements.txt` — Python dependencies (just `requests`)
- `.venv/` — your local virtualenv (created during setup; do not commit)
