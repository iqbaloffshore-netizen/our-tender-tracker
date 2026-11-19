import requests
from duckduckgo_search import DDGS
import os
import datetime
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram Configuration (from GitHub Secrets)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Search Queries Configuration
# Govt tenders: Focus on official portals
# Pvt tenders: Focus on news/awards
SEARCH_QUERIES = {
    "🏛️ Government Tenders": [
        "site:eprocure.gov.in steel structure tender active",
        "site:gem.gov.in industrial supply fabrication tender",
        "site:eprocure.gov.in steel plates pipes tender"
    ],
    "🏭 Private Sector Awards": [
        "awarded steel structure contract private refinery india",
        "tender awarded steel fabrication private steel plant india",
        "contract awarded industrial supply private sector india"
    ]
}

def send_telegram_message(message: str) -> bool:
    """Send formatted message to Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("Message sent to Telegram successfully")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def search_tenders(query: str, max_results: int = 3) -> list:
    """Search for tenders using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results, timelimit='w'))
            logging.info(f"Found {len(results)} results for query: {query}")
            return results
    except Exception as e:
        logging.error(f"Search failed for query '{query}': {e}")
        return []

def format_tender_alert(category: str, results: list) -> str:
    """Format search results into Telegram message"""
    if not results:
        return ""
    
    message = f"*{category}*\n\n"
    for idx, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        link = result.get('href', '#')
        snippet = result.get('body', '')[:100]
        
        message += f"{idx}. *{title}*\n"
        message += f"   🔗 {link}\n"
        if snippet:
            message += f"   _{snippet}..._\n"
        message += "\n"
    
    return message

def main():
    """Main execution function"""
    logging.info("Starting Wootz Tender Tracker...")
    
    current_date = datetime.datetime.now().strftime("%d %B %Y")
    final_message = f"*📊 Wootz Solutions - Daily Tender Update*\n"
    final_message += f"*📅 Date:* {current_date}\n\n"
    
    total_alerts = 0
    
    # Process each category
    for category, queries in SEARCH_QUERIES.items():
        category_results = []
        
        # Execute each query for this category
        for query in queries:
            results = search_tenders(query, max_results=2)
            category_results.extend(results)
        
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in category_results:
            url = result.get('href')
            if url and url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(url)
        
        # Format and add to final message
        if unique_results:
            alert_message = format_tender_alert(category, unique_results[:5])
            final_message += alert_message
            total_alerts += len(unique_results)
    
    # Send to Telegram if we have any alerts
    if total_alerts > 0:
        final_message += f"\n_✅ Total {total_alerts} relevant tenders found_"
        send_telegram_message(final_message)
        logging.info(f"Sent {total_alerts} tender alerts to Telegram")
    else:
        logging.info("No new tenders found today")

if __name__ == "__main__":
    main()
