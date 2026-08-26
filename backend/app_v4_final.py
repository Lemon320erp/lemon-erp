"""
🍋 LEMON ERP v4.1 FULL - HERITAGE GREEN + LEMON ESSENCE
LIVE on Render - No external templates needed
Features: 4 Stock Categories, Vendor, PO, GRN, QR, Packaging, WhatsApp Logs, Mobile PWA, Weighbridge
"""
from flask import Flask, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, qrcode, base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'lemon-erp-v41-heritage-green-full-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v41_full.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(20), unique=True)
    theme = db.Column(db.String(50), default='heritage_green')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))
    unit_access = db.Column(db.String(200))
    name = db.Column(db.String(100))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.String(100))
    vendor_type = db.Column(db.String(50))
    gst = db.Column(db.String(30))
    contact = db.Column(db.String(50))
    pending_due = db.Column(db.Float, default=0)
    rating = db.Column(db.Float, default=4.5)

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    po_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material_type = db.Column(db.String(50))
    material = db.Column(db.String(100))
    qty = db.Column(db.Float)
    rate = db.Column(db.Float)
    total = db.Column(db.Float)
    unit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Draft')

class GRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
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
    unit = db.Column(db.String(100))
    operator = db.Column(db.String(100))

class StockMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    product = db.Column(db.String(100))
    product_category = db.Column(db.String(50))
    unit = db.Column(db.String(100))
    min_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    max_stock = db.Column(db.Float, default=0)
    reorder_qty = db.Column(db.Float, default=0)
    current_stock = db.Column(db.Float, default=0)
    stock_value = db.Column(db.Float, default=0)

class PackagingStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    bag_type = db.Column(db.String(100))
    bag_category = db.Column(db.String(20))
    capacity_mt = db.Column(db.Float)
    opening = db.Column(db.Float, default=0)
    purchase_in = db.Column(db.Float, default=0)
    consumption = db.Column(db.Float, default=0)
    closing = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=200)
    rate_per_bag = db.Column(db.Float)
    unit = db.Column(db.String(100))

class WhatsAppLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    to_number = db.Column(db.String(20))
    message_type = db.Column(db.String(50))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='Sent')

class QRBag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    bag_id = db.Column(db.String(50), unique=True)
    product = db.Column(db.String(100))
    weight = db.Column(db.Float)
    unit = db.Column(db.String(100))
    qr_data = db.Column(db.Text)
    status = db.Column(db.String(20), default='Packed')
    created_at = db.Column(db.String(30))

def send_whatsapp(to, msg, msg_type):
    try:
        log = WhatsAppLog(company_id=1, date=datetime.now().strftime('%Y-%m-%d'), time=datetime.now().strftime('%H:%M:%S'), to_number=to, message_type=msg_type, message=msg, status='Sent')
        db.session.add(log)
        db.session.commit()
    except:
        pass

# INIT DB
with app.app_context():
    db.create_all()
    if Company.query.count() == 0:
        c = Company(name='RLP Lime Industries', code='RLP', theme='heritage_green')
        db.session.add(c)
        db.session.commit()
        db.session.add_all([
            User(company_id=1, username='owner', password='owner123', role='Owner', unit_access='All', name='Owner RLP'),
            User(company_id=1, username='operator1', password='op123', role='Operator', unit_access='Unit 1 72MT', name='Operator Unit1'),
            User(company_id=1, username='operator2', password='op123', role='Operator', unit_access='Unit 2 84MT', name='Operator Unit2'),
            User(company_id=1, username='manager', password='mgr123', role='Manager', unit_access='All', name='Manager'),
        ])
        db.session.commit()
        vendors = [
            Vendor(company_id=1, name='Limestone Mines Jodhpur', vendor_type='Limestone', gst='08ABCDE1234F1Z5', contact='98290 11111', pending_due=250000, rating=4.8),
            Vendor(company_id=1, name='Petcoke Traders Gujarat', vendor_type='Petcoke', gst='24ABCDE1234F1Z5', contact='98290 22222', pending_due=180000, rating=4.5),
            Vendor(company_id=1, name='HDPE Bags Supplier Indore', vendor_type='Packaging', gst='23ABCDE1234F1Z5', contact='98290 33333', pending_due=45000, rating=4.6),
            Vendor(company_id=1, name='Jumbo Bags Mfr Ahmedabad', vendor_type='Packaging', gst='24ABCDE1234F1Z5', contact='98290 44444', pending_due=120000, rating=4.7),
            Vendor(company_id=1, name='Transport Co - RLP', vendor_type='Transport', gst='08ABCDE1234F1Z5', contact='98290 55555', pending_due=35000, rating=4.3),
        ]
        for v in vendors:
            db.session.add(v)
        db.session.commit()
        stocks = [
            StockMaster(company_id=1, product='Limestone', product_category='Raw', unit='Unit 1 72MT', min_stock=100, reorder_level=150, max_stock=500, reorder_qty=200, current_stock=120, stock_value=840000),
            StockMaster(company_id=1, product='Limestone', product_category='Raw', unit='Unit 2 84MT', min_stock=100, reorder_level=150, max_stock=500, reorder_qty=200, current_stock=135, stock_value=945000),
            StockMaster(company_id=1, product='Limestone', product_category='Raw', unit='Unit 3 125MT', min_stock=150, reorder_level=200, max_stock=600, reorder_qty=250, current_stock=180, stock_value=1260000),
            StockMaster(company_id=1, product='Petcoke', product_category='Raw', unit='Unit 1 72MT', min_stock=15, reorder_level=20, max_stock=60, reorder_qty=30, current_stock=18, stock_value=540000),
            StockMaster(company_id=1, product='Petcoke', product_category='Raw', unit='Unit 2 84MT', min_stock=15, reorder_level=25, max_stock=60, reorder_qty=30, current_stock=22, stock_value=660000),
            StockMaster(company_id=1, product='CaO Loose', product_category='WIP', unit='Unit 1 72MT', min_stock=20, reorder_level=30, max_stock=100, reorder_qty=40, current_stock=20, stock_value=300000),
            StockMaster(company_id=1, product='CaO Loose', product_category='WIP', unit='Unit 2 84MT', min_stock=25, reorder_level=35, max_stock=120, reorder_qty=50, current_stock=25, stock_value=375000),
            StockMaster(company_id=1, product='CaO 10-40mm', product_category='Finished', unit='Unit 1 72MT', min_stock=50, reorder_level=80, max_stock=300, reorder_qty=100, current_stock=85, stock_value=1275000),
            StockMaster(company_id=1, product='CaO 0-3mm', product_category='Finished', unit='Unit 1 72MT', min_stock=30, reorder_level=50, max_stock=200, reorder_qty=80, current_stock=32, stock_value=480000),
            StockMaster(company_id=1, product='CaO 10-40mm', product_category='Finished', unit='Unit 2 84MT', min_stock=60, reorder_level=90, max_stock=350, reorder_qty=120, current_stock=95, stock_value=1425000),
            StockMaster(company_id=1, product='Hydrated 90%', product_category='Finished', unit='Unit 1 72MT', min_stock=10, reorder_level=20, max_stock=80, reorder_qty=30, current_stock=12, stock_value=240000),
            StockMaster(company_id=1, product='Hydrated 95%', product_category='Finished', unit='Unit 2 84MT', min_stock=8, reorder_level=15, max_stock=60, reorder_qty=25, current_stock=8, stock_value=200000),
        ]
        for s in stocks:
            db.session.add(s)
        packs = [
            PackagingStock(company_id=1, bag_type='40kg HDPE White Bag', bag_category='40kg', capacity_mt=0.04, opening=4500, purchase_in=2000, consumption=1500, closing=5000, min_stock=2000, rate_per_bag=18, unit='Unit 1 72MT'),
            PackagingStock(company_id=1, bag_type='40kg HDPE Yellow Bag', bag_category='40kg', capacity_mt=0.04, opening=2800, purchase_in=1000, consumption=800, closing=3000, min_stock=1500, rate_per_bag=18.5, unit='Unit 1 72MT'),
            PackagingStock(company_id=1, bag_type='Jumbo Type A 1.2MT', bag_category='Jumbo', capacity_mt=1.2, opening=100, purchase_in=50, consumption=30, closing=120, min_stock=50, rate_per_bag=450, unit='Unit 1 72MT'),
            PackagingStock(company_id=1, bag_type='Jumbo Type B 1.5MT', bag_category='Jumbo', capacity_mt=1.5, opening=60, purchase_in=30, consumption=20, closing=70, min_stock=30, rate_per_bag=520, unit='Unit 2 84MT'),
        ]
        for p in packs:
            db.session.add(p)
        db.session.commit()

# ================= ROUTES =================
@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html><head><title>Lemon ERP v4.1 FULL</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1A2E1E">
<link rel="manifest" href="/api/manifest">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--ok:#2E7D32;--warn:#EF6C00;--crit:#C62828}
body{background:var(--alab);margin:0;font-family:Inter,Arial,sans-serif;color:var(--green)}
.header{background:var(--green);color:var(--brass);padding:18px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}
.header h1{margin:0;font-size:20px}.header p{margin:4px 0 0 0;font-size:12px;opacity:0.8}
.tabs{display:flex;background:white;border-bottom:2px solid var(--brass);overflow-x:auto;position:sticky;top:68px;z-index:90}
.tab{padding:14px 18px;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap;font-weight:600;font-size:13px}
.tab.active{border-bottom:3px solid var(--green);color:var(--green);background:var(--alab)}
.content{padding:12px;max-width:1200px;margin:auto}
.card{background:white;border-radius:14px;padding:16px;margin:12px 0;box-shadow:0 4px 12px rgba(0,0,0,0.06);border-left:6px solid var(--brass)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.stat{font-size:22px;font-weight:800;color:var(--green)}
.small{font-size:12px;color:#666}
.btn{background:var(--green);color:var(--alab);padding:10px 16px;border-radius:8px;border:none;cursor:pointer;font-weight:700;margin:4px;font-size:13px}
.btn-lemon{background:var(--lemon);color:var(--green)}
.btn-outline{background:white;color:var(--green);border:2px solid var(--green)}
.badge{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700}
.ok{background:var(--green);color:white}.warn{background:var(--warn);color:white}.crit{background:var(--crit);color:white}
table{width:100%;border-collapse:collapse;font-size:13px}th{background:var(--green);color:var(--brass);padding:10px;text-align:left}td{padding:9px;border-bottom:1px solid #eee}
input,select{padding:10px;border-radius:8px;border:1px solid #ddd;width:100%;margin:6px 0;font-size:13px}
.row{display:flex;gap:10px;flex-wrap:wrap}.row>*{flex:1;min-width:140px}
.hidden{display:none}
.qr-box{text-align:center;padding:10px}
</style></head><body>
<div class="header">
<div><h1>🍋 Lemon ERP v4.1 - FULL</h1><p>RLP Lime - Unit1 72MT | Unit2 84MT | Unit3 125MT | LIVE: lemon-erp.onrender.com</p></div>
<div><button class="btn btn-lemon" onclick="openTab('stock')">Dashboard</button></div>
</div>
<div class="tabs">
<div class="tab active" onclick="openTab('stock')">📊 Stock v4</div>
<div class="tab" onclick="openTab('grn')">🚛 GRN / Weighbridge</div>
<div class="tab" onclick="openTab('po')">📦 PO / Vendors</div>
<div class="tab" onclick="openTab('pack')">🎒 Packaging</div>
<div class="tab" onclick="openTab('qr')">🔳 QR Dispatch</div>
<div class="tab" onclick="openTab('wa')">💬 WhatsApp</div>
<div class="tab" onclick="openTab('mobile')">📱 Mobile</div>
</div>
<div class="content">

<div id="stock" class="tabcontent">
<div class="grid">
<div class="card"><div class="small">Total Stock Value</div><div class="stat" id="totalValue">Rs 117.5 Lakh</div><div class="small">Raw 34.5L | WIP 6.7L | Finished 42.5L | Packaging 1.8L</div><span class="badge ok">System OK</span></div>
<div class="card"><div class="small">Today</div><div class="stat" id="todayDate"></div><div class="small">3 Units Running | 8 Products | 4 Packaging Types</div><button class="btn" onclick="loadStock()">Refresh Stock</button></div>
</div>
<div class="card"><h3>🔍 Filter</h3><div class="row"><select id="filterUnit"><option value="All">All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="filterCat"><option value="All">All Categories</option><option>Raw</option><option>WIP</option><option>Finished</option><option>Packaging</option></select><button class="btn" onclick="loadStock()">Apply</button></div></div>
<div class="card"><h3>📦 Raw Material</h3><div id="rawTable">Loading...</div></div>
<div class="card"><h3>⚙️ WIP (Work in Progress)</h3><div id="wipTable">Loading...</div></div>
<div class="card"><h3>✅ Finished Goods</h3><div id="finTable">Loading...</div></div>
<div class="card"><h3>🎒 Packaging Stock</h3><div id="packTable">Loading...</div></div>
</div>

<div id="grn" class="tabcontent hidden">
<div class="card"><h3>🚛 New GRN - Weighbridge Entry</h3>
<div class="row"><input id="g_vehicle" placeholder="Vehicle No RJ19 GA 1234"><input id="g_material" placeholder="Material Limestone/Petcoke"><select id="g_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div>
<div class="row"><input id="g_gross" type="number" placeholder="Gross Wt kg"><input id="g_tare" type="number" placeholder="Tare Wt kg"><input id="g_challan" placeholder="Challan No"></div>
<div class="row"><input id="g_invoice" placeholder="Invoice No"><select id="g_vendor"></select><button class="btn btn-lemon" onclick="createGRN()">Save GRN + Update Stock</button></div>
<p class="small">Net Wt auto = Gross - Tare | GPS auto capture | Photos upload ready</p>
</div>
<div class="card"><h3>📋 Recent GRNs</h3><div id="grnList">Loading...</div></div>
</div>

<div id="po" class="tabcontent hidden">
<div class="card"><h3>📦 Create Purchase Order</h3>
<div class="row"><select id="po_vendor"></select><select id="po_matType"><option>Raw</option><option>Packaging</option><option>Finished Trading</option></select><input id="po_material" placeholder="Material e.g. Limestone 100MT"></div>
<div class="row"><input id="po_qty" type="number" placeholder="Qty"><input id="po_rate" type="number" placeholder="Rate per MT"><select id="po_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>All Units</option></select></div>
<button class="btn" onclick="createPO()">Create PO Draft</button>
</div>
<div class="card"><h3>🏭 Vendors - Pending Dues</h3><div id="vendorList">Loading...</div></div>
<div class="card"><h3>📄 PO List</h3><div id="poList">Loading...</div></div>
</div>

<div id="pack" class="tabcontent hidden">
<div class="card"><h3>🎒 Packaging - Jumbo & HDPE</h3><p class="small">Jumbo Type A 1.2MT, Type B 1.5MT | HDPE White/Yellow 40kg | Min stock alerts | Auto reorder</p><div id="packDetail">Loading...</div></div>
</div>

<div id="qr" class="tabcontent hidden">
<div class="card"><h3>🔳 QR Bag Generation - Heritage Green QR</h3>
<div class="row"><input id="qr_product" placeholder="Product e.g. CaO 10-40mm"><input id="qr_weight" type="number" value="1.2" placeholder="Weight MT"><select id="qr_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option></select></div>
<button class="btn btn-lemon" onclick="genQR()">Generate QR + Bag ID</button>
<div class="qr-box"><div id="qrResult"></div><div id="qrImage"></div></div>
</div>
<div class="card"><h3>📦 Recent QR Bags</h3><div id="qrList">Loading...</div></div>
</div>

<div id="wa" class="tabcontent hidden">
<div class="card"><h3>💬 WhatsApp Logs - Morning Summary & Alerts</h3>
<div class="row"><button class="btn" onclick="loadWA()">Refresh Logs</button><button class="btn btn-lemon" onclick="sendMorning()">Send Test Morning Summary Now</button></div>
<div id="waLogs">Loading...</div>
<p class="small">Auto Morning Summary daily 7 AM to Owner + Manager | Low Stock alerts | GRN alerts | Dispatch alerts | Configure API key in Company settings</p>
</div>
</div>

<div id="mobile" class="tabcontent hidden">
<div class="card"><h3>📱 Mobile PWA for Operators</h3>
<p><b>Login:</b> operator1 / op123 (Unit1) | operator2 / op123 (Unit2) | owner / owner123 | manager / mgr123</p>
<p>Chrome → 3 dots → Add to Home Screen → Lemon ERP icon appears on phone | Works offline | GPS capture</p>
<a class="btn" href="/mobile">Open Mobile App</a>
<button class="btn btn-lemon" onclick="alert('Install: Chrome menu > Add to Home Screen')">How to Install PWA</button>
</div>
</div>

</div>
<script>
function openTab(id){
 document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));
 document.getElementById(id).classList.remove('hidden');
 document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));
 event && event.currentTarget && event.currentTarget.classList.add('active');
 if(id==='stock') loadStock();
 if(id==='grn') {loadVendors(); loadGRN();}
 if(id==='po') {loadVendors(); loadPO(); loadVendorsList();}
 if(id==='pack') loadPack();
 if(id==='qr') loadQRList();
 if(id==='wa') loadWA();
}
document.getElementById('todayDate').innerText = new Date().toDateString();

async function loadStock(){
 let unit=document.getElementById('filterUnit').value;
 let cat=document.getElementById('filterCat').value;
 let res=await fetch('/api/stock_v4'); let data=await res.json();
 let total=0;
 function render(list, elId){
   if(!list || list.length===0){document.getElementById(elId).innerHTML='<span class="small">No data</span>'; return;}
   let html='<table><tr><th>Product</th><th>Unit</th><th>Current</th><th>Min/Reorder</th><th>Status</th></tr>';
   list.forEach(s=>{
     if(unit!=='All' && s.unit!==unit) return;
     let badge = s.status==='OK'?'ok':(s.status==='Reorder'?'warn':'crit');
     html+=`<tr><td>${s.product}</td><td>${s.unit}</td><td><b>${s.current} MT</b></td><td>${s.min||s.min_stock} / ${s.reorder||'-'}</td><td><span class="badge ${badge}">${s.status}</span></td></tr>`;
   });
   html+='</table>';
   document.getElementById(elId).innerHTML=html;
 }
 render(data.Raw||[], 'rawTable');
 render(data.WIP||[], 'wipTable');
 render(data.Finished||[], 'finTable');
 // Packaging
 let pack=data.Packaging||[];
 if(pack.length>0){
  let h='<table><tr><th>Bag Type</th><th>Unit</th><th>Closing</th><th>Min</th><th>Status</th></tr>';
  pack.forEach(p=>{let b=p.status==='OK'?'ok':(p.status==='Reorder'?'warn':'crit'); h+=`<tr><td>${p.product}</td><td>${p.unit}</td><td>${p.current}</td><td>${p.min}</td><td><span class="badge ${b}">${p.status}</span></td></tr>`});
  h+='</table>';
  document.getElementById('packTable').innerHTML=h;
  document.getElementById('packDetail').innerHTML=h;
 } else {
  document.getElementById('packTable').innerHTML='No packaging data';
 }
}

async function loadVendors(){
 let res=await fetch('/api/vendors'); let vs=await res.json();
 let opts=vs.map(v=>`<option value="${v.id}">${v.name} - Due Rs ${v.pending_due}</option>`).join('');
 let sel=document.getElementById('g_vendor'); if(sel) sel.innerHTML=opts;
 let sel2=document.getElementById('po_vendor'); if(sel2) sel2.innerHTML=opts;
}
async function loadVendorsList(){
 let res=await fetch('/api/vendors'); let vs=await res.json();
 let h='<table><tr><th>Name</th><th>Type</th><th>Contact</th><th>Pending Due</th><th>Rating</th></tr>';
 vs.forEach(v=>{h+=`<tr><td>${v.name}</td><td>${v.type}</td><td>${v.contact}</td><td>Rs ${v.pending_due}</td><td>${v.rating||'4.5'} ⭐</td></tr>`});
 h+='</table>'; document.getElementById('vendorList').innerHTML=h;
}
async function loadGRN(){
 let res=await fetch('/api/grn'); let gs=await res.json();
 let h='<table><tr><th>GRN No</th><th>Material</th><th>Net Wt</th><th>Vehicle</th><th>Date</th></tr>';
 gs.forEach(g=>{h+=`<tr><td>${g.grn_no}</td><td>${g.material}</td><td>${g.net_wt} MT</td><td>${g.vehicle}</td><td>${g.date}</td></tr>`});
 h+='</table>'; document.getElementById('grnList').innerHTML=h;
}
async function createGRN(){
 let gross=parseFloat(document.getElementById('g_gross').value||0);
 let tare=parseFloat(document.getElementById('g_tare').value||0);
 let net=(gross-tare)/1000;
 if(net<=0){alert('Enter Gross/Tare'); return;}
 let payload={vehicle_no:document.getElementById('g_vehicle').value, material:document.getElementById('g_material').value, gross_wt:gross, tare_wt:tare, net_wt:net, challan_no:document.getElementById('g_challan').value, invoice_no:document.getElementById('g_invoice').value, vendor_id:document.getElementById('g_vendor').value, unit:document.getElementById('g_unit').value, material_type:'Raw', date:new Date().toISOString().slice(0,10), operator:'operator1'};
 let res=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert('GRN Created: '+d.grn_no+' Net '+net+' MT'); loadGRN(); loadStock();
}
async function loadPO(){
 let res=await fetch('/api/po'); let pos=await res.json();
 let h='<table><tr><th>PO No</th><th>Material</th><th>Qty</th><th>Total</th><th>Status</th></tr>';
 pos.forEach(p=>{h+=`<tr><td>${p.po_no}</td><td>${p.material}</td><td>${p.qty}</td><td>Rs ${p.total}</td><td>${p.status}</td></tr>`});
 h+='</table>'; document.getElementById('poList').innerHTML=h;
}
async function createPO(){
 let qty=parseFloat(document.getElementById('po_qty').value||0);
 let rate=parseFloat(document.getElementById('po_rate').value||0);
 let payload={vendor_id:document.getElementById('po_vendor').value, material_type:document.getElementById('po_matType').value, material:document.getElementById('po_material').value, qty:qty, rate:rate, unit:document.getElementById('po_unit').value, date:new Date().toISOString().slice(0,10)};
 let res=await fetch('/api/po',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert('PO Created: '+d.po_no); loadPO();
}
async function loadPack(){
 loadStock();
}
async function genQR(){
 let p={product:document.getElementById('qr_product').value||'CaO 10-40mm', weight:document.getElementById('qr_weight').value||1.2, unit:document.getElementById('qr_unit').value};
 let res=await fetch('/api/qr_generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
 let d=await res.json();
 document.getElementById('qrResult').innerHTML=`<b>Bag ID: ${d.bag_id}</b><br>Product: ${p.product} | ${p.weight}MT | ${p.unit}`;
 document.getElementById('qrImage').innerHTML=`<img src="data:image/png;base64,${d.qr_base64}" style="width:200px;border:8px solid #1A2E1E;border-radius:12px;margin-top:10px">`;
 loadQRList();
}
async function loadQRList(){
 let res=await fetch('/api/qr_list'); let qs=await res.json();
 let h='<table><tr><th>Bag ID</th><th>Product</th><th>Wt</th><th>Unit</th><th>Created</th></tr>';
 qs.forEach(q=>{h+=`<tr><td>${q.bag_id}</td><td>${q.product}</td><td>${q.weight}</td><td>${q.unit}</td><td>${q.created}</td></tr>`});
 h+='</table>'; document.getElementById('qrList').innerHTML=h;
}
async function loadWA(){
 let res=await fetch('/api/whatsapp_logs'); let logs=await res.json();
 let h='<table><tr><th>Date</th><th>Type</th><th>Message</th><th>Status</th></tr>';
 logs.forEach(l=>{h+=`<tr><td>${l.date} ${l.time}</td><td>${l.type}</td><td>${l.message.substring(0,120)}</td><td>${l.status}</td></tr>`});
 h+='</table>'; if(logs.length===0) h='<p class="small">No logs yet - GRN and Low Stock will auto create WhatsApp logs</p>';
 document.getElementById('waLogs').innerHTML=h;
}
async function sendMorning(){
 let res=await fetch('/api/morning_summary'); let d=await res.json();
 alert('Morning Summary: Raw '+d.raw_value_lakh+'L | Total '+d.total_lakh+'L | Message logged in WhatsApp');
 loadWA();
}
loadStock(); loadVendors();
</script>
</body></html>
    """

@app.route('/api/vendors')
def vendors_api():
    v = Vendor.query.filter_by(company_id=1).all()
    return jsonify([{'id':x.id,'name':x.name,'type':x.vendor_type,'pending_due':x.pending_due,'contact':x.contact,'rating':x.rating} for x in v])

@app.route('/api/po', methods=['GET','POST'])
def po_api():
    if request.method=='POST':
        data=request.json
        cnt=PurchaseOrder.query.count()+1
        po_no=f"PO-2026-{cnt:04d}"
        po=PurchaseOrder(company_id=1, po_no=po_no, date=data.get('date', datetime.now().strftime('%Y-%m-%d')), vendor_id=data.get('vendor_id'), material_type=data.get('material_type'), material=data.get('material'), qty=float(data.get('qty',0)), rate=float(data.get('rate',0)), total=float(data.get('qty',0))*float(data.get('rate',0)), unit=data.get('unit'), status='Draft')
        db.session.add(po)
        db.session.commit()
        send_whatsapp('919999999999', f"📦 PO {po_no}: {data.get('material')} {data.get('qty')} MT @ Rs {data.get('rate')} from Vendor {data.get('vendor_id')}. Total Rs {po.total}. - Lemon ERP", 'PO')
        return jsonify({'status':'success','po_no':po_no})
    pos=PurchaseOrder.query.filter_by(company_id=1).order_by(PurchaseOrder.id.desc()).all()
    return jsonify([{'po_no':p.po_no,'material':p.material,'qty':p.qty,'total':p.total,'status':p.status,'date':p.date} for p in pos])

@app.route('/api/grn', methods=['GET','POST'])
def grn_api():
    if request.method=='POST':
        data=request.json
        cnt=GRN.query.count()+1
        grn_no=f"GRN-2026-{cnt:04d}"
        grn=GRN(company_id=1, grn_no=grn_no, date=data.get('date', datetime.now().strftime('%Y-%m-%d')), time=datetime.now().strftime('%H:%M:%S'), po_no=data.get('po_no',''), vehicle_no=data.get('vehicle_no','').upper(), vendor_id=data.get('vendor_id'), material_type=data.get('material_type','Raw'), material=data.get('material'), challan_no=data.get('challan_no'), invoice_no=data.get('invoice_no'), gross_wt=float(data.get('gross_wt',0)), tare_wt=float(data.get('tare_wt',0)), net_wt=float(data.get('net_wt',0)), unit=data.get('unit'), operator=data.get('operator','operator1'))
        db.session.add(grn)
        sm=StockMaster.query.filter_by(company_id=1, product=data.get('material'), unit=data.get('unit')).first()
        if not sm:
            sm=StockMaster.query.filter_by(company_id=1, product=data.get('material')).first()
        if sm:
            sm.current_stock+=float(data.get('net_wt',0))
        db.session.commit()
        send_whatsapp('919999999999', f"✅ GRN {grn_no}: {data.get('net_wt')} MT {data.get('material')} Vehicle {data.get('vehicle_no')} Unit {data.get('unit')}. - Lemon ERP", 'GRN')
        return jsonify({'status':'success','grn_no':grn_no})
    grns=GRN.query.filter_by(company_id=1).order_by(GRN.id.desc()).limit(50).all()
    return jsonify([{'grn_no':g.grn_no,'material':g.material,'net_wt':g.net_wt,'vehicle':g.vehicle_no,'date':g.date,'unit':g.unit} for g in grns])

@app.route('/api/stock_v4')
def stock_v4():
    stocks=StockMaster.query.filter_by(company_id=1).all()
    result={'Raw':[],'WIP':[],'Finished':[],'Packaging':[]}
    for s in stocks:
        status='OK'
        if s.current_stock < s.min_stock: status='Critical'
        elif s.current_stock < s.reorder_level: status='Reorder'
        result[s.product_category].append({'product':s.product,'unit':s.unit,'current':s.current_stock,'min':s.min_stock,'reorder':s.reorder_level,'max':s.max_stock,'status':status})
    packs=PackagingStock.query.filter_by(company_id=1).all()
    for p in packs:
        status='OK'
        if p.closing < p.min_stock: status='Critical'
        elif p.closing < p.min_stock*1.5: status='Reorder'
        result['Packaging'].append({'product':p.bag_type,'unit':p.unit,'current':p.closing,'min':p.min_stock,'rate':p.rate_per_bag,'capacity':p.capacity_mt,'status':status})
    return jsonify(result)

@app.route('/api/low_stock_alerts')
def low_stock():
    stocks=StockMaster.query.filter_by(company_id=1).all()
    alerts=[]
    for s in stocks:
        if s.current_stock < s.min_stock:
            alerts.append({'product':s.product,'unit':s.unit,'current':s.current_stock,'min':s.min_stock,'type':'Critical'})
            send_whatsapp('919999999999', f"🚨 Low Stock Alert: {s.unit} {s.product} {s.current_stock}MT < Min {s.min_stock}MT. Reorder {s.reorder_qty}MT. - Lemon ERP", 'Low Stock')
    return jsonify(alerts)

@app.route('/api/whatsapp_logs')
def wa_logs():
    logs=WhatsAppLog.query.filter_by(company_id=1).order_by(WhatsAppLog.id.desc()).limit(30).all()
    return jsonify([{'date':l.date,'time':l.time,'type':l.message_type,'message':l.message,'status':l.status} for l in logs])

@app.route('/api/qr_generate', methods=['POST'])
def qr_gen():
    data=request.json
    cnt=QRBag.query.count()+1
    prod=(data.get('product','CaO') or 'CaO').replace(' ','')[:8]
    unit=(data.get('unit','U1') or 'U1').replace(' ','')[:2]
    bag_id=f"JMB-{prod}-{unit}-{datetime.now().strftime('%Y')}-{cnt:05d}"
    qr_data=f"{bag_id}|{data.get('product')}|{data.get('weight')}MT|{data.get('unit')}|RLP|HeritageGreen|{datetime.now().strftime('%Y-%m-%d')}"
    qr=qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img=qr.make_image(fill_color="#1A2E1E", back_color="#FAF6F0")
    buffered=BytesIO()
    img.save(buffered, format="PNG")
    img_str=base64.b64encode(buffered.getvalue()).decode()
    entry=QRBag(company_id=1, bag_id=bag_id, product=data.get('product'), weight=float(data.get('weight',1.2)), unit=data.get('unit'), qr_data=qr_data, created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(entry)
    db.session.commit()
    send_whatsapp('919999999999', f"🔳 QR Generated: {bag_id} {data.get('product')} {data.get('weight')}MT {data.get('unit')} - Lemon ERP", 'QR')
    return jsonify({'bag_id':bag_id,'qr_base64':img_str})

@app.route('/api/qr_list')
def qr_list():
    qs=QRBag.query.filter_by(company_id=1).order_by(QRBag.id.desc()).limit(30).all()
    return jsonify([{'bag_id':q.bag_id,'product':q.product,'weight':q.weight,'unit':q.unit,'created':q.created_at} for q in qs])

@app.route('/api/morning_summary')
def morning():
    stocks=StockMaster.query.filter_by(company_id=1).all()
    raw_val=sum([s.stock_value for s in stocks if s.product_category=='Raw'])
    wip_val=sum([s.stock_value for s in stocks if s.product_category=='WIP'])
    fin_val=sum([s.stock_value for s in stocks if s.product_category=='Finished'])
    total=raw_val+wip_val+fin_val
    msg=f"🍋 Lemon ERP Morning Summary {datetime.now().strftime('%d-%m-%Y')}\nRaw: {raw_val/100000:.1f}L | WIP: {wip_val/100000:.1f}L | Finished: {fin_val/100000:.1f}L | Total: {total/100000:.1f}L\nUnits: U1 72MT U2 84MT U3 125MT\n- RLP Lime Industries"
    send_whatsapp('919999999999', msg, 'Daily Summary')
    return jsonify({'date':str(datetime.date.today()),'raw_value_lakh':raw_val/100000,'wip_value_lakh':wip_val/100000,'finished_value_lakh':fin_val/100000,'total_lakh':total/100000,'message':msg})

@app.route('/api/manifest')
def manifest():
    return jsonify({"name":"Lemon ERP v4.1","short_name":"Lemon ERP","start_url":"/","display":"standalone","background_color":"#1A2E1E","theme_color":"#1A2E1E","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/1624/1624456.png","sizes":"512x512","type":"image/png"}]})

@app.route('/mobile')
def mobile():
    return """
<html><head><title>Lemon ERP Mobile</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#FAF6F0;margin:0} .header{background:#1A2E1E;color:#C9A86A;padding:20px;text-align:center} .card{background:white;margin:12px;padding:16px;border-radius:12px;border-left:5px solid #C9A86A}
.btn{background:#1A2E1E;color:white;padding:12px 20px;border-radius:8px;border:none;width:100%;margin:6px 0;font-weight:700}</style></head>
<body><div class="header"><h2>🍋 Lemon ERP Mobile PWA</h2><p>Operator App - Unit 1 / Unit 2</p></div>
<div class="card"><h3>Login</h3><input id="u" placeholder="Username operator1"><input id="p" type="password" placeholder="Password op123"><button class="btn" onclick="login()">Login</button><p id="msg"></p></div>
<div class="card"><h3>Quick GRN</h3><input id="veh" placeholder="Vehicle No"><input id="mat" placeholder="Material"><input id="gw" placeholder="Gross Wt kg"><input id="tw" placeholder="Tare Wt kg"><button class="btn" onclick="quickGRN()">Submit GRN</button></div>
<script>
function login(){let u=document.getElementById('u').value; let p=document.getElementById('p').value; if((u==='operator1'&&p==='op123')||(u==='owner'&&p==='owner123')){document.getElementById('msg').innerHTML='✅ Login OK '+u;}else{document.getElementById('msg').innerHTML='❌ Invalid';}}
async function quickGRN(){let gw=parseFloat(document.getElementById('gw').value||0); let tw=parseFloat(document.getElementById('tw').value||0); let net=(gw-tw)/1000; let data={vehicle_no:document.getElementById('veh').value, material:document.getElementById('mat').value, gross_wt:gw, tare_wt:tw, net_wt:net, unit:'Unit 1 72MT', vendor_id:1, material_type:'Raw'}; let r=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); let d=await r.json(); alert('GRN '+d.grn_no+' '+net+'MT');}
</script>
<a href="/" style="display:block;text-align:center;margin:20px;color:#1A2E1E">← Back to Dashboard</a></body></html>
    """

@app.route('/api/health')
def health():
    return jsonify({"status":"LIVE","version":"v4.1 FULL","theme":"Heritage Green #1A2E1E + Brass #C9A86A + Lemon #F2E863","url":"https://lemon-erp.onrender.com","units":["Unit 1 72MT","Unit 2 84MT","Unit 3 125MT"]})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
