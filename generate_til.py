import os
import sys
import json
import datetime
import urllib.request
import urllib.error
import ssl

def get_ssl_context():
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()

def get_today_date():
    # Return YYYY-MM-DD in UTC+7 (WIB)
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    wib_now = utc_now + datetime.timedelta(hours=7)
    return wib_now.strftime("%Y-%m-%d")

def fetch_json(url, context):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (DailyTILBot/1.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10, context=context) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError:
        unverified = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=10, context=unverified) as resp:
            return json.loads(resp.read().decode("utf-8"))

def generate_via_hn(date_str):
    ctx = get_ssl_context()
    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json", ctx)[:5]

    items = []
    for item_id in ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        try:
            data = fetch_json(item_url, ctx)
            if data and "title" in data:
                items.append(data)
        except Exception:
            continue

    lines = [
        f"# Today I Learned: {date_str}",
        "",
        "## Tech Highlights & Industry Radar",
        ""
    ]
    for it in items:
        title = it.get("title", "")
        url = it.get("url", f"https://news.ycombinator.com/item?id={it.get('id')}")
        score = it.get("score", 0)
        by = it.get("by", "community")
        lines.append(f"### {title}")
        lines.append(f"- **URL**: [{url}]({url})")
        lines.append(f"- **Discussions**: {by} ({score} upvotes)")
        lines.append("")
    return "\n".join(lines).strip() + "\n"

def main():
    date_str = get_today_date()
    filename = f"{date_str}-til.md"

    content = generate_via_hn(date_str)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Generated {filename}")

if __name__ == "__main__":
    main()
