import requests
from duckduckgo_search import DDGS
import os
import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# SHARPENED QUERIES FOR WOOTZ SOLUTIONS
SEARCH_QUERIES = {
    "🏛️ Govt Steel/Industrial": [
        "site:eprocure.gov.in steel structure OR fabrication OR industrial supply tender active",
        "site:gem.gov.in steel plates OR pipes OR structural steel tender",
        "RDSS steel tower OR substation structure tender eprocure"
    ],
    "🏭 Pvt Awards & Contracts": [
        "Reliance OR Tata Steel OR JSW awarded steel contract india",
        "L&T OR Adani Ports steel structure contract awarded",
        "IOCL OR BPCL OR Nayara refinery maintenance tender awarded"
    ],
    "🚉 Railway & Bridges": [
        "IRCON OR RITES steel bridge OR girder tender awarded",
        "railway station redevelopment steel structure tender india"
    ]
}

def main():
    logging.info("Wootz Tender Tracker started...")
    date_str = datetime.datetime.now().strftime("%d %B %Y")
    msg = f"*📊 Wootz Solutions - Night Scan ({date_str})*\n\n"
    
    seen_urls = set()
    total = 0
    
    for category, queries in SEARCH_QUERIES.items():
        cat_alerts = []
        for q in queries:
            results = search_tenders(q, max_results=2)
            for r in results:
                url = r.get('href', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    cat_alerts.append(r)
        
        if cat_alerts:
            msg += f"*{category}*\n"
            for i, r in enumerate(cat_alerts[:4], 1):
                msg += f"{i}. *{r['title']}*\n   🔗 {r['href']}\n\n"
            total += len(cat_alerts)
    
    if total > 0:
        msg += f"_✅ {total} unique tenders found_"
        send_telegram_message(msg)
        logging.info(f"Sent {total} alerts")
    else:
        logging.info("No new tenders tonight")

# 👇 YE WALA BLOCK SABSE NEECHE HONA CHAHIYE
if __name__ == "__main__":
    main()
    # Daily status message force karne ke liye ye line yahan honi chahiye
    send_telegram_message("🤖 *Wootz Night Scan Complete*\nSystem successfully ran at 11:00 PM IST.")
