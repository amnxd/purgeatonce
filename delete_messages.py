import getpass
import sys
import time

import requests

API = "https://discord.com/api/v10"


def headers(token: str) -> dict:
    return {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }


def request(method: str, url: str, token: str, **kwargs) -> requests.Response:
    while True:
        r = requests.request(method, url, headers=headers(token), timeout=30, **kwargs)
        if r.status_code == 429:
            retry = r.json().get("retry_after", 1)
            print(f"  rate limited, sleeping {retry:.2f}s")
            time.sleep(retry + 0.1)
            continue
        return r


def get_self_id(token: str) -> str:
    r = request("GET", f"{API}/users/@me", token)
    if r.status_code != 200:
        sys.exit(f"failed to authenticate ({r.status_code}): {r.text}")
    return r.json()["id"]


def fetch_batch(token: str, channel_id: str, before: str | None) -> list[dict]:
    params = {"limit": 100}
    if before:
        params["before"] = before
    r = request("GET", f"{API}/channels/{channel_id}/messages", token, params=params)
    if r.status_code != 200:
        sys.exit(f"failed to fetch messages ({r.status_code}): {r.text}")
    return r.json()


def delete_message(token: str, channel_id: str, message_id: str) -> bool:
    r = request("DELETE", f"{API}/channels/{channel_id}/messages/{message_id}", token)
    if r.status_code == 204:
        return True
    print(f"  could not delete {message_id} ({r.status_code}): {r.text}")
    return False


def main() -> None:
    token = getpass.getpass("Discord token: ").strip()
    channel_id = input("DM channel ID: ").strip()
    target = int(input("How many of your messages to delete: ").strip())

    self_id = get_self_id(token)
    print(f"authenticated as user id {self_id}")

    deleted = 0
    before: str | None = None

    while deleted < target:
        batch = fetch_batch(token, channel_id, before)
        if not batch:
            print("no more messages in this channel")
            break

        before = batch[-1]["id"]

        for msg in batch:
            if deleted >= target:
                break
            if msg["author"]["id"] != self_id:
                continue
            if delete_message(token, channel_id, msg["id"]):
                deleted += 1
                print(f"deleted {deleted}/{target}: {msg['content'][:60]!r}")
                time.sleep(0.4)

    print(f"done. deleted {deleted} message(s).")


if __name__ == "__main__":
    main()
