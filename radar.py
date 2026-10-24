import asyncio, json, os, sys
from dotenv import load_dotenv

# Load API key from .env file if present
load_dotenv()

from tinyfish import TinyFish, AsyncTinyFish, RunStatus, BrowserProfile

if not os.getenv("TINYFISH_API_KEY"):
    sys.exit("Set TINYFISH_API_KEY first (see the setup guide).")

GOAL = (
    "Find internships open to students (software, AI or data roles preferred). "
    "For each one return title, location, remote (true/false), deadline and apply_link."
)

SCHEMA = {  # same fields on every run
    "type": "object",
    "properties": {
        "internships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "location": {"type": "string"},
                    "remote": {"type": "boolean"},
                    "deadline": {"type": "string"},
                    "apply_link": {"type": "string"},
                },
            },
        }
    },
}

PAGES = {  # swap in your own careers pages (test each one first)
    "Jane Street": "https://www.janestreet.com/join-jane-street/open-roles/",
    "Google": "https://www.google.com/about/careers/applications/jobs/results/?q=intern",
    "Microsoft": "https://jobs.careers.microsoft.com/global/en/search?q=intern",
    "Razorpay": "https://razorpay.com/jobs/",
}


def stage1():
    print("Starting Stage 1: Single agent on Jane Street...")
    client = TinyFish()  # reads TINYFISH_API_KEY
    url = PAGES["Jane Street"]
    # For sites that block bots: add browser_profile=BrowserProfile.STEALTH
    run = client.agent.run(url=url, goal=GOAL)
    print(f"Status: {run.status}")
    if run.status == RunStatus.COMPLETED:
        print(json.dumps(run.result, indent=2))
    else:
        print(f"Run ended with status: {run.status}")


async def scrape(pages):
    agents = AsyncTinyFish()
    runs = await asyncio.gather(
        *[agents.agent.run(url=u, goal=GOAL, output_schema=SCHEMA) for u in pages.values()],
        return_exceptions=True,
    )
    rows = []
    for name, run in zip(pages, runs):
        if isinstance(run, Exception) or run.status != RunStatus.COMPLETED:
            print(f"! {name}: no result ({run if isinstance(run, Exception) else run.status})")
            continue
        items = run.result.get("internships", []) if isinstance(run.result, dict) else []
        rows += [{"source": name, **i} for i in items]
    return rows


def save(rows):
    rows.sort(key=lambda r: not r.get("remote"))  # remote roles first
    with open("internships.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    for r in rows[:15]:
        tag = "REMOTE" if r.get("remote") else "      "
        print(
            f"{tag} {r.get('source', ''):<12} {r.get('title', '?')} | {r.get('location', '?')} | {r.get('deadline', '-')}"
        )
    print(f"\n-> internships.json written ({len(rows)} roles)")


def stage2():
    print("Starting Stage 2: Parallel scraping across career pages...")
    save(asyncio.run(scrape(PAGES)))


def stage3():
    print("Starting Stage 3: TinyFish Search query finding pages automatically...")
    hits = TinyFish().search.query(query="software engineering internship apply 2026")
    pages = {r.url: r.url for r in hits.results[:5]}  # search is free
    print(f"Found {len(pages)} pages via search. Scraping now...")
    save(asyncio.run(scrape(pages)))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    actions = {"1": stage1, "2": stage2, "3": stage3}
    if stage in actions:
        actions[stage]()
    else:
        print(f"Unknown stage '{stage}'. Choose 1, 2, or 3.")
