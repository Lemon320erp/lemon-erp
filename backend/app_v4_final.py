"""
🍋 LEMON ERP v4.4 - ODOO MANUFACTURING - CLEAN MASTER
Requirements: Short headings, Empty masters, Create/Edit/Delete for all masters
No seeded vendors/products/customers - User creates fresh
Odoo-like but short headings: Dash, Stock, Make, Buy, Sell, Products, Kilns, Vendors, Customers, Pack, QR, Cost, Mobile
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode, base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'lemon-erp-v44-clean-masters-short-headings-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v44_clean.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS - CLEAN =================
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vendor_type = db.Column(db.String(50))
    gst = db.Column(db.String(30))
    contact = db.Column(db.String(50))
    credit_limit = db.Column(db.Float, default=0)
    pending_due = db.Column(db.Float, default=0)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    customer_type = db.Column(db.String(50))
    gst = db.Column(db.String(30))
    contact = db.Column(db.String(50))
    pending_receivable = db.Column(db.Float, default=0)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))  # Raw, WIP, Finished
    sale_price = db.Column(db.Float, default=0)
    purchase_price = db.Column(db.Float, default=0)
    loose_stock_mt = db.Column(db.Float, default=0)
    jumbo_bags_count = db.Column(db.Float, default=0)
    jumbo_mt = db.Column(db.Float, default=0)
    hdpe_40kg_count = db.Column(db.Float, default=0)
    hdpe_40kg_mt = db.Column(db.Float, default=0)
    total_stock_mt = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    location = db.Column(db.String(100))

class WorkCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    unit = db.Column(db.String(100))
    wc_type = db.Column(db.String(50))
    capacity_mt_per_day = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Running')

class PackagingStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bag_type = db.Column(db.String(100))
    bag_category = db.Column(db.String(20))
    capacity_mt = db.Column(db.Float, default=0)
    closing = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    rate_per_bag = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))

class ManufacturingOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mo_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    workcenter_id = db.Column(db.Integer, db.ForeignKey('work_center.id'))
    unit = db.Column(db.String(100))
    mo_type = db.Column(db.String(50))
    input_product = db.Column(db.String(100))
    input_qty_mt = db.Column(db.Float, default=0)
    limestone_mt = db.Column(db.Float, default=0)
    petcoke_mt = db.Column(db.Float, default=0)
    petcoke_ratio = db.Column(db.Float, default=0)
    output_product = db.Column(db.String(100))
    output_qty_mt = db.Column(db.Float, default=0)
    wastage_mt = db.Column(db.Float, default=0)
    wastage_pct = db.Column(db.Float, default=0)
    burning_loss_pct = db.Column(db.Float, default=0)
    operator = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Done')

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material = db.Column(db.String(100))
    qty = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Draft')

class GRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grn_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vehicle_no = db.Column(db.String(50))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material = db.Column(db.String(100))
    net_wt = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))

class QRBag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bag_id = db.Column(db.String(50), unique=True)
    product = db.Column(db.String(100))
    weight = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Packed')
    created_at = db.Column(db.String(30))

class Dispatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    vehicle_no = db.Column(db.String(50))
    product = db.Column(db.String(100))
    qty_mt = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Dispatched')

with app.app_context():
    db.create_all()
    # CLEAN - NO SEEDED DATA - User creates everything fresh

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html><head><title>Lemon ERP v4.4 - Clean</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--line:#E8E0D5;--gray:#F6F5F3}
*{box-sizing:border-box} body{margin:0;font-family:Inter,Arial;background:var(--gray);color:var(--green);font-size:13px}
.topnav{background:var(--green);color:white;padding:0 14px;display:flex;justify-content:space-between;align-items:center;height:44px;position:sticky;top:0;z-index:200}
.topnav .brand{font-weight:900;font-size:15px} .topnav .brand span.l{color:var(--lemon)}
.layout{display:flex}
.sidebar{width:200px;background:white;border-right:1px solid var(--line);padding:10px 0;position:sticky;top:44px;height:calc(100vh - 44px);overflow-y:auto}
.sidebar h4{font-size:10px;color:#888;margin:14px 10px 4px;text-transform:uppercase;letter-spacing:0.6px}
.menu{padding:7px 10px;margin:2px 6px;border-radius:7px;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:12px;color:#444}
.menu:hover{background:var(--alab)} .menu.active{background:var(--green);color:var(--brass)}
.content{flex:1;padding:14px;max-width:1400px}
.card{background:white;border-radius:10px;padding:14px;margin:8px 0;box-shadow:0 2px 6px rgba(0,0,0,0.04);border:1px solid var(--line)}
.card h3{margin:0 0 10px;font-size:13px;font-weight:800}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.kpi{border-left:4px solid var(--brass);padding:12px}
.kpi .val{font-size:20px;font-weight:900}
.btn{padding:7px 12px;border-radius:7px;border:none;cursor:pointer;font-weight:700;font-size:11px}
.btn-g{background:var(--green);color:white} .btn-y{background:var(--lemon);color:var(--green)} .btn-w{background:white;color:var(--green);border:1px solid var(--line)} .btn-r{background:#C5221F;color:white}
.badge{padding:3px 8px;border-radius:12px;font-size:10px;font-weight:800}
.ok{background:#E6F4EA;color:#1E7D32} .warn{background:#FEF3CD;color:#9C6F00} .crit{background:#FCE8E6;color:#C5221F}
table{width:100%;border-collapse:collapse;font-size:12px} th{background:#F8F6F3;padding:8px 6px;text-align:left;font-weight:700;border-bottom:2px solid var(--line)} td{padding:7px 6px;border-bottom:1px solid #F0EBE2}
input,select{padding:7px 8px;border-radius:6px;border:1px solid var(--line);width:100%;font-size:12px;margin:3px 0}
.row{display:flex;gap:6px;flex-wrap:wrap}.row>*{flex:1;min-width:120px}
.hidden{display:none}
.form-box{background:var(--alab);padding:12px;border-radius:8px;border:1px dashed var(--brass);margin-bottom:10px}
</style></head><body>
<div class="topnav"><div class="brand">🍋 Lemon ERP <span class="l">v4.4 Clean</span> <span style="font-size:10px;background:var(--brass);color:var(--green);padding:2px 6px;border-radius:10px;margin-left:6px">Empty Masters - Create New</span></div><div><button class="btn btn-y" onclick="location.reload()">Reload</button></div></div>
<div class="layout">
<div class="sidebar">
<h4>Main</h4>
<div class="menu active" onclick="openTab('dash')"><i class="bi bi-speedometer2"></i> Dash</div>
<div class="menu" onclick="openTab('stock')"><i class="bi bi-box-seam"></i> Stock</div>
<div class="menu" onclick="openTab('make')"><i class="bi bi-gear"></i> Make</div>
<div class="menu" onclick="openTab('buy')"><i class="bi bi-cart"></i> Buy</div>
<div class="menu" onclick="openTab('sell')"><i class="bi bi-truck"></i> Sell</div>
<h4>Masters</h4>
<div class="menu" onclick="openTab('products')"><i class="bi bi-bag"></i> Products</div>
<div class="menu" onclick="openTab('kilns')"><i class="bi bi-building"></i> Kilns</div>
<div class="menu" onclick="openTab('vendors')"><i class="bi bi-people"></i> Vendors</div>
<div class="menu" onclick="openTab('customers')"><i class="bi bi-person"></i> Customers</div>
<div class="menu" onclick="openTab('pack')"><i class="bi bi-box"></i> Pack</div>
<div class="menu" onclick="openTab('qr')"><i class="bi bi-qr-code"></i> QR</div>
<h4>Reports</h4>
<div class="menu" onclick="openTab('cost')"><i class="bi bi-calculator"></i> Cost</div>
<div class="menu" onclick="openTab('mobile')"><i class="bi bi-phone"></i> Mobile</div>
</div>

<div class="content">
<!-- DASH -->
<div id="dash" class="tabcontent">
<div class="card"><h3>Dash - Overview - Empty DB - Create Masters First</h3>
<div class="kpi-grid">
<div class="card kpi"><div style="font-size:11px">Total Value</div><div class="val" id="totalVal">Rs 0 Lakh</div><div style="font-size:10px">Create Products + Stock</div></div>
<div class="card kpi" style="border-left-color:var(--lemon)"><div style="font-size:11px">Production Today</div><div class="val" id="prodToday">0 MT</div><div style="font-size:10px">Create Kilns + Make Orders</div></div>
<div class="card kpi"><div style="font-size:11px">Stock Alerts</div><div class="val" id="alertCnt">0</div><div style="font-size:10px">Min/Reorder check</div></div>
<div class="card kpi"><div style="font-size:11px">Date</div><div class="val" style="font-size:14px" id="todayDate"></div><div style="font-size:10px">3 Units - Create Masters</div></div>
</div>
</div>
<div class="card"><h3>Quick Setup - Create in Order</h3><p style="font-size:11px">1. Kilns → 2. Products → 3. Vendors → 4. Customers → 5. Pack → 6. Then Make/Buy/Sell</p><div class="row"><button class="btn btn-g" onclick="openTab('kilns')">1. Create Kilns</button><button class="btn btn-g" onclick="openTab('products')">2. Create Products</button><button class="btn btn-g" onclick="openTab('vendors')">3. Create Vendors</button><button class="btn btn-g" onclick="openTab('customers')">4. Create Customers</button></div></div>
<div class="card"><h3>Alerts - Low Stock</h3><div id="alerts">No products yet - Create Products first</div></div>
</div>

<!-- STOCK -->
<div id="stock" class="tabcontent hidden">
<div class="card"><h3>Stock - Loose+Jumbo+40kg Combined - Filter by Unit</h3><div class="row"><select id="fUnit"><option value="All">All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="loadStock()">Filter</button></div></div>
<div class="card"><h3>Raw</h3><div id="rawTbl">No products - Create in Products tab</div></div>
<div class="card"><h3>WIP</h3><div id="wipTbl">No products</div></div>
<div class="card"><h3>Finished - Total = Loose+Jumbo+40kg</h3><div id="finTbl">No products</div></div>
</div>

<!-- MAKE -->
<div id="make" class="tabcontent hidden">
<div class="card"><h3>Make - Manufacturing Orders - Kiln, Sizing, Hydration</h3>
<div class="form-box">
<div class="row"><select id="make_wc"></select><select id="make_type"><option>Kiln</option><option>Sizing</option><option>Hydration</option></select><input id="make_unit" placeholder="Unit e.g. Unit 1 72MT" value="Unit 1 72MT"></div>
<div class="row"><input id="make_lime" type="number" placeholder="Limestone MT (Kiln) / Input MT (Sizing)"><input id="make_pet" type="number" placeholder="Petcoke MT"><input id="make_out" type="number" placeholder="Output MT CaO / Sized"></div>
<div class="row"><input id="make_waste" type="number" placeholder="Wastage MT (Sizing)"><input id="make_inProd" placeholder="Input Product e.g. Limestone / CaO Loose"><input id="make_outProd" placeholder="Output Product e.g. CaO Loose / 10-40mm"></div>
<div class="row"><input id="make_op" placeholder="Operator"><button class="btn btn-g" onclick="createMO()">Create MO</button></div>
<p style="font-size:10px">Ratio Petcoke/Lime must 0.154-0.166 | Wastage alert >5% | Hydration gain 15%</p>
</div>
<div id="moList">No MO - Create first</div>
</div>
</div>

<!-- BUY -->
<div id="buy" class="tabcontent hidden">
<div class="card"><h3>Buy - PO + GRN - Weighbridge</h3>
<div class="form-box"><h3>New PO</h3><div class="row"><select id="po_vendor"></select><input id="po_mat" placeholder="Material"><input id="po_qty" type="number" placeholder="Qty"><input id="po_rate" type="number" placeholder="Rate"></div><div class="row"><select id="po_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="po_status"><option>Draft</option><option>Sent</option><option>Received</option></select><button class="btn btn-g" onclick="createPO()">Create PO</button></div></div>
<div class="form-box"><h3>New GRN - Gross/Tare → Net MT Auto</h3><div class="row"><input id="g_vehicle" placeholder="Vehicle No"><input id="g_material" placeholder="Material"><select id="g_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div><div class="row"><input id="g_gross" type="number" placeholder="Gross kg"><input id="g_tare" type="number" placeholder="Tare kg"><select id="g_vendor"></select><button class="btn btn-y" onclick="createGRN()">Save GRN - Stock Update</button></div></div>
<div class="card"><h3>PO List</h3><div id="poList">No PO</div></div>
<div class="card"><h3>GRN List</h3><div id="grnList">No GRN</div></div>
</div>
</div>

<!-- SELL -->
<div id="sell" class="tabcontent hidden">
<div class="card"><h3>Sell - Dispatch - Customer + Vehicle + QR Scan</h3>
<div class="form-box"><div class="row"><select id="d_customer"></select><input id="d_vehicle" placeholder="Vehicle No"><select id="d_product"></select><input id="d_qty" type="number" placeholder="Qty MT"></div><div class="row"><input id="d_qr" placeholder="QR Bags comma separated"><select id="d_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="createDispatch()">Create Dispatch</button></div></div>
<div class="card"><h3>Dispatch List</h3><div id="dispatchList">No Dispatch</div></div>
</div>
</div>

<!-- PRODUCTS MASTER - WITH CREATE/EDIT/DELETE -->
<div id="products" class="tabcontent hidden">
<div class="card"><h3>Products - Create/Edit/Delete - Size-wise - Loose+Jumbo+40kg Combined</h3>
<div class="form-box">
<h3 id="prodFormTitle">Add New Product</h3>
<input type="hidden" id="prod_id">
<div class="row"><input id="prod_name" placeholder="Name e.g. Limestone, CaO 10-40mm, Hydrated 90%"><select id="prod_cat"><option>Raw</option><option>WIP</option><option>Finished</option></select><input id="prod_location" placeholder="Location e.g. Unit 1 Yard, Near Kilns"></div>
<div class="row"><input id="prod_loose" type="number" placeholder="Loose MT e.g. 25"><input id="prod_jumbo_cnt" type="number" placeholder="Jumbo Bags Count e.g. 42"><input id="prod_jumbo_mt" type="number" placeholder="Jumbo MT e.g. 50"><input id="prod_hdpe_cnt" type="number" placeholder="40kg Bags Count e.g. 250"></div>
<div class="row"><input id="prod_hdpe_mt" type="number" placeholder="40kg MT e.g. 10"><input id="prod_sale" type="number" placeholder="Sale Price Rs/MT e.g. 15000"><input id="prod_purchase" type="number" placeholder="Purchase Price Rs/MT e.g. 7000"><input id="prod_min" type="number" placeholder="Min Stock MT"></div>
<div class="row"><input id="prod_reorder" type="number" placeholder="Reorder Level MT"><button class="btn btn-g" onclick="saveProduct()">Save Product</button><button class="btn btn-w" onclick="resetProdForm()">Reset</button></div>
<p style="font-size:10px">Excel logic: Total = Loose + Jumbo MT + 40kg MT → e.g. 85 = 25 + 50 + 10 | Jumbo 1.2MT per bag, 40kg 0.04 MT per bag</p>
</div>
<div id="productTbl">No products - Add new above - Masters empty as requested</div>
</div>
</div>

<!-- KILNS MASTER -->
<div id="kilns" class="tabcontent hidden">
<div class="card"><h3>Kilns - Work Centers - Create/Edit/Delete - 15 Kilns Example</h3>
<div class="form-box">
<h3 id="kilnFormTitle">Add New Kiln / Work Center</h3>
<input type="hidden" id="kiln_id">
<div class="row"><input id="kiln_name" placeholder="Name e.g. Kiln 1, Sizing Plant 10-40mm, Hydration Plant 90%"><select id="kiln_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="kiln_type"><option>Kiln</option><option>Sizing</option><option>Hydration</option><option>Packing</option></select></div>
<div class="row"><input id="kiln_cap" type="number" placeholder="Capacity MT/day e.g. 15"><select id="kiln_status"><option>Running</option><option>Idle</option><option>Maintenance</option></select><button class="btn btn-g" onclick="saveKiln()">Save Kiln</button><button class="btn btn-w" onclick="resetKilnForm()">Reset</button></div>
</div>
<div id="wcTbl">No kilns - Add new - Masters empty</div>
</div>
</div>

<!-- VENDORS MASTER -->
<div id="vendors" class="tabcontent hidden">
<div class="card"><h3>Vendors - Create/Edit/Delete</h3>
<div class="form-box">
<h3 id="vendFormTitle">Add New Vendor</h3>
<input type="hidden" id="vend_id">
<div class="row"><input id="vend_name" placeholder="Name e.g. Limestone Mines Jodhpur"><select id="vend_type"><option>Limestone</option><option>Petcoke</option><option>Packaging</option><option>Transport</option><option>Trading</option></select><input id="vend_gst" placeholder="GST No"></div>
<div class="row"><input id="vend_contact" placeholder="Contact 98290..."><input id="vend_credit" type="number" placeholder="Credit Limit Rs"><input id="vend_due" type="number" placeholder="Pending Due Rs"><button class="btn btn-g" onclick="saveVendor()">Save Vendor</button><button class="btn btn-w" onclick="resetVendForm()">Reset</button></div>
</div>
<div id="vendorTbl">No vendors - Add new - Masters empty</div>
</div>
</div>

<!-- CUSTOMERS MASTER -->
<div id="customers" class="tabcontent hidden">
<div class="card"><h3>Customers - Create/Edit/Delete</h3>
<div class="form-box">
<h3 id="custFormTitle">Add New Customer</h3>
<input type="hidden" id="cust_id">
<div class="row"><input id="cust_name" placeholder="Name e.g. UltraTech Cement"><select id="cust_type"><option>Cement</option><option>Steel</option><option>Chemical</option><option>Trader</option></select><input id="cust_gst" placeholder="GST No"></div>
<div class="row"><input id="cust_contact" placeholder="Contact"><input id="cust_recv" type="number" placeholder="Pending Receivable Rs"><button class="btn btn-g" onclick="saveCustomer()">Save Customer</button><button class="btn btn-w" onclick="resetCustForm()">Reset</button></div>
</div>
<div id="customerTbl">No customers - Add new - Masters empty</div>
</div>
</div>

<!-- PACK MASTER -->
<div id="pack" class="tabcontent hidden">
<div class="card"><h3>Pack - Packaging - Create/Edit/Delete - Jumbo/HDPE</h3>
<div class="form-box">
<h3 id="packFormTitle">Add New Pack</h3>
<input type="hidden" id="pack_id">
<div class="row"><input id="pack_type" placeholder="Bag Type e.g. 40kg HDPE White, Jumbo Type A 1.2MT"><select id="pack_cat"><option>40kg</option><option>Jumbo</option></select><input id="pack_cap" type="number" placeholder="Capacity MT 0.04 or 1.2"></div>
<div class="row"><input id="pack_closing" type="number" placeholder="Closing Bags e.g. 5000"><input id="pack_min" type="number" placeholder="Min Stock e.g. 2000"><input id="pack_rate" type="number" placeholder="Rate per Bag Rs 18"><select id="pack_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div>
<div class="row"><button class="btn btn-g" onclick="savePack()">Save Pack</button><button class="btn btn-w" onclick="resetPackForm()">Reset</button></div>
</div>
<div id="packTbl">No packs - Add new</div>
</div>
</div>

<!-- QR -->
<div id="qr" class="tabcontent hidden">
<div class="card"><h3>QR - Bag QR - Loose to Packed</h3>
<div class="form-box"><div class="row"><select id="qr_product"></select><input id="qr_weight" type="number" value="1.2"><select id="qr_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-y" onclick="genQR()">Generate QR</button></div><div style="text-align:center;background:var(--alab);padding:10px;border-radius:8px;margin-top:8px"><div id="qrResult"></div><div id="qrImg"></div></div></div>
<div class="card"><h3>QR List</h3><div id="qrList">No QR</div></div>
</div>
</div>

<!-- COST -->
<div id="cost" class="tabcontent hidden">
<div class="card"><h3>Cost - Costing Report - Rs/MT</h3><div id="costVal">Rs 0 Lakh - Create products first</div><div id="costTbl">No data</div></div>
</div>

<!-- MOBILE -->
<div id="mobile" class="tabcontent hidden">
<div class="card"><h3>Mobile - PWA - Operators</h3><p style="font-size:11px">operator1/op123 U1 | operator2/op123 U2 | operator3/op123 U3 | owner/owner123 | manager/mgr123 | Chrome → Add to Home Screen</p><a class="btn btn-g" href="/mobile">Open Mobile App</a></div>
</div>

</div>
</div>

<script>
function openTab(id){
 document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));
 document.getElementById(id).classList.remove('hidden');
 document.querySelectorAll('.menu').forEach(e=>e.classList.remove('active'));
 document.querySelectorAll('.menu').forEach(t=>{ if(t.getAttribute('onclick').includes("'"+id+"'")) t.classList.add('active'); });
 if(id==='dash') loadDash();
 if(id==='stock') loadStock();
 if(id==='make'){loadWCOptions(); loadMO();}
 if(id==='buy'){loadVendorsOpt(); loadPOList(); loadGRNList();}
 if(id==='sell'){loadCustomersOpt(); loadProductsOpt(); loadDispatchList();}
 if(id==='products') loadProducts();
 if(id==='kilns') loadKilns();
 if(id==='vendors') loadVendors();
 if(id==='customers') loadCustomers();
 if(id==='pack') loadPack();
 if(id==='qr'){loadProductsOpt(); loadQRList();}
 if(id==='cost') loadCost();
}
document.getElementById('todayDate').innerText=new Date().toLocaleDateString('en-IN',{weekday:'short',day:'numeric',month:'short',year:'numeric'});

async function loadDash(){
 let res=await fetch('/api/inventory/combined'); let data=await res.json();
 document.getElementById('totalVal').innerText='Rs '+(data.total_value_lakh||0).toFixed(1)+' Lakh';
 document.getElementById('alertCnt').innerText=(data.alerts||[]).length;
 let prodRes=await fetch('/api/mo/total'); let prodData=await prodRes.json(); document.getElementById('prodToday').innerText=(prodData.total||0)+' MT';
 let h='';
 if((data.alerts||[]).length===0) h='No alerts - Create products with Min/Reorder';
 else { h='<table><tr><th>Product</th><th>Total L+J+40kg</th><th>Min</th><th>Status</th></tr>'; data.alerts.slice(0,5).forEach(a=>{ let b=a.status==='Critical'?'crit':'warn'; h+=`<tr><td>${a.product}</td><td>${a.total_mt} MT</td><td>${a.min}</td><td><span class="badge ${b}">${a.status}</span></td></tr>`; }); h+='</table>'; }
 document.getElementById('alerts').innerHTML=h;
}

async function loadStock(){
 let res=await fetch('/api/inventory/combined'); let data=await res.json();
 let fUnit=document.getElementById('fUnit').value;
 function filt(list){ if(fUnit==='All') return list; return list.filter(x=> (x.location||'').includes(fUnit.split(' ')[1]) || (x.unit||'').includes(fUnit.split(' ')[1])); }
 let raw=filt(data.raw||[]); let wip=filt(data.wip||[]); let fin=filt(data.finished||[]);
 document.getElementById('rawTbl').innerHTML=raw.length?'<table><tr><th>Product</th><th>Location</th><th>Loose</th><th>Jumbo</th><th>40kg</th><th>Total</th><th>Status</th></tr>'+raw.map(r=>`<tr><td>${r.product}</td><td style="font-size:10px">${r.location}</td><td>${r.loose_stock_mt} MT</td><td>${r.jumbo_bags_count}/${r.jumbo_mt} MT</td><td>${r.hdpe_40kg_count}/${r.hdpe_40kg_mt} MT</td><td><b>${r.total_mt} MT</b></td><td><span class="badge ${r.status==='Critical'?'crit':(r.status==='Reorder'?'warn':'ok')}">${r.status}</span></td></tr>`).join('')+'</table>':'No Raw products - Create in Products tab';
 document.getElementById('wipTbl').innerHTML=wip.length?'<table><tr><th>Product</th><th>Location</th><th>Loose</th><th>Total</th><th>Status</th></tr>'+wip.map(r=>`<tr><td>${r.product}</td><td style="font-size:10px">${r.location}</td><td>${r.loose_stock_mt} MT</td><td><b>${r.total_mt} MT</b></td><td><span class="badge ${r.status==='Critical'?'crit':(r.status==='Reorder'?'warn':'ok')}">${r.status}</span></td></tr>`).join('')+'</table>':'No WIP';
 document.getElementById('finTbl').innerHTML=fin.length?'<table><tr><th>Product</th><th>Location</th><th>Loose</th><th>Jumbo</th><th>40kg</th><th>Total L+J+40kg</th><th>Status</th></tr>'+fin.map(r=>`<tr><td><b>${r.product}</b></td><td style="font-size:10px">${r.location}</td><td>${r.loose_stock_mt} MT</td><td>${r.jumbo_bags_count} / ${r.jumbo_mt} MT</td><td>${r.hdpe_40kg_count} / ${r.hdpe_40kg_mt} MT</td><td style="background:#FAF6F0"><b>${r.total_mt} MT</b><br><span style="font-size:9px">${r.loose_stock_mt}+${r.jumbo_mt}+${r.hdpe_40kg_mt}</span></td><td><span class="badge ${r.status==='Critical'?'crit':(r.status==='Reorder'?'warn':'ok')}">${r.status}</span></td></tr>`).join('')+'</table>':'No Finished - Create Products first';
}

// PRODUCTS CRUD
async function loadProducts(){
 let res=await fetch('/api/products'); let ps=await res.json();
 if(ps.length===0){ document.getElementById('productTbl').innerHTML='No products - Add new above - Masters empty as requested'; document.getElementById('qr_product').innerHTML=''; document.getElementById('d_product').innerHTML=''; return; }
 let h='<table><tr><th>Name</th><th>Cat</th><th>Location</th><th>Loose</th><th>Jumbo C/MT</th><th>40kg C/MT</th><th>Total</th><th>Sale/Purchase</th><th>Min/Reorder</th><th>Actions</th></tr>';
 ps.forEach(p=>{ h+=`<tr><td><b>${p.name}</b></td><td>${p.category}</td><td style="font-size:10px">${p.location||'-'}</td><td>${p.loose_stock_mt} MT</td><td>${p.jumbo_bags_count}/${p.jumbo_mt}</td><td>${p.hdpe_40kg_count}/${p.hdpe_40kg_mt}</td><td><b>${p.total_stock_mt} MT</b></td><td>Rs ${p.sale_price}/Rs ${p.purchase_price}</td><td>${p.min_stock}/${p.reorder_level}</td><td><button class="btn btn-w" onclick="editProduct(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProduct(${p.id})">Del</button></td></tr>`; });
 h+='</table>'; document.getElementById('productTbl').innerHTML=h;
 // for dropdowns
 let opts=ps.map(p=>`<option value="${p.name}">${p.name} - ${p.total_stock_mt} MT</option>`).join('');
 let el1=document.getElementById('qr_product'); if(el1) el1.innerHTML=opts;
 let el2=document.getElementById('d_product'); if(el2) el2.innerHTML=opts;
}
async function saveProduct(){
 let id=document.getElementById('prod_id').value;
 let payload={name:document.getElementById('prod_name').value, category:document.getElementById('prod_cat').value, location:document.getElementById('prod_location').value, loose_stock_mt:parseFloat(document.getElementById('prod_loose').value||0), jumbo_bags_count:parseFloat(document.getElementById('prod_jumbo_cnt').value||0), jumbo_mt:parseFloat(document.getElementById('prod_jumbo_mt').value||0), hdpe_40kg_count:parseFloat(document.getElementById('prod_hdpe_cnt').value||0), hdpe_40kg_mt:parseFloat(document.getElementById('prod_hdpe_mt').value||0), sale_price:parseFloat(document.getElementById('prod_sale').value||0), purchase_price:parseFloat(document.getElementById('prod_purchase').value||0), min_stock:parseFloat(document.getElementById('prod_min').value||0), reorder_level:parseFloat(document.getElementById('prod_reorder').value||0)};
 if(!payload.name){alert('Enter Product Name'); return;}
 let url=id?'/api/products/'+id:'/api/products'; let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json(); alert(id?'✅ Product Updated':'✅ Product Created: '+d.name); resetProdForm(); loadProducts(); loadStock();
}
async function editProduct(id){
 let res=await fetch('/api/products/'+id); let p=await res.json();
 document.getElementById('prod_id').value=p.id; document.getElementById('prod_name').value=p.name; document.getElementById('prod_cat').value=p.category; document.getElementById('prod_location').value=p.location; document.getElementById('prod_loose').value=p.loose_stock_mt; document.getElementById('prod_jumbo_cnt').value=p.jumbo_bags_count; document.getElementById('prod_jumbo_mt').value=p.jumbo_mt; document.getElementById('prod_hdpe_cnt').value=p.hdpe_40kg_count; document.getElementById('prod_hdpe_mt').value=p.hdpe_40kg_mt; document.getElementById('prod_sale').value=p.sale_price; document.getElementById('prod_purchase').value=p.purchase_price; document.getElementById('prod_min').value=p.min_stock; document.getElementById('prod_reorder').value=p.reorder_level;
 document.getElementById('prodFormTitle').innerText='Edit Product - '+p.name; window.scrollTo(0,0);
}
function resetProdForm(){ document.getElementById('prod_id').value=''; ['prod_name','prod_location','prod_loose','prod_jumbo_cnt','prod_jumbo_mt','prod_hdpe_cnt','prod_hdpe_mt','prod_sale','prod_purchase','prod_min','prod_reorder'].forEach(id=>{ document.getElementById(id).value=''; }); document.getElementById('prodFormTitle').innerText='Add New Product'; }
async function delProduct(id){ if(!confirm('Delete Product?')) return; await fetch('/api/products/'+id,{method:'DELETE'}); alert('Deleted'); loadProducts(); }

// KILNS CRUD
async function loadKilns(){
 let res=await fetch('/api/workcenters'); let wcs=await res.json();
 if(wcs.length===0){ document.getElementById('wcTbl').innerHTML='No kilns - Add new - Masters empty'; document.getElementById('make_wc').innerHTML=''; return; }
 let h='<table><tr><th>Name</th><th>Unit</th><th>Type</th><th>Cap MT/day</th><th>Status</th><th>Actions</th></tr>';
 wcs.forEach(w=>{ h+=`<tr><td><b>${w.name}</b></td><td>${w.unit}</td><td>${w.wc_type}</td><td>${w.capacity}</td><td><span class="badge ${w.status==='Running'?'ok':(w.status==='Maintenance'?'warn':'crit')}">${w.status}</span></td><td><button class="btn btn-w" onclick="editKiln(${w.id})">Edit</button> <button class="btn btn-r" onclick="delKiln(${w.id})">Del</button></td></tr>`; });
 h+='</table>'; document.getElementById('wcTbl').innerHTML=h;
 let opts=wcs.map(w=>`<option value="${w.id}">${w.name} - ${w.unit} - ${w.wc_type}</option>`).join('');
 let el=document.getElementById('make_wc'); if(el) el.innerHTML=opts;
}
async function saveKiln(){
 let id=document.getElementById('kiln_id').value;
 let payload={name:document.getElementById('kiln_name').value, unit:document.getElementById('kiln_unit').value, wc_type:document.getElementById('kiln_type').value, capacity_mt_per_day:parseFloat(document.getElementById('kiln_cap').value||0), status:document.getElementById('kiln_status').value};
 if(!payload.name){alert('Enter Kiln Name'); return;}
 let url=id?'/api/workcenters/'+id:'/api/workcenters'; let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Kiln Updated':'✅ Kiln Created'); resetKilnForm(); loadKilns();
}
async function editKiln(id){ let res=await fetch('/api/workcenters/'+id); let w=await res.json(); document.getElementById('kiln_id').value=w.id; document.getElementById('kiln_name').value=w.name; document.getElementById('kiln_unit').value=w.unit; document.getElementById('kiln_type').value=w.wc_type; document.getElementById('kiln_cap').value=w.capacity; document.getElementById('kiln_status').value=w.status; document.getElementById('kilnFormTitle').innerText='Edit Kiln - '+w.name; }
function resetKilnForm(){ document.getElementById('kiln_id').value=''; ['kiln_name','kiln_cap'].forEach(id=>document.getElementById(id).value=''); document.getElementById('kilnFormTitle').innerText='Add New Kiln / Work Center'; }
async function delKiln(id){ if(!confirm('Delete Kiln?')) return; await fetch('/api/workcenters/'+id,{method:'DELETE'}); loadKilns(); }
async function loadWCOptions(){ let res=await fetch('/api/workcenters'); let wcs=await res.json(); let opts=wcs.map(w=>`<option value="${w.id}">${w.name} - ${w.unit}</option>`).join(''); let el=document.getElementById('make_wc'); if(el) el.innerHTML=opts; }

// VENDORS CRUD
async function loadVendors(){
 let res=await fetch('/api/vendors'); let vs=await res.json();
 if(vs.length===0){ document.getElementById('vendorTbl').innerHTML='No vendors - Add new - Masters empty'; document.getElementById('po_vendor').innerHTML=''; document.getElementById('g_vendor').innerHTML=''; return; }
 let h='<table><tr><th>Name</th><th>Type</th><th>GST</th><th>Contact</th><th>Credit Limit</th><th>Pending Due</th><th>Actions</th></tr>';
 vs.forEach(v=>{ h+=`<tr><td><b>${v.name}</b></td><td>${v.vendor_type}</td><td style="font-size:10px">${v.gst||'-'}</td><td>${v.contact||'-'}</td><td>Rs ${v.credit_limit}</td><td>Rs ${v.pending_due}</td><td><button class="btn btn-w" onclick="editVendor(${v.id})">Edit</button> <button class="btn btn-r" onclick="delVendor(${v.id})">Del</button></td></tr>`; });
 h+='</table>'; document.getElementById('vendorTbl').innerHTML=h;
 let opts=vs.map(v=>`<option value="${v.id}">${v.name} - ${v.vendor_type}</option>`).join('');
 ['po_vendor','g_vendor'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; });
}
async function saveVendor(){
 let id=document.getElementById('vend_id').value;
 let payload={name:document.getElementById('vend_name').value, vendor_type:document.getElementById('vend_type').value, gst:document.getElementById('vend_gst').value, contact:document.getElementById('vend_contact').value, credit_limit:parseFloat(document.getElementById('vend_credit').value||0), pending_due:parseFloat(document.getElementById('vend_due').value||0)};
 if(!payload.name){alert('Enter Vendor Name'); return;}
 let url=id?'/api/vendors/'+id:'/api/vendors'; let method=id?'PUT':'POST';
 await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Vendor Updated':'✅ Vendor Created'); resetVendForm(); loadVendors();
}
async function editVendor(id){ let res=await fetch('/api/vendors/'+id); let v=await res.json(); document.getElementById('vend_id').value=v.id; document.getElementById('vend_name').value=v.name; document.getElementById('vend_type').value=v.vendor_type; document.getElementById('vend_gst').value=v.gst; document.getElementById('vend_contact').value=v.contact; document.getElementById('vend_credit').value=v.credit_limit; document.getElementById('vend_due').value=v.pending_due; document.getElementById('vendFormTitle').innerText='Edit Vendor - '+v.name; }
function resetVendForm(){ document.getElementById('vend_id').value=''; ['vend_name','vend_gst','vend_contact','vend_credit','vend_due'].forEach(id=>document.getElementById(id).value=''); document.getElementById('vendFormTitle').innerText='Add New Vendor'; }
async function delVendor(id){ if(!confirm('Delete Vendor?')) return; await fetch('/api/vendors/'+id,{method:'DELETE'}); loadVendors(); }
async function loadVendorsOpt(){ let res=await fetch('/api/vendors'); let vs=await res.json(); let opts=vs.map(v=>`<option value="${v.id}">${v.name}</option>`).join(''); ['po_vendor','g_vendor'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }

// CUSTOMERS CRUD
async function loadCustomers(){
 let res=await fetch('/api/customers'); let cs=await res.json();
 if(cs.length===0){ document.getElementById('customerTbl').innerHTML='No customers - Add new - Masters empty'; document.getElementById('d_customer').innerHTML=''; return; }
 let h='<table><tr><th>Name</th><th>Type</th><th>GST</th><th>Contact</th><th>Receivable</th><th>Actions</th></tr>';
 cs.forEach(c=>{ h+=`<tr><td><b>${c.name}</b></td><td>${c.customer_type}</td><td style="font-size:10px">${c.gst||'-'}</td><td>${c.contact||'-'}</td><td>Rs ${c.pending_receivable}</td><td><button class="btn btn-w" onclick="editCustomer(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCustomer(${c.id})">Del</button></td></tr>`; });
 h+='</table>'; document.getElementById('customerTbl').innerHTML=h;
 let opts=cs.map(c=>`<option value="${c.id}">${c.name} - ${c.customer_type}</option>`).join(''); let el=document.getElementById('d_customer'); if(el) el.innerHTML=opts;
}
async function saveCustomer(){
 let id=document.getElementById('cust_id').value;
 let payload={name:document.getElementById('cust_name').value, customer_type:document.getElementById('cust_type').value, gst:document.getElementById('cust_gst').value, contact:document.getElementById('cust_contact').value, pending_receivable:parseFloat(document.getElementById('cust_recv').value||0)};
 if(!payload.name){alert('Enter Customer Name'); return;}
 let url=id?'/api/customers/'+id:'/api/customers'; let method=id?'PUT':'POST';
 await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Customer Updated':'✅ Customer Created'); resetCustForm(); loadCustomers();
}
async function editCustomer(id){ let res=await fetch('/api/customers/'+id); let c=await res.json(); document.getElementById('cust_id').value=c.id; document.getElementById('cust_name').value=c.name; document.getElementById('cust_type').value=c.customer_type; document.getElementById('cust_gst').value=c.gst; document.getElementById('cust_contact').value=c.contact; document.getElementById('cust_recv').value=c.pending_receivable; document.getElementById('custFormTitle').innerText='Edit Customer - '+c.name; }
function resetCustForm(){ document.getElementById('cust_id').value=''; ['cust_name','cust_gst','cust_contact','cust_recv'].forEach(id=>document.getElementById(id).value=''); document.getElementById('custFormTitle').innerText='Add New Customer'; }
async function delCustomer(id){ if(!confirm('Delete Customer?')) return; await fetch('/api/customers/'+id,{method:'DELETE'}); loadCustomers(); }
async function loadCustomersOpt(){ let res=await fetch('/api/customers'); let cs=await res.json(); let opts=cs.map(c=>`<option value="${c.id}">${c.name}</option>`).join(''); let el=document.getElementById('d_customer'); if(el) el.innerHTML=opts; }

// PACK CRUD
async function loadPack(){
 let res=await fetch('/api/packaging'); let ps=await res.json();
 if(ps.length===0){ document.getElementById('packTbl').innerHTML='No packs - Add new'; return; }
 let h='<table><tr><th>Bag Type</th><th>Cat</th><th>Cap MT</th><th>Closing</th><th>Min</th><th>Rate/Bag</th><th>Unit</th><th>Actions</th></tr>';
 ps.forEach(p=>{ h+=`<tr><td><b>${p.bag_type}</b></td><td>${p.bag_category}</td><td>${p.capacity_mt}</td><td>${p.closing}</td><td>${p.min_stock}</td><td>Rs ${p.rate_per_bag}</td><td>${p.unit}</td><td><button class="btn btn-w" onclick="editPack(${p.id})">Edit</button> <button class="btn btn-r" onclick="delPack(${p.id})">Del</button></td></tr>`; });
 h+='</table>'; document.getElementById('packTbl').innerHTML=h;
}
async function savePack(){
 let id=document.getElementById('pack_id').value;
 let payload={bag_type:document.getElementById('pack_type').value, bag_category:document.getElementById('pack_cat').value, capacity_mt:parseFloat(document.getElementById('pack_cap').value||0), closing:parseFloat(document.getElementById('pack_closing').value||0), min_stock:parseFloat(document.getElementById('pack_min').value||0), rate_per_bag:parseFloat(document.getElementById('pack_rate').value||0), unit:document.getElementById('pack_unit').value};
 if(!payload.bag_type){alert('Enter Bag Type'); return;}
 let url=id?'/api/packaging/'+id:'/api/packaging'; let method=id?'PUT':'POST';
 await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Pack Updated':'✅ Pack Created'); resetPackForm(); loadPack();
}
async function editPack(id){ let res=await fetch('/api/packaging/'+id); let p=await res.json(); document.getElementById('pack_id').value=p.id; document.getElementById('pack_type').value=p.bag_type; document.getElementById('pack_cat').value=p.bag_category; document.getElementById('pack_cap').value=p.capacity_mt; document.getElementById('pack_closing').value=p.closing; document.getElementById('pack_min').value=p.min_stock; document.getElementById('pack_rate').value=p.rate_per_bag; document.getElementById('pack_unit').value=p.unit; document.getElementById('packFormTitle').innerText='Edit Pack - '+p.bag_type; }
function resetPackForm(){ document.getElementById('pack_id').value=''; ['pack_type','pack_cap','pack_closing','pack_min','pack_rate'].forEach(id=>document.getElementById(id).value=''); document.getElementById('packFormTitle').innerText='Add New Pack'; }
async function delPack(id){ if(!confirm('Delete Pack?')) return; await fetch('/api/packaging/'+id,{method:'DELETE'}); loadPack(); }

// MAKE
async function loadMO(){
 let res=await fetch('/api/manufacturing_orders'); let mos=await res.json();
 if(mos.length===0){ document.getElementById('moList').innerHTML='No MO - Create first - Kilns + Products needed'; return; }
 let h='<table><tr><th>MO No</th><th>Type</th><th>WC</th><th>Unit</th><th>Input→Output</th><th>Ratio/Waste/Burn</th><th>Operator</th><th>Status</th></tr>';
 mos.forEach(m=>{ h+=`<tr><td><b>${m.mo_no}</b></td><td><span class="badge ok">${m.mo_type}</span></td><td>${m.workcenter}</td><td>${m.unit}</td><td>${m.input_product} ${m.input_qty}→${m.output_product} ${m.output_qty} MT</td><td>Ratio:${(m.petcoke_ratio||0).toFixed(3)} Waste:${(m.wastage_pct||0).toFixed(1)}% Burn:${(m.burning_loss_pct||0).toFixed(1)}%</td><td>${m.operator}</td><td>${m.status}</td></tr>`; });
 h+='</table>'; document.getElementById('moList').innerHTML=h;
}
async function createMO(){
 let wc=document.getElementById('make_wc').value;
 if(!wc){alert('Create Kilns first'); return;}
 let lime=parseFloat(document.getElementById('make_lime').value||0); let pet=parseFloat(document.getElementById('make_pet').value||0); let out=parseFloat(document.getElementById('make_out').value||0); let waste=parseFloat(document.getElementById('make_waste').value||0);
 let payload={workcenter_id:wc, unit:document.getElementById('make_unit').value, mo_type:document.getElementById('make_type').value, limestone_mt:lime, petcoke_mt:pet, input_qty_mt:lime||parseFloat(document.getElementById('make_lime').value||0), output_qty_mt:out, wastage_mt:waste, input_product:document.getElementById('make_inProd').value, output_product:document.getElementById('make_outProd').value, operator:document.getElementById('make_op').value||'operator1'};
 let res=await fetch('/api/manufacturing_orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ MO Created: '+d.mo_no); loadMO(); loadDash();
}

// BUY / SELL helpers
async function createPO(){ let qty=parseFloat(document.getElementById('po_qty').value||0); let rate=parseFloat(document.getElementById('po_rate').value||0); if(qty<=0||rate<=0){alert('Qty & Rate'); return;} let payload={vendor_id:document.getElementById('po_vendor').value, material:document.getElementById('po_mat').value, qty:qty, rate:rate, unit:document.getElementById('po_unit').value, status:document.getElementById('po_status').value, date:new Date().toISOString().slice(0,10)}; let res=await fetch('/api/po',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ PO '+d.po_no); loadPOList(); }
async function loadPOList(){ let res=await fetch('/api/po'); let pos=await res.json(); document.getElementById('poList').innerHTML=pos.length?'<table><tr><th>PO No</th><th>Material</th><th>Qty</th><th>Rate</th><th>Total</th><th>Unit</th><th>Status</th></tr>'+pos.map(p=>`<tr><td>${p.po_no}</td><td>${p.material}</td><td>${p.qty}</td><td>${p.rate}</td><td>${p.total}</td><td>${p.unit}</td><td>${p.status}</td></tr>`).join('')+'</table>':'No PO'; }
async function createGRN(){ let gross=parseFloat(document.getElementById('g_gross').value||0); let tare=parseFloat(document.getElementById('g_tare').value||0); if(gross<=0||tare<=0){alert('Gross/Tare'); return;} let net=(gross-tare)/1000; let payload={vehicle_no:document.getElementById('g_vehicle').value, material:document.getElementById('g_material').value, gross_wt:gross, tare_wt:tare, net_wt:net, unit:document.getElementById('g_unit').value, vendor_id:document.getElementById('g_vendor').value}; let res=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ GRN '+d.grn_no+' Net '+net.toFixed(2)+' MT'); loadGRNList(); loadStock(); }
async function loadGRNList(){ let res=await fetch('/api/grn'); let gs=await res.json(); document.getElementById('grnList').innerHTML=gs.length?'<table><tr><th>GRN No</th><th>Vehicle</th><th>Material</th><th>Net MT</th><th>Unit</th></tr>'+gs.map(g=>`<tr><td>${g.grn_no}</td><td>${g.vehicle_no}</td><td>${g.material}</td><td>${g.net_wt} MT</td><td>${g.unit}</td></tr>`).join('')+'</table>':'No GRN'; }
async function createDispatch(){ let qty=parseFloat(document.getElementById('d_qty').value||0); if(qty<=0){alert('Qty'); return;} let payload={customer_id:document.getElementById('d_customer').value, vehicle_no:document.getElementById('d_vehicle').value, product:document.getElementById('d_product').value, qty_mt:qty, unit:document.getElementById('d_unit').value, qr_bags:document.getElementById('d_qr').value, date:new Date().toISOString().slice(0,10)}; let res=await fetch('/api/dispatch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ Dispatch '+d.dispatch_no); loadDispatchList(); loadStock(); }
async function loadDispatchList(){ let res=await fetch('/api/dispatch'); let ds=await res.json(); document.getElementById('dispatchList').innerHTML=ds.length?'<table><tr><th>Disp No</th><th>Customer</th><th>Vehicle</th><th>Product</th><th>Qty</th><th>Unit</th></tr>'+ds.map(d=>`<tr><td>${d.dispatch_no}</td><td>${d.customer}</td><td>${d.vehicle_no}</td><td>${d.product}</td><td>${d.qty_mt} MT</td><td>${d.unit}</td></tr>`).join('')+'</table>':'No Dispatch'; }
async function loadProductsOpt(){ let res=await fetch('/api/products'); let ps=await res.json(); let opts=ps.map(p=>`<option value="${p.name}">${p.name}</option>`).join(''); ['qr_product','d_product'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function genQR(){ let prod=document.getElementById('qr_product').value; if(!prod){alert('Create Products first'); return;} let wt=parseFloat(document.getElementById('qr_weight').value||1.2); let res=await fetch('/api/qr_generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product:prod, weight:wt, unit:document.getElementById('qr_unit').value})}); let d=await res.json(); document.getElementById('qrResult').innerHTML='<b>Bag ID: '+d.bag_id+'</b> '+prod+' '+wt+' MT'; document.getElementById('qrImg').innerHTML='<img src="data:image/png;base64,'+d.qr_base64+'" style="width:180px;border:6px solid #1A2E1E;border-radius:10px;margin-top:8px">'; loadQRList(); }
async function loadQRList(){ let res=await fetch('/api/qr_list'); let qs=await res.json(); document.getElementById('qrList').innerHTML=qs.length?'<table><tr><th>Bag ID</th><th>Product</th><th>Wt</th><th>Unit</th><th>Status</th></tr>'+qs.map(q=>`<tr><td><b>${q.bag_id}</b></td><td>${q.product}</td><td>${q.weight} MT</td><td>${q.unit}</td><td>${q.status}</td></tr>`).join('')+'</table>':'No QR'; }
async function loadCost(){ let res=await fetch('/api/inventory/combined'); let data=await res.json(); document.getElementById('costVal').innerText='Rs '+(data.total_value_lakh||0).toFixed(1)+' Lakh'; let all=[...(data.raw||[]),...(data.finished||[])]; document.getElementById('costTbl').innerHTML=all.length?'<table><tr><th>Product</th><th>Total MT</th><th>Cost/MT</th><th>Value</th><th>Sale</th><th>Margin</th></tr>'+all.map(r=>`<tr><td>${r.product}</td><td>${r.total_mt} MT</td><td>Rs ${r.purchase_price||r.sale_price||0}</td><td>Rs ${(r.value/1000).toFixed(1)}k</td><td>Rs ${r.sale_price||0}</td><td>Rs ${(r.sale_price-(r.purchase_price||0))}</td></tr>`).join('')+'</table>':'No data - Create products'; }

loadDash();
</script>
</body></html>
    """

# APIs with CRUD
@app.route('/api/inventory/combined')
def inv_combined():
    prods=Product.query.all()
    result={'raw':[],'wip':[],'finished':[],'alerts':[],'total_value_lakh':0}
    total_val=0
    for p in prods:
        total_mt=(p.loose_stock_mt or 0)+(p.jumbo_mt or 0)+(p.hdpe_40kg_mt or 0)
        rate=p.purchase_price if p.category=='Raw' else (p.sale_price or p.purchase_price or 0)
        if p.category=='WIP': rate=rate*0.5
        value=total_mt*rate
        total_val+=value
        status='OK'
        if total_mt < p.min_stock: status='Critical'
        elif total_mt < p.reorder_level: status='Reorder'
        entry={'product':p.name,'location':p.location,'loose_stock_mt':p.loose_stock_mt,'jumbo_bags_count':p.jumbo_bags_count,'jumbo_mt':p.jumbo_mt,'hdpe_40kg_count':p.hdpe_40kg_count,'hdpe_40kg_mt':p.hdpe_40kg_mt,'total_mt':total_mt,'total_stock_mt':total_mt,'purchase_price':p.purchase_price,'sale_price':p.sale_price,'value':value,'status':status,'min':p.min_stock}
        if p.category=='Raw': result['raw'].append(entry)
        elif p.category=='WIP': result['wip'].append(entry)
        else: result['finished'].append(entry)
        if status!='OK': result['alerts'].append(entry)
    packs=PackagingStock.query.all()
    for pk in packs: total_val+=pk.closing*pk.rate_per_bag
    result['total_value_lakh']=total_val/100000
    return jsonify(result)

@app.route('/api/products', methods=['GET','POST'])
def products_api():
    if request.method=='POST':
        data=request.json
        p=Product(name=data.get('name'), category=data.get('category'), location=data.get('location'), loose_stock_mt=float(data.get('loose_stock_mt',0)), jumbo_bags_count=float(data.get('jumbo_bags_count',0)), jumbo_mt=float(data.get('jumbo_mt',0)), hdpe_40kg_count=float(data.get('hdpe_40kg_count',0)), hdpe_40kg_mt=float(data.get('hdpe_40kg_mt',0)), sale_price=float(data.get('sale_price',0)), purchase_price=float(data.get('purchase_price',0)), min_stock=float(data.get('min_stock',0)), reorder_level=float(data.get('reorder_level',0)))
        p.total_stock_mt=p.loose_stock_mt+p.jumbo_mt+p.hdpe_40kg_mt
        db.session.add(p)
        db.session.commit()
        return jsonify({'id':p.id,'name':p.name})
    prods=Product.query.all()
    return jsonify([{'id':p.id,'name':p.name,'category':p.category,'location':p.location,'loose_stock_mt':p.loose_stock_mt,'jumbo_bags_count':p.jumbo_bags_count,'jumbo_mt':p.jumbo_mt,'hdpe_40kg_count':p.hdpe_40kg_count,'hdpe_40kg_mt':p.hdpe_40kg_mt,'total_stock_mt':p.total_stock_mt,'sale_price':p.sale_price,'purchase_price':p.purchase_price,'min_stock':p.min_stock,'reorder_level':p.reorder_level} for p in prods])

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
def product_one(pid):
    p=Product.query.get_or_404(pid)
    if request.method=='GET':
        return jsonify({'id':p.id,'name':p.name,'category':p.category,'location':p.location,'loose_stock_mt':p.loose_stock_mt,'jumbo_bags_count':p.jumbo_bags_count,'jumbo_mt':p.jumbo_mt,'hdpe_40kg_count':p.hdpe_40kg_count,'hdpe_40kg_mt':p.hdpe_40kg_mt,'total_stock_mt':p.total_stock_mt,'sale_price':p.sale_price,'purchase_price':p.purchase_price,'min_stock':p.min_stock,'reorder_level':p.reorder_level})
    elif request.method=='PUT':
        data=request.json
        for k in ['name','category','location']:
            if k in data: setattr(p,k,data[k])
        for k in ['loose_stock_mt','jumbo_bags_count','jumbo_mt','hdpe_40kg_count','hdpe_40kg_mt','sale_price','purchase_price','min_stock','reorder_level']:
            if k in data: setattr(p,k,float(data[k] or 0))
        p.total_stock_mt=p.loose_stock_mt+p.jumbo_mt+p.hdpe_40kg_mt
        db.session.commit()
        return jsonify({'status':'updated'})
    else:
        db.session.delete(p)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/workcenters', methods=['GET','POST'])
def wc_api():
    if request.method=='POST':
        data=request.json
        w=WorkCenter(name=data.get('name'), unit=data.get('unit'), wc_type=data.get('wc_type'), capacity_mt_per_day=float(data.get('capacity_mt_per_day',0)), status=data.get('status','Running'))
        db.session.add(w)
        db.session.commit()
        return jsonify({'id':w.id})
    wcs=WorkCenter.query.all()
    return jsonify([{'id':w.id,'name':w.name,'unit':w.unit,'wc_type':w.wc_type,'capacity':w.capacity_mt_per_day,'status':w.status} for w in wcs])

@app.route('/api/workcenters/<int:wid>', methods=['GET','PUT','DELETE'])
def wc_one(wid):
    w=WorkCenter.query.get_or_404(wid)
    if request.method=='GET':
        return jsonify({'id':w.id,'name':w.name,'unit':w.unit,'wc_type':w.wc_type,'capacity':w.capacity_mt_per_day,'status':w.status})
    elif request.method=='PUT':
        data=request.json
        w.name=data.get('name',w.name)
        w.unit=data.get('unit',w.unit)
        w.wc_type=data.get('wc_type',w.wc_type)
        w.capacity_mt_per_day=float(data.get('capacity_mt_per_day',w.capacity_mt_per_day))
        w.status=data.get('status',w.status)
        db.session.commit()
        return jsonify({'status':'updated'})
    else:
        db.session.delete(w)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/vendors', methods=['GET','POST'])
def vendors_api():
    if request.method=='POST':
        data=request.json
        v=Vendor(name=data.get('name'), vendor_type=data.get('vendor_type'), gst=data.get('gst'), contact=data.get('contact'), credit_limit=float(data.get('credit_limit',0)), pending_due=float(data.get('pending_due',0)))
        db.session.add(v)
        db.session.commit()
        return jsonify({'id':v.id})
    vs=Vendor.query.all()
    return jsonify([{'id':v.id,'name':v.name,'vendor_type':v.vendor_type,'gst':v.gst,'contact':v.contact,'credit_limit':v.credit_limit,'pending_due':v.pending_due} for v in vs])

@app.route('/api/vendors/<int:vid>', methods=['GET','PUT','DELETE'])
def vendor_one(vid):
    v=Vendor.query.get_or_404(vid)
    if request.method=='GET':
        return jsonify({'id':v.id,'name':v.name,'vendor_type':v.vendor_type,'gst':v.gst,'contact':v.contact,'credit_limit':v.credit_limit,'pending_due':v.pending_due})
    elif request.method=='PUT':
        data=request.json
        v.name=data.get('name',v.name)
        v.vendor_type=data.get('vendor_type',v.vendor_type)
        v.gst=data.get('gst',v.gst)
        v.contact=data.get('contact',v.contact)
        v.credit_limit=float(data.get('credit_limit',v.credit_limit))
        v.pending_due=float(data.get('pending_due',v.pending_due))
        db.session.commit()
        return jsonify({'status':'updated'})
    else:
        db.session.delete(v)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/customers', methods=['GET','POST'])
def customers_api():
    if request.method=='POST':
        data=request.json
        c=Customer(name=data.get('name'), customer_type=data.get('customer_type'), gst=data.get('gst'), contact=data.get('contact'), pending_receivable=float(data.get('pending_receivable',0)))
        db.session.add(c)
        db.session.commit()
        return jsonify({'id':c.id})
    cs=Customer.query.all()
    return jsonify([{'id':c.id,'name':c.name,'customer_type':c.customer_type,'gst':c.gst,'contact':c.contact,'pending_receivable':c.pending_receivable} for c in cs])

@app.route('/api/customers/<int:cid>', methods=['GET','PUT','DELETE'])
def customer_one(cid):
    c=Customer.query.get_or_404(cid)
    if request.method=='GET':
        return jsonify({'id':c.id,'name':c.name,'customer_type':c.customer_type,'gst':c.gst,'contact':c.contact,'pending_receivable':c.pending_receivable})
    elif request.method=='PUT':
        data=request.json
        c.name=data.get('name',c.name)
        c.customer_type=data.get('customer_type',c.customer_type)
        c.gst=data.get('gst',c.gst)
        c.contact=data.get('contact',c.contact)
        c.pending_receivable=float(data.get('pending_receivable',c.pending_receivable))
        db.session.commit()
        return jsonify({'status':'updated'})
    else:
        db.session.delete(c)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/packaging', methods=['GET','POST'])
def pack_api():
    if request.method=='POST':
        data=request.json
        p=PackagingStock(bag_type=data.get('bag_type'), bag_category=data.get('bag_category'), capacity_mt=float(data.get('capacity_mt',0)), closing=float(data.get('closing',0)), min_stock=float(data.get('min_stock',0)), rate_per_bag=float(data.get('rate_per_bag',0)), unit=data.get('unit'))
        db.session.add(p)
        db.session.commit()
        return jsonify({'id':p.id})
    ps=PackagingStock.query.all()
    return jsonify([{'id':p.id,'bag_type':p.bag_type,'bag_category':p.bag_category,'capacity_mt':p.capacity_mt,'closing':p.closing,'min_stock':p.min_stock,'rate_per_bag':p.rate_per_bag,'unit':p.unit} for p in ps])

@app.route('/api/packaging/<int:pid>', methods=['GET','PUT','DELETE'])
def pack_one(pid):
    p=PackagingStock.query.get_or_404(pid)
    if request.method=='GET':
        return jsonify({'id':p.id,'bag_type':p.bag_type,'bag_category':p.bag_category,'capacity_mt':p.capacity_mt,'closing':p.closing,'min_stock':p.min_stock,'rate_per_bag':p.rate_per_bag,'unit':p.unit})
    elif request.method=='PUT':
        data=request.json
        p.bag_type=data.get('bag_type',p.bag_type)
        p.bag_category=data.get('bag_category',p.bag_category)
        p.capacity_mt=float(data.get('capacity_mt',p.capacity_mt))
        p.closing=float(data.get('closing',p.closing))
        p.min_stock=float(data.get('min_stock',p.min_stock))
        p.rate_per_bag=float(data.get('rate_per_bag',p.rate_per_bag))
        p.unit=data.get('unit',p.unit)
        db.session.commit()
        return jsonify({'status':'updated'})
    else:
        db.session.delete(p)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/manufacturing_orders', methods=['GET','POST'])
def mo_api():
    if request.method=='POST':
        data=request.json
        cnt=ManufacturingOrder.query.count()+1
        mo_no=f"MO-{data.get('mo_type','Kiln')[:4].upper()}-2026-{cnt:04d}"
        lime=float(data.get('limestone_mt',0) or data.get('input_qty_mt',0))
        pet=float(data.get('petcoke_mt',0))
        out=float(data.get('output_qty_mt',0))
        waste=float(data.get('wastage_mt',0))
        ratio=pet/lime if lime>0 else 0
        burn=((lime-out)/lime*100) if lime>0 and data.get('mo_type')=='Kiln' else 0
        waste_pct=(waste/(lime or 1)*100) if data.get('mo_type')=='Sizing' else 0
        mo=ManufacturingOrder(mo_no=mo_no, date=datetime.now().strftime('%Y-%m-%d'), workcenter_id=data.get('workcenter_id'), unit=data.get('unit'), mo_type=data.get('mo_type'), input_product=data.get('input_product'), input_qty_mt=float(data.get('input_qty_mt',0) or lime), limestone_mt=lime, petcoke_mt=pet, petcoke_ratio=ratio, output_product=data.get('output_product'), output_qty_mt=out, wastage_mt=waste, wastage_pct=waste_pct, burning_loss_pct=burn, operator=data.get('operator','operator1'), status='Done')
        db.session.add(mo)
        db.session.commit()
        return jsonify({'mo_no':mo_no,'burning_loss_pct':burn,'petcoke_ratio':ratio,'wastage_pct':waste_pct})
    mos=ManufacturingOrder.query.order_by(ManufacturingOrder.id.desc()).limit(50).all()
    wcs={w.id:w.name for w in WorkCenter.query.all()}
    return jsonify([{'mo_no':m.mo_no,'date':m.date,'unit':m.unit,'workcenter':wcs.get(m.workcenter_id,'-'),'mo_type':m.mo_type,'input_product':m.input_product,'input_qty':m.input_qty_mt,'limestone_mt':m.limestone_mt,'petcoke_mt':m.petcoke_mt,'petcoke_ratio':m.petcoke_ratio,'output_product':m.output_product,'output_qty':m.output_qty_mt,'wastage_mt':m.wastage_mt,'wastage_pct':m.wastage_pct,'burning_loss_pct':m.burning_loss_pct,'operator':m.operator,'status':m.status} for m in mos])

@app.route('/api/mo/total')
def mo_total():
    mos=ManufacturingOrder.query.all()
    total=sum([m.output_qty_mt for m in mos if m.output_qty_mt])
    return jsonify({'total':total})

@app.route('/api/po', methods=['GET','POST'])
def po_api():
    if request.method=='POST':
        data=request.json
        cnt=PurchaseOrder.query.count()+1
        po_no=f"PO-2026-{cnt:04d}"
        total=float(data.get('qty',0))*float(data.get('rate',0))
        po=PurchaseOrder(po_no=po_no, date=data.get('date', datetime.now().strftime('%Y-%m-%d')), vendor_id=data.get('vendor_id'), material=data.get('material'), qty=float(data.get('qty',0)), rate=float(data.get('rate',0)), total=total, unit=data.get('unit'), status=data.get('status','Draft'))
        db.session.add(po)
        db.session.commit()
        return jsonify({'po_no':po_no})
    pos=PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).all()
    return jsonify([{'po_no':p.po_no,'date':p.date,'material':p.material,'qty':p.qty,'rate':p.rate,'total':p.total,'unit':p.unit,'status':p.status} for p in pos])

@app.route('/api/grn', methods=['GET','POST'])
def grn_api():
    if request.method=='POST':
        data=request.json
        cnt=GRN.query.count()+1
        grn_no=f"GRN-2026-{cnt:04d}"
        net=(float(data.get('gross_wt',0))-float(data.get('tare_wt',0)))/1000 if data.get('gross_wt') else float(data.get('net_wt',0) or 0)
        if 'net_wt' in data: net=float(data.get('net_wt',0))
        grn=GRN(grn_no=grn_no, date=datetime.now().strftime('%Y-%m-%d'), vehicle_no=data.get('vehicle_no',''), vendor_id=data.get('vendor_id'), material=data.get('material'), net_wt=net, unit=data.get('unit'))
        db.session.add(grn)
        # update product loose if exists
        prod=Product.query.filter(Product.name.contains((data.get('material') or '')[:5])).first()
        if prod:
            prod.loose_stock_mt+=net
            prod.total_stock_mt=prod.loose_stock_mt+prod.jumbo_mt+prod.hdpe_40kg_mt
        db.session.commit()
        return jsonify({'grn_no':grn_no})
    grns=GRN.query.order_by(GRN.id.desc()).limit(50).all()
    return jsonify([{'grn_no':g.grn_no,'date':g.date,'vehicle_no':g.vehicle_no,'material':g.material,'net_wt':g.net_wt,'unit':g.unit} for g in grns])

@app.route('/api/dispatch', methods=['GET','POST'])
def dispatch_api():
    if request.method=='POST':
        data=request.json
        cnt=Dispatch.query.count()+1
        d_no=f"DISP-2026-{cnt:04d}"
        disp=Dispatch(dispatch_no=d_no, date=datetime.now().strftime('%Y-%m-%d'), customer_id=data.get('customer_id'), vehicle_no=data.get('vehicle_no'), product=data.get('product'), qty_mt=float(data.get('qty_mt',0)), unit=data.get('unit'), status='Dispatched')
        db.session.add(disp)
        prod=Product.query.filter(Product.name.contains((data.get('product') or '')[:5])).first()
        if prod:
            qty=float(data.get('qty_mt',0))
            if prod.loose_stock_mt>=qty:
                prod.loose_stock_mt-=qty
            else:
                prod.loose_stock_mt=0
            prod.total_stock_mt=prod.loose_stock_mt+prod.jumbo_mt+prod.hdpe_40kg_mt
        db.session.commit()
        return jsonify({'dispatch_no':d_no})
    ds=Dispatch.query.order_by(Dispatch.id.desc()).limit(50).all()
    customers={c.id:c.name for c in Customer.query.all()}
    return jsonify([{'dispatch_no':d.dispatch_no,'date':d.date,'customer':customers.get(d.customer_id,'-'),'vehicle_no':d.vehicle_no,'product':d.product,'qty_mt':d.qty_mt,'unit':d.unit,'status':d.status} for d in ds])

@app.route('/api/qr_generate', methods=['POST'])
def qr_gen():
    data=request.json
    cnt=QRBag.query.count()+1
    prod=(data.get('product','CaO') or 'CaO').replace(' ','')[:8]
    bag_id=f"JMB-{prod}-2026-{cnt:05d}"
    qr_data=f"{bag_id}|{data.get('product')}|{data.get('weight')}MT|{data.get('unit')}"
    qr=qrcode.QRCode(version=1, box_size=8, border=3)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img=qr.make_image(fill_color="#1A2E1E", back_color="#FAF6F0")
    buffered=BytesIO()
    img.save(buffered, format="PNG")
    img_str=base64.b64encode(buffered.getvalue()).decode()
    entry=QRBag(bag_id=bag_id, product=data.get('product'), weight=float(data.get('weight',1.2)), unit=data.get('unit'), status='Packed', created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(entry)
    db.session.commit()
    return jsonify({'bag_id':bag_id,'qr_base64':img_str})

@app.route('/api/qr_list')
def qr_list():
    qs=QRBag.query.order_by(QRBag.id.desc()).limit(50).all()
    return jsonify([{'bag_id':q.bag_id,'product':q.product,'weight':q.weight,'unit':q.unit,'status':q.status,'created':q.created_at} for q in qs])

@app.route('/api/health')
def health():
    return jsonify({"status":"LIVE","version":"v4.4 Clean Masters - Short Headings","features":["Empty masters - No seeded data","Create/Edit/Delete Products Vendors Customers Kilns Pack","Short headings: Dash Stock Make Buy Sell","Loose+Jumbo+40kg combined","MO with Ratio 0.154-0.166 Wastage <5%","Odoo-like"],"url":"https://lemon-erp.onrender.com"})

@app.route('/mobile')
def mobile():
    return "<html><body><h2>v4.4 Mobile</h2><p>Clean Masters - Create Kilns & Products first on desktop then use mobile</p><a href='/'>Back</a></body></html>"

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
