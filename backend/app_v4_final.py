"""
🍋 LEMON ERP v4.4.7 - Base v4.4.6 unchanged, only SBUs module changes
1. Kiln lining and health status is for kiln, not per product - put under kiln name asked once - when add product dont club lining and health
2. Fix edit bug - edit creates new SBU and erases name/address - fix + keep edit + provide duplicate of SBU option
3. Remove text line "Module name Kilns renamed to SBUs - Landing page heading Strategic Business Units" after Heading and line "b-Add New SBU Button Below Heading - Popup with X closing option on top right" after add button
4. Arrange data of SBUs in tabular format so as to look clean
Keep everything else unchanged in v4.4.6 - Products refined etc
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'lemon-erp-v44-7-sbus-clean-tabular-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v44_1_category.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    product_code = db.Column(db.String(50), unique=True)
    hsn_code = db.Column(db.String(20))
    description = db.Column(db.Text)
    loose_stock_mt = db.Column(db.Float, default=0)
    jumbo_mt = db.Column(db.Float, default=0)
    hdpe_40kg_mt = db.Column(db.Float, default=0)
    total_stock_mt = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    sale_price = db.Column(db.Float, default=0)
    purchase_price = db.Column(db.Float, default=0)
    location = db.Column(db.String(100))

class SBU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_name = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class KilnAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    kiln_no = db.Column(db.String(50))
    lining_installation_date = db.Column(db.String(20))
    health_status = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)

class SizingPlantAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    plant_no = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)
    machineries = db.Column(db.Text)

class HydrationPlantAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    plant_no = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)
    machineries = db.Column(db.Text)

class StockYardAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    yard_name = db.Column(db.String(100))
    yard_items = db.Column(db.Text)

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
    workcenter_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    unit = db.Column(db.String(100))
    mo_type = db.Column(db.String(50))
    input_product = db.Column(db.String(100))
    input_qty_mt = db.Column(db.Float, default=0)
    output_product = db.Column(db.String(100))
    output_qty_mt = db.Column(db.Float, default=0)
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
    cat_code = ''.join([c for c in category_name if c.isalnum()])[:4].upper() if category_name else 'PROD'
    if len(cat_code) < 3:
        cat_code = (cat_code + 'X'*3)[:3]
    return f"{cat_code[:4]}-{count:04d}"

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html><head><title>Lemon ERP v4.4.7 - SBUs Clean Tabular</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--line:#E8E0D5;--gray:#F6F5F3}
*{box-sizing:border-box} body{margin:0;font-family:Inter,Arial;background:var(--gray);color:var(--green);font-size:13px}
.topnav{background:var(--green);color:white;padding:0 14px;display:flex;justify-content:space-between;align-items:center;height:44px;position:sticky;top:0;z-index:200}
.topnav .brand{font-weight:900;font-size:15px} .topnav .brand span.l{color:var(--lemon)}
.layout{display:flex}
.sidebar{width:210px;background:white;border-right:1px solid var(--line);padding:10px 0;position:sticky;top:44px;height:calc(100vh - 44px);overflow-y:auto}
.sidebar h4{font-size:10px;color:#888;margin:14px 10px 4px;text-transform:uppercase;letter-spacing:0.6px}
.menu{padding:7px 10px;margin:2px 6px;border-radius:7px;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:12px;color:#444}
.menu:hover{background:var(--alab)} .menu.active{background:var(--green);color:var(--brass)}
.content{flex:1;padding:14px;max-width:1500px}
.card{background:white;border-radius:10px;padding:14px;margin:8px 0;box-shadow:0 2px 6px rgba(0,0,0,0.04);border:1px solid var(--line)}
.card h3{margin:0 0 10px;font-size:13px;font-weight:800}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.kpi{border-left:4px solid var(--brass);padding:12px}
.kpi .val{font-size:20px;font-weight:900}
.btn{padding:7px 12px;border-radius:7px;border:none;cursor:pointer;font-weight:700;font-size:11px}
.btn-g{background:var(--green);color:white} .btn-y{background:var(--lemon);color:var(--green)} .btn-w{background:white;color:var(--green);border:1px solid var(--line)} .btn-r{background:#C5221F;color:white} .btn-b{background:#E8F0FE;color:#1A2E1E;border:1px solid #C2D6FF} .btn-o{background:#FFF3E0;color:#8C4A00;border:1px solid #FFD8A8}
.badge{padding:3px 8px;border-radius:12px;font-size:10px;font-weight:800}
.ok{background:#E6F4EA;color:#1E7D32} .warn{background:#FEF3CD;color:#9C6F00} .crit{background:#FCE8E6;color:#C5221F} .brass{background:#FFFBEB;color:#8C6B2A;border:1px solid var(--brass)}
table{width:100%;border-collapse:collapse;font-size:12px} th{background:#F8F6F3;padding:8px 6px;text-align:left;font-weight:700;border-bottom:2px solid var(--line)} td{padding:7px 6px;border-bottom:1px solid #F0EBE2;vertical-align:top}
input,select,textarea{padding:8px 10px;border-radius:7px;border:1.5px solid var(--line);width:100%;font-size:12px;margin:4px 0}
.row{display:flex;gap:8px;flex-wrap:wrap}.row>*{flex:1;min-width:140px}
.hidden{display:none !important}
.form-box{background:var(--alab);padding:12px;border-radius:8px;border:1px dashed var(--brass);margin-bottom:10px}
.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(26,46,30,0.65);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(4px)}
.modal-content{background:white;border-radius:14px;width:100%;max-width:1000px;max-height:94vh;display:flex;flex-direction:column;box-shadow:0 24px 64px rgba(0,0,0,0.35);border:1px solid var(--brass);animation:slideUp 0.25s ease}
@keyframes slideUp{from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1}}
.modal-header{padding:16px 20px;border-bottom:2px solid var(--line);display:flex;justify-content:space-between;align-items:center;background:var(--alab);border-radius:14px 14px 0 0;position:sticky;top:0;z-index:2}
.modal-body{padding:16px 20px;overflow-y:auto;flex:1}
.modal-footer{padding:14px 20px;border-top:2px solid var(--line);background:var(--alab);border-radius:0 0 14px 14px;display:flex;gap:10px;position:sticky;bottom:0;z-index:2}
.close-x{background:white;border:1.5px solid var(--line);border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:900;font-size:18px}
.close-x:hover{background:#FCE8E6;color:#C5221F;border-color:#C5221F}
.asset-section{background:white;border:1.5px solid var(--line);border-radius:12px;padding:14px;margin:14px 0}
.kiln-line{background:#FFFBEB;border:1.5px solid var(--brass);border-radius:10px;padding:12px;margin:10px 0}
.product-line{background:white;border:1px dashed var(--brass);border-radius:8px;padding:10px;margin:8px 0;margin-left:12px;border-left:4px solid var(--brass)}
.tooltip{position:relative;cursor:pointer;border-bottom:1px dashed var(--brass)}
.tooltip .tooltiptext{visibility:hidden;width:260px;background:var(--green);color:white;text-align:left;border-radius:8px;padding:10px;position:absolute;z-index:10;bottom:125%;left:50%;margin-left:-130px;opacity:0;transition:opacity 0.2s;font-size:11px;line-height:1.4}
.tooltip:hover .tooltiptext{visibility:visible;opacity:1}
.sbu-card{border-left:5px solid var(--green);margin:14px 0}
.sbu-header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding:12px;background:var(--alab);border-radius:10px 10px 0 0;border-bottom:2px solid var(--line)}
.sbu-table{margin:0;border-radius:0 0 10px 10px;overflow:hidden}
.sbu-table th{background:var(--green);color:var(--brass);font-size:11px;padding:10px 8px}
.sbu-table td{font-size:11px;padding:8px}
.tabular-section{margin:12px 0;border:1.5px solid var(--line);border-radius:10px;overflow:hidden}
.tabular-header{background:var(--green);color:white;padding:10px 14px;font-weight:800;font-size:12px;display:flex;justify-content:space-between;align-items:center}
</style></head><body>
<div class="topnav"><div class="brand">🍋 Lemon ERP <span class="l">v4.4.7 Clean Tabular</span> <span style="font-size:10px;background:var(--brass);color:var(--green);padding:2px 6px;border-radius:10px;margin-left:6px">SBUs Fixed + Duplicate + Tabular</span></div><div><button class="btn btn-y" onclick="location.reload()">Reload</button></div></div>
<div class="layout">
<div class="sidebar">
<h4>Main</h4>
<div class="menu active" onclick="openTab('dash')"><i class="bi bi-speedometer2"></i> Dash</div>
<div class="menu" onclick="openTab('stock')"><i class="bi bi-box-seam"></i> Stock</div>
<div class="menu" onclick="openTab('make')"><i class="bi bi-gear"></i> Make</div>
<div class="menu" onclick="openTab('buy')"><i class="bi bi-cart"></i> Buy</div>
<div class="menu" onclick="openTab('sell')"><i class="bi bi-truck"></i> Sell</div>
<h4>Masters</h4>
<div class="menu" onclick="openTab('product_categories')"><i class="bi bi-tags"></i> Product Category</div>
<div class="menu" onclick="openTab('products')"><i class="bi bi-bag"></i> Products *Refined v4.4.3</div>
<div class="menu" onclick="openTab('sbus')" style="background:var(--alab);border:1.5px solid var(--brass)"><i class="bi bi-building"></i> SBUs *Clean Tabular</div>
<div class="menu" onclick="openTab('vendors')"><i class="bi bi-people"></i> Vendors</div>
<div class="menu" onclick="openTab('customers')"><i class="bi bi-person"></i> Customers</div>
<div class="menu" onclick="openTab('pack')"><i class="bi bi-box"></i> Pack</div>
<div class="menu" onclick="openTab('qr')"><i class="bi bi-qr-code"></i> QR</div>
<h4>Reports</h4>
<div class="menu" onclick="openTab('cost')"><i class="bi bi-calculator"></i> Cost</div>
<div class="menu" onclick="openTab('mobile')"><i class="bi bi-phone"></i> Mobile</div>
</div>

<div class="content">
<div id="dash" class="tabcontent">
<div class="card"><h3>Dash - v4.4.7 Clean Tabular - SBUs Fixed</h3>
<div class="kpi-grid">
<div class="card kpi"><div style="font-size:11px">Total Value</div><div class="val" id="totalVal">Rs 0 Lakh</div></div>
<div class="card kpi"><div style="font-size:11px">SBUs</div><div class="val" id="sbuCountDash">0</div></div>
<div class="card kpi"><div style="font-size:11px">Products</div><div class="val" id="prodCountDash">0</div></div>
<div class="card kpi"><div style="font-size:11px">Categories</div><div class="val" id="catCountDash">0</div></div>
</div>
</div>
<div class="card"><h3>v4.4.7 Changes - Only SBUs Module</h3><ul style="font-size:11px;margin:6px 0"><li>1. Kiln lining and health status moved under Kiln Name - asked once per kiln - not repeated for all products - Product add only Product name + Capacity/Day</li><li>2. Edit bug fixed - edit no longer creates new SBU and erases name/address - Edit keeps data - Duplicate option added</li><li>3. Removed text lines after heading and after Add New SBU button - Clean landing</li><li>4. Arrange data of SBUs in tabular format - clean tables</li></ul></div>
<div class="card"><h3>Alerts</h3><div id="alerts">No products yet</div></div>
</div>

<div id="product_categories" class="tabcontent hidden">
<div class="card"><h3><i class="bi bi-tags"></i> Product Category Master - DB File for Further Use - v4.4.3 Unchanged</h3>
<p style="font-size:11px">DB File: lemon_erp_v44_1_category.db - Table: product_category</p>
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">
<h3>Add Product Category - 1 Input Field</h3>
<input type="hidden" id="cat_id">
<div class="row" style="align-items:end"><div style="flex:3"><label style="font-size:11px;font-weight:700">Category Name *</label><input id="cat_name" placeholder="Category Name"></div><div style="flex:1"><button class="btn btn-g" style="width:100%;padding:10px" onclick="saveCategory()">Save Category</button><button class="btn btn-w" style="width:100%;margin-top:4px" onclick="resetCatForm()">Reset</button></div></div>
</div>
<div class="card"><h3>List of Categories Added</h3><div id="categoryList">No categories</div></div>
</div>
</div>

<div id="products" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:20px">
<h1 style="text-align:center;margin:0 0 14px;font-size:22px;font-weight:900"><i class="bi bi-bag"></i> Products</h1>
<p style="font-size:11px;color:#666">Landing Page Heading Products centrally aligned - HSN + Description + Auto Code + Category-wise + Hover narration - v4.4.3 Unchanged</p>
<button class="btn btn-y" style="padding:12px 28px;font-size:14px;font-weight:800" onclick="openAddProductPopup()"><i class="bi bi-plus-lg"></i> Add New Product</button>
</div>
<div id="productListContainer">Loading Products category wise...</div>
</div>

<div id="sbus" class="tabcontent">
<div class="card" style="text-align:center;padding:24px">
<!-- 3. Remove text line after Heading - Clean -->
<h1 style="text-align:center;margin:0 0 18px;font-size:26px;font-weight:900"><i class="bi bi-building"></i> Strategic Business Units</h1>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddSBU()"><i class="bi bi-plus-lg"></i> Add New SBU</button>
<!-- Removed line b-Add New SBU Button Below Heading - Popup with X -->
</div>
<div id="sbuList">Loading SBUs in tabular format...</div>
</div>

<div id="stock" class="tabcontent hidden"><div class="card"><h3>Stock - v4.4 Unchanged</h3><div class="row"><select id="fUnit"><option value="All">All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="loadStock()">Filter</button></div></div><div class="card"><h3>Raw</h3><div id="rawTbl">No products</div></div><div class="card"><h3>WIP</h3><div id="wipTbl">No products</div></div><div class="card"><h3>Finished</h3><div id="finTbl">No products</div></div></div>
<div id="make" class="tabcontent hidden"><div class="card"><h3>Make - v4.4 Unchanged</h3><div class="form-box"><div class="row"><select id="make_wc"></select><select id="make_type"><option>Kiln</option><option>Sizing</option><option>Hydration</option></select><input id="make_unit" placeholder="Unit" value="Unit 1 72MT"></div><div class="row"><input id="make_lime" type="number" placeholder="Limestone MT"><input id="make_pet" type="number" placeholder="Petcoke MT"><input id="make_out" type="number" placeholder="Output MT"></div><div class="row"><input id="make_waste" type="number" placeholder="Wastage"><input id="make_inProd" placeholder="Input Product"><input id="make_outProd" placeholder="Output Product"></div><div class="row"><input id="make_op" placeholder="Operator"><button class="btn btn-g" onclick="createMO()">Create MO</button></div></div><div id="moList">No MO</div></div></div>
<div id="buy" class="tabcontent hidden"><div class="card"><h3>Buy - v4.4 Unchanged</h3><div class="form-box"><h3>New PO</h3><div class="row"><select id="po_vendor"></select><input id="po_mat" placeholder="Material"><input id="po_qty" type="number" placeholder="Qty"><input id="po_rate" type="number" placeholder="Rate"></div><div class="row"><select id="po_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><select id="po_status"><option>Draft</option><option>Sent</option><option>Received</option></select><button class="btn btn-g" onclick="createPO()">Create PO</button></div></div><div class="form-box"><h3>New GRN</h3><div class="row"><input id="g_vehicle" placeholder="Vehicle No"><input id="g_material" placeholder="Material"><select id="g_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div><div class="row"><input id="g_gross" type="number" placeholder="Gross kg"><input id="g_tare" type="number" placeholder="Tare kg"><select id="g_vendor"></select><button class="btn btn-y" onclick="createGRN()">Save GRN</button></div></div><div class="card"><h3>PO List</h3><div id="poList">No PO</div></div><div class="card"><h3>GRN List</h3><div id="grnList">No GRN</div></div></div></div>
<div id="sell" class="tabcontent hidden"><div class="card"><h3>Sell - v4.4 Unchanged</h3><div class="form-box"><div class="row"><select id="d_customer"></select><input id="d_vehicle" placeholder="Vehicle No"><select id="d_product"></select><input id="d_qty" type="number" placeholder="Qty MT"></div><div class="row"><input id="d_qr" placeholder="QR Bags"><select id="d_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="createDispatch()">Create Dispatch</button></div></div><div class="card"><h3>Dispatch List</h3><div id="dispatchList">No Dispatch</div></div></div></div>
<div id="vendors" class="tabcontent hidden"><div class="card"><h3>Vendors - v4.4 Unchanged</h3><div class="form-box"><h3>Add New Vendor</h3><input type="hidden" id="vend_id"><div class="row"><input id="vend_name" placeholder="Name"><select id="vend_type"><option>Limestone</option><option>Petcoke</option><option>Packaging</option><option>Transport</option><option>Trading</option></select><input id="vend_gst" placeholder="GST No"></div><div class="row"><input id="vend_contact" placeholder="Contact"><input id="vend_credit" type="number" placeholder="Credit Limit"><input id="vend_due" type="number" placeholder="Pending Due"><button class="btn btn-g" onclick="saveVendor()">Save Vendor</button><button class="btn btn-w" onclick="resetVendForm()">Reset</button></div></div><div id="vendorTbl">No vendors</div></div></div>
<div id="customers" class="tabcontent hidden"><div class="card"><h3>Customers - v4.4 Unchanged</h3><div class="form-box"><h3>Add New Customer</h3><input type="hidden" id="cust_id"><div class="row"><input id="cust_name" placeholder="Name"><select id="cust_type"><option>Cement</option><option>Steel</option><option>Chemical</option><option>Trader</option></select><input id="cust_gst" placeholder="GST No"></div><div class="row"><input id="cust_contact" placeholder="Contact"><input id="cust_recv" type="number" placeholder="Pending Receivable"><button class="btn btn-g" onclick="saveCustomer()">Save Customer</button><button class="btn btn-w" onclick="resetCustForm()">Reset</button></div></div><div id="customerTbl">No customers</div></div></div>
<div id="pack" class="tabcontent hidden"><div class="card"><h3>Pack - v4.4 Unchanged</h3><div class="form-box"><h3>Add New Pack</h3><input type="hidden" id="pack_id"><div class="row"><input id="pack_type" placeholder="Bag Type"><select id="pack_cat"><option>40kg</option><option>Jumbo</option></select><input id="pack_cap" type="number" placeholder="Capacity MT"></div><div class="row"><input id="pack_closing" type="number" placeholder="Closing"><input id="pack_min" type="number" placeholder="Min"><input id="pack_rate" type="number" placeholder="Rate"><select id="pack_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select></div><div class="row"><button class="btn btn-g" onclick="savePack()">Save Pack</button><button class="btn btn-w" onclick="resetPackForm()">Reset</button></div></div><div id="packTbl">No packs</div></div></div>
<div id="qr" class="tabcontent hidden"><div class="card"><h3>QR - v4.4 Unchanged</h3><div class="form-box"><div class="row"><select id="qr_product"></select><input id="qr_weight" type="number" value="1.2"><select id="qr_unit"><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-y" onclick="genQR()">Generate QR</button></div><div style="text-align:center;background:var(--alab);padding:10px;border-radius:8px;margin-top:8px"><div id="qrResult"></div><div id="qrImg"></div></div></div><div class="card"><h3>QR List</h3><div id="qrList">No QR</div></div></div></div>
<div id="cost" class="tabcontent hidden"><div class="card"><h3>Cost - v4.4 Unchanged</h3><div id="costVal">Rs 0 Lakh</div><div id="costTbl">No data</div></div></div>
<div id="mobile" class="tabcontent hidden"><div class="card"><h3>Mobile - v4.4 Unchanged</h3></div></div>
</div>
</div>

<!-- PRODUCTS POPUP - v4.4.3 UNCHANGED -->
<div id="productModal" class="modal hidden" onclick="if(event.target===this) closeProductPopup()">
<div class="modal-content" style="max-width:620px">
<div class="modal-header"><h3><i class="bi bi-bag-plus"></i> Add Product - v4.4.3</h3><button class="close-x" onclick="closeProductPopup()">x</button></div>
<div class="modal-body">
<input type="hidden" id="prod_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">
<h3>Product Details - Mandatory *</h3>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Name *</label><input id="prod_name" placeholder="Product Name"></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Category *</label><select id="prod_cat"><option value="">Select Category</option></select></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">HSN Code *</label><input id="prod_hsn" placeholder="HSN Code"></div><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Code (Auto)</label><input id="prod_code_preview" placeholder="Auto generate" disabled style="background:var(--alab);font-weight:800"></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Product Description *</label><textarea id="prod_desc" placeholder="Description"></textarea></div></div>
</div>
</div>
<div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:13px" onclick="saveProduct()"><i class="bi bi-check-lg"></i> Save Product</button><button class="btn btn-w" style="padding:13px" onclick="closeProductPopup()">Cancel</button></div>
</div>
</div>

<!-- SBU POPUP - FIXED 1. Kiln lining/health under kiln name once + X + Delete buttons -->
<div id="sbuModal" class="modal hidden" onclick="if(event.target===this) closeAddSBU()">
<div class="modal-content">
<div class="modal-header"><h3 id="sbuModalTitle"><i class="bi bi-building-add"></i> Add SBU - Strategic Business Units</h3><button class="close-x" onclick="closeAddSBU()">x</button></div>
<div class="modal-body">
<input type="hidden" id="sbu_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><h3><i class="bi bi-info-circle"></i> SBU Details</h3>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">SBU Name - e.g. Unit 1 72MT, Jodhpur Plant *</label><input id="sbu_name" placeholder="SBU Name"></div></div>
<div class="row"><div style="flex:1"><label style="font-size:11px;font-weight:700">Address - Full address field</label><textarea id="sbu_address" placeholder="Full address field"></textarea></div></div>
</div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h4 style="margin:0">🔥 Kilns - 1. Fix: Lining & Health under Kiln Name asked once</h4><button class="btn btn-g" onclick="addKilnField()"><i class="bi bi-plus"></i> Add Kiln</button></div>
<div id="kilnsContainer"><p style="font-size:11px;color:#888;text-align:center;padding:12px">No kilns</p></div>
</div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h4 style="margin:0">⚙️ Sizing Plants</h4><button class="btn btn-g" onclick="addSizingField()"><i class="bi bi-plus"></i> Add Sizing Plant</button></div>
<div id="sizingContainer"><p style="font-size:11px;color:#888;text-align:center;padding:12px">No sizing plants</p></div>
</div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h4 style="margin:0">💧 Hydration Plants</h4><button class="btn btn-g" onclick="addHydrationField()"><i class="bi bi-plus"></i> Add Hydration Plant</button></div>
<div id="hydrationContainer"><p style="font-size:11px;color:#888;text-align:center;padding:8px">No hydration plants</p></div>
</div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h4 style="margin:0">📦 Stock Yards - All category products + Opening stock</h4><button class="btn btn-y" onclick="addYardField()"><i class="bi bi-plus"></i> Add Stock Yard</button></div>
<div id="yardsContainer"><p style="font-size:11px;color:#888;text-align:center;padding:8px">No stock yards</p></div>
</div>

</div>
<div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="saveSBU()"><i class="bi bi-check-lg"></i> Save SBU</button><button class="btn btn-w" style="padding:14px" onclick="closeAddSBU()">Cancel</button></div>
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
 if(id==='sbus') loadSBUs();
 if(id==='vendors') loadVendors();
 if(id==='customers') loadCustomers();
 if(id==='pack') loadPack();
 if(id==='qr'){loadProductsOpt(); loadQRList();}
 if(id==='cost') loadCost();
 if(id==='product_categories') loadCategories();
}

let kilnCounter=0, sizingCounter=0, hydCounter=0, yardCounter=0;

// CATEGORIES - v4.4.3 UNCHANGED
async function loadCategories(){
 let res=await fetch('/api/product_categories'); let cats=await res.json();
 document.getElementById('catCountDash') && (document.getElementById('catCountDash').innerText=cats.length);
 if(cats.length===0){
   document.getElementById('categoryList').innerHTML='<div style="text-align:center;padding:20px"><p>No categories</p></div>';
 } else {
   let h='<table><tr><th>#</th><th>Category Name</th><th>Created At</th><th>DB File</th><th>Actions</th></tr>';
   cats.forEach((c,i)=>{ h+=`<tr><td>${i+1}</td><td><b>${c.category_name}</b></td><td style="font-size:10px">${c.created_at}</td><td style="font-size:10px">lemon_erp_v44_1_category.db<br>ID:${c.id}</td><td><button class="btn btn-w" onclick="editCategory(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCategory(${c.id})">Del</button></td></tr>`; });
   h+='</table>'; document.getElementById('categoryList').innerHTML=h;
 }
 let opts='<option value="">Select Category</option>' + cats.map(c=>`<option value="${c.category_name}">${c.category_name}</option>`).join('');
 let prodCat=document.getElementById('prod_cat');
 if(prodCat) prodCat.innerHTML=opts;
}
async function saveCategory(){
 let name=document.getElementById('cat_name').value.trim();
 if(!name){alert('Enter Category Name'); return;}
 let id=document.getElementById('cat_id').value;
 let payload={category_name:name};
 let url=id?'/api/product_categories/'+id:'/api/product_categories';
 let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 if(res.status===400){ let err=await res.json(); alert(err.error); return; }
 alert(id?'✅ Category Updated':'✅ Category Created'); resetCatForm(); loadCategories();
}
async function editCategory(id){ let res=await fetch('/api/product_categories/'+id); let c=await res.json(); document.getElementById('cat_id').value=c.id; document.getElementById('cat_name').value=c.category_name; }
function resetCatForm(){ document.getElementById('cat_id').value=''; document.getElementById('cat_name').value=''; }
async function delCategory(id){ if(!confirm('Delete Category?')) return; await fetch('/api/product_categories/'+id,{method:'DELETE'}); loadCategories(); }

// PRODUCTS - v4.4.3
function openAddProductPopup(){
 document.getElementById('productModal').classList.remove('hidden');
 document.getElementById('prod_id').value='';
 document.getElementById('prod_name').value='';
 document.getElementById('prod_hsn').value='';
 document.getElementById('prod_desc').value='';
 document.getElementById('prod_code_preview').value='Auto generate Product code when product is saved';
 loadCategories();
 document.body.style.overflow='hidden';
}
function closeProductPopup(){ document.getElementById('productModal').classList.add('hidden'); document.body.style.overflow=''; }
async function loadProducts(){
 let res=await fetch('/api/products'); let products=await res.json();
 document.getElementById('prodCountDash') && (document.getElementById('prodCountDash').innerText=products.length);
 let container=document.getElementById('productListContainer');
 if(products.length===0){
   container.innerHTML='<div class="card" style="text-align:center;padding:30px"><p>No products</p><button class="btn btn-y" onclick="openAddProductPopup()"><i class="bi bi-plus-lg"></i> Add First Product</button></div>';
   return;
 }
 let grouped={};
 products.forEach(p=>{ let cat=p.category||'Uncategorized'; if(!grouped[cat]) grouped[cat]=[]; grouped[cat].push(p); });
 let html='';
 for(let cat in grouped){
   html+=`<div style="border:1.5px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden"><div style="background:var(--green);color:var(--brass);padding:10px 14px;font-weight:800;font-size:12px"><i class="bi bi-tags"></i> ${cat} - ${grouped[cat].length} Products</div><div style="padding:8px"><table><tr><th>Product Code</th><th>HSN</th><th>Product Name - Hover for Narration</th><th>Description</th><th>Actions</th></tr>`;
   grouped[cat].forEach(p=>{
     html+=`<tr><td><b style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line)">${p.product_code||'-'}</b></td><td><span class="badge ok">${p.hsn_code||'-'}</span></td><td><span class="tooltip"><b>${p.name}</b><span class="tooltiptext"><b>${p.name}</b><br>Code: ${p.product_code}<br>HSN: ${p.hsn_code}<br>Category: ${p.category}<br><br>Narration:<br>${p.description||''}</span></span></td><td style="font-size:10px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.description||'-'}</td><td><button class="btn btn-w" onclick="editProduct(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProduct(${p.id})">Del</button></td></tr>`;
   });
   html+='</table></div></div>';
 }
 container.innerHTML=html;
}
async function saveProduct(){
 let name=document.getElementById('prod_name').value.trim();
 let category=document.getElementById('prod_cat').value;
 let hsn=document.getElementById('prod_hsn').value.trim();
 let desc=document.getElementById('prod_desc').value.trim();
 if(!name){alert('Product Name Mandatory'); return;}
 if(!category){alert('Product Category Mandatory'); return;}
 if(!hsn){alert('HSN Code Mandatory'); return;}
 if(!desc){alert('Product Description Mandatory'); return;}
 let id=document.getElementById('prod_id').value;
 let payload={name:name, category:category, hsn_code:hsn, description:desc};
 let url=id?'/api/products/'+id:'/api/products';
 let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 if(!res.ok){ let err=await res.json(); alert(err.error); return; }
 let d=await res.json();
 alert((id?'✅ Updated: ':'✅ Created: ')+d.name+' - Code: '+d.product_code);
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
 document.getElementById('prod_code_preview').value=p.product_code;
}
async function delProduct(id){ if(!confirm('Delete Product?')) return; await fetch('/api/products/'+id,{method:'DELETE'}); loadProducts(); }

// SBUs - v4.4.7 FIXED - KILN LINING/HEALTH UNDER KILN NAME ONCE + EDIT BUG FIX + DUPLICATE + TABULAR
let editingSBUId = null; // FIX 2: track editing id properly

function openAddSBU(){
 // FIX: Reset for new SBU
 editingSBUId = null;
 document.getElementById('sbu_id').value='';
 document.getElementById('sbuModalTitle').innerHTML='<i class="bi bi-building-add"></i> Add SBU - Strategic Business Units';
 document.getElementById('sbuModal').classList.remove('hidden');
 document.getElementById('sbu_name').value='';
 document.getElementById('sbu_address').value='';
 document.getElementById('kilnsContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:12px">No kilns - Click Add Kiln</p>';
 document.getElementById('sizingContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:12px">No sizing plants</p>';
 document.getElementById('hydrationContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:8px">No hydration plants</p>';
 document.getElementById('yardsContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:8px">No stock yards</p>';
 kilnCounter=0; sizingCounter=0; hydCounter=0; yardCounter=0;
 loadAllProductsForSBU();
 document.body.style.overflow='hidden';
}
function closeAddSBU(){ document.getElementById('sbuModal').classList.add('hidden'); document.body.style.overflow=''; editingSBUId=null; }

async function loadAllProductsForSBU(){
 let res=await fetch('/api/products'); let ps=await res.json();
 window.allProducts=ps;
 window.finishedProducts=ps.filter(p=> (p.category||'').toLowerCase().includes('finish') || (p.category||'').toLowerCase().includes('quicklime') || (p.category||'').toLowerCase().includes('cao'));
 if(window.finishedProducts.length===0) window.finishedProducts=ps;
}

function getFinishedProductOptions(selectedId=null){
 let opts=(window.finishedProducts||[]).map(p=>`<option value="${p.id}" ${selectedId==p.id?'selected':''}>${p.name} (${p.product_code||''}) - ${p.category}</option>`).join('');
 if(opts==='') return '<option>No finished products - Create in Products</option>';
 return '<option value="">Select Product from Finished Product List</option>'+opts;
}
function getAllProductOptions(selectedId=null){
 let opts=(window.allProducts||[]).map(p=>`<option value="${p.id}" ${selectedId==p.id?'selected':''}>${p.name} (${p.product_code||''}) - ${p.category}</option>`).join('');
 if(opts==='') return '<option>No products</option>';
 return '<option value="">Dropdown selection field (all category)</option>'+opts;
}

// 1. FIX: Kiln lining and health status under kiln name asked once - not per product
function addKilnField(data=null){
 let container=document.getElementById('kilnsContainer');
 if(container.innerHTML.includes('No kilns')) container.innerHTML='';
 kilnCounter++;
 let id='kiln_'+kilnCounter+'_'+Date.now();
 // data.products_capacity is array of {product_id, capacity_per_day}
 // data now has kiln_no, lining_installation_date, health_status, products_capacity
 let html=`<div id="${id}" class="kiln-line">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><b>🔥 Kiln Line - *Kiln No. *Lining Date *Health Status (asked once per kiln) *Products and Capacity</b><div><button class="btn btn-b" onclick="addKilnProduct('${id}')"><i class="bi bi-plus"></i> Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete Kiln</button></div></div>
<!-- 1. Lining and Health under Kiln Name - asked once per kiln -->
<div class="row" style="margin-top:10px;background:white;padding:10px;border-radius:8px;border:1px solid var(--line)"><div style="flex:1"><label style="font-size:11px;font-weight:700">*Kiln No. - e.g. Kiln 1, K-01</label><input class="k_no" placeholder="Kiln No. e.g. Kiln 1, K-01" value="${data?data.kiln_no||'':''}"></div><div style="flex:1"><label style="font-size:11px;font-weight:700">Lining Installation Date - Date picker (for kiln - asked once)</label><input class="k_lining" type="date" value="${data?data.lining_installation_date||data.lining_date||''}"></div><div style="flex:1"><label style="font-size:11px;font-weight:700">Health Status - Good, Needs Repair, Critical, New (for kiln - asked once)</label><select class="k_health"><option ${data&&data.health_status==='Good'?'selected':''}>Good</option><option ${data&&data.health_status==='Needs Repair'?'selected':''}>Needs Repair</option><option ${data&&data.health_status==='Critical'?'selected':''}>Critical</option><option ${data&&data.health_status==='New'?'selected':''}>New</option></select></div></div>
<div style="margin-top:10px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b style="font-size:11px">*Products and Capacity - Add Product Button → Only Product name + Capacity/Day (Lining/Health NOT clubbed)</b><div class="kiln-products-container" style="margin-top:8px">${data && data.products_capacity ? data.products_capacity.map(pc=>renderKilnProductLine(pc)).join('') : '<p style="font-size:10px;color:#888">No products - Click Add Product → Only Product name (Finished List), Capacity/Day - Lining/Health separate above</p>'}</div></div>
</div>`;
 container.insertAdjacentHTML('beforeend', html);
}

function renderKilnProductLine(pc){
 let id='kprod_'+Date.now()+'_'+Math.random().toString(36).substr(2,5);
 // 1. FIX: Only Product name + Capacity/Day - dont club lining and health
 return `<div id="${id}" class="product-line"><div class="row" style="align-items:end"><div style="flex:2"><label style="font-size:10px;font-weight:700">Product name (selected from Finished Product List)</label><select class="kp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div style="flex:1"><label style="font-size:10px;font-weight:700">Capacity/Day - MT/day e.g. 15</label><input class="kp_capacity" type="number" placeholder="Capacity/Day" value="${pc.capacity_per_day||pc.capacity||''}"></div><div style="flex:0"><button class="btn btn-r" style="margin-top:18px" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete</button></div></div></div>`;
}

function addKilnProduct(kilnId){
 let kilnDiv=document.getElementById(kilnId);
 let container=kilnDiv.querySelector('.kiln-products-container');
 if(container.innerHTML.includes('No products')) container.innerHTML='';
 container.insertAdjacentHTML('beforeend', renderKilnProductLine({}));
}

function addSizingField(data=null){
 let container=document.getElementById('sizingContainer');
 if(container.innerHTML.includes('No sizing')) container.innerHTML='';
 sizingCounter++;
 let id='sizing_'+sizingCounter+'_'+Date.now();
 let html=`<div id="${id}" class="kiln-line" style="background:#F6FFF6;border-color:#C5E1C5">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><b>⚙️ Sizing Plant - Plant No.</b><div><button class="btn btn-b" onclick="addSizingProduct('${id}')"><i class="bi bi-plus"></i> Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete</button></div></div>
<div class="row" style="margin-top:8px"><div style="flex:1"><label style="font-size:10px;font-weight:700">*Plant No. - e.g. Sizing 1, SP-01</label><input class="s_no" placeholder="Plant No." value="${data?data.plant_no||'':''}"></div></div>
<div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><div class="sizing-products-container">${data && data.products_capacity ? data.products_capacity.map(pc=>renderSizingProductLine(pc)).join('') : '<p style="font-size:10px;color:#888">No products - Add Product → Product name, Capacity/hour, List of Machineries</p>'}</div></div>
<div class="row"><div style="flex:1"><label style="font-size:10px;font-weight:700">List of Machineries - Whole plant - e.g. Crusher, Vibrating Screen 10-40mm, Conveyor 20m, Dust Collector</label><textarea class="s_mach" placeholder="List of Machineries">${data?data.machineries||'':''}</textarea></div></div>
</div>`;
 container.insertAdjacentHTML('beforeend', html);
}

function renderSizingProductLine(pc){
 let id='sprod_'+Date.now()+'_'+Math.random().toString(36).substr(2,5);
 return `<div id="${id}" class="product-line" style="border-left-color:#1A2E1E"><div class="row" style="align-items:end"><div style="flex:2"><label style="font-size:10px;font-weight:700">Product name (Finished Product List)</label><select class="sp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div style="flex:1"><label style="font-size:10px;font-weight:700">Capacity/hour - MT/hour e.g. 5</label><input class="sp_capacity" type="number" placeholder="Capacity/hour" value="${pc.capacity_per_hour||pc.capacity||''}"></div><div style="flex:0"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete</button></div></div><div class="row"><div style="flex:1"><label style="font-size:10px;font-weight:700">List of Machineries - for this product line</label><textarea class="sp_mach_line" placeholder="Machineries for this product">${pc.machineries||''}</textarea></div></div></div>`;
}

function addSizingProduct(sizingId){
 let div=document.getElementById(sizingId);
 let container=div.querySelector('.sizing-products-container');
 if(container.innerHTML.includes('No products')) container.innerHTML='';
 container.insertAdjacentHTML('beforeend', renderSizingProductLine({}));
}

function addHydrationField(data=null){
 let container=document.getElementById('hydrationContainer');
 if(container.innerHTML.includes('No hydration')) container.innerHTML='';
 hydCounter++;
 let id='hyd_'+hydCounter+'_'+Date.now();
 let html=`<div id="${id}" class="kiln-line" style="background:#F0F8FF;border-color:#C2D6FF">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><b>💧 Hydration Plant - Plant No.</b><div><button class="btn btn-b" onclick="addHydrationProduct('${id}')"><i class="bi bi-plus"></i> Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete</button></div></div>
<div class="row" style="margin-top:8px"><div style="flex:1"><label style="font-size:10px;font-weight:700">*Plant No. - e.g. Hydration 1, HP-01</label><input class="h_no" placeholder="Plant No." value="${data?data.plant_no||'':''}"></div></div>
<div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><div class="hydration-products-container">${data && data.products_capacity ? data.products_capacity.map(pc=>renderHydrationProductLine(pc)).join('') : '<p style="font-size:10px;color:#888">No products</p>'}</div></div>
<div class="row"><div style="flex:1"><label style="font-size:10px;font-weight:700">List of machineries - Whole plant → Hydrator Reactor 5MT, Water Pump, Bagging Machine</label><textarea class="h_mach" placeholder="Machineries">${data?data.machineries||'':''}</textarea></div></div>
</div>`;
 container.insertAdjacentHTML('beforeend', html);
}

function renderHydrationProductLine(pc){
 let id='hprod_'+Date.now()+'_'+Math.random().toString(36).substr(2,5);
 return `<div id="${id}" class="product-line" style="border-left-color:#0A3D91"><div class="row" style="align-items:end"><div style="flex:2"><label style="font-size:10px;font-weight:700">Product name (Finished Product List)</label><select class="hp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div style="flex:1"><label style="font-size:10px;font-weight:700">Capacity/hour</label><input class="hp_capacity" type="number" placeholder="Capacity/hour" value="${pc.capacity_per_hour||pc.capacity||''}"></div><div style="flex:0"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete</button></div></div><div class="row"><div style="flex:1"><label style="font-size:10px;font-weight:700">List of machineries for this product line</label><textarea class="hp_mach_line" placeholder="Machineries">${pc.machineries||''}</textarea></div></div></div>`;
}

function addHydrationProduct(hydId){
 let div=document.getElementById(hydId);
 let container=div.querySelector('.hydration-products-container');
 if(container.innerHTML.includes('No products')) container.innerHTML='';
 container.insertAdjacentHTML('beforeend', renderHydrationProductLine({}));
}

function addYardField(data=null){
 let container=document.getElementById('yardsContainer');
 if(container.innerHTML.includes('No stock yards')) container.innerHTML='';
 yardCounter++;
 let id='yard_'+yardCounter+'_'+Date.now();
 let html=`<div id="${id}" class="kiln-line" style="background:#FFFBEB">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><b>📦 Stock Yard - Yard Name + Yard Items</b><div><button class="btn btn-b" onclick="addYardItem('${id}')"><i class="bi bi-plus"></i> Add Yard Items</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete Yard</button></div></div>
<div class="row" style="margin-top:8px"><div style="flex:1"><label style="font-size:10px;font-weight:700">*Yard Name - e.g. Limestone Yard 1, Finished Godown A</label><input class="y_name" placeholder="Yard Name" value="${data?data.yard_name||'':''}"></div></div>
<div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><div class="yard-items-container" style="margin-top:8px">${data && data.yard_items ? data.yard_items.map(yi=>renderYardItemLine(yi)).join('') : '<p style="font-size:10px;color:#888">No yard items - Add Yard Items → Product from all category + Opening stock</p>'}</div></div>
</div>`;
 container.insertAdjacentHTML('beforeend', html);
}

function renderYardItemLine(yi){
 let id='yitem_'+Date.now()+'_'+Math.random().toString(36).substr(2,5);
 return `<div id="${id}" class="product-line" style="border-left-color:var(--brass)"><div class="row" style="align-items:end"><div style="flex:2"><label style="font-size:10px;font-weight:700">Dropdown selection field (all category products)</label><select class="yi_product">${getAllProductOptions(yi.product_id)}</select></div><div style="flex:1"><label style="font-size:10px;font-weight:700">Opening stock MT</label><input class="yi_opening" type="number" placeholder="Opening stock e.g. 150 MT" value="${yi.opening_stock||yi.opening||''}"></div><div style="flex:0"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()"><i class="bi bi-trash"></i> Delete</button></div></div></div>`;
}

function addYardItem(yardId){
 let div=document.getElementById(yardId);
 let container=div.querySelector('.yard-items-container');
 if(container.innerHTML.includes('No yard items')) container.innerHTML='';
 container.insertAdjacentHTML('beforeend', renderYardItemLine({}));
}

async function saveSBU(){
 let sbuName=document.getElementById('sbu_name').value.trim();
 if(!sbuName){alert('Enter SBU Name'); return;}
 // 1. FIX: Kiln lining and health under kiln - once per kiln
 let kilns=[]; document.querySelectorAll('#kilnsContainer > div[id^="kiln_"]').forEach(div=>{
   let products_capacity=[];
   div.querySelectorAll('.kiln-products-container > div[id^="kprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.kp_product').value;
     let cap=pdiv.querySelector('.kp_capacity').value;
     if(pid) products_capacity.push({product_id:parseInt(pid), capacity_per_day:parseFloat(cap||0), capacity:parseFloat(cap||0)});
   });
   kilns.push({
     kiln_no:div.querySelector('.k_no').value, 
     lining_installation_date:div.querySelector('.k_lining').value,
     lining_date:div.querySelector('.k_lining').value,
     health_status:div.querySelector('.k_health').value,
     products_capacity:products_capacity
   });
 });
 let sizings=[]; document.querySelectorAll('#sizingContainer > div[id^="sizing_"]').forEach(div=>{
   let products_capacity=[];
   div.querySelectorAll('.sizing-products-container > div[id^="sprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.sp_product').value;
     let cap=pdiv.querySelector('.sp_capacity').value;
     let machLine=pdiv.querySelector('.sp_mach_line')?.value||'';
     if(pid) products_capacity.push({product_id:parseInt(pid), capacity_per_hour:parseFloat(cap||0), capacity:parseFloat(cap||0), machineries:machLine});
   });
   sizings.push({plant_no:div.querySelector('.s_no').value, products_capacity:products_capacity, machineries:div.querySelector('.s_mach').value});
 });
 let hydrations=[]; document.querySelectorAll('#hydrationContainer > div[id^="hyd_"]').forEach(div=>{
   let products_capacity=[];
   div.querySelectorAll('.hydration-products-container > div[id^="hprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.hp_product').value;
     let cap=pdiv.querySelector('.hp_capacity').value;
     let machLine=pdiv.querySelector('.hp_mach_line')?.value||'';
     if(pid) products_capacity.push({product_id:parseInt(pid), capacity_per_hour:parseFloat(cap||0), capacity:parseFloat(cap||0), machineries:machLine});
   });
   hydrations.push({plant_no:div.querySelector('.h_no').value, products_capacity:products_capacity, machineries:div.querySelector('.h_mach').value});
 });
 let yards=[]; document.querySelectorAll('#yardsContainer > div[id^="yard_"]').forEach(div=>{
   let yard_items=[];
   div.querySelectorAll('.yard-items-container > div[id^="yitem_"]').forEach(idiv=>{
     let pid=idiv.querySelector('.yi_product').value;
     let opening=idiv.querySelector('.yi_opening').value;
     if(pid) yard_items.push({product_id:parseInt(pid), opening_stock:parseFloat(opening||0), opening:parseFloat(opening||0)});
   });
   yards.push({yard_name:div.querySelector('.y_name').value, yard_items:yard_items});
 });
 let payload={sbu_name:sbuName, address:document.getElementById('sbu_address').value, kilns:kilns, sizing_plants:sizings, hydration_plants:hydrations, stock_yards:yards};
 // 2. FIX: Use editingSBUId properly - not erasing name/address
 let sbuId = editingSBUId || document.getElementById('sbu_id').value;
 let url=sbuId?'/api/sbus/'+sbuId:'/api/sbus';
 let method=sbuId?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json();
 alert(sbuId?'✅ SBU Updated: '+d.sbu_name+' - Edit bug fixed':'✅ SBU Created: '+d.sbu_name);
 closeAddSBU(); loadSBUs(); loadDash();
}

// 4. Arrange data in tabular format - clean tables
async function loadSBUs(){
 let res=await fetch('/api/sbus'); let sbus=await res.json();
 document.getElementById('sbuCountDash') && (document.getElementById('sbuCountDash').innerText=sbus.length);
 if(sbus.length===0){
   document.getElementById('sbuList').innerHTML='<div style="text-align:center;padding:30px"><p>No SBUs - Strategic Business Units - Tabular Format Clean</p><button class="btn btn-y" onclick="openAddSBU()"><i class="bi bi-plus-lg"></i> Add First SBU</button></div>';
   return;
 }
 let h='';
 for(let s of sbus){
   let kilnBadge=(s.kilns||[]).length, sizingBadge=(s.sizing_plants||[]).length, hydBadge=(s.hydration_plants||[]).length, yardBadge=(s.stock_yards||[]).length;
   // SBU Card with tabular format
   h+=`<div class="card sbu-card" style="padding:0;overflow:hidden">
<div class="sbu-header"><div><h3 style="margin:0;font-size:16px"><i class="bi bi-building"></i> ${s.sbu_name}</h3><p style="margin:4px 0 0;font-size:11px;color:#666"><i class="bi bi-geo-alt"></i> ${s.address||'No address - Full address field'}</p><p style="margin:6px 0 0"><span class="badge brass">${kilnBadge} Kilns</span> <span class="badge brass">${sizingBadge} Sizing</span> <span class="badge brass">${hydBadge} Hydration</span> <span class="badge brass">${yardBadge} Yards</span></p></div><div style="display:flex;gap:6px;flex-wrap:wrap"><button class="btn btn-w" onclick="editSBU(${s.id})"><i class="bi bi-pencil"></i> Edit</button><button class="btn btn-o" onclick="duplicateSBU(${s.id})"><i class="bi bi-files"></i> Duplicate</button><button class="btn btn-r" onclick="delSBU(${s.id})"><i class="bi bi-trash"></i> Delete</button></div></div>
<div style="padding:12px">
<!-- Kilns Table - Clean Tabular -->
${(s.kilns||[]).length>0?`<div class="tabular-section"><div class="tabular-header"><span>🔥 Kilns - Tabular Format Clean - Kiln No, Lining Date, Health Status, Products, Capacity/Day</span></div><table class="sbu-table"><tr><th>Kiln No.</th><th>Lining Installation Date</th><th>Health Status</th><th>Products (Finished List) + Capacity/Day</th></tr>${(s.kilns||[]).map(k=>`<tr><td><b>${k.kiln_no||'Kiln'}</b></td><td>${k.lining_installation_date||k.lining_date||'-'}</td><td><span class="badge ${k.health_status==='Good'?'ok':(k.health_status==='Critical'?'crit':'warn')}">${k.health_status||'Good'}</span></td><td>${(k.products_capacity||[]).map(pc=>`<span style="display:inline-block;background:var(--alab);padding:3px 8px;border-radius:12px;margin:2px;border:1px solid var(--line);font-size:10px"><b>${pc.product_name||pc.product_id}</b> - ${pc.capacity_per_day||pc.capacity||0} MT/day</span>`).join('')||'- No products - Add Product Button → Product name, Capacity/Day only'}</td></tr>`).join('')+`</table></div>`:''}
<!-- Sizing Table -->
${(s.sizing_plants||[]).length>0?`<div class="tabular-section"><div class="tabular-header"><span>⚙️ Sizing Plants - Plant No, Products, Cap/hr, Machineries</span></div><table class="sbu-table"><tr><th>Plant No.</th><th>Products (Finished List) + Capacity/hour</th><th>List of Machineries</th></tr>${(s.sizing_plants||[]).map(sp=>`<tr><td><b>${sp.plant_no||'Sizing Plant'}</b></td><td>${(sp.products_capacity||[]).map(pc=>`<span style="display:inline-block;background:#F6FFF6;padding:3px 8px;border-radius:12px;margin:2px;border:1px solid #C5E1C5;font-size:10px">${pc.product_name||pc.product_id} - ${pc.capacity_per_hour||pc.capacity||0} MT/hr</span>`).join('')||'-'}</td><td style="font-size:10px;max-width:280px">${(sp.products_capacity||[]).map(pc=>pc.machineries?`<div>${pc.product_name}: ${pc.machineries}</div>`:'' ).join('')||''}<div style="margin-top:4px;border-top:1px dashed var(--line);padding-top:4px"><b>Whole plant:</b> ${sp.machineries||'-'} - e.g. Crusher, Vibrating Screen 10-40mm, Conveyor 20m, Dust Collector</div></td></tr>`).join('')+`</table></div>`:''}
<!-- Hydration Table -->
${(s.hydration_plants||[]).length>0?`<div class="tabular-section"><div class="tabular-header"><span>💧 Hydration Plants - Plant No, Products, Cap/hour, Machineries</span></div><table class="sbu-table"><tr><th>Plant No.</th><th>Products + Cap/hour</th><th>Machineries</th></tr>${(s.hydration_plants||[]).map(hp=>`<tr><td><b>${hp.plant_no||'Hydration'}</b></td><td>${(hp.products_capacity||[]).map(pc=>`${pc.product_name||pc.product_id} - ${pc.capacity_per_hour||pc.capacity||0} MT/hr`).join('<br>')||'-'}</td><td style="font-size:10px">${hp.machineries||'-'}<br><span style="color:#666">Hydrator Reactor 5MT, Water Pump, Bagging Machine</span></td></tr>`).join('')+`</table></div>`:''}
<!-- Stock Yards Table -->
${(s.stock_yards||[]).length>0?`<div class="tabular-section"><div class="tabular-header"><span>📦 Stock Yards - Yard Name + Yard Items (All category products + Opening stock)</span></div><table class="sbu-table"><tr><th>Yard Name</th><th>Yard Items - Product (All category) + Opening Stock</th></tr>${(s.stock_yards||[]).map(y=>`<tr><td><b>${y.yard_name}</b></td><td>${(y.yard_items||[]).map(yi=>`<span style="display:inline-block;background:#FFFBEB;padding:3px 8px;border-radius:12px;margin:2px;border:1px solid var(--brass);font-size:10px">${yi.product_name||yi.product_id} - Opening: ${yi.opening_stock||yi.opening||0} MT</span>`).join('')||'No items'}</td></tr>`).join('')+`</table></div>`:''}
</div>
</div>`;
 }
 document.getElementById('sbuList').innerHTML=h;
}

// 2. FIX EDIT BUG + DUPLICATE OPTION
async function editSBU(id){
 let res=await fetch('/api/sbus/'+id); let s=await res.json();
 // FIX: Store editing id BEFORE opening modal (which clears id field)
 editingSBUId = s.id;
 document.getElementById('sbu_id').value = s.id;
 document.getElementById('sbuModalTitle').innerHTML='<i class="bi bi-pencil-square"></i> Edit SBU - '+s.sbu_name+' - Bug Fixed - Name/Address not erased';
 document.getElementById('sbuModal').classList.remove('hidden');
 // FIX: Set name and address immediately - not erased
 document.getElementById('sbu_name').value = s.sbu_name;
 document.getElementById('sbu_address').value = s.address;
 document.getElementById('kilnsContainer').innerHTML='<p style="font-size:11px;color:#888">Loading kilns...</p>';
 document.getElementById('sizingContainer').innerHTML='<p style="font-size:11px;color:#888">Loading sizing...</p>';
 document.getElementById('hydrationContainer').innerHTML='<p style="font-size:11px;color:#888">Loading hydration...</p>';
 document.getElementById('yardsContainer').innerHTML='<p style="font-size:11px;color:#888">Loading yards...</p>';
 await loadAllProductsForSBU();
 document.body.style.overflow='hidden';
 setTimeout(()=>{
   document.getElementById('kilnsContainer').innerHTML='';
   document.getElementById('sizingContainer').innerHTML='';
   document.getElementById('hydrationContainer').innerHTML='';
   document.getElementById('yardsContainer').innerHTML='';
   if((s.kilns||[]).length===0) document.getElementById('kilnsContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:12px">No kilns</p>';
   if((s.sizing_plants||[]).length===0) document.getElementById('sizingContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:12px">No sizing</p>';
   if((s.hydration_plants||[]).length===0) document.getElementById('hydrationContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:8px">No hydration</p>';
   if((s.stock_yards||[]).length===0) document.getElementById('yardsContainer').innerHTML='<p style="font-size:11px;color:#888;text-align:center;padding:8px">No yards</p>';
   (s.kilns||[]).forEach(k=>{ addKilnField(k); });
   (s.sizing_plants||[]).forEach(sp=>{ addSizingField(sp); });
   (s.hydration_plants||[]).forEach(hp=>{ addHydrationField(hp); });
   (s.stock_yards||[]).forEach(y=>{ addYardField(y); });
 },400);
}

async function duplicateSBU(id){
 if(!confirm('Duplicate SBU? Create duplicate so you need not fill each details again and again - Will create copy of SBU with same Kilns, Sizing, Hydration, Yards')) return;
 let res=await fetch('/api/sbus/'+id); let s=await res.json();
 // Create duplicate with "Copy" suffix
 let payload={
   sbu_name: s.sbu_name + ' - Copy',
   address: s.address,
   kilns: (s.kilns||[]).map(k=>({kiln_no:k.kiln_no+' - Copy', lining_installation_date:k.lining_installation_date||k.lining_date, health_status:k.health_status, products_capacity:(k.products_capacity||[]).map(pc=>({product_id:pc.product_id, capacity_per_day:pc.capacity_per_day||pc.capacity}))})),
   sizing_plants: (s.sizing_plants||[]).map(sp=>({plant_no:sp.plant_no+' - Copy', products_capacity:(sp.products_capacity||[]).map(pc=>({product_id:pc.product_id, capacity_per_hour:pc.capacity_per_hour||pc.capacity, machineries:pc.machineries})), machineries:sp.machineries})),
   hydration_plants: (s.hydration_plants||[]).map(hp=>({plant_no:hp.plant_no+' - Copy', products_capacity:(hp.products_capacity||[]).map(pc=>({product_id:pc.product_id, capacity_per_hour:pc.capacity_per_hour||pc.capacity, machineries:pc.machineries})), machineries:hp.machineries})),
   stock_yards: (s.stock_yards||[]).map(y=>({yard_name:y.yard_name+' - Copy', yard_items:(y.yard_items||[]).map(yi=>({product_id:yi.product_id, opening_stock:yi.opening_stock||yi.opening}))}))
 };
 let res2=await fetch('/api/sbus',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res2.json();
 alert('✅ SBU Duplicated: '+d.sbu_name+' - Duplicate created so you need not fill each details again and again');
 loadSBUs();
}

async function delSBU(id){ if(!confirm('Delete SBU?')) return; await fetch('/api/sbus/'+id,{method:'DELETE'}); loadSBUs(); }

// UNCHANGED v4.4.6 + v4.4.3
async function loadStock(){
 let res=await fetch('/api/inventory/combined'); let data=await res.json();
 let fUnit=document.getElementById('fUnit').value;
 function filt(list){ if(fUnit==='All') return list; return list.filter(x=> (x.location||'').includes(fUnit.split(' ')[1])); }
 let raw=filt(data.raw||[]); let wip=filt(data.wip||[]); let fin=filt(data.finished||[]);
 document.getElementById('rawTbl').innerHTML=raw.length?'<table><tr><th>Product</th><th>Code</th><th>HSN</th><th>Total</th><th>Status</th></tr>'+raw.map(r=>`<tr><td>${r.product}</td><td style="font-size:10px">${r.product_code||'-'}</td><td>${r.hsn_code||'-'}</td><td><b>${r.total_mt} MT</b></td><td><span class="badge ${r.status==='Critical'?'crit':(r.status==='Reorder'?'warn':'ok')}">${r.status}</span></td></tr>`).join('')+'</table>':'No Raw';
 document.getElementById('wipTbl').innerHTML=wip.length?'<table><tr><th>Product</th><th>Total</th></tr>'+wip.map(r=>`<tr><td>${r.product}</td><td>${r.total_mt} MT</td></tr>`).join('')+'</table>':'No WIP';
 document.getElementById('finTbl').innerHTML=fin.length?'<table><tr><th>Product</th><th>Code</th><th>HSN</th><th>Total</th></tr>'+fin.map(r=>`<tr><td><b>${r.product}</b></td><td style="font-size:10px">${r.product_code||'-'}</td><td>${r.hsn_code||'-'}</td><td><b>${r.total_mt} MT</b></td></tr>`).join('')+'</table>':'No Finished';
}
async function loadDash(){
 let res=await fetch('/api/inventory/combined'); let data=await res.json();
 document.getElementById('totalVal').innerText='Rs '+(data.total_value_lakh||0).toFixed(1)+' Lakh';
 document.getElementById('alertCnt').innerText=(data.alerts||[]).length;
 let prodRes=await fetch('/api/mo/total'); let prodData=await prodRes.json(); document.getElementById('prodToday').innerText=(prodData.total||0)+' MT';
 let h=''; if((data.alerts||[]).length===0) h='No alerts'; else { h='<table><tr><th>Product</th><th>Total</th><th>Status</th></tr>'; data.alerts.slice(0,5).forEach(a=>{ let b=a.status==='Critical'?'crit':'warn'; h+=`<tr><td>${a.product}</td><td>${a.total_mt} MT</td><td><span class="badge ${b}">${a.status}</span></td></tr>`; }); h+='</table>'; }
 document.getElementById('alerts').innerHTML=h;
 let catRes=await fetch('/api/product_categories'); let cats=await catRes.json(); document.getElementById('catCountDash') && (document.getElementById('catCountDash').innerText=cats.length);
 let prodRes2=await fetch('/api/products'); let prods=await prodRes2.json(); document.getElementById('prodCountDash') && (document.getElementById('prodCountDash').innerText=prods.length);
 let sbuRes=await fetch('/api/sbus'); let sbus=await sbuRes.json(); document.getElementById('sbuCountDash') && (document.getElementById('sbuCountDash').innerText=sbus.length);
}
async function loadWCOptions(){ let res=await fetch('/api/sbus'); let sbus=await res.json(); let opts=sbus.map(s=>`<option value="${s.id}">${s.sbu_name}</option>`).join(''); let el=document.getElementById('make_wc'); if(el) el.innerHTML=opts; }
async function loadVendors(){ let res=await fetch('/api/vendors'); let vs=await res.json(); if(vs.length===0){ document.getElementById('vendorTbl').innerHTML='No vendors'; return; } let h='<table><tr><th>Name</th><th>Type</th><th>Actions</th></tr>'; vs.forEach(v=>{ h+=`<tr><td><b>${v.name}</b></td><td>${v.vendor_type}</td><td><button class="btn btn-w" onclick="editVendor(${v.id})">Edit</button> <button class="btn btn-r" onclick="delVendor(${v.id})">Del</button></td></tr>`; }); h+='</table>'; document.getElementById('vendorTbl').innerHTML=h; let opts=vs.map(v=>`<option value="${v.id}">${v.name}</option>`).join(''); ['po_vendor','g_vendor'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function saveVendor(){ let id=document.getElementById('vend_id').value; let payload={name:document.getElementById('vend_name').value, vendor_type:document.getElementById('vend_type').value, gst:document.getElementById('vend_gst').value, contact:document.getElementById('vend_contact').value, credit_limit:parseFloat(document.getElementById('vend_credit').value||0), pending_due:parseFloat(document.getElementById('vend_due').value||0)}; if(!payload.name){alert('Enter Vendor Name'); return;} let url=id?'/api/vendors/'+id:'/api/vendors'; let method=id?'PUT':'POST'; await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Vendor Updated':'✅ Vendor Created'); resetVendForm(); loadVendors(); }
async function editVendor(id){ let res=await fetch('/api/vendors/'+id); let v=await res.json(); document.getElementById('vend_id').value=v.id; document.getElementById('vend_name').value=v.name; document.getElementById('vend_type').value=v.vendor_type; document.getElementById('vend_gst').value=v.gst; document.getElementById('vend_contact').value=v.contact; document.getElementById('vend_credit').value=v.credit_limit; document.getElementById('vend_due').value=v.pending_due; }
function resetVendForm(){ document.getElementById('vend_id').value=''; ['vend_name','vend_gst','vend_contact','vend_credit','vend_due'].forEach(id=>document.getElementById(id).value=''); }
async function delVendor(id){ if(!confirm('Delete Vendor?')) return; await fetch('/api/vendors/'+id,{method:'DELETE'}); loadVendors(); }
async function loadVendorsOpt(){ let res=await fetch('/api/vendors'); let vs=await res.json(); let opts=vs.map(v=>`<option value="${v.id}">${v.name}</option>`).join(''); ['po_vendor','g_vendor'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function loadCustomers(){ let res=await fetch('/api/customers'); let cs=await res.json(); if(cs.length===0){ document.getElementById('customerTbl').innerHTML='No customers'; return; } let h='<table><tr><th>Name</th><th>Type</th><th>Actions</th></tr>'; cs.forEach(c=>{ h+=`<tr><td><b>${c.name}</b></td><td>${c.customer_type}</td><td><button class="btn btn-w" onclick="editCustomer(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCustomer(${c.id})">Del</button></td></tr>`; }); h+='</table>'; document.getElementById('customerTbl').innerHTML=h; let opts=cs.map(c=>`<option value="${c.id}">${c.name}</option>`).join(''); let el=document.getElementById('d_customer'); if(el) el.innerHTML=opts; }
async function saveCustomer(){ let id=document.getElementById('cust_id').value; let payload={name:document.getElementById('cust_name').value, customer_type:document.getElementById('cust_type').value, gst:document.getElementById('cust_gst').value, contact:document.getElementById('cust_contact').value, pending_receivable:parseFloat(document.getElementById('cust_recv').value||0)}; if(!payload.name){alert('Enter Customer Name'); return;} let url=id?'/api/customers/'+id:'/api/customers'; let method=id?'PUT':'POST'; await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Customer Updated':'✅ Customer Created'); resetCustForm(); loadCustomers(); }
async function editCustomer(id){ let res=await fetch('/api/customers/'+id); let c=await res.json(); document.getElementById('cust_id').value=c.id; document.getElementById('cust_name').value=c.name; document.getElementById('cust_type').value=c.customer_type; document.getElementById('cust_gst').value=c.gst; document.getElementById('cust_contact').value=c.contact; document.getElementById('cust_recv').value=c.pending_receivable; }
function resetCustForm(){ document.getElementById('cust_id').value=''; ['cust_name','cust_gst','cust_contact','cust_recv'].forEach(id=>document.getElementById(id).value=''); }
async function delCustomer(id){ if(!confirm('Delete Customer?')) return; await fetch('/api/customers/'+id,{method:'DELETE'}); loadCustomers(); }
async function loadCustomersOpt(){ let res=await fetch('/api/customers'); let cs=await res.json(); let opts=cs.map(c=>`<option value="${c.id}">${c.name}</option>`).join(''); let el=document.getElementById('d_customer'); if(el) el.innerHTML=opts; }
async function loadPack(){ let res=await fetch('/api/packaging'); let ps=await res.json(); if(ps.length===0){ document.getElementById('packTbl').innerHTML='No packs'; return; } let h='<table><tr><th>Bag Type</th><th>Cat</th><th>Actions</th></tr>'; ps.forEach(p=>{ h+=`<tr><td><b>${p.bag_type}</b></td><td>${p.bag_category}</td><td><button class="btn btn-w" onclick="editPack(${p.id})">Edit</button> <button class="btn btn-r" onclick="delPack(${p.id})">Del</button></td></tr>`; }); h+='</table>'; document.getElementById('packTbl').innerHTML=h; }
async function savePack(){ let id=document.getElementById('pack_id').value; let payload={bag_type:document.getElementById('pack_type').value, bag_category:document.getElementById('pack_cat').value, capacity_mt:parseFloat(document.getElementById('pack_cap').value||0), closing:parseFloat(document.getElementById('pack_closing').value||0), min_stock:parseFloat(document.getElementById('pack_min').value||0), rate_per_bag:parseFloat(document.getElementById('pack_rate').value||0), unit:document.getElementById('pack_unit').value}; if(!payload.bag_type){alert('Enter Bag Type'); return;} let url=id?'/api/packaging/'+id:'/api/packaging'; let method=id?'PUT':'POST'; await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); alert(id?'✅ Pack Updated':'✅ Pack Created'); resetPackForm(); loadPack(); }
async function editPack(id){ let res=await fetch('/api/packaging/'+id); let p=await res.json(); document.getElementById('pack_id').value=p.id; document.getElementById('pack_type').value=p.bag_type; document.getElementById('pack_cat').value=p.bag_category; document.getElementById('pack_cap').value=p.capacity_mt; document.getElementById('pack_closing').value=p.closing; document.getElementById('pack_min').value=p.min_stock; document.getElementById('pack_rate').value=p.rate_per_bag; document.getElementById('pack_unit').value=p.unit; }
function resetPackForm(){ document.getElementById('pack_id').value=''; ['pack_type','pack_cap','pack_closing','pack_min','pack_rate'].forEach(id=>document.getElementById(id).value=''); }
async function delPack(id){ if(!confirm('Delete Pack?')) return; await fetch('/api/packaging/'+id,{method:'DELETE'}); loadPack(); }
async function loadMO(){ let res=await fetch('/api/manufacturing_orders'); let mos=await res.json(); if(mos.length===0){ document.getElementById('moList').innerHTML='No MO'; return; } let h='<table><tr><th>MO No</th><th>Type</th><th>WC/SBU</th><th>Status</th></tr>'; mos.forEach(m=>{ h+=`<tr><td><b>${m.mo_no}</b></td><td>${m.mo_type}</td><td>${m.workcenter}</td><td>${m.status}</td></tr>`; }); h+='</table>'; document.getElementById('moList').innerHTML=h; }
async function createMO(){ let wc=document.getElementById('make_wc').value; if(!wc){alert('Create SBUs first'); return;} let payload={workcenter_id:wc, unit:document.getElementById('make_unit').value, mo_type:document.getElementById('make_type').value, input_qty_mt:parseFloat(document.getElementById('make_lime').value||0), output_qty_mt:parseFloat(document.getElementById('make_out').value||0), wastage_mt:parseFloat(document.getElementById('make_waste').value||0), input_product:document.getElementById('make_inProd').value, output_product:document.getElementById('make_outProd').value, operator:document.getElementById('make_op').value||'operator1'}; let res=await fetch('/api/manufacturing_orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ MO '+d.mo_no); loadMO(); }
async function createPO(){ let qty=parseFloat(document.getElementById('po_qty').value||0); let rate=parseFloat(document.getElementById('po_rate').value||0); if(qty<=0||rate<=0){alert('Qty & Rate'); return;} let payload={vendor_id:document.getElementById('po_vendor').value, material:document.getElementById('po_mat').value, qty:qty, rate:rate, unit:document.getElementById('po_unit').value, status:document.getElementById('po_status').value, date:new Date().toISOString().slice(0,10)}; let res=await fetch('/api/po',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ PO '+d.po_no); loadPOList(); }
async function loadPOList(){ let res=await fetch('/api/po'); let pos=await res.json(); document.getElementById('poList').innerHTML=pos.length?'<table><tr><th>PO No</th><th>Material</th><th>Qty</th><th>Total</th><th>Unit</th><th>Status</th></tr>'+pos.map(p=>`<tr><td>${p.po_no}</td><td>${p.material}</td><td>${p.qty}</td><td>${p.total}</td><td>${p.unit}</td><td>${p.status}</td></tr>`).join('')+'</table>':'No PO'; }
async function createGRN(){ let gross=parseFloat(document.getElementById('g_gross').value||0); let tare=parseFloat(document.getElementById('g_tare').value||0); if(gross<=0||tare<=0){alert('Gross/Tare'); return;} let net=(gross-tare)/1000; let payload={vehicle_no:document.getElementById('g_vehicle').value, material:document.getElementById('g_material').value, gross_wt:gross, tare_wt:tare, net_wt:net, unit:document.getElementById('g_unit').value, vendor_id:document.getElementById('g_vendor').value}; let res=await fetch('/api/grn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ GRN '+d.grn_no); loadGRNList(); loadStock(); }
async function loadGRNList(){ let res=await fetch('/api/grn'); let gs=await res.json(); document.getElementById('grnList').innerHTML=gs.length?'<table><tr><th>GRN No</th><th>Vehicle</th><th>Material</th><th>Net MT</th><th>Unit</th></tr>'+gs.map(g=>`<tr><td>${g.grn_no}</td><td>${g.vehicle_no}</td><td>${g.material}</td><td>${g.net_wt} MT</td><td>${g.unit}</td></tr>`).join('')+'</table>':'No GRN'; }
async function createDispatch(){ let qty=parseFloat(document.getElementById('d_qty').value||0); if(qty<=0){alert('Qty'); return;} let payload={customer_id:document.getElementById('d_customer').value, vehicle_no:document.getElementById('d_vehicle').value, product:document.getElementById('d_product').value, qty_mt:qty, unit:document.getElementById('d_unit').value, qr_bags:document.getElementById('d_qr').value, date:new Date().toISOString().slice(0,10)}; let res=await fetch('/api/dispatch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let d=await res.json(); alert('✅ Dispatch '+d.dispatch_no); loadDispatchList(); loadStock(); }
async function loadDispatchList(){ let res=await fetch('/api/dispatch'); let ds=await res.json(); document.getElementById('dispatchList').innerHTML=ds.length?'<table><tr><th>Disp No</th><th>Customer</th><th>Vehicle</th><th>Product</th><th>Qty</th><th>Unit</th></tr>'+ds.map(d=>`<tr><td>${d.dispatch_no}</td><td>${d.customer}</td><td>${d.vehicle_no}</td><td>${d.product}</td><td>${d.qty_mt} MT</td><td>${d.unit}</td></tr>`).join('')+'</table>':'No Dispatch'; }
async function loadProductsOpt(){ let res=await fetch('/api/products'); let ps=await res.json(); let opts=ps.map(p=>`<option value="${p.name}">${p.name} - ${p.product_code}</option>`).join(''); ['qr_product','d_product'].forEach(id=>{ let el=document.getElementById(id); if(el) el.innerHTML=opts; }); }
async function genQR(){ let prod=document.getElementById('qr_product').value; if(!prod){alert('Create Products first'); return;} let wt=parseFloat(document.getElementById('qr_weight').value||1.2); let res=await fetch('/api/qr_generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product:prod, weight:wt, unit:document.getElementById('qr_unit').value})}); let d=await res.json(); document.getElementById('qrResult').innerHTML='<b>Bag ID: '+d.bag_id+'</b>'; document.getElementById('qrImg').innerHTML='<img src="data:image/png;base64,'+d.qr_base64+'" style="width:180px;border:6px solid #1A2E1E;border-radius:10px;margin-top:8px">'; loadQRList(); }
async function loadQRList(){ let res=await fetch('/api/qr_list'); let qs=await res.json(); document.getElementById('qrList').innerHTML=qs.length?'<table><tr><th>Bag ID</th><th>Product</th><th>Wt</th><th>Unit</th><th>Status</th></tr>'+qs.map(q=>`<tr><td><b>${q.bag_id}</b></td><td>${q.product}</td><td>${q.weight} MT</td><td>${q.unit}</td><td>${q.status}</td></tr>`).join('')+'</table>':'No QR'; }
async function loadCost(){ let res=await fetch('/api/inventory/combined'); let data=await res.json(); document.getElementById('costVal').innerText='Rs '+(data.total_value_lakh||0).toFixed(1)+' Lakh'; let all=[...(data.raw||[]),...(data.finished||[])]; document.getElementById('costTbl').innerHTML=all.length?'<table><tr><th>Product</th><th>Total MT</th><th>Value</th></tr>'+all.map(r=>`<tr><td>${r.product}</td><td>${r.total_mt} MT</td><td>Rs ${(r.value/1000).toFixed(1)}k</td></tr>`).join('')+'</table>':'No data'; }

loadDash(); loadCategories(); loadProducts(); loadSBUs();
</script>
</body></html>
    """

@app.route('/api/product_categories', methods=['GET','POST'])
def product_categories_api():
    if request.method=='POST':
        data=request.json
        cat_name=(data.get('category_name') or '').strip()
        if not cat_name:
            return jsonify({'error':'Category Name required'}), 400
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
        entry={'product':p.name,'total_mt':total_mt,'value':value,'status':status,'product_code':p.product_code,'hsn_code':p.hsn_code}
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
        if not data.get('name') or not data.get('name').strip():
            return jsonify({'error':'Product Name Mandatory'}), 400
        if not data.get('category') or not data.get('category').strip():
            return jsonify({'error':'Product Category Mandatory'}), 400
        if not data.get('hsn_code') or not data.get('hsn_code').strip():
            return jsonify({'error':'HSN Code Mandatory'}), 400
        if not data.get('description') or not data.get('description').strip():
            return jsonify({'error':'Product Description Mandatory'}), 400
        cnt=Product.query.count()+1
        prod_code=generate_product_code(data.get('category'), cnt)
        while Product.query.filter_by(product_code=prod_code).first():
            cnt+=1
            prod_code=generate_product_code(data.get('category'), cnt)
        p=Product(name=data.get('name').strip(), category=data.get('category').strip(), product_code=prod_code, hsn_code=data.get('hsn_code').strip(), description=data.get('description').strip())
        db.session.add(p)
        db.session.commit()
        return jsonify({'id':p.id,'name':p.name,'product_code':p.product_code,'hsn_code':p.hsn_code,'category':p.category})
    prods=Product.query.order_by(Product.id.desc()).all()
    return jsonify([{'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description} for p in prods])

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
def product_one(pid):
    p=Product.query.get_or_404(pid)
    if request.method=='GET':
        return jsonify({'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description})
    elif request.method=='PUT':
        data=request.json
        p.name=data.get('name').strip()
        p.category=data.get('category').strip()
        p.hsn_code=data.get('hsn_code').strip()
        p.description=data.get('description').strip()
        db.session.commit()
        return jsonify({'id':p.id,'name':p.name,'product_code':p.product_code,'hsn_code':p.hsn_code})
    else:
        db.session.delete(p)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/sbus', methods=['GET','POST'])
def sbus_api():
    if request.method=='POST':
        data=request.json
        sbu=SBU(sbu_name=data.get('sbu_name'), address=data.get('address',''))
        db.session.add(sbu)
        db.session.flush()
        for k in data.get('kilns',[]):
            ka=KilnAsset(sbu_id=sbu.id, kiln_no=k.get('kiln_no'), lining_installation_date=k.get('lining_installation_date',''), health_status=k.get('health_status','Good'), products_capacity=json.dumps(k.get('products_capacity',[])))
            db.session.add(ka)
        for sp in data.get('sizing_plants',[]):
            sa=SizingPlantAsset(sbu_id=sbu.id, plant_no=sp.get('plant_no'), products_capacity=json.dumps(sp.get('products_capacity',[])), machineries=sp.get('machineries',''))
            db.session.add(sa)
        for hp in data.get('hydration_plants',[]):
            ha=HydrationPlantAsset(sbu_id=sbu.id, plant_no=hp.get('plant_no'), products_capacity=json.dumps(hp.get('products_capacity',[])), machineries=hp.get('machineries',''))
            db.session.add(ha)
        for y in data.get('stock_yards',[]):
            ya=StockYardAsset(sbu_id=sbu.id, yard_name=y.get('yard_name'), yard_items=json.dumps(y.get('yard_items',[])))
            db.session.add(ya)
        db.session.commit()
        return jsonify({'id':sbu.id,'sbu_name':sbu.sbu_name})
    sbus=SBU.query.all()
    result=[]
    all_products={p.id:p for p in Product.query.all()}
    def resolve_pc(pc_list_json):
        try:
            pcs=json.loads(pc_list_json) if pc_list_json else []
            out=[]
            for pc in pcs:
                pid=pc.get('product_id')
                prod=all_products.get(pid)
                out.append({'product_id':pid,'product_name':prod.name if prod else f'ID {pid}','product_code':prod.product_code if prod else '', 'capacity_per_day':pc.get('capacity_per_day',0),'capacity_per_hour':pc.get('capacity_per_hour',0),'capacity':pc.get('capacity',0),'machineries':pc.get('machineries','')})
            return out
        except:
            return []
    def resolve_yard(yard_json):
        try:
            items=json.loads(yard_json) if yard_json else []
            out=[]
            for it in items:
                pid=it.get('product_id')
                prod=all_products.get(pid)
                out.append({'product_id':pid,'product_name':prod.name if prod else f'ID {pid}','product_code':prod.product_code if prod else '','opening_stock':it.get('opening_stock',0),'opening':it.get('opening',0)})
            return out
        except:
            return []
    for s in sbus:
        kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
        sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
        hyds=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
        yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
        result.append({
            'id':s.id,'sbu_name':s.sbu_name,'address':s.address,
            'kilns':[{'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':resolve_pc(k.products_capacity)} for k in kilns],
            'sizing_plants':[{'plant_no':sp.plant_no,'products_capacity':resolve_pc(sp.products_capacity),'machineries':sp.machineries} for sp in sizings],
            'hydration_plants':[{'plant_no':hp.plant_no,'products_capacity':resolve_pc(hp.products_capacity),'machineries':hp.machineries} for hp in hyds],
            'stock_yards':[{'yard_name':y.yard_name,'yard_items':resolve_yard(y.yard_items)} for y in yards]
        })
    return jsonify(result)

@app.route('/api/sbus/<int:sid>', methods=['GET','PUT','DELETE'])
def sbu_one(sid):
    s=SBU.query.get_or_404(sid)
    all_products={p.id:p for p in Product.query.all()}
    def resolve_pc(pc_list_json):
        try:
            pcs=json.loads(pc_list_json) if pc_list_json else []
            out=[]
            for pc in pcs:
                pid=pc.get('product_id')
                prod=all_products.get(pid)
                out.append({'product_id':pid,'product_name':prod.name if prod else f'ID {pid}','product_code':prod.product_code if prod else '', 'capacity_per_day':pc.get('capacity_per_day',0),'capacity_per_hour':pc.get('capacity_per_hour',0),'capacity':pc.get('capacity',0),'machineries':pc.get('machineries','')})
            return out
        except:
            return []
    def resolve_yard(yard_json):
        try:
            items=json.loads(yard_json) if yard_json else []
            out=[]
            for it in items:
                pid=it.get('product_id')
                prod=all_products.get(pid)
                out.append({'product_id':pid,'product_name':prod.name if prod else f'ID {pid}','product_code':prod.product_code if prod else '','opening_stock':it.get('opening_stock',0),'opening':it.get('opening',0)})
            return out
        except:
            return []
    if request.method=='GET':
        kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
        sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
        hyds=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
        yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
        return jsonify({
            'id':s.id,'sbu_name':s.sbu_name,'address':s.address,
            'kilns':[{'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':resolve_pc(k.products_capacity),'products_capacity_raw':k.products_capacity} for k in kilns],
            'sizing_plants':[{'plant_no':sp.plant_no,'products_capacity':resolve_pc(sp.products_capacity),'products_capacity_raw':sp.products_capacity,'machineries':sp.machineries} for sp in sizings],
            'hydration_plants':[{'plant_no':hp.plant_no,'products_capacity':resolve_pc(hp.products_capacity),'products_capacity_raw':hp.products_capacity,'machineries':hp.machineries} for hp in hyds],
            'stock_yards':[{'yard_name':y.yard_name,'yard_items':resolve_yard(y.yard_items),'yard_items_raw':y.yard_items} for y in yards]
        })
    elif request.method=='PUT':
        data=request.json
        s.sbu_name=data.get('sbu_name',s.sbu_name)
        s.address=data.get('address',s.address)
        KilnAsset.query.filter_by(sbu_id=s.id).delete()
        SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
        HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
        StockYardAsset.query.filter_by(sbu_id=s.id).delete()
        for k in data.get('kilns',[]):
            ka=KilnAsset(sbu_id=s.id, kiln_no=k.get('kiln_no'), lining_installation_date=k.get('lining_installation_date',''), health_status=k.get('health_status','Good'), products_capacity=json.dumps(k.get('products_capacity',[])))
            db.session.add(ka)
        for sp in data.get('sizing_plants',[]):
            sa=SizingPlantAsset(sbu_id=s.id, plant_no=sp.get('plant_no'), products_capacity=json.dumps(sp.get('products_capacity',[])), machineries=sp.get('machineries',''))
            db.session.add(sa)
        for hp in data.get('hydration_plants',[]):
            ha=HydrationPlantAsset(sbu_id=s.id, plant_no=hp.get('plant_no'), products_capacity=json.dumps(hp.get('products_capacity',[])), machineries=hp.get('machineries',''))
            db.session.add(ha)
        for y in data.get('stock_yards',[]):
            ya=StockYardAsset(sbu_id=s.id, yard_name=y.get('yard_name'), yard_items=json.dumps(y.get('yard_items',[])))
            db.session.add(ya)
        db.session.commit()
        return jsonify({'id':s.id,'sbu_name':s.sbu_name})
    else:
        KilnAsset.query.filter_by(sbu_id=s.id).delete()
        SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
        HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
        StockYardAsset.query.filter_by(sbu_id=s.id).delete()
        db.session.delete(s)
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
        mo=ManufacturingOrder(mo_no=mo_no, date=datetime.now().strftime('%Y-%m-%d'), workcenter_id=data.get('workcenter_id'), unit=data.get('unit'), mo_type=data.get('mo_type'), input_product=data.get('input_product'), input_qty_mt=float(data.get('input_qty_mt',0)), output_product=data.get('output_product'), output_qty_mt=float(data.get('output_qty_mt',0)), operator=data.get('operator','operator1'), status='Done')
        db.session.add(mo)
        db.session.commit()
        return jsonify({'mo_no':mo_no})
    mos=ManufacturingOrder.query.order_by(ManufacturingOrder.id.desc()).limit(50).all()
    sbus={s.id:s.sbu_name for s in SBU.query.all()}
    return jsonify([{'mo_no':m.mo_no,'date':m.date,'unit':m.unit,'workcenter':sbus.get(m.workcenter_id,'-'),'mo_type':m.mo_type,'input_product':m.input_product,'input_qty':m.input_qty_mt,'output_product':m.output_product,'output_qty':m.output_qty_mt,'operator':m.operator,'status':m.status} for m in mos])

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
    import qrcode, base64
    from io import BytesIO
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
    return jsonify({"status":"LIVE","version":"v4.4.7 Clean Tabular - Keep v4.4.6 unchanged only SBU changes - 1 Kiln lining/health asked once under kiln name not per product - Product add only Product name + Capacity/Day - 2 Edit bug fixed + Duplicate option - 3 Remove text lines after heading and button - 4 Tabular format clean","db_file":"lemon_erp_v44_1_category.db","url":"https://lemon-erp.onrender.com"})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
