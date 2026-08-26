"""
🍋 LEMON ERP v4.4.3 - Base v4.4 + Products ONLY Refined - Ignore previous
Base: v4.4 Clean Masters - Everything unchanged except Products tab
Products Refinement:
- Landing Heading Products centrally aligned
- Add New Product Button below heading
- Popup: Product Name (Mandatory), Product Category dropdown from product_category DB (Mandatory), HSN Code (Mandatory), Product Description (Mandatory), Auto generate Product code when saved, Save button
- List category-wise with product code, hsn code, product name & shows narration when roll mouse over name, edit/delete
- DB File: lemon_erp_v44_1_category.db - Table: product_category - Fields: id PK, category_name Unique 1 input, created_at timestamp - for further use
Keep everything else unchanged as per v4.4 base
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode, base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'lemon-erp-v44-3-products-hsn-desc-code-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v44_1_category.db'  # As requested: lemon_erp_v44_1_category.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELS - v4.4 Base + Product Category DB file + Products refined fields
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)  # PK
    category_name = db.Column(db.String(100), unique=True)  # Unique, 1 input field
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # timestamp

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
    name = db.Column(db.String(100))  # Product Name Mandatory
    category = db.Column(db.String(100))  # Product Category dropdown from DB Mandatory
    product_code = db.Column(db.String(50), unique=True)  # Auto generate Product code when saved
    hsn_code = db.Column(db.String(20))  # HSN Code Mandatory
    description = db.Column(db.Text)  # Product Description Mandatory - Narration on hover
    # Keep v4.4 base stock fields for unchanged logic
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

def generate_product_code(category_name, count):
    """Auto generate Product code when product is saved"""
    # Take first 3 letters of category + 3 letters of product? Simple: CAT + count
    cat_code = ''.join([c for c in category_name if c.isalnum()])[:4].upper() if category_name else 'PROD'
    if len(cat_code) < 3:
        cat_code = (cat_code + 'X'*3)[:3]
    # Format: CAT-0001, e.g., RAW-0001, FIN-0001, LIME-0001
    return f"{cat_code[:4]}-{count:04d}"

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html><head><title>Lemon ERP v4.4.3 - Products Refined - HSN + Desc + Code</title>
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
.btn{padding:7px 12px;border-radius:7px;border:none;cursor:pointer;font-weight:700;font-size:11px;transition:0.15s}
.btn-g{background:var(--green);color:white} .btn-y{background:var(--lemon);color:var(--green)} .btn-w{background:white;color:var(--green);border:1px solid var(--line)} .btn-r{background:#C5221F;color:white}
.badge{padding:3px 8px;border-radius:12px;font-size:10px;font-weight:800}
.ok{background:#E6F4EA;color:#1E7D32} .warn{background:#FEF3CD;color:#9C6F00} .crit{background:#FCE8E6;color:#C5221F}
table{width:100%;border-collapse:collapse;font-size:12px} th{background:#F8F6F3;padding:8px 6px;text-align:left;font-weight:700;border-bottom:2px solid var(--line)} td{padding:7px 6px;border-bottom:1px solid #F0EBE2}
input,select,textarea{padding:8px 10px;border-radius:7px;border:1.5px solid var(--line);width:100%;font-size:12px;margin:4px 0;transition:0.15s}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--brass);box-shadow:0 0 0 3px rgba(201,168,106,0.15)}
textarea{resize:vertical;min-height:60px}
.row{display:flex;gap:8px;flex-wrap:wrap}.row>*{flex:1;min-width:140px}
.hidden{display:none !important}
.form-box{background:var(--alab);padding:12px;border-radius:8px;border:1px dashed var(--brass);margin-bottom:10px}
.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(26,46,30,0.65);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(4px)}
.modal-content{background:white;border-radius:14px;width:100%;max-width:620px;max-height:92vh;display:flex;flex-direction:column;box-shadow:0 24px 64px rgba(0,0,0,0.35);border:1px solid var(--brass);animation:slideUp 0.25s ease}
@keyframes slideUp{from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1}}
.modal-header{padding:16px 20px;border-bottom:2px solid var(--line);display:flex;justify-content:space-between;align-items:center;background:var(--alab);border-radius:14px 14px 0 0}
.modal-header h3{margin:0;font-size:15px;font-weight:900}
.modal-body{padding:16px 20px;overflow-y:auto;flex:1}
.modal-footer{padding:14px 20px;border-top:2px solid var(--line);background:var(--alab);border-radius:0 0 14px 14px;display:flex;gap:10px}
.close-btn{background:white;border:1.5px solid var(--line);border-radius:8px;padding:8px 14px;cursor:pointer;font-weight:700;font-size:12px}
.close-btn:hover{background:var(--alab)}
.cat-group{border:1.5px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden}
.cat-header{background:var(--green);color:var(--brass);padding:10px 14px;font-weight:800;font-size:12px;display:flex;justify-content:space-between}
.tooltip{position:relative;cursor:pointer;border-bottom:1px dashed var(--brass)}
.tooltip .tooltiptext{visibility:hidden;width:260px;background:var(--green);color:white;text-align:left;border-radius:8px;padding:10px;position:absolute;z-index:1;bottom:125%;left:50%;margin-left:-130px;opacity:0;transition:opacity 0.2s;font-size:11px;line-height:1.4;box-shadow:0 8px 20px rgba(0,0,0,0.3)}
.tooltip:hover .tooltiptext{visibility:visible;opacity:1}
</style></head><body>
<div class="topnav"><div class="brand">🍋 Lemon ERP <span class="l">v4.4.3 Products Refined</span> <span style="font-size:10px;background:var(--brass);color:var(--green);padding:2px 6px;border-radius:10px;margin-left:6px">v4.4 Base + Products Only - HSN + Desc + Auto Code</span></div><div><button class="btn btn-y" onclick="location.reload()">Reload</button></div></div>
<div class="layout">
<div class="sidebar">
<h4>Main</h4>
<div class="menu active" onclick="openTab('dash')"><i class="bi bi-speedometer2"></i> Dash</div>
<div class="menu" onclick="openTab('stock')"><i class="bi bi-box-seam"></i> Stock</div>
<div class="menu" onclick="openTab('make')"><i class="bi bi-gear"></i> Make</div>
<div class="menu" onclick="openTab('buy')"><i class="bi bi-cart"></i> Buy</div>
<div class="menu" onclick="openTab('sell')"><i class="bi bi-truck"></i> Sell</div>
<h4>Masters - v4.4 Base</h4>
<div class="menu" onclick="openTab('product_categories')"><i class="bi bi-tags"></i> Product Category</div>
<div class="menu" onclick="openTab('products')" style="background:var(--alab);border:1.5px solid var(--brass)"><i class="bi bi-bag"></i> Products *Refined</div>
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
<!-- DASH - UNCHANGED v4.4 -->
<div id="dash" class="tabcontent">
<div class="card"><h3>Dash - v4.4 Base Unchanged + Products Refined Only - HSN + Description + Auto Code</h3>
<div class="kpi-grid">
<div class="card kpi"><div style="font-size:11px">Total Value</div><div class="val" id="totalVal">Rs 0 Lakh</div></div>
<div class="card kpi"><div style="font-size:11px">Production Today</div><div class="val" id="prodToday">0 MT</div></div>
<div class="card kpi"><div style="font-size:11px">Stock Alerts</div><div class="val" id="alertCnt">0</div></div>
<div class="card kpi"><div style="font-size:11px">Categories</div><div class="val" id="catCountDash">0</div><div style="font-size:10px">DB: lemon_erp_v44_1_category.db</div></div>
</div>
</div>
<div class="card"><h3>Quick Setup - v4.4 Base</h3><p style="font-size:11px">1. Product Category (DB: lemon_erp_v44_1_category.db) → 2. Products (Refined: Name, Category dropdown, HSN, Description, Auto Code) → 3. Kilns → 4. Vendors → 5. Customers</p></div>
<div class="card"><h3>Alerts</h3><div id="alerts">No products yet</div></div>
</div>

<!-- PRODUCT CATEGORY - DB file for further use - UNCHANGED -->
<div id="product_categories" class="tabcontent hidden">
<div class="card"><h3><i class="bi bi-tags"></i> Product Category Master - DB File for Further Use</h3>
<p style="font-size:11px;color:#666">Database file for same where input can be saved for further use:<br><b>DB File:</b> lemon_erp_v44_1_category.db (new)<br><b>Table:</b> product_category<br><b>Fields:</b> id (PK), category_name (Unique, 1 input field), created_at (timestamp)</p>
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">
<h3>Add Product Category - 1 Input Field + Save</h3>
<input type="hidden" id="cat_id">
<div class="row" style="align-items:end"><div style="flex:3"><label style="font-size:11px;font-weight:700">Category Name * (1 Input Field)</label><input id="cat_name" placeholder="Category Name e.g. Raw - Limestone, Finished - Quicklime 10-40mm"></div><div style="flex:1"><button class="btn btn-g" style="width:100%;padding:10px" onclick="saveCategory()">Save Category</button><button class="btn btn-w" style="width:100%;margin-top:4px" onclick="resetCatForm()">Reset</button></div></div>
</div>
<div class="card"><h3>List of Categories Added - Table: # | Category Name | Created At | Saved in DB File | Actions</h3><p style="font-size:10px;color:#666">Shows ID, timestamp, DB file name - lemon_erp_v44_1_category.db</p><div id="categoryList">No categories - Database empty</div></div>
</div>
</div>

<!-- PRODUCTS - REFINED ONLY - AS REQUESTED -->
<div id="products" class="tabcontent">
<!-- Landing Page Heading Products (centrally aligned) -->
<div class="card" style="text-align:center;padding:20px">
<h1 style="text-align:center;margin:0 0 14px;font-size:22px;font-weight:900;letter-spacing:0.5px"><i class="bi bi-bag"></i> Products</h1>
<p style="font-size:11px;color:#666;text-align:center;margin:0 0 16px">Landing Page Heading Products (centrally aligned) - Refined - Product Code Auto + HSN + Description + Category-wise List + Narration on hover</p>
<!-- add new product Button below heading -->
<button class="btn btn-y" style="padding:12px 28px;font-size:14px;font-weight:800" onclick="openAddProductPopup()"><i class="bi bi-plus-lg"></i> Add New Product</button>
<p style="font-size:10px;color:#888;margin-top:10px">When click Add button > Popup Add product form with Product Name (Mandatory), Category dropdown (Mandatory), HSN Code (Mandatory), Description (Mandatory), Auto Product Code, Save button</p>
</div>

<!-- List of Products category wise with product code, hsn code, product name & shows narration when roll mouse over name. edit, delete button -->
<div id="productListContainer">Loading Products category wise...</div>
</div>

<!-- STOCK - UNCHANGED v4.4 -->
<div id="stock" class="tabcontent hidden">
<div class="card"><h3>Stock - Loose+Jumbo+40kg Combined - v4.4 Base Unchanged</h3><div class="row"><select id="fUnit"><option value="All">All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="loadStock()">Filter</button></div></div>
<div class="card"><h3>Raw</h3><div id="rawTbl">No products</div></div>
<div class="card"><h3>WIP</h3><div id="wipTbl">No products</div></div>
<div class="card"><h3>Finished</h3><div id="finTbl">No products</div></div>
</div>

<!-- MAKE/BUY/SELL/KILNS/VENDORS/CUSTOMERS/PACK/QR/COST/MOBILE - UNCHANGED v4.4 -->
<div id="make" class="tabcontent hidden"><div class="card"><h3>Make - Manufacturing Orders - v4.4 Unchanged</h3><div class="form-box"><div class="row"><select id="make_wc"></select><select id="make_type"><option>Kiln</option><option>Sizing</option><option>Hydration</option></select><input id="make_unit" placeholder="Unit e.g. Unit 1 72MT" value="Unit 1 72MT"></div><div class="row"><input id="make_lime" type="number" placeholder="Limestone MT"><input id="make_pet" type="number" placeholder="Petcoke MT"><input id="make_out" type="number" placeholder="Output MT"></div><div class="row"><input id="make_waste" type="number" placeholder="Wastage MT"><input id="make_inProd" placeholder="Input Product"><input id="make_outProd" placeholder="Output Product"></div><div class="row"><input id="make_op" placeholder="Operator"><button class="btn btn-g" onclick="createMO()">Create MO</button></div></div><div id="moList">No MO</div></div></div>
<div id="buy" class="tabcontent hidden"><div class="card"><h3>Buy - PO + GRN - v4.4 Unchanged</h3><div class="form-box"><h3>New PO</h3><div class="row"><select id="po_vendor"></select><input id="po_mat" placeholder="Material"><input id="po_qty" type="number" placeholder="Qty"><input id="po_rate" type="number" placeholder="Rate"></div><div class="row"><select id="po_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="po_status"><option>Draft</option><option>Sent</option><option>Received</option></select><button class="btn btn-g" onclick="createPO()">Create PO</button></div></div><div class="form-box"><h3>New GRN</h3><div class="row"><input id="g_vehicle" placeholder="Vehicle No"><input id="g_material" placeholder="Material"><select id="g_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div><div class="row"><input id="g_gross" type="number" placeholder="Gross kg"><input id="g_tare" type="number" placeholder="Tare kg"><select id="g_vendor"></select><button class="btn btn-y" onclick="createGRN()">Save GRN</button></div></div><div class="card"><h3>PO List</h3><div id="poList">No PO</div></div><div class="card"><h3>GRN List</h3><div id="grnList">No GRN</div></div></div></div>
<div id="sell" class="tabcontent hidden"><div class="card"><h3>Sell - Dispatch - v4.4 Unchanged</h3><div class="form-box"><div class="row"><select id="d_customer"></select><input id="d_vehicle" placeholder="Vehicle No"><select id="d_product"></select><input id="d_qty" type="number" placeholder="Qty MT"></div><div class="row"><input id="d_qr" placeholder="QR Bags"><select id="d_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="createDispatch()">Create Dispatch</button></div></div><div class="card"><h3>Dispatch List</h3><div id="dispatchList">No Dispatch</div></div></div></div>
<div id="kilns" class="tabcontent hidden"><div class="card"><h3>Kilns - v4.4 Unchanged</h3><div class="form-box"><h3 id="kilnFormTitle">Add New Kiln</h3><input type="hidden" id="kiln_id"><div class="row"><input id="kiln_name" placeholder="Name e.g. Kiln 1"><select id="kiln_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="kiln_type"><option>Kiln</option><option>Sizing</option><option>Hydration</option><option>Packing</option></select></div><div class="row"><input id="kiln_cap" type="number" placeholder="Capacity MT/day"><select id="kiln_status"><option>Running</option><option>Idle</option><option>Maintenance</option></select><button class="btn btn-g" onclick="saveKiln()">Save Kiln</button><button class="btn btn-w" onclick="resetKilnForm()">Reset</button></div></div><div id="wcTbl">No kilns</div></div></div>
<div id="vendors" class="tabcontent hidden"><div class="card"><h3>Vendors - v4.4 Unchanged</h3><div class="form-box"><h3 id="vendFormTitle">Add New Vendor</h3><input type="hidden" id="vend_id"><div class="row"><input id="vend_name" placeholder="Name"><select id="vend_type"><option>Limestone</option><option>Petcoke</option><option>Packaging</option><option>Transport</option><option>Trading</option></select><input id="vend_gst" placeholder="GST No"></div><div class="row"><input id="vend_contact" placeholder="Contact"><input id="vend_credit" type="number" placeholder="Credit Limit"><input id="vend_due" type="number" placeholder="Pending Due"><button class="btn btn-g" onclick="saveVendor()">Save Vendor</button><button class="btn btn-w" onclick="resetVendForm()">Reset</button></div></div><div id="vendorTbl">No vendors</div></div></div>
<div id="customers" class="tabcontent hidden"><div class="card"><h3>Customers - v4.4 Unchanged</h3><div class="form-box"><h3 id="custFormTitle">Add New Customer</h3><input type="hidden" id="cust_id"><div class="row"><input id="cust_name" placeholder="Name"><select id="cust_type"><option>Cement</option><option>Steel</option><option>Chemical</option><option>Trader</option></select><input id="cust_gst" placeholder="GST No"></div><div class="row"><input id="cust_contact" placeholder="Contact"><input id="cust_recv" type="number" placeholder="Pending Receivable"><button class="btn btn-g" onclick="saveCustomer()">Save Customer</button><button class="btn btn-w" onclick="resetCustForm()">Reset</button></div></div><div id="customerTbl">No customers</div></div></div>
<div id="pack" class="tabcontent hidden"><div class="card"><h3>Pack - v4.4 Unchanged</h3><div class="form-box"><h3 id="packFormTitle">Add New Pack</h3><input type="hidden" id="pack_id"><div class="row"><input id="pack_type" placeholder="Bag Type"><select id="pack_cat"><option>40kg</option><option>Jumbo</option></select><input id="pack_cap" type="number" placeholder="Capacity MT"></div><div class="row"><input id="pack_closing" type="number" placeholder="Closing"><input id="pack_min" type="number" placeholder="Min"><input id="pack_rate" type="number" placeholder="Rate"><select id="pack_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div><div class="row"><button class="btn btn-g" onclick="savePack()">Save Pack</button><button class="btn btn-w" onclick="resetPackForm()">Reset</button></div></div><div id="packTbl">No packs</div></div></div>
<div id="qr" class="tabcontent hidden"><div class="card"><h3>QR - v4.4 Unchanged</h3><div class="form-box"><div class="row"><select id="qr_product"></select><input id="qr_weight" type="number" value="1.2"><select id="qr_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-y" onclick="genQR()">Generate QR</button></div><div style="text-align:center;background:var(--alab);padding:10px;border-radius:8px;margin-top:8px"><div id="qrResult"></div><div id="qrImg"></div></div></div><div class="card"><h3>QR List</h3><div id="qrList">No QR</div></div></div></div>
<div id="cost" class="tabcontent hidden"><div class="card"><h3>Cost - v4.4 Unchanged</h3><div id="costVal">Rs 0 Lakh</div><div id="costTbl">No data</div></div></div>
<div id="mobile" class="tabcontent hidden"><div class="card"><h3>Mobile - v4.4 Unchanged</h3><p style="font-size:11px">operator1/op123 U1 etc</p></div></div>
</div>
</div>

<!-- PRODUCTS POPUP - REFINED AS REQUESTED -->
<div id="productModal" class="modal hidden" onclick="if(event.target===this) closeProductPopup()">
<div class="modal-content">
<div class="modal-header"><h3><i class="bi bi-bag-plus"></i> Add Product - HSN + Description + Auto Code</h3><button class="close-btn" onclick="closeProductPopup()"><i class="bi bi-x-lg"></i> Close</button></div>
<div class="modal-body">
<input type="hidden" id="prod_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">
<h3>Product Details - Mandatory Fields *</h3>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Name * (Mandatory)</label><input id="prod_name" placeholder="Product Name e.g. CaO 10-40mm, Limestone, Hydrated 90% - Mandatory"></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Category - Dropdown from product_category DB * (Mandatory)</label><select id="prod_cat" style="padding:10px;font-weight:600"><option value="">Select Category from product_category database - Mandatory</option></select><p style="font-size:9px;color:#666;margin:2px 0">DB File: lemon_erp_v44_1_category.db - Table: product_category - Fields: id PK, category_name Unique 1 input, created_at timestamp - Dropdown for further use</p></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">HSN Code * (Mandatory)</label><input id="prod_hsn" placeholder="HSN Code e.g. 2522, 25222000, 2517 - Mandatory for GST"></div><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Code (Auto Generate when saved)</label><input id="prod_code_preview" placeholder="Auto generate Product code when product is saved - e.g. RAW-0001, FIN-0002" disabled style="background:var(--alab);font-weight:800;color:var(--green)"></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Description * (Mandatory) - Narration on hover</label><textarea id="prod_desc" placeholder="Product Description e.g. High purity quicklime 10-40mm size for steel industry, CaO 90% min, low silica - Mandatory - Shows narration when roll mouse over name in list"></textarea></div></div>
<p style="font-size:10px;color:#666">Auto generate Product code when product is saved - Format: Category Code + Sequence e.g. RAW-0001, FIN-0002, LIME-0003 - Generated on save</p>
</div>
</div>
<div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:13px;font-size:13px" onclick="saveProduct()"><i class="bi bi-check-lg"></i> Save Product - Auto Code Generate</button><button class="btn btn-w" style="padding:13px" onclick="closeProductPopup()">Cancel</button></div>
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
 if(id==='product_categories') loadCategories();
}

// CATEGORIES - DB File for further use
async function loadCategories(){
 let res=await fetch('/api/product_categories'); let cats=await res.json();
 document.getElementById('catCountDash') && (document.getElementById('catCountDash').innerText=cats.length);
 if(cats.length===0){
   document.getElementById('categoryList').innerHTML='<div style="text-align:center;padding:20px"><p>No categories - Add new - DB File: lemon_erp_v44_1_category.db - Table: product_category - Fields: id PK, category_name Unique 1 input, created_at timestamp - Database empty - For further use</p><p style="font-size:10px">Table: # | Category Name | Created At | Saved in DB File | Actions - Shows ID, timestamp, DB file name</p></div>';
 } else {
   let h='<table><tr><th>#</th><th>Category Name</th><th>Created At</th><th>Saved in DB File</th><th>Actions</th></tr>';
   cats.forEach((c,i)=>{ h+=`<tr><td>${i+1}</td><td><b>${c.category_name}</b></td><td style="font-size:10px">${c.created_at}</td><td style="font-size:10px">DB: lemon_erp_v44_1_category.db<br>Table: product_category<br>Fields: id PK, category_name Unique, created_at timestamp<br>ID: ${c.id}</td><td><button class="btn btn-w" onclick="editCategory(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCategory(${c.id})">Del</button></td></tr>`; });
   h+='</table><p style="font-size:10px;color:#666">DB File: lemon_erp_v44_1_category.db - Table: product_category - Fields: id (PK), category_name (Unique, 1 input), created_at (timestamp) - For further use - Shows ID, timestamp, DB file name</p>';
   document.getElementById('categoryList').innerHTML=h;
 }
 // Update product category dropdown - Mandatory
 let opts='<option value="">Select Category from product_category database - Mandatory - Dropdown from DB</option>' + cats.map(c=>`<option value="${c.category_name}">${c.category_name}</option>`).join('');
 let prodCat=document.getElementById('prod_cat');
 if(prodCat) prodCat.innerHTML=opts;
}
async function saveCategory(){
 let name=document.getElementById('cat_name').value.trim();
 if(!name){alert('Enter Category Name - 1 Input Field - e.g. Raw - Limestone'); return;}
 let id=document.getElementById('cat_id').value;
 let payload={category_name:name};
 let url=id?'/api/product_categories/'+id:'/api/product_categories';
 let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 if(res.status===400){ let err=await res.json(); alert(err.error); return; }
 alert(id?'✅ Category Updated: '+name+' - DB: lemon_erp_v44_1_category.db':'✅ Category Created: '+name+' - Saved in DB File lemon_erp_v44_1_category.db - Table product_category - For further use');
 resetCatForm(); loadCategories();
}
async function editCategory(id){ let res=await fetch('/api/product_categories/'+id); let c=await res.json(); document.getElementById('cat_id').value=c.id; document.getElementById('cat_name').value=c.category_name; window.scrollTo(0,0); }
function resetCatForm(){ document.getElementById('cat_id').value=''; document.getElementById('cat_name').value=''; }
async function delCategory(id){ if(!confirm('Delete Category? From DB file lemon_erp_v44_1_category.db')) return; await fetch('/api/product_categories/'+id,{method:'DELETE'}); loadCategories(); }

// PRODUCTS REFINED - Central heading + Button below + Popup with Mandatory fields + Auto Code + Category-wise list + Narration on hover
function openAddProductPopup(){
 document.getElementById('productModal').classList.remove('hidden');
 document.getElementById('prod_id').value='';
 document.getElementById('prod_name').value='';
 document.getElementById('prod_hsn').value='';
 document.getElementById('prod_desc').value='';
 document.getElementById('prod_code_preview').value='Auto generate Product code when product is saved - e.g. RAW-0001';
 loadCategories();
 document.body.style.overflow='hidden';
}
function closeProductPopup(){ document.getElementById('productModal').classList.add('hidden'); document.body.style.overflow=''; }

async function loadProducts(){
 let res=await fetch('/api/products'); let products=await res.json();
 let container=document.getElementById('productListContainer');
 if(products.length===0){
   container.innerHTML='<div class="card" style="text-align:center;padding:30px"><p>No products - Masters empty as per v4.4 base</p><p style="font-size:11px;color:#666">Landing Page Heading Products centrally aligned + Add New Product Button below heading + Popup with Product Name (Mandatory), Category dropdown (Mandatory), HSN Code (Mandatory), Description (Mandatory), Auto Product Code</p><button class="btn btn-y" onclick="openAddProductPopup()"><i class="bi bi-plus-lg"></i> Add First Product</button></div>';
   return;
 }
 // Group category wise
 let grouped={};
 products.forEach(p=>{
   let cat=p.category||'Uncategorized';
   if(!grouped[cat]) grouped[cat]=[];
   grouped[cat].push(p);
 });
 let html='';
 for(let cat in grouped){
   html+=`<div class="cat-group"><div class="cat-header"><span><i class="bi bi-tags"></i> ${cat} - ${grouped[cat].length} Products</span><span style="font-size:10px">Category-wise List</span></div><div style="padding:8px"><table><tr><th>Product Code (Auto)</th><th>HSN Code</th><th>Product Name - Hover for Narration</th><th>Description Preview</th><th>Actions</th></tr>`;
   grouped[cat].forEach(p=>{
     let safeDesc=(p.description||'').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
     html+=`<tr>
<td><b style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line)">${p.product_code||'-'}</b></td>
<td><span class="badge ok">${p.hsn_code||'-'}</span></td>
<td><span class="tooltip"><b>${p.name}</b><span class="tooltiptext"><b>${p.name}</b><br><b>Code:</b> ${p.product_code}<br><b>HSN:</b> ${p.hsn_code}<br><b>Category:</b> ${p.category}<br><br><b>Narration/Description:</b><br>${p.description||'No description'}<br><br><i>Shows narration when roll mouse over name</i></span></span></td>
<td style="font-size:10px;max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="${safeDesc}">${p.description||'-'}</td>
<td><button class="btn btn-w" onclick="editProduct(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProduct(${p.id})">Del</button></td>
</tr>`;
   });
   html+='</table></div></div>';
 }
 html+=`<p style="font-size:10px;color:#666;margin-top:8px">List of Products category wise with product code, hsn code, product name & shows narration when roll mouse over name. edit, delete button - Category-wise grouped - Auto Product Code generated</p>`;
 container.innerHTML=html;
}

async function saveProduct(){
 let name=document.getElementById('prod_name').value.trim();
 let category=document.getElementById('prod_cat').value;
 let hsn=document.getElementById('prod_hsn').value.trim();
 let desc=document.getElementById('prod_desc').value.trim();
 if(!name){alert('Product Name is Mandatory *'); return;}
 if(!category){alert('Product Category is Mandatory * - Dropdown from product_category database'); return;}
 if(!hsn){alert('HSN Code is Mandatory *'); return;}
 if(!desc){alert('Product Description is Mandatory * - Narration'); return;}
 let id=document.getElementById('prod_id').value;
 let payload={name:name, category:category, hsn_code:hsn, description:desc};
 let url=id?'/api/products/'+id:'/api/products';
 let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 if(!res.ok){ let err=await res.json(); alert(err.error||'Error'); return; }
 let d=await res.json();
 alert((id?'✅ Product Updated: ':'✅ Product Created: ')+d.name+' - Product Code: '+d.product_code+' - Auto generate Product code when product is saved - HSN: '+d.hsn_code+' - Category: '+category);
 closeProductPopup(); loadProducts(); loadStock(); loadDash();
}
async function editProduct(id){
 let res=await fetch('/api/products/'+id); let p=await res.json();
 openAddProductPopup();
 document.getElementById('prod_id').value=p.id;
 document.getElementById('prod_name').value=p.name;
 setTimeout(()=>{ document.getElementById('prod_cat').value=p.category; },300);
 document.getElementById('prod_hsn').value=p.hsn_code;
 document.getElementById('prod_desc').value=p.description;
 document.getElementById('prod_code_preview').value=p.product_code+' (Auto generated code - will keep on edit)';
}
async function delProduct(id){ if(!confirm('Delete Product? Product Code will be freed')) return; await fetch('/api/products/'+id,{method:'DELETE'}); loadProducts(); }

// UNCHANGED v4.4 FUNCTIONS - STOCK, DASH, KILNS, VENDORS, CUSTOMERS, PACK, MAKE, BUY, SELL, QR, COST
async function loadStock(){
 let res=await fetch('/api/inventory/combined'); let data=await res.json();
 let fUnit=document.getElementById('fUnit').value;
 function filt(list){ if(fUnit==='All') return list; return list.filter(x=> (x.location||'').includes(fUnit.split(' ')[1])); }
 let raw=filt(data.raw||[]); let wip=filt(data.wip||[]); let fin=filt(data.finished||[]);
 document.getElementById('rawTbl').innerHTML=raw.length?'<table><tr><th>Product</th><th>Location</th><th>Loose</th><th>Total</th><th>Status</th></tr>'+raw.map(r=>`<tr><td>${r.product}</td><td style="font-size:10px">${r.location}</td><td>${r.loose_stock_mt} MT</td><td><b>${r.total_mt} MT</b></td><td><span class="badge ${r.status==='Critical'?'crit':(r.status==='Reorder'?'warn':'ok')}">${r.status}</span></td></tr>`).join('')+'</table>':'No Raw';
 document.getElementById('wipTbl').innerHTML=wip.length?'<table><tr><th>Product</th><th>Location</th><th>Loose</th><th>Total</th></tr>'+wip.map(r=>`<tr><td>${r.product}</td><td>${r.location}</td><td>${r.loose_stock_mt} MT</td><td>${r.total_mt} MT</td></tr>`).join('')+'</table>':'No WIP';
 document.getElementById('finTbl').innerHTML=fin.length?'<table><tr><th>Product</th><th>Location</th><th>Code</th><th>HSN</th><th>Total</th></tr>'+fin.map(r=>`<tr><td><b>${r.product}</b></td><td style="font-size:10px">${r.location}</td><td style="font-size:10px">${r.product_code||'-'}</td><td>${r.hsn_code||'-'}</td><td><b>${r.total_mt} MT</b></td></tr>`).join('')+'</table>':'No Finished';
}
async function loadDash(){
 let res=await fetch('/api/inventory/combined'); let data=await res.json();
 document.getElementById('totalVal').innerText='Rs '+(data.total_value_lakh||0).toFixed(1)+' Lakh';
 document.getElementById('alertCnt').innerText=(data.alerts||[]).length;
 let prodRes=await fetch('/api/mo/total'); let prodData=await prodRes.json(); document.getElementById('prodToday').innerText=(prodData.total||0)+' MT';
 let h=''; if((data.alerts||[]).length===0) h='No alerts'; else { h='<table><tr><th>Product</th><th>Total</th><th>Status</th></tr>'; data.alerts.slice(0,5).forEach(a=>{ let b=a.status==='Critical'?'crit':'warn'; h+=`<tr><td>${a.product}</td><td>${a.total_mt} MT</td><td><span class="badge ${b}">${a.status}</span></td></tr>`; }); h+='</table>'; }
 document.getElementById('alerts').innerHTML=h;
 let catRes=await fetch('/api/product_categories'); let cats=await catRes.json(); document.getElementById('catCountDash') && (document.getElementById('catCountDash').innerText=cats.length);
}
async function loadKilns(){
 let res=await fetch('/api/workcenters'); let wcs=await res.json();
 if(wcs.length===0){ document.getElementById('wcTbl').innerHTML='No kilns - Masters empty - v4.4 base unchanged'; document.getElementById('make_wc').innerHTML=''; return; }
 let h='<table><tr><th>Name</th><th>Unit</th><th>Type</th><th>Cap</th><th>Status</th><th>Actions</th></tr>';
 wcs.forEach(w=>{ h+=`<tr><td><b>${w.name}</b></td><td>${w.unit}</td><td>${w.wc_type}</td><td>${w.capacity}</td><td><span class="badge ${w.status==='Running'?'ok':'warn'}">${w.status}</span></td><td><button class="btn btn-w" onclick="editKiln(${w.id})">Edit</button> <button class="btn btn-r" onclick="delKiln(${w.id})">Del</button></td></tr>`; });
 h+='</table>'; document.getElementById('wcTbl').innerHTML=h;
 let opts=wcs.map(w=>`<option value="${w.id}">${w.name} - ${w.unit}</option>`).join('');
 let el=document.getElementById('make_wc'); if(el) el.innerHTML=opts;
}
async function saveKiln(){
 let id=document.getElementById('kiln_id').value;
 let payload={name:document.getElementById('kiln_name').value, unit:document.getElementById('kiln_unit').value, wc_type:document.getElementById('kiln_type').value, capacity_mt_per_day:parseFloat(document.getElementById('kiln_cap').value||0), status:document.getElementById('kiln_status').value};
 if(!payload.name){alert('Enter Kiln Name'); return;}
 let url=id?'/api/workcenters/'+id:'/api/workcenters'; let method=id?'PUT':'POST';
 await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Kiln Updated':'✅ Kiln Created'); resetKilnForm(); loadKilns();
}
async function editKiln(id){ let res=await fetch('/api/workcenters/'+id); let w=await res.json(); document.getElementById('kiln_id').value=w.id; document.getElementById('kiln_name').value=w.name; document.getElementById('kiln_unit').value=w.unit; document.getElementById('kiln_type').value=w.wc_type; document.getElementById('kiln_cap').value=w.capacity; document.getElementById('kiln_status').value=w.status; }
function resetKilnForm(){ document.getElementById('kiln_id').value=''; ['kiln_name','kiln_cap'].forEach(id=>document.getElementById(id).value=''); }
async function delKiln(id){ if(!confirm('Delete Kiln?')) return; await fetch('/api/workcenters/'+id,{method:'DELETE'}); loadKilns(); }
async function loadWCOptions(){ let res=await fetch('/api/workcenters'); let wcs=await res.json(); let opts=wcs.map(w=>`<option value="${w.id}">${w.name} - ${w.unit}</option>`).join(''); let el=document.getElementById('make_wc'); if(el) el.innerHTML=opts; }
async function loadVendors(){ let res=await fetch('/api/vendors'); let vs=await res.json(); if(vs.length===0){ document.getElementById('vendorTbl').innerHTML='No vendors - v4.4 base unchanged - Masters empty'; return; } let h='<table><tr><th>Name</th><th>Type</th><th>GST</th><th>Contact</th><th>Actions</th></tr>'; vs.forEach(v=>{ h+=`<tr><td><b>${v.name}</b></td><td>${v.vendor_type}</td><td>${v.gst||'-'}</td><td>${v.contact||'-'}</td><td><button class="btn btn-w" onclick="editVendor(${v.id})">Edit</button> <button class="btn btn-r" onclick="delVendor(${v.id})">Del</button></td></tr>`; }); h+='</table>'; document.getElementById('vendorTbl').innerHTML=h; let opts=vs.map(v=>`<option value="${v.id}">${v.name}</option>`).join(''); ['po_vendor','g_vendor'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function saveVendor(){ let id=document.getElementById('vend_id').value; let payload={name:document.getElementById('vend_name').value, vendor_type:document.getElementById('vend_type').value, gst:document.getElementById('vend_gst').value, contact:document.getElementById('vend_contact').value, credit_limit:parseFloat(document.getElementById('vend_credit').value||0), pending_due:parseFloat(document.getElementById('vend_due').value||0)}; if(!payload.name){alert('Enter Vendor Name'); return;} let url=id?'/api/vendors/'+id:'/api/vendors'; let method=id?'PUT':'POST'; await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Vendor Updated':'✅ Vendor Created'); resetVendForm(); loadVendors(); }
async function editVendor(id){ let res=await fetch('/api/vendors/'+id); let v=await res.json(); document.getElementById('vend_id').value=v.id; document.getElementById('vend_name').value=v.name; document.getElementById('vend_type').value=v.vendor_type; document.getElementById('vend_gst').value=v.gst; document.getElementById('vend_contact').value=v.contact; document.getElementById('vend_credit').value=v.credit_limit; document.getElementById('vend_due').value=v.pending_due; }
function resetVendForm(){ document.getElementById('vend_id').value=''; ['vend_name','vend_gst','vend_contact','vend_credit','vend_due'].forEach(id=>document.getElementById(id).value=''); }
async function delVendor(id){ if(!confirm('Delete Vendor?')) return; await fetch('/api/vendors/'+id,{method:'DELETE'}); loadVendors(); }
async function loadVendorsOpt(){ let res=await fetch('/api/vendors'); let vs=await res.json(); let opts=vs.map(v=>`<option value="${v.id}">${v.name}</option>`).join(''); ['po_vendor','g_vendor'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function loadCustomers(){ let res=await fetch('/api/customers'); let cs=await res.json(); if(cs.length===0){ document.getElementById('customerTbl').innerHTML='No customers - v4.4 base unchanged'; return; } let h='<table><tr><th>Name</th><th>Type</th><th>GST</th><th>Contact</th><th>Actions</th></tr>'; cs.forEach(c=>{ h+=`<tr><td><b>${c.name}</b></td><td>${c.customer_type}</td><td>${c.gst||'-'}</td><td>${c.contact||'-'}</td><td><button class="btn btn-w" onclick="editCustomer(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCustomer(${c.id})">Del</button></td></tr>`; }); h+='</table>'; document.getElementById('customerTbl').innerHTML=h; let opts=cs.map(c=>`<option value="${c.id}">${c.name}</option>`).join(''); let el=document.getElementById('d_customer'); if(el) el.innerHTML=opts; }
async function saveCustomer(){ let id=document.getElementById('cust_id').value; let payload={name:document.getElementById('cust_name').value, customer_type:document.getElementById('cust_type').value, gst:document.getElementById('cust_gst').value, contact:document.getElementById('cust_contact').value, pending_receivable:parseFloat(document.getElementById('cust_recv').value||0)}; if(!payload.name){alert('Enter Customer Name'); return;} let url=id?'/api/customers/'+id:'/api/customers'; let method=id?'PUT':'POST'; await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Customer Updated':'✅ Customer Created'); resetCustForm(); loadCustomers(); }
async function editCustomer(id){ let res=await fetch('/api/customers/'+id); let c=await res.json(); document.getElementById('cust_id').value=c.id; document.getElementById('cust_name').value=c.name; document.getElementById('cust_type').value=c.customer_type; document.getElementById('cust_gst').value=c.gst; document.getElementById('cust_contact').value=c.contact; document.getElementById('cust_recv').value=c.pending_receivable; }
function resetCustForm(){ document.getElementById('cust_id').value=''; ['cust_name','cust_gst','cust_contact','cust_recv'].forEach(id=>document.getElementById(id).value=''); }
async function delCustomer(id){ if(!confirm('Delete Customer?')) return; await fetch('/api/customers/'+id,{method:'DELETE'}); loadCustomers(); }
async function loadCustomersOpt(){ let res=await fetch('/api/customers'); let cs=await res.json(); let opts=cs.map(c=>`<option value="${c.id}">${c.name}</option>`).join(''); let el=document.getElementById('d_customer'); if(el) el.innerHTML=opts; }
async function loadPack(){ let res=await fetch('/api/packaging'); let ps=await res.json(); if(ps.length===0){ document.getElementById('packTbl').innerHTML='No packs - v4.4 base unchanged'; return; } let h='<table><tr><th>Bag Type</th><th>Cat</th><th>Cap</th><th>Closing</th><th>Min</th><th>Rate</th><th>Unit</th><th>Actions</th></tr>'; ps.forEach(p=>{ h+=`<tr><td><b>${p.bag_type}</b></td><td>${p.bag_category}</td><td>${p.capacity_mt}</td><td>${p.closing}</td><td>${p.min_stock}</td><td>Rs ${p.rate_per_bag}</td><td>${p.unit}</td><td><button class="btn btn-w" onclick="editPack(${p.id})">Edit</button> <button class="btn btn-r" onclick="delPack(${p.id})">Del</button></td></tr>`; }); h+='</table>'; document.getElementById('packTbl').innerHTML=h; }
async function savePack(){ let id=document.getElementById('pack_id').value; let payload={bag_type:document.getElementById('pack_type').value, bag_category:document.getElementById('pack_cat').value, capacity_mt:parseFloat(document.getElementById('pack_cap').value||0), closing:parseFloat(document.getElementById('pack_closing').value||0), min_stock:parseFloat(document.getElementById('pack_min').value||0), rate_per_bag:parseFloat(document.getElementById('pack_rate').value||0), unit:document.getElementById('pack_unit').value}; if(!payload.bag_type){alert('Enter Bag Type'); return;} let url=id?'/api/packaging/'+id:'/api/packaging'; let method=id?'PUT':'POST'; await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Pack Updated':'✅ Pack Created'); resetPackForm(); loadPack(); }
async function editPack(id){ let res=await fetch('/api/packaging/'+id); let p=await res.json(); document.getElementById('pack_id').value=p.id; document.getElementById('pack_type').value=p.bag_type; document.getElementById('pack_cat').value=p.bag_category; document.getElementById('pack_cap').value=p.capacity_mt; document.getElementById('pack_closing').value=p.closing; document.getElementById('pack_min').value=p.min_stock; document.getElementById('pack_rate').value=p.rate_per_bag; document.getElementById('pack_unit').value=p.unit; }
function resetPackForm(){ document.getElementById('pack_id').value=''; ['pack_type','pack_cap','pack_closing','pack_min','pack_rate'].forEach(id=>document.getElementById(id).value=''); }
async function delPack(id){ if(!confirm('Delete Pack?')) return; await fetch('/api/packaging/'+id,{method:'DELETE'}); loadPack(); }
async function loadMO(){ let res=await fetch('/api/manufacturing_orders'); let mos=await res.json(); if(mos.length===0){ document.getElementById('moList').innerHTML='No MO - v4.4 unchanged'; return; } let h='<table><tr><th>MO No</th><th>Type</th><th>WC</th><th>Unit</th><th>Input→Output</th><th>Status</th></tr>'; mos.forEach(m=>{ h+=`<tr><td><b>${m.mo_no}</b></td><td>${m.mo_type}</td><td>${m.workcenter}</td><td>${m.unit}</td><td>${m.input_product} ${m.input_qty}→${m.output_product} ${m.output_qty} MT</td><td>${m.status}</td></tr>`; }); h+='</table>'; document.getElementById('moList').innerHTML=h; }
async function createMO(){ let wc=document.getElementById('make_wc').value; if(!wc){alert('Create Kilns first'); return;} let payload={workcenter_id:wc, unit:document.getElementById('make_unit').value, mo_type:document.getElementById('make_type').value, input_qty_mt:parseFloat(document.getElementById('make_lime').value||0), output_qty_mt:parseFloat(document.getElementById('make_out').value||0), wastage_mt:parseFloat(document.getElementById('make_waste').value||0), input_product:document.getElementById('make_inProd').value, output_product:document.getElementById('make_outProd').value, operator:document.getElementById('make_op').value||'operator1'}; let res=await fetch('/api/manufacturing_orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ MO '+d.mo_no); loadMO(); }
async function createPO(){ let qty=parseFloat(document.getElementById('po_qty').value||0); let rate=parseFloat(document.getElementById('po_rate').value||0); if(qty<=0||rate<=0){alert('Qty & Rate'); return;} let payload={vendor_id:document.getElementById('po_vendor').value, material:document.getElementById('po_mat').value, qty:qty, rate:rate, unit:document.getElementById('po_unit').value, status:document.getElementById('po_status').value, date:new Date().toISOString().slice(0,10)}; let res=await fetch('/api/po',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ PO '+d.po_no); loadPOList(); }
async function loadPOList(){ let res=await fetch('/api/po'); let pos=await res.json(); document.getElementById('poList').innerHTML=pos.length?'<table><tr><th>PO No</th><th>Material</th><th>Qty</th><th>Rate</th><th>Total</th><th>Unit</th><th>Status</th></tr>'+pos.map(p=>`<tr><td>${p.po_no}</td><td>${p.material}</td><td>${p.qty}</td><td>${p.rate}</td><td>${p.total}</td><td>${p.unit}</td><td>${p.status}</td></tr>`).join('')+'</table>':'No PO - v4.4 unchanged'; }
async function createGRN(){ let gross=parseFloat(document.getElementById('g_gross').value||0); let tare=parseFloat(document.getElementById('g_tare').value||0); if(gross<=0||tare<=0){alert('Gross/Tare'); return;} let net=(gross-tare)/1000; let payload={vehicle_no:document.getElementById('g_vehicle').value, material:document.getElementById('g_material').value, gross_wt:gross, tare_wt:tare, net_wt:net, unit:document.getElementById('g_unit').value, vendor_id:document.getElementById('g_vendor').value}; let res=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ GRN '+d.grn_no); loadGRNList(); loadStock(); }
async function loadGRNList(){ let res=await fetch('/api/grn'); let gs=await res.json(); document.getElementById('grnList').innerHTML=gs.length?'<table><tr><th>GRN No</th><th>Vehicle</th><th>Material</th><th>Net MT</th><th>Unit</th></tr>'+gs.map(g=>`<tr><td>${g.grn_no}</td><td>${g.vehicle_no}</td><td>${g.material}</td><td>${g.net_wt} MT</td><td>${g.unit}</td></tr>`).join('')+'</table>':'No GRN - v4.4 unchanged'; }
async function createDispatch(){ let qty=parseFloat(document.getElementById('d_qty').value||0); if(qty<=0){alert('Qty'); return;} let payload={customer_id:document.getElementById('d_customer').value, vehicle_no:document.getElementById('d_vehicle').value, product:document.getElementById('d_product').value, qty_mt:qty, unit:document.getElementById('d_unit').value, qr_bags:document.getElementById('d_qr').value, date:new Date().toISOString().slice(0,10)}; let res=await fetch('/api/dispatch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ Dispatch '+d.dispatch_no); loadDispatchList(); loadStock(); }
async function loadDispatchList(){ let res=await fetch('/api/dispatch'); let ds=await res.json(); document.getElementById('dispatchList').innerHTML=ds.length?'<table><tr><th>Disp No</th><th>Customer</th><th>Vehicle</th><th>Product</th><th>Qty</th><th>Unit</th></tr>'+ds.map(d=>`<tr><td>${d.dispatch_no}</td><td>${d.customer}</td><td>${d.vehicle_no}</td><td>${d.product}</td><td>${d.qty_mt} MT</td><td>${d.unit}</td></tr>`).join('')+'</table>':'No Dispatch - v4.4 unchanged'; }
async function loadProductsOpt(){ let res=await fetch('/api/products'); let ps=await res.json(); let opts=ps.map(p=>`<option value="${p.name}">${p.name} - ${p.product_code}</option>`).join(''); ['qr_product','d_product'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function genQR(){ let prod=document.getElementById('qr_product').value; if(!prod){alert('Create Products first'); return;} let wt=parseFloat(document.getElementById('qr_weight').value||1.2); let res=await fetch('/api/qr_generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product:prod, weight:wt, unit:document.getElementById('qr_unit').value})}); let d=await res.json(); document.getElementById('qrResult').innerHTML='<b>Bag ID: '+d.bag_id+'</b>'; document.getElementById('qrImg').innerHTML='<img src="data:image/png;base64,'+d.qr_base64+'" style="width:180px;border:6px solid #1A2E1E;border-radius:10px;margin-top:8px">'; loadQRList(); }
async function loadQRList(){ let res=await fetch('/api/qr_list'); let qs=await res.json(); document.getElementById('qrList').innerHTML=qs.length?'<table><tr><th>Bag ID</th><th>Product</th><th>Wt</th><th>Unit</th><th>Status</th></tr>'+qs.map(q=>`<tr><td><b>${q.bag_id}</b></td><td>${q.product}</td><td>${q.weight} MT</td><td>${q.unit}</td><td>${q.status}</td></tr>`).join('')+'</table>':'No QR - v4.4 unchanged'; }
async function loadCost(){ let res=await fetch('/api/inventory/combined'); let data=await res.json(); document.getElementById('costVal').innerText='Rs '+(data.total_value_lakh||0).toFixed(1)+' Lakh'; let all=[...(data.raw||[]),...(data.finished||[])]; document.getElementById('costTbl').innerHTML=all.length?'<table><tr><th>Product</th><th>Total MT</th><th>Value</th></tr>'+all.map(r=>`<tr><td>${r.product}</td><td>${r.total_mt} MT</td><td>Rs ${(r.value/1000).toFixed(1)}k</td></tr>`).join('')+'</table>':'No data'; }

loadDash(); loadCategories(); loadProducts();
</script>
</body></html>
    """

@app.route('/api/product_categories', methods=['GET','POST'])
def product_categories_api():
    if request.method=='POST':
        data=request.json
        cat_name=(data.get('category_name') or '').strip()
        if not cat_name:
            return jsonify({'error':'Category Name required - 1 input field'}), 400
        existing=ProductCategory.query.filter_by(category_name=cat_name).first()
        if existing:
            return jsonify({'error':'Category already exists: '+cat_name}), 400
        c=ProductCategory(category_name=cat_name)
        db.session.add(c)
        db.session.commit()
        return jsonify({'id':c.id,'category_name':c.category_name,'created_at':c.created_at})
    cats=ProductCategory.query.order_by(ProductCategory.id.desc()).all()
    return jsonify([{'id':c.id,'category_name':c.category_name,'created_at':c.created_at} for c in cats])

@app.route('/api/product_categories/<int:cid>', methods=['GET','PUT','DELETE'])
def product_category_one(cid):
    c=ProductCategory.query.get_or_404(cid)
    if request.method=='GET':
        return jsonify({'id':c.id,'category_name':c.category_name,'created_at':c.created_at})
    elif request.method=='PUT':
        data=request.json
        cat_name=(data.get('category_name') or '').strip()
        if not cat_name:
            return jsonify({'error':'Category Name required'}), 400
        c.category_name=cat_name
        db.session.commit()
        return jsonify({'id':c.id,'category_name':c.category_name})
    else:
        db.session.delete(c)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/inventory/combined')
def inv_combined():
    prods=Product.query.all()
    result={'raw':[],'wip':[],'finished':[],'alerts':[],'total_value_lakh':0}
    total_val=0
    for p in prods:
        total_mt=(p.loose_stock_mt or 0)+(p.jumbo_mt or 0)+(p.hdpe_40kg_mt or 0)
        rate=p.purchase_price or p.sale_price or 0
        value=total_mt*rate
        total_val+=value
        status='OK'
        if total_mt < p.min_stock: status='Critical'
        elif total_mt < p.reorder_level: status='Reorder'
        entry={'product':p.name,'location':p.location,'loose_stock_mt':p.loose_stock_mt,'total_mt':total_mt,'purchase_price':p.purchase_price,'sale_price':p.sale_price,'value':value,'status':status,'min':p.min_stock,'product_code':p.product_code,'hsn_code':p.hsn_code}
        if 'Raw' in (p.category or ''): result['raw'].append(entry)
        elif 'WIP' in (p.category or ''): result['wip'].append(entry)
        else: result['finished'].append(entry)
        if status!='OK': result['alerts'].append(entry)
    result['total_value_lakh']=total_val/100000
    return jsonify(result)

@app.route('/api/products', methods=['GET','POST'])
def products_api():
    if request.method=='POST':
        data=request.json
        # Validate Mandatory fields
        if not data.get('name') or not data.get('name').strip():
            return jsonify({'error':'Product Name is Mandatory *'}), 400
        if not data.get('category') or not data.get('category').strip():
            return jsonify({'error':'Product Category is Mandatory * - Dropdown from product_category database'}), 400
        if not data.get('hsn_code') or not data.get('hsn_code').strip():
            return jsonify({'error':'HSN Code is Mandatory *'}), 400
        if not data.get('description') or not data.get('description').strip():
            return jsonify({'error':'Product Description is Mandatory *'}), 400
        # Auto generate Product code when product is saved
        cnt=Product.query.count()+1
        prod_code=generate_product_code(data.get('category'), cnt)
        # Ensure unique
        while Product.query.filter_by(product_code=prod_code).first():
            cnt+=1
            prod_code=generate_product_code(data.get('category'), cnt)
        p=Product(name=data.get('name').strip(), category=data.get('category').strip(), product_code=prod_code, hsn_code=data.get('hsn_code').strip(), description=data.get('description').strip(), sale_price=0, purchase_price=0, loose_stock_mt=0, jumbo_mt=0, hdpe_40kg_mt=0, total_stock_mt=0, location='')
        db.session.add(p)
        db.session.commit()
        return jsonify({'id':p.id,'name':p.name,'product_code':p.product_code,'hsn_code':p.hsn_code,'category':p.category})
    prods=Product.query.order_by(Product.id.desc()).all()
    return jsonify([{'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description,'total_stock_mt':p.total_stock_mt} for p in prods])

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
def product_one(pid):
    p=Product.query.get_or_404(pid)
    if request.method=='GET':
        return jsonify({'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description})
    elif request.method=='PUT':
        data=request.json
        if not data.get('name') or not data.get('name').strip():
            return jsonify({'error':'Product Name Mandatory'}), 400
        if not data.get('category') or not data.get('category').strip():
            return jsonify({'error':'Product Category Mandatory'}), 400
        if not data.get('hsn_code') or not data.get('hsn_code').strip():
            return jsonify({'error':'HSN Code Mandatory'}), 400
        if not data.get('description') or not data.get('description').strip():
            return jsonify({'error':'Product Description Mandatory'}), 400
        p.name=data.get('name').strip()
        p.category=data.get('category').strip()
        p.hsn_code=data.get('hsn_code').strip()
        p.description=data.get('description').strip()
        # Keep product_code same on edit (auto generated only on create)
        db.session.commit()
        return jsonify({'id':p.id,'name':p.name,'product_code':p.product_code,'hsn_code':p.hsn_code})
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
        lime=float(data.get('input_qty_mt',0))
        pet=float(data.get('petcoke_mt',0))
        out=float(data.get('output_qty_mt',0))
        waste=float(data.get('wastage_mt',0))
        ratio=pet/lime if lime>0 else 0
        burn=((lime-out)/lime*100) if lime>0 and data.get('mo_type')=='Kiln' else 0
        waste_pct=(waste/(lime or 1)*100) if data.get('mo_type')=='Sizing' else 0
        mo=ManufacturingOrder(mo_no=mo_no, date=datetime.now().strftime('%Y-%m-%d'), workcenter_id=data.get('workcenter_id'), unit=data.get('unit'), mo_type=data.get('mo_type'), input_product=data.get('input_product'), input_qty_mt=float(data.get('input_qty_mt',0)), limestone_mt=lime, petcoke_mt=pet, petcoke_ratio=ratio, output_product=data.get('output_product'), output_qty_mt=out, wastage_mt=waste, wastage_pct=waste_pct, burning_loss_pct=burn, operator=data.get('operator','operator1'), status='Done')
        db.session.add(mo)
        db.session.commit()
        return jsonify({'mo_no':mo_no})
    mos=ManufacturingOrder.query.order_by(ManufacturingOrder.id.desc()).limit(50).all()
    wcs={w.id:w.name for w in WorkCenter.query.all()}
    return jsonify([{'mo_no':m.mo_no,'date':m.date,'unit':m.unit,'workcenter':wcs.get(m.workcenter_id,'-'),'mo_type':m.mo_type,'input_product':m.input_product,'input_qty':m.input_qty_mt,'output_product':m.output_product,'output_qty':m.output_qty_mt,'operator':m.operator,'status':m.status} for m in mos])

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
        net=float(data.get('net_wt',0))
        grn=GRN(grn_no=grn_no, date=datetime.now().strftime('%Y-%m-%d'), vehicle_no=data.get('vehicle_no',''), vendor_id=data.get('vendor_id'), material=data.get('material'), net_wt=net, unit=data.get('unit'))
        db.session.add(grn)
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
    return jsonify({"status":"LIVE","version":"v4.4.3 Products Refined - HSN + Description + Auto Code + Category-wise + Narration Hover","base":"v4.4 Base Unchanged except Products Only","refinement":"Products: Central heading Products, Add New Product Button below heading, Popup with Product Name Mandatory, Category dropdown from DB Mandatory, HSN Code Mandatory, Description Mandatory, Auto Product Code on save, List category wise with product code, hsn, name & narration on mouse over name, edit delete","db_file":"lemon_erp_v44_1_category.db - Table product_category Fields id PK, category_name Unique 1 input, created_at timestamp + product table with product_code, hsn_code, description","url":"https://lemon-erp.onrender.com"})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
