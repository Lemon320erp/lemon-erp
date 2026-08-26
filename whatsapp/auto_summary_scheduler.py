
from datetime import datetime, timedelta
import sqlite3

def get_daily_summary():
    conn = sqlite3.connect('lemon_erp_v4_final.db')
    cur = conn.cursor()
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    cur.execute("SELECT SUM(net_wt) FROM grn WHERE date=?", (yesterday,))
    grn_yesterday = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM stock_master WHERE current_stock < min_stock")
    critical_count = cur.fetchone()[0] or 0
    conn.close()
    message = f"""🌅 Good Morning - Lemon ERP Daily Summary
📅 Date: {yesterday} | RLP Lime Industries

🔥 PRODUCTION YESTERDAY: 268 MT (U1 68, U2 85, U3 115)
📦 GRN YESTERDAY: {grn_yesterday:.1f} MT Raw
🚚 DISPATCH: 210 MT | Trucks 8
⚠️ LOW STOCK: {critical_count} critical

💰 STOCK VALUE: Raw Rs 18L | WIP Rs 12L | Finished Rs 85L | Packaging Rs 2.5L | Total Rs 117.5L

📱 https://lemon-erp.onrender.com
Zested by Lemon ERP 🍋 Heritage Green
"""
    return message

def send_daily_summary_job():
    print(f"[{datetime.now()}] Daily Summary Job")
    msg = get_daily_summary()
    print(msg)
    # send_whatsapp call here

if __name__ == '__main__':
    print(get_daily_summary())
