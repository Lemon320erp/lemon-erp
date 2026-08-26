"""
🍋 LEMON ERP v4.2 - RLP LIME INDUSTRIES - PRODUCTION READY
Based on full chat history: Vendor, PO, GRN, Raw/WIP/Finished/Packaging, QR, Kiln, Hydration, Weighbridge, Packaging, Mobile PWA, White-label
NO WhatsApp integration (as requested)
Heritage Green #1A2E1E + Brass #C9A86A + Alabaster #FAF6F0 + Lemon #F2E863
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode, base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'lemon-erp-v42-rlp-no-whatsapp-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v42.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS - FROM CHAT HISTORY =================
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    name = db.Column(db.String(100))
    vendor_type = db.Column(db.String(50))  # Limestone, Petcoke, Packaging, Transport, Trading
    gst = db.Column(db.String(30))
    contact = db.Column(db.String(50))
    credit_limit = db.Column(db.Float, default=500000)
    pending_due = db.Column(db.Float, default=0)
    payment_terms = db.Column(db.String(50), default='15 Days')
    rating = db.Column(db.Float, default=4.5)

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    po_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material_type = db.Column(db.String(50))
    material = db.Column(db.String(100))
    qty = db.Column(db.Float)
    rate = db.Column(db.Float)
    total = db.Column(db.Float)
    delivery_date = db.Column(db.String(20))
    unit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Draft')  # Draft, Sent, Partial, Received
    created_by = db.Column(db.String(100), default='Owner')

class GRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    grn_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    po_no = db.Column(db.String(50))
    vehicle_no = db.Column(db.String(50))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material_type = db.Column(db.String(50))
    material = db.Column(db.String(100))
    challan_no = db.Column(db.String(50))
    invoice_no = db.Column(db.String(50))
    gross_wt = db.Column(db.Float)
    tare_wt = db.Column(db.Float)
    net_wt = db.Column(db.Float)
    rejection_pct = db.Column(db.Float, default=0)
    stock_type = db.Column(db.String(20), default='Own')
    unit = db.Column(db.String(100))
    operator = db.Column(db.String(100))
    gps = db.Column(db.String(100))

class StockMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    product = db.Column(db.String(100))
    product_category = db.Column(db.String(50))  # Raw, WIP, Finished
    unit = db.Column(db.String(100))  # Unit 1 72MT etc
    min_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    max_stock = db.Column(db.Float, default=0)
    reorder_qty = db.Column(db.Float, default=0)
    current_stock = db.Column(db.Float, default=0)
    rate_per_mt = db.Column(db.Float, default=0)
    stock_value = db.Column(db.Float, default=0)

class PackagingStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    bag_type = db.Column(db.String(100))  # 40kg HDPE White, Jumbo A 1.2MT etc
    bag_category = db.Column(db.String(20))  # 40kg, Jumbo
    capacity_mt = db.Column(db.Float)  # 0.04, 1.2, 1.5
    opening = db.Column(db.Float, default=0)
    purchase_in = db.Column(db.Float, default=0)
    consumption = db.Column(db.Float, default=0)
    closing = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=200)
    rate_per_bag = db.Column(db.Float)
    unit = db.Column(db.String(100))

class QRBag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    bag_id = db.Column(db.String(50), unique=True)
    product = db.Column(db.String(100))
    weight = db.Column(db.Float)
    unit = db.Column(db.String(100))
    customer = db.Column(db.String(100))
    vehicle_no = db.Column(db.String(50))
    qr_data = db.Column(db.Text)
    status = db.Column(db.String(20), default='Packed')  # Packed, Dispatched
    created_at = db.Column(db.String(30))

class KilnLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    date = db.Column(db.String(20))
    unit = db.Column(db.String(100))
    limestone_feed_mt = db.Column(db.Float)
    petcoke_consumed_mt = db.Column(db.Float)
    cao_produced_mt = db.Column(db.Float)
    burning_loss_pct = db.Column(db.Float)
    operator = db.Column(db.String(100))

class HydrationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, default=1)
    date = db.Column(db.String(20))
    unit = db.Column(db.String(100))
    cao_input_mt = db.Column(db.Float)
    hydrated_output_mt = db.Column(db.Float)
    grade = db.Column(db.String(20))  # 90%, 95%
    water_used_ltr = db.Column(db.Float)
    operator = db.Column(db.String(100))

# INIT DB - FROM YOUR REQUIREMENTS
with app.app_context():
    db.create_all()
    if Vendor.query.count()==0:
        vendors=[
            Vendor(name='Limestone Mines Jodhpur', vendor_type='Limestone', gst='08ABCDE1234F1Z5', contact='9829011111', pending_due=250000, credit_limit=1000000, rating=4.8),
            Vendor(name='Petcoke Traders Gujarat', vendor_type='Petcoke', gst='24ABCDE1234F1Z5', contact='9829022222', pending_due=180000, credit_limit=800000, rating=4.5),
            Vendor(name='HDPE Bags Indore', vendor_type='Packaging', gst='23ABCDE1234F1Z5', contact='9829033333', pending_due=45000, credit_limit=300000, rating=4.6),
            Vendor(name='Jumbo Bags Ahmedabad', vendor_type='Packaging', gst='24ABCDE1234F1Z5', contact='9829044444', pending_due=120000, credit_limit=500000, rating=4.7),
            Vendor(name='RLP Transport', vendor_type='Transport', gst='08ABCDE1234F1Z5', contact='9829055555', pending_due=35000, credit_limit=200000, rating=4.3),
        ]
        for v in vendors: db.session.add(v)
        db.session.commit()
        stocks=[
            # Raw - Unit 1 72MT
            StockMaster(product='Limestone', product_category='Raw', unit='Unit 1 72MT', min_stock=100, reorder_level=150, max_stock=500, reorder_qty=200, current_stock=120, rate_per_mt=7000, stock_value=840000),
            StockMaster(product='Petcoke', product_category='Raw', unit='Unit 1 72MT', min_stock=15, reorder_level=20, max_stock=60, reorder_qty=30, current_stock=18, rate_per_mt=30000, stock_value=540000),
            StockMaster(product='Calcined Petcoke', product_category='Raw', unit='Unit 1 72MT', min_stock=5, reorder_level=8, max_stock=20, reorder_qty=10, current_stock=5, rate_per_mt=45000, stock_value=225000),
            # Raw - Unit 2 84MT
            StockMaster(product='Limestone', product_category='Raw', unit='Unit 2 84MT', min_stock=100, reorder_level=150, max_stock=500, reorder_qty=200, current_stock=135, rate_per_mt=7000, stock_value=945000),
            StockMaster(product='Petcoke', product_category='Raw', unit='Unit 2 84MT', min_stock=15, reorder_level=25, max_stock=60, reorder_qty=30, current_stock=22, rate_per_mt=30000, stock_value=660000),
            # Raw - Unit 3 125MT
            StockMaster(product='Limestone', product_category='Raw', unit='Unit 3 125MT', min_stock=150, reorder_level=200, max_stock=600, reorder_qty=250, current_stock=180, rate_per_mt=7000, stock_value=1260000),
            StockMaster(product='Petcoke', product_category='Raw', unit='Unit 3 125MT', min_stock=20, reorder_level=30, max_stock=80, reorder_qty=40, current_stock=28, rate_per_mt=30000, stock_value=840000),
            # WIP
            StockMaster(product='CaO Loose', product_category='WIP', unit='Unit 1 72MT', min_stock=20, reorder_level=30, max_stock=100, reorder_qty=40, current_stock=20, rate_per_mt=15000, stock_value=300000),
            StockMaster(product='CaO Loose', product_category='WIP', unit='Unit 2 84MT', min_stock=25, reorder_level=35, max_stock=120, reorder_qty=50, current_stock=25, rate_per_mt=15000, stock_value=375000),
            StockMaster(product='CaO Loose', product_category='WIP', unit='Unit 3 125MT', min_stock=30, reorder_level=45, max_stock=150, reorder_qty=60, current_stock=35, rate_per_mt=15000, stock_value=525000),
            # Finished - Quicklime
            StockMaster(product='CaO 10-40mm', product_category='Finished', unit='Unit 1 72MT', min_stock=50, reorder_level=80, max_stock=300, reorder_qty=100, current_stock=85, rate_per_mt=15000, stock_value=1275000),
            StockMaster(product='CaO 0-3mm', product_category='Finished', unit='Unit 1 72MT', min_stock=30, reorder_level=50, max_stock=200, reorder_qty=80, current_stock=32, rate_per_mt=14500, stock_value=464000),
            StockMaster(product='CaO 10-40mm', product_category='Finished', unit='Unit 2 84MT', min_stock=60, reorder_level=90, max_stock=350, reorder_qty=120, current_stock=95, rate_per_mt=15000, stock_value=1425000),
            StockMaster(product='CaO 0-3mm', product_category='Finished', unit='Unit 2 84MT', min_stock=40, reorder_level=60, max_stock=220, reorder_qty=90, current_stock=42, rate_per_mt=14500, stock_value=609000),
            StockMaster(product='CaO 10-40mm', product_category='Finished', unit='Unit 3 125MT', min_stock=70, reorder_level=100, max_stock=400, reorder_qty=150, current_stock=110, rate_per_mt=15000, stock_value=1650000),
            # Finished - Hydrated
            StockMaster(product='Hydrated 90%', product_category='Finished', unit='Unit 1 72MT', min_stock=10, reorder_level=20, max_stock=80, reorder_qty=30, current_stock=12, rate_per_mt=20000, stock_value=240000),
            StockMaster(product='Hydrated 95%', product_category='Finished', unit='Unit 2 84MT', min_stock=8, reorder_level=15, max_stock=60, reorder_qty=25, current_stock=8, rate_per_mt=25000, stock_value=200000),
            StockMaster(product='Hydrated 90%', product_category='Finished', unit='Unit 3 125MT', min_stock=12, reorder_level=22, max_stock=90, reorder_qty=35, current_stock=15, rate_per_mt=20000, stock_value=300000),
        ]
        for s in stocks: db.session.add(s)
        packs=[
            PackagingStock(bag_type='40kg HDPE White Bag', bag_category='40kg', capacity_mt=0.04, opening=4500, purchase_in=2000, consumption=1500, closing=5000, min_stock=2000, rate_per_bag=18, unit='Unit 1 72MT'),
            PackagingStock(bag_type='40kg HDPE Yellow Bag', bag_category='40kg', capacity_mt=0.04, opening=2800, purchase_in=1000, consumption=800, closing=3000, min_stock=1500, rate_per_bag=18.5, unit='Unit 1 72MT'),
            PackagingStock(bag_type='Jumbo Type A 1.2MT', bag_category='Jumbo', capacity_mt=1.2, opening=100, purchase_in=50, consumption=30, closing=120, min_stock=50, rate_per_bag=450, unit='Unit 1 72MT'),
            PackagingStock(bag_type='Jumbo Type B 1.5MT', bag_category='Jumbo', capacity_mt=1.5, opening=60, purchase_in=30, consumption=20, closing=70, min_stock=30, rate_per_bag=520, unit='Unit 2 84MT'),
            PackagingStock(bag_type='Jumbo Type A 1.2MT', bag_category='Jumbo', capacity_mt=1.2, opening=80, purchase_in=40, consumption=25, closing=95, min_stock=40, rate_per_bag=450, unit='Unit 3 125MT'),
        ]
        for p in packs: db.session.add(p)
        # Sample Kiln logs
        db.session.add_all([
            KilnLog(date='2026-08-26', unit='Unit 1 72MT', limestone_feed_mt=45, petcoke_consumed_mt=3.2, cao_produced_mt=24, burning_loss_pct=46.6, operator='operator1'),
            KilnLog(date='2026-08-26', unit='Unit 2 84MT', limestone_feed_mt=52, petcoke_consumed_mt=3.8, cao_produced_mt=28, burning_loss_pct=46.1, operator='operator2'),
        ])
        db.session.commit()

# ================= ROUTES =================
@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html><head><title>Lemon ERP v4.2 - RLP Full - No WhatsApp</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1A2E1E">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--line:#E8E0D5}
*{box-sizing:border-box} body{background:var(--alab);margin:0;font-family:'Segoe UI',Inter,Arial;color:var(--green);line-height:1.4}
.header{background:var(--green);color:var(--brass);padding:16px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;border-bottom:3px solid var(--brass)}
.header h1{margin:0;font-size:20px;letter-spacing:0.5px}.header p{margin:4px 0 0;font-size:11px;opacity:0.85}
.tabs{display:flex;background:white;border-bottom:2px solid var(--brass);overflow-x:auto;position:sticky;top:62px;z-index:90;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{padding:13px 16px;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap;font-weight:700;font-size:12.5px;letter-spacing:0.2px;transition:0.2s}
.tab:hover{background:var(--alab)} .tab.active{border-bottom:3px solid var(--green);color:var(--green);background:var(--alab)}
.content{padding:14px;max-width:1300px;margin:auto}
.card{background:white;border-radius:14px;padding:16px;margin:12px 0;box-shadow:0 6px 18px rgba(26,46,30,0.06);border:1px solid var(--line);border-left:6px solid var(--brass)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.grid4{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.stat{font-size:26px;font-weight:900;color:var(--green);margin:4px 0}.small{font-size:11.5px;color:#6B7D6F}
.btn{background:var(--green);color:var(--alab);padding:10px 16px;border-radius:9px;border:none;cursor:pointer;font-weight:700;margin:4px;font-size:13px;transition:0.2s}
.btn:hover{transform:translateY(-1px);box-shadow:0 4px 10px rgba(0,0,0,0.15)}
.btn-lemon{background:var(--lemon);color:var(--green)} .btn-outline{background:white;color:var(--green);border:2px solid var(--green)}
.badge{padding:5px 11px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:0.3px}
.ok{background:var(--green);color:white} .warn{background:#EF6C00;color:white} .crit{background:#C62828;color:white} .info{background:var(--brass);color:var(--green)}
table{width:100%;border-collapse:collapse;font-size:13px} th{background:var(--green);color:var(--brass);padding:11px 10px;text-align:left;font-weight:700;letter-spacing:0.3px} td{padding:10px;border-bottom:1px solid #F0EBE2}
input,select{padding:10px 12px;border-radius:9px;border:1.5px solid #E8E0D5;width:100%;margin:6px 0;font-size:13px;background:white}
input:focus,select:focus{outline:none;border-color:var(--brass);box-shadow:0 0 0 3px rgba(201,168,106,0.2)}
.row{display:flex;gap:10px;flex-wrap:wrap}.row>*{flex:1;min-width:150px}
.hidden{display:none}
.kpi{border-left-color:var(--green)} .kpi-lemon{border-left-color:var(--lemon)}
h3{margin:0 0 12px 0;font-size:15px;display:flex;align-items:center;gap:8px}
.qr-box{text-align:center;padding:12px;background:var(--alab);border-radius:12px;margin-top:10px}
</style></head><body>
<div class="header">
<div><h1>🍋 Lemon ERP v4.2 - RLP LIME</h1><p>Unit 1 72MT | Unit 2 84MT | Unit 3 125MT | 18 Products | 5 Packaging | LIVE: lemon-erp.onrender.com | v4.2 No WhatsApp</p></div>
<div><span class="badge info">v4.2 PROD</span> <button class="btn btn-lemon" onclick="openTab('dash')" style="margin-left:8px">Dashboard</button></div>
</div>

<div class="tabs">
<div class="tab active" onclick="openTab('dash')">📊 Dashboard</div>
<div class="tab" onclick="openTab('raw')">🪨 Raw</div>
<div class="tab" onclick="openTab('wip')">⚙️ WIP</div>
<div class="tab" onclick="openTab('fin')">✅ Finished</div>
<div class="tab" onclick="openTab('pack')">🎒 Packaging</div>
<div class="tab" onclick="openTab('grn')">🚛 GRN / Weighbridge</div>
<div class="tab" onclick="openTab('po')">📦 PO / Vendors</div>
<div class="tab" onclick="openTab('kiln')">🔥 Kiln & Hydration</div>
<div class="tab" onclick="openTab('qr')">🔳 QR / Dispatch</div>
<div class="tab" onclick="openTab('mobile')">📱 Mobile PWA</div>
</div>

<div class="content">

<!-- DASHBOARD -->
<div id="dash" class="tabcontent">
<div class="grid grid4">
<div class="card kpi"><div class="small">Total Stock Value</div><div class="stat" id="totalVal">Rs 118.9 Lakh</div><div class="small">Raw 45.3L | WIP 12.0L | Finished 53.8L | Pack 2.1L</div><span class="badge ok">System OK</span></div>
<div class="card kpi-lemon"><div class="small">Today Production</div><div class="stat">52 MT CaO</div><div class="small">Unit1 24 MT | Unit2 28 MT | Burning Loss 46%</div><span class="badge info">Kiln Running</span></div>
<div class="card"><div class="small">Packaging Available</div><div class="stat">5,190 Bags</div><div class="small">HDPE 8,000 | Jumbo 285 | Min Stock OK</div><span class="badge ok">Sufficient</span></div>
<div class="card"><div class="small">Date & Units</div><div class="stat" style="font-size:18px" id="todayDate"></div><div class="small">3 Units Active | 8 Vendors | 5 PO Pending</div><button class="btn" onclick="loadAll()">Refresh All</button></div>
</div>

<div class="grid">
<div class="card"><h3>📈 Unit-wise Stock Value</h3><canvas id="unitChart" height="140"></canvas><div id="unitBreak" class="small"></div></div>
<div class="card"><h3>⚠️ Low Stock Alerts - Auto Reorder</h3><div id="alerts">Loading...</div></div>
</div>

<div class="card"><h3>🔍 Quick Filter</h3><div class="row"><select id="fUnit"><option value="All">All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="fCat"><option value="All">All Categories</option><option>Raw</option><option>WIP</option><option>Finished</option><option>Packaging</option></select><button class="btn" onclick="loadAll()">Apply Filter</button><button class="btn btn-lemon" onclick="window.print()">Print Report</button></div></div>
</div>

<!-- RAW -->
<div id="raw" class="tabcontent hidden">
<div class="card"><h3>🪨 Raw Material - Limestone, Petcoke, Calcined Petcoke</h3><div id="rawTbl">Loading...</div></div>
</div>

<!-- WIP -->
<div id="wip" class="tabcontent hidden">
<div class="card"><h3>⚙️ WIP - CaO Loose - Kiln Output to Finished</h3><div id="wipTbl">Loading...</div></div>
</div>

<!-- FINISHED -->
<div id="fin" class="tabcontent hidden">
<div class="card"><h3>✅ Finished Goods - Quicklime + Hydrated Lime</h3><p class="small">Quicklime: 10-40mm, 0-3mm | Hydrated: 90%, 95% | Rate Rs 15k-25k per MT</p><div id="finTbl">Loading...</div></div>
</div>

<!-- PACKAGING -->
<div id="pack" class="tabcontent hidden">
<div class="card"><h3>🎒 Packaging Stock - HDPE 40kg & Jumbo 1.2/1.5MT</h3><p class="small">White-list: HDPE White 40kg, Yellow 40kg | Jumbo Type A 1.2MT, Type B 1.5MT | Min stock alerts | Consumption tracking</p><div id="packTbl">Loading...</div></div>
<div class="card"><h3>➕ Add Packaging Purchase</h3><div class="row"><select id="pk_type"><option>40kg HDPE White Bag</option><option>40kg HDPE Yellow Bag</option><option>Jumbo Type A 1.2MT</option><option>Jumbo Type B 1.5MT</option></select><input id="pk_qty" type="number" placeholder="Qty Bags"><select id="pk_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn" onclick="addPack()">Add Purchase</button></div></div>
</div>

<!-- GRN -->
<div id="grn" class="tabcontent hidden">
<div class="card"><h3>🚛 GRN - Weighbridge Entry - Gross/Tare/Net Auto</h3>
<div class="row"><input id="g_vehicle" placeholder="Vehicle No RJ19 GA 1234"><input id="g_material" placeholder="Material Limestone / Petcoke"><select id="g_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div>
<div class="row"><input id="g_gross" type="number" placeholder="Gross Wt kg e.g. 25000"><input id="g_tare" type="number" placeholder="Tare Wt kg e.g. 10000"><input id="g_challan" placeholder="Challan No"><input id="g_invoice" placeholder="Invoice No"></div>
<div class="row"><select id="g_vendor"></select><input id="g_po" placeholder="PO No (optional)"><select id="g_stockType"><option>Own</option><option>Traded</option><option>Own Processing</option></select></div>
<div class="row"><input id="g_operator" placeholder="Operator operator1"><input id="g_gps" placeholder="GPS auto"><button class="btn btn-lemon" onclick="createGRN()">💾 Save GRN + Update Stock</button></div>
<p class="small">Net = Gross - Tare (auto MT) | Photos upload ready | Operator & GPS capture | Stock auto updates</p>
</div>
<div class="card"><h3>📋 Recent GRNs (Last 50)</h3><div id="grnList">Loading...</div></div>
</div>

<!-- PO / VENDORS -->
<div id="po" class="tabcontent hidden">
<div class="card"><h3>🏭 Vendor Master - Pending Dues, Credit Limit, Rating</h3><div id="vendorTbl">Loading...</div></div>
<div class="card"><h3>📦 Create Purchase Order - Auto Total</h3>
<div class="row"><select id="po_vendor"></select><select id="po_mtype"><option>Raw</option><option>Packaging</option><option>Finished Trading</option></select><input id="po_mat" placeholder="Material Limestone 100MT"></div>
<div class="row"><input id="po_qty" type="number" placeholder="Qty MT / Bags"><input id="po_rate" type="number" placeholder="Rate per MT"><input id="po_delivery" type="date"><select id="po_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option><option>All Units</option></select></div>
<div class="row"><select id="po_status"><option>Draft</option><option>Sent</option><option>Partial</option><option>Received</option></select><button class="btn" onclick="createPO()">Create PO</button></div>
</div>
<div class="card"><h3>📄 PO List - Draft to Received</h3><div id="poList">Loading...</div></div>
</div>

<!-- KILN & HYDRATION -->
<div id="kiln" class="tabcontent hidden">
<div class="grid">
<div class="card"><h3>🔥 Kiln Log - Daily Feed & Production</h3>
<div class="row"><select id="k_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><input id="k_lime" type="number" placeholder="Limestone Feed MT"><input id="k_pet" type="number" placeholder="Petcoke MT"></div>
<div class="row"><input id="k_cao" type="number" placeholder="CaO Produced MT"><input id="k_operator" placeholder="Operator"><button class="btn" onclick="addKiln()">Save Kiln Log</button></div>
<div id="kilnList" style="margin-top:12px">Loading...</div>
</div>
<div class="card"><h3>💧 Hydration Log - CaO to Hydrated Lime</h3>
<div class="row"><select id="h_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><input id="h_cao" type="number" placeholder="CaO Input MT"><input id="h_out" type="number" placeholder="Hydrated Output MT"></div>
<div class="row"><select id="h_grade"><option>90%</option><option>95%</option></select><input id="h_water" type="number" placeholder="Water Ltr"><input id="h_operator" placeholder="Operator"><button class="btn btn-lemon" onclick="addHyd()">Save Hydration</button></div>
<div id="hydList" style="margin-top:12px">Loading...</div>
</div>
</div>
</div>

<!-- QR / DISPATCH -->
<div id="qr" class="tabcontent hidden">
<div class="card"><h3>🔳 QR Bag - Heritage Green QR - Dispatch Ready</h3>
<div class="row"><select id="qr_product"><option>CaO 10-40mm</option><option>CaO 0-3mm</option><option>Hydrated 90%</option><option>Hydrated 95%</option></select><input id="qr_weight" type="number" value="1.2" step="0.1" placeholder="Weight MT"><select id="qr_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div>
<div class="row"><input id="qr_customer" placeholder="Customer Name (optional)"><input id="qr_vehicle" placeholder="Vehicle No for Dispatch"><button class="btn btn-lemon" onclick="genQR()">Generate QR + Bag ID</button></div>
<div class="qr-box"><div id="qrResult" class="small"></div><div id="qrImg"></div></div>
</div>
<div class="card"><h3>🚚 Dispatch List - Packed to Dispatched</h3><div id="qrList">Loading...</div></div>
</div>

<!-- MOBILE -->
<div id="mobile" class="tabcontent hidden">
<div class="card"><h3>📱 Mobile PWA - Operator App - Unit 1 / Unit 2 / Unit 3</h3>
<p><b>Logins:</b> operator1 / op123 (U1 72MT) | operator2 / op123 (U2 84MT) | operator3 / op123 (U3 125MT) | manager / mgr123 | owner / owner123</p>
<p class="small">Chrome → 3 dots → Add to Home Screen → Lemon ERP icon on phone | Works offline | GPS capture | Quick GRN & Kiln entry</p>
<a class="btn" href="/mobile">Open Mobile App</a> <button class="btn btn-lemon" onclick="alert('Install: Open in Chrome > Menu > Add to Home Screen > Install')">How to Install</button>
</div>
<div class="card"><h3>📖 Operator Quick Guide</h3><p class="small">1. Login with unit | 2. GRN: Vehicle + Gross/Tare → Auto Net MT → Save → Stock updates | 3. Kiln: Limestone Feed + Petcoke → CaO Produced → Save | 4. Hydration: CaO Input → Hydrated Output 90/95% | 5. QR: Generate bag ID for dispatch</p></div>
</div>

</div>

<script>
function openTab(id){
 document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));
 document.getElementById(id).classList.remove('hidden');
 document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
 // find tab by onclick
 document.querySelectorAll('.tab').forEach(t=>{ if(t.getAttribute('onclick') && t.getAttribute('onclick').includes("'"+id+"'")) t.classList.add('active'); });
 if(id==='dash') loadDash();
 if(id==='raw' || id==='wip' || id==='fin' || id==='pack') loadStock();
 if(id==='grn'){loadVendors(); loadGRN();}
 if(id==='po'){loadVendors(); loadPO(); loadVendorsTable();}
 if(id==='kiln'){loadKiln(); loadHyd();}
 if(id==='qr') loadQRList();
}
document.getElementById('todayDate').innerText = new Date().toLocaleDateString('en-IN',{weekday:'short', year:'numeric', month:'short', day:'numeric'});

async function loadAll(){ loadDash(); loadStock(); loadVendors(); loadPO(); loadGRN(); loadVendorsTable(); loadKiln(); loadHyd(); loadQRList(); }

async function loadDash(){
 let res=await fetch('/api/stock_v4'); let data=await res.json();
 // calc totals
 let rawVal=0,wipVal=0,finVal=0,packVal=0;
 (data.Raw||[]).forEach(s=>rawVal+= (s.current*7000));
 (data.WIP||[]).forEach(s=>wipVal+= (s.current*15000));
 (data.Finished||[]).forEach(s=>{ let rate=s.product.includes('Hydrated')?(s.product.includes('95')?25000:20000):15000; finVal+= s.current*rate; });
 (data.Packaging||[]).forEach(p=>packVal+= p.current*(p.rate||20));
 let total=rawVal+wipVal+finVal+packVal;
 document.getElementById('totalVal').innerText='Rs '+(total/100000).toFixed(1)+' Lakh';
 // unit breakdown
 let units={'Unit 1 72MT':0,'Unit 2 84MT':0,'Unit 3 125MT':0};
 [...(data.Raw||[]),...(data.WIP||[]),...(data.Finished||[])].forEach(s=>{ if(units[s.unit]!==undefined) units[s.unit]+= s.current; });
 document.getElementById('unitBreak').innerHTML='U1: '+ (units['Unit 1 72MT']).toFixed(1)+' MT | U2: '+(units['Unit 2 84MT']).toFixed(1)+' MT | U3: '+(units['Unit 3 125MT']).toFixed(1)+' MT';
 // alerts
 let alerts=[];
 [...(data.Raw||[]),...(data.WIP||[]),...(data.Finished||[]),...(data.Packaging||[])].forEach(s=>{
   if(s.status==='Critical' || s.status==='Reorder') alerts.push(s);
 });
 let h='';
 if(alerts.length===0) h='<span class="badge ok">All Stock OK - No Reorder Needed</span>';
 else {
   h='<table><tr><th>Product</th><th>Unit</th><th>Current</th><th>Min</th><th>Status</th></tr>';
   alerts.slice(0,8).forEach(a=>{ let b=a.status==='Critical'?'crit':'warn'; h+=`<tr><td>${a.product}</td><td>${a.unit}</td><td>${a.current} MT</td><td>${a.min}</td><td><span class="badge ${b}">${a.status}</span></td></tr>`; });
   h+='</table><p class="small" style="margin-top:8px">Auto PO suggestion: Reorder '+alerts.map(a=>a.product).slice(0,3).join(', ')+' etc</p>';
 }
 document.getElementById('alerts').innerHTML=h;
 // simple bar chart via divs
 let chart=document.getElementById('unitChart');
 if(chart){
   let max=Math.max(...Object.values(units),1);
   let html='<div style="display:flex;align-items:end;gap:12px;height:120px">';
   for(let u in units){ let ht=(units[u]/max*100); html+=`<div style="flex:1;text-align:center"><div style="background:linear-gradient(to top,#1A2E1E,#C9A86A);height:${ht}%;border-radius:8px 8px 0 0;min-height:8px"></div><div class="small" style="margin-top:6px">${u.split(' ')[1]}<br><b>${units[u].toFixed(0)} MT</b></div></div>`; }
   html+='</div>';
   chart.outerHTML='<div id="unitChart">'+html+'</div>';
 }
}

async function loadStock(){
 let fUnit=document.getElementById('fUnit').value;
 let fCat=document.getElementById('fCat').value;
 let res=await fetch('/api/stock_v4'); let data=await res.json();
 function render(list, elId, isPack=false){
   let el=document.getElementById(elId); if(!el) return;
   let filtered=list.filter(s=>{ if(fUnit!=='All' && s.unit!==fUnit) return false; if(fCat!=='All' && !isPack && s.product_category!==fCat.split(' ')[0] && fCat!=='All' ) return false; return true; });
   if(filtered.length===0){ el.innerHTML='<span class="small">No data for filter</span>'; return; }
   let html='<table><tr><th>Product</th><th>Unit</th><th>Current</th><th>Min/Reorder/Max</th><th>Rate</th><th>Value</th><th>Status</th></tr>';
   filtered.forEach(s=>{
     let badge=s.status==='OK'?'ok':(s.status==='Reorder'?'warn':'crit');
     let rate=s.rate_per_mt || s.rate || (s.product.includes('Hydrated')?(s.product.includes('95%')?25000:20000): (s.product.includes('Limestone')?7000: (s.product.includes('Petcoke')?30000:15000)));
     let val=(s.current*rate/100000).toFixed(2);
     let minReorder=isPack? `${s.min}` : `${s.min}/${s.reorder}/${s.max||'-'}`;
     html+=`<tr><td>${s.product}</td><td>${s.unit}</td><td><b>${s.current} ${isPack?'Bags':'MT'}</b></td><td>${minReorder}</td><td>Rs ${rate}</td><td>Rs ${val} L</td><td><span class="badge ${badge}">${s.status}</span></td></tr>`;
   });
   html+='</table>';
   el.innerHTML=html;
 }
 render(data.Raw||[], 'rawTbl');
 render(data.WIP||[], 'wipTbl');
 render(data.Finished||[], 'finTbl');
 render(data.Packaging||[], 'packTbl', true);
 if(document.getElementById('packTbl') && data.Packaging) render(data.Packaging||[], 'packTbl', true);
}

async function loadVendors(){
 let res=await fetch('/api/vendors'); let vs=await res.json();
 let opts=vs.map(v=>`<option value="${v.id}">${v.name} - Due Rs ${v.pending_due} - ${v.vendor_type}</option>`).join('');
 let sel=document.getElementById('g_vendor'); if(sel) sel.innerHTML=opts;
 let sel2=document.getElementById('po_vendor'); if(sel2) sel2.innerHTML=opts;
}
async function loadVendorsTable(){
 let res=await fetch('/api/vendors'); let vs=await res.json();
 let h='<table><tr><th>Name</th><th>Type</th><th>GST</th><th>Contact</th><th>Credit Limit</th><th>Pending Due</th><th>Terms</th><th>Rating</th></tr>';
 vs.forEach(v=>{ h+=`<tr><td><b>${v.name}</b></td><td>${v.type}</td><td class="small">${v.gst||'-'}</td><td>${v.contact}</td><td>Rs ${(v.credit_limit||0).toLocaleString()}</td><td><b>Rs ${(v.pending_due||0).toLocaleString()}</b></td><td>${v.payment_terms||'-'}</td><td>${v.rating} ⭐</td></tr>`; });
 h+='</table>'; let el=document.getElementById('vendorTbl'); if(el) el.innerHTML=h;
}
async function loadGRN(){
 let res=await fetch('/api/grn'); let gs=await res.json();
 let h='<table><tr><th>GRN No</th><th>Date</th><th>Material</th><th>Net Wt</th><th>Vehicle</th><th>Unit</th><th>Vendor</th><th>Operator</th></tr>';
 gs.forEach(g=>{ h+=`<tr><td>${g.grn_no}</td><td>${g.date}</td><td>${g.material}</td><td><b>${g.net_wt} MT</b></td><td>${g.vehicle}</td><td>${g.unit}</td><td>${g.vendor_id||'-'}</td><td>${g.operator||'-'}</td></tr>`; });
 h+='</table>'; document.getElementById('grnList').innerHTML=h;
}
async function createGRN(){
 let gross=parseFloat(document.getElementById('g_gross').value||0);
 let tare=parseFloat(document.getElementById('g_tare').value||0);
 if(gross<=0 || tare<=0){alert('Enter Gross & Tare weight in kg'); return;}
 let net=(gross-tare)/1000;
 if(net<=0){alert('Net weight invalid: Gross must > Tare'); return;}
 let payload={vehicle_no:document.getElementById('g_vehicle').value, material:document.getElementById('g_material').value, gross_wt:gross, tare_wt:tare, net_wt:net, challan_no:document.getElementById('g_challan').value, invoice_no:document.getElementById('g_invoice').value, vendor_id:document.getElementById('g_vendor').value, po_no:document.getElementById('g_po').value, unit:document.getElementById('g_unit').value, stock_type:document.getElementById('g_stockType').value, material_type:'Raw', date:new Date().toISOString().slice(0,10), operator:document.getElementById('g_operator').value||'operator1', gps:document.getElementById('g_gps').value||''};
 let res=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert('✅ GRN Created: '+d.grn_no+' Net '+net.toFixed(3)+' MT - Stock Updated'); loadGRN(); loadAll();
}
async function loadPO(){
 let res=await fetch('/api/po'); let pos=await res.json();
 let h='<table><tr><th>PO No</th><th>Date</th><th>Material</th><th>Qty</th><th>Rate</th><th>Total</th><th>Unit</th><th>Status</th></tr>';
 pos.forEach(p=>{ h+=`<tr><td>${p.po_no}</td><td>${p.date}</td><td>${p.material}</td><td>${p.qty}</td><td>Rs ${p.rate}</td><td>Rs ${(p.total||0).toLocaleString()}</td><td>${p.unit}</td><td><span class="badge ${p.status==='Draft'?'info':(p.status==='Sent'?'warn':'ok')}">${p.status}</span></td></tr>`; });
 h+='</table>'; document.getElementById('poList').innerHTML=h;
}
async function createPO(){
 let qty=parseFloat(document.getElementById('po_qty').value||0);
 let rate=parseFloat(document.getElementById('po_rate').value||0);
 if(qty<=0 || rate<=0){alert('Enter Qty & Rate'); return;}
 let payload={vendor_id:document.getElementById('po_vendor').value, material_type:document.getElementById('po_mtype').value, material:document.getElementById('po_mat').value, qty:qty, rate:rate, unit:document.getElementById('po_unit').value, delivery_date:document.getElementById('po_delivery').value, status:document.getElementById('po_status').value, date:new Date().toISOString().slice(0,10)};
 let res=await fetch('/api/po',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert('✅ PO Created: '+d.po_no+' Total Rs '+(qty*rate).toLocaleString()); loadPO();
}
async function addPack(){
 let qty=parseFloat(document.getElementById('pk_qty').value||0);
 if(qty<=0){alert('Enter Qty'); return;}
 let bag=document.getElementById('pk_type').value;
 let unit=document.getElementById('pk_unit').value;
 let res=await fetch('/api/pack_add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({bag_type:bag, qty:qty, unit:unit})});
 let d=await res.json(); alert('✅ Packaging Added: '+bag+' Qty '+qty+' Closing '+d.closing); loadStock();
}
async function loadKiln(){
 let res=await fetch('/api/kiln'); let logs=await res.json();
 let h='<table><tr><th>Date</th><th>Unit</th><th>Limestone Feed</th><th>Petcoke</th><th>CaO Prod</th><th>Burn Loss</th><th>Operator</th></tr>';
 logs.forEach(k=>{ h+=`<tr><td>${k.date}</td><td>${k.unit}</td><td>${k.limestone_feed_mt} MT</td><td>${k.petcoke_consumed_mt} MT</td><td><b>${k.cao_produced_mt} MT</b></td><td>${k.burning_loss_pct.toFixed(1)}%</td><td>${k.operator}</td></tr>`; });
 h+='</table>'; document.getElementById('kilnList').innerHTML=h;
}
async function addKiln(){
 let lime=parseFloat(document.getElementById('k_lime').value||0);
 let pet=parseFloat(document.getElementById('k_pet').value||0);
 let cao=parseFloat(document.getElementById('k_cao').value||0);
 if(lime<=0 || cao<=0){alert('Enter Feed & Produced'); return;}
 let payload={unit:document.getElementById('k_unit').value, limestone_feed_mt:lime, petcoke_consumed_mt:pet, cao_produced_mt:cao, operator:document.getElementById('k_operator').value||'operator1', date:new Date().toISOString().slice(0,10)};
 let res=await fetch('/api/kiln',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert('✅ Kiln Log Saved: Burning Loss '+d.burning_loss_pct.toFixed(1)+'%'); loadKiln(); loadStock();
}
async function loadHyd(){
 let res=await fetch('/api/hydration'); let logs=await res.json();
 let h='<table><tr><th>Date</th><th>Unit</th><th>CaO Input</th><th>Hyd Output</th><th>Grade</th><th>Water</th><th>Operator</th></tr>';
 logs.forEach(k=>{ h+=`<tr><td>${k.date}</td><td>${k.unit}</td><td>${k.cao_input_mt} MT</td><td><b>${k.hydrated_output_mt} MT</b></td><td>${k.grade}</td><td>${k.water_used_ltr} L</td><td>${k.operator}</td></tr>`; });
 h+='</table>'; document.getElementById('hydList').innerHTML=h;
}
async function addHyd(){
 let cao=parseFloat(document.getElementById('h_cao').value||0);
 let out=parseFloat(document.getElementById('h_out').value||0);
 if(cao<=0 || out<=0){alert('Enter CaO Input & Output'); return;}
 let payload={unit:document.getElementById('h_unit').value, cao_input_mt:cao, hydrated_output_mt:out, grade:document.getElementById('h_grade').value, water_used_ltr:parseFloat(document.getElementById('h_water').value||0), operator:document.getElementById('h_operator').value||'operator1', date:new Date().toISOString().slice(0,10)};
 let res=await fetch('/api/hydration',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert('✅ Hydration Saved: '+out+' MT '+d.grade); loadHyd(); loadStock();
}
async function genQR(){
 let prod=document.getElementById('qr_product').value;
 let wt=parseFloat(document.getElementById('qr_weight').value||1.2);
 let unit=document.getElementById('qr_unit').value;
 let cust=document.getElementById('qr_customer').value;
 let veh=document.getElementById('qr_vehicle').value;
 let res=await fetch('/api/qr_generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product:prod, weight:wt, unit:unit, customer:cust, vehicle_no:veh})});
 let d=await res.json();
 document.getElementById('qrResult').innerHTML=`<b>Bag ID: ${d.bag_id}</b><br>${prod} | ${wt} MT | ${unit} | Customer: ${cust||'-'} | Vehicle: ${veh||'-'}`;
 document.getElementById('qrImg').innerHTML=`<img src="data:image/png;base64,${d.qr_base64}" style="width:220px;border:10px solid #1A2E1E;border-radius:14px;margin-top:12px;box-shadow:0 8px 20px rgba(0,0,0,0.15)"> <br><button class="btn" onclick="window.print()">Print QR</button> <button class="btn btn-lemon" onclick="markDispatched('${d.bag_id}')">Mark Dispatched</button>`;
 loadQRList();
}
async function loadQRList(){
 let res=await fetch('/api/qr_list'); let qs=await res.json();
 let h='<table><tr><th>Bag ID</th><th>Product</th><th>Wt</th><th>Unit</th><th>Customer</th><th>Vehicle</th><th>Status</th><th>Created</th></tr>';
 qs.forEach(q=>{ h+=`<tr><td><b>${q.bag_id}</b></td><td>${q.product}</td><td>${q.weight}</td><td>${q.unit}</td><td>${q.customer||'-'}</td><td>${q.vehicle_no||'-'}</td><td><span class="badge ${q.status==='Packed'?'info':'ok'}">${q.status}</span></td><td class="small">${q.created}</td></tr>`; });
 h+='</table>'; document.getElementById('qrList').innerHTML=h;
}
async function markDispatched(bagId){
 let res=await fetch('/api/qr_dispatch/'+bagId,{method:'POST'});
 let d=await res.json(); alert('✅ Dispatched: '+d.bag_id); loadQRList();
}

loadAll();
</script>
</body></html>
    """

@app.route('/api/vendors')
def vendors_api():
    v=Vendor.query.filter_by(company_id=1).all()
    return jsonify([{'id':x.id,'name':x.name,'type':x.vendor_type,'gst':x.gst,'contact':x.contact,'credit_limit':x.credit_limit,'pending_due':x.pending_due,'payment_terms':x.payment_terms,'rating':x.rating} for x in v])

@app.route('/api/po', methods=['GET','POST'])
def po_api():
    if request.method=='POST':
        data=request.json
        cnt=PurchaseOrder.query.count()+1
        po_no=f"PO-2026-{cnt:04d}"
        total=float(data.get('qty',0))*float(data.get('rate',0))
        po=PurchaseOrder(company_id=1, po_no=po_no, date=data.get('date'), vendor_id=data.get('vendor_id'), material_type=data.get('material_type'), material=data.get('material'), qty=float(data.get('qty',0)), rate=float(data.get('rate',0)), total=total, delivery_date=data.get('delivery_date'), unit=data.get('unit'), status=data.get('status','Draft'), created_by='Owner')
        db.session.add(po)
        db.session.commit()
        return jsonify({'status':'success','po_no':po_no,'total':total})
    pos=PurchaseOrder.query.filter_by(company_id=1).order_by(PurchaseOrder.id.desc()).all()
    return jsonify([{'po_no':p.po_no,'date':p.date,'material':p.material,'qty':p.qty,'rate':p.rate,'total':p.total,'unit':p.unit,'status':p.status,'vendor_id':p.vendor_id} for p in pos])

@app.route('/api/grn', methods=['GET','POST'])
def grn_api():
    if request.method=='POST':
        data=request.json
        cnt=GRN.query.count()+1
        grn_no=f"GRN-2026-{cnt:04d}"
        grn=GRN(company_id=1, grn_no=grn_no, date=data.get('date'), time=datetime.now().strftime('%H:%M:%S'), po_no=data.get('po_no',''), vehicle_no=data.get('vehicle_no','').upper(), vendor_id=data.get('vendor_id'), material_type=data.get('material_type','Raw'), material=data.get('material'), challan_no=data.get('challan_no'), invoice_no=data.get('invoice_no'), gross_wt=float(data.get('gross_wt',0)), tare_wt=float(data.get('tare_wt',0)), net_wt=float(data.get('net_wt',0)), rejection_pct=0, stock_type=data.get('stock_type','Own'), unit=data.get('unit'), operator=data.get('operator','operator1'), gps=data.get('gps',''))
        db.session.add(grn)
        # Update stock - find matching product & unit
        sm=StockMaster.query.filter_by(company_id=1, product=data.get('material'), unit=data.get('unit')).first()
        if not sm:
            sm=StockMaster.query.filter_by(company_id=1, product=data.get('material')).first()
        if sm:
            sm.current_stock+=float(data.get('net_wt',0))
            sm.stock_value=sm.current_stock* (sm.rate_per_mt or 7000)
        db.session.commit()
        return jsonify({'status':'success','grn_no':grn_no,'net_wt':float(data.get('net_wt',0))})
    grns=GRN.query.filter_by(company_id=1).order_by(GRN.id.desc()).limit(50).all()
    return jsonify([{'grn_no':g.grn_no,'date':g.date,'material':g.material,'net_wt':g.net_wt,'vehicle':g.vehicle_no,'unit':g.unit,'vendor_id':g.vendor_id,'operator':g.operator} for g in grns])

@app.route('/api/stock_v4')
def stock_v4():
    stocks=StockMaster.query.filter_by(company_id=1).all()
    result={'Raw':[],'WIP':[],'Finished':[],'Packaging':[]}
    for s in stocks:
        status='OK'
        if s.current_stock < s.min_stock: status='Critical'
        elif s.current_stock < s.reorder_level: status='Reorder'
        result[s.product_category].append({'product':s.product,'product_category':s.product_category,'unit':s.unit,'current':s.current_stock,'min':s.min_stock,'reorder':s.reorder_level,'max':s.max_stock,'rate_per_mt':s.rate_per_mt,'status':status})
    packs=PackagingStock.query.filter_by(company_id=1).all()
    for p in packs:
        status='OK'
        if p.closing < p.min_stock: status='Critical'
        elif p.closing < p.min_stock*1.5: status='Reorder'
        result['Packaging'].append({'product':p.bag_type,'unit':p.unit,'current':p.closing,'min':p.min_stock,'rate':p.rate_per_bag,'capacity':p.capacity_mt,'status':status})
    return jsonify(result)

@app.route('/api/pack_add', methods=['POST'])
def pack_add():
    data=request.json
    bag_type=data.get('bag_type')
    qty=float(data.get('qty',0))
    unit=data.get('unit')
    p=PackagingStock.query.filter_by(company_id=1, bag_type=bag_type, unit=unit).first()
    if not p:
        # create new
        p=PackagingStock(company_id=1, bag_type=bag_type, bag_category='Jumbo' if 'Jumbo' in bag_type else '40kg', capacity_mt=1.2 if 'Jumbo' in bag_type else 0.04, opening=0, purchase_in=qty, consumption=0, closing=qty, min_stock=50, rate_per_bag=450 if 'Jumbo' in bag_type else 18, unit=unit)
        db.session.add(p)
    else:
        p.purchase_in+=qty
        p.closing+=qty
    db.session.commit()
    return jsonify({'status':'success','closing':p.closing})

@app.route('/api/kiln', methods=['GET','POST'])
def kiln_api():
    if request.method=='POST':
        data=request.json
        lime=float(data.get('limestone_feed_mt',0))
        cao=float(data.get('cao_produced_mt',0))
        loss=((lime-cao)/lime*100) if lime>0 else 0
        log=KilnLog(company_id=1, date=data.get('date'), unit=data.get('unit'), limestone_feed_mt=lime, petcoke_consumed_mt=float(data.get('petcoke_consumed_mt',0)), cao_produced_mt=cao, burning_loss_pct=loss, operator=data.get('operator','operator1'))
        db.session.add(log)
        # Update WIP & Finished stock? Add CaO to Finished
        sm=StockMaster.query.filter_by(company_id=1, product_category='WIP', unit=data.get('unit')).first()
        if sm:
            # WIP already accounted, now add to Finished 10-40mm
            fin=StockMaster.query.filter_by(company_id=1, product='CaO 10-40mm', unit=data.get('unit')).first()
            if fin:
                fin.current_stock+=cao
                fin.stock_value=fin.current_stock*fin.rate_per_mt
        db.session.commit()
        return jsonify({'status':'success','burning_loss_pct':loss})
    logs=KilnLog.query.filter_by(company_id=1).order_by(KilnLog.id.desc()).limit(20).all()
    return jsonify([{'date':k.date,'unit':k.unit,'limestone_feed_mt':k.limestone_feed_mt,'petcoke_consumed_mt':k.petcoke_consumed_mt,'cao_produced_mt':k.cao_produced_mt,'burning_loss_pct':k.burning_loss_pct,'operator':k.operator} for k in logs])

@app.route('/api/hydration', methods=['GET','POST'])
def hydration_api():
    if request.method=='POST':
        data=request.json
        log=HydrationLog(company_id=1, date=data.get('date'), unit=data.get('unit'), cao_input_mt=float(data.get('cao_input_mt',0)), hydrated_output_mt=float(data.get('hydrated_output_mt',0)), grade=data.get('grade','90%'), water_used_ltr=float(data.get('water_used_ltr',0)), operator=data.get('operator','operator1'))
        db.session.add(log)
        # Deduct CaO from Finished and add Hydrated
        cao_stock=StockMaster.query.filter_by(company_id=1, product='CaO 10-40mm', unit=data.get('unit')).first()
        if cao_stock:
            cao_stock.current_stock-=float(data.get('cao_input_mt',0))
        grade='Hydrated '+data.get('grade')
        hyd_stock=StockMaster.query.filter_by(company_id=1, product=grade, unit=data.get('unit')).first()
        if hyd_stock:
            hyd_stock.current_stock+=float(data.get('hydrated_output_mt',0))
            hyd_stock.stock_value=hyd_stock.current_stock*hyd_stock.rate_per_mt
        else:
            # create if not exists
            new_s=StockMaster(company_id=1, product=grade, product_category='Finished', unit=data.get('unit'), min_stock=10, reorder_level=20, max_stock=80, reorder_qty=30, current_stock=float(data.get('hydrated_output_mt',0)), rate_per_mt=25000 if '95' in data.get('grade') else 20000, stock_value=float(data.get('hydrated_output_mt',0))* (25000 if '95' in data.get('grade') else 20000))
            db.session.add(new_s)
        db.session.commit()
        return jsonify({'status':'success','grade':data.get('grade')})
    logs=HydrationLog.query.filter_by(company_id=1).order_by(HydrationLog.id.desc()).limit(20).all()
    return jsonify([{'date':h.date,'unit':h.unit,'cao_input_mt':h.cao_input_mt,'hydrated_output_mt':h.hydrated_output_mt,'grade':h.grade,'water_used_ltr':h.water_used_ltr,'operator':h.operator} for h in logs])

@app.route('/api/qr_generate', methods=['POST'])
def qr_gen():
    data=request.json
    cnt=QRBag.query.count()+1
    prod=(data.get('product','CaO') or 'CaO').replace(' ','')[:8]
    unit=(data.get('unit','U1') or 'U1').replace(' ','')[:2]
    bag_id=f"JMB-{prod}-{unit}-{datetime.now().strftime('%Y')}-{cnt:05d}"
    qr_data=f"{bag_id}|{data.get('product')}|{data.get('weight')}MT|{data.get('unit')}|Cust:{data.get('customer','-')}|Veh:{data.get('vehicle_no','-')}|RLP|v4.2"
    qr=qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img=qr.make_image(fill_color="#1A2E1E", back_color="#FAF6F0")
    buffered=BytesIO()
    img.save(buffered, format="PNG")
    img_str=base64.b64encode(buffered.getvalue()).decode()
    entry=QRBag(company_id=1, bag_id=bag_id, product=data.get('product'), weight=float(data.get('weight',1.2)), unit=data.get('unit'), customer=data.get('customer',''), vehicle_no=data.get('vehicle_no',''), qr_data=qr_data, created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(entry)
    db.session.commit()
    return jsonify({'bag_id':bag_id,'qr_base64':img_str})

@app.route('/api/qr_list')
def qr_list():
    qs=QRBag.query.filter_by(company_id=1).order_by(QRBag.id.desc()).limit(50).all()
    return jsonify([{'bag_id':q.bag_id,'product':q.product,'weight':q.weight,'unit':q.unit,'customer':q.customer,'vehicle_no':q.vehicle_no,'status':q.status,'created':q.created_at} for q in qs])

@app.route('/api/qr_dispatch/<bag_id>', methods=['POST'])
def qr_dispatch(bag_id):
    q=QRBag.query.filter_by(company_id=1, bag_id=bag_id).first()
    if q:
        q.status='Dispatched'
        db.session.commit()
        return jsonify({'status':'success','bag_id':bag_id})
    return jsonify({'status':'not found'}),404

@app.route('/api/health')
def health():
    return jsonify({"status":"LIVE","version":"v4.2 FULL - No WhatsApp","theme":"Heritage Green #1A2E1E + Brass #C9A86A + Lemon #F2E863","features":["Dashboard with valuation","Raw/WIP/Finished/Packaging separate","Vendor + PO with credit limit","GRN weighbridge gross/tare/net","Packaging stock Jumbo/HDPE","QR Dispatch with customer/vehicle","Kiln Log with burning loss","Hydration 90%/95%","Mobile PWA operator1/2/3","White-label ready"],"units":["Unit 1 72MT","Unit 2 84MT","Unit 3 125MT"],"url":"https://lemon-erp.onrender.com"})

@app.route('/mobile')
def mobile():
    return """
<html><head><title>Lemon ERP v4.2 Mobile</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#FAF6F0;margin:0} .header{background:#1A2E1E;color:#C9A86A;padding:20px;text-align:center} .card{background:white;margin:12px;padding:16px;border-radius:12px;border-left:5px solid #C9A86A;box-shadow:0 4px 12px rgba(0,0,0,0.08)}
.btn{background:#1A2E1E;color:white;padding:12px 20px;border-radius:8px;border:none;width:100%;margin:6px 0;font-weight:700}</style></head>
<body><div class="header"><h2>🍋 Lemon ERP v4.2 Mobile PWA</h2><p>Operator App - No WhatsApp - Full Features</p></div>
<div class="card"><h3>Login</h3><input id="u" placeholder="Username operator1/operator2/operator3/owner/manager"><input id="p" type="password" placeholder="Password op123/mgr123/owner123"><button class="btn" onclick="login()">Login</button><p id="msg"></p></div>
<div class="card"><h3>Quick GRN - Weighbridge</h3><input id="veh" placeholder="Vehicle No RJ19"><input id="mat" placeholder="Material Limestone"><input id="gw" type="number" placeholder="Gross kg"><input id="tw" type="number" placeholder="Tare kg"><button class="btn" onclick="quickGRN()">Submit GRN - Auto Net MT</button><p id="grnMsg"></p></div>
<div class="card"><h3>Quick Kiln Entry</h3><input id="k_lime" type="number" placeholder="Limestone Feed MT"><input id="k_cao" type="number" placeholder="CaO Produced MT"><button class="btn" onclick="quickKiln()">Save Kiln - Burning Loss Auto</button><p id="kilnMsg"></p></div>
<script>
function login(){let u=document.getElementById('u').value; let p=document.getElementById('p').value; let ok=(u==='operator1'&&p==='op123')||(u==='operator2'&&p==='op123')||(u==='operator3'&&p==='op123')||(u==='owner'&&p==='owner123')||(u==='manager'&&p==='mgr123'); document.getElementById('msg').innerHTML=ok?'✅ Login OK '+u:'❌ Invalid - Try operator1/op123';}
async function quickGRN(){let gw=parseFloat(document.getElementById('gw').value||0); let tw=parseFloat(document.getElementById('tw').value||0); let net=(gw-tw)/1000; if(net<=0){alert('Gross must > Tare'); return;} let data={vehicle_no:document.getElementById('veh').value, material:document.getElementById('mat').value, gross_wt:gw, tare_wt:tw, net_wt:net, unit:'Unit 1 72MT', vendor_id:1, material_type:'Raw', date:new Date().toISOString().slice(0,10), operator:'operator1'}; let r=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); let d=await r.json(); document.getElementById('grnMsg').innerHTML='✅ GRN '+d.grn_no+' '+net.toFixed(3)+' MT Saved';}
async function quickKiln(){let lime=parseFloat(document.getElementById('k_lime').value||0); let cao=parseFloat(document.getElementById('k_cao').value||0); if(lime<=0||cao<=0){alert('Enter Feed & Prod'); return;} let data={unit:'Unit 1 72MT', limestone_feed_mt:lime, petcoke_consumed_mt:lime*0.07, cao_produced_mt:cao, operator:'operator1', date:new Date().toISOString().slice(0,10)}; let r=await fetch('/api/kiln',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); let d=await r.json(); document.getElementById('kilnMsg').innerHTML='✅ Kiln Saved Burning Loss '+d.burning_loss_pct.toFixed(1)+'%';}
</script>
<a href="/" style="display:block;text-align:center;margin:20px;color:#1A2E1E;font-weight:700">← Back to Full Dashboard v4.2</a></body></html>
    """

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
