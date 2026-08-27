import json
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# Fix relative paths by getting repo root
REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"

def fetch_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    print(f"Fetching {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching contributions: {e}")
        sys.exit(1)
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Parse days
    days = soup.find_all("td", {"class": "ContributionCalendar-day"})
    
    if not days:
        print("Error: Could not parse any contribution days. The HTML structure might have changed.")
        sys.exit(1)
        
    contributions = []
    total_count = 0
    current_streak = 0
    longest_streak = 0
    best_day_count = 0
    best_day_date = ""
    
    for day in days:
        date = day.get('data-date')
        if not date:
            continue
            
        level = int(day.get('data-level', 0))
        # Github's new HTML uses a tool-tip with the count, or sometimes the text inside the span.
        # Let's try to extract it from the id, but usually it's just text inside.
        # It's safer to extract from the inner text if available, or just rely on level.
        # Wait, the exact count is often in the 'data-ix' or span text.
        # Actually, GitHub currently puts the count in `<tool-tip>N contributions on YYYY-MM-DD</tool-tip>`
        # Or inside `<span class="sr-only">N contributions on...</span>`
        count = 0
        sr_only = day.find('span', {'class': 'sr-only'})
        if sr_only:
            text = sr_only.text.strip()
            if text.lower().startswith('no '):
                count = 0
            else:
                try:
                    count = int(text.split(' ')[0])
                except ValueError:
                    pass
        
        contributions.append({
            "date": date,
            "level": level,
            "count": count
        })
        
        total_count += count
        if count > 0:
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
        else:
            current_streak = 0
            
        if count > best_day_count:
            best_day_count = count
            best_day_date = date
            
    if not contributions:
        print("Error: Parsed days but found no valid dates.")
        sys.exit(1)

    print(f"Successfully fetched {len(contributions)} days of contributions.")
    print(f"Total Contributions: {total_count}")
    
    result = {
        "username": username,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total_contributions": total_count,
        "longest_streak": longest_streak,
        "best_day": {"date": best_day_date, "count": best_day_count},
        "days": contributions
    }
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "contributions.json"
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"Saved contributions to {out_path}")

if __name__ == "__main__":
    # Import username from config
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from profile_config import config
        username = config.get("username", "ShubhamPawale108")
    except ImportError:
        username = "ShubhamPawale108"
        
    fetch_contributions(username)
