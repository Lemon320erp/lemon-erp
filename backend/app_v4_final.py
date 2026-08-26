"""
🍋 LEMON ERP v4.6 - SBU + PRODUCTS REFINEMENT - v4.4 Base Remembered
Refinement 1 Fixed: Stock Yard Button fields: Yard Name, Product selection from ALL products, Opening Qty, UOM, Packaging type for finished
Refinement 2: Products Master - Landing category-wise, Add Product: Product Name, Category (from Category Master), Packaging Type, Size, Opening Qty, UOM, + Create Category Master for future selection
Base: v4.4 Clean Masters (Empty)
Previous: v4.5 SBU Master (Kilns, Sizing, Hydration)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'lemon-erp-v46-sbu-products-refinement-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v46.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================
class CategoryMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)  # e.g. Raw, WIP, Finished, Limestone, Quicklime, Hydrated, etc
    category_type = db.Column(db.String(50), default='Finished')  # Raw/WIP/Finished for grouping
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))  # Product Name
    category_id = db.Column(db.Integer, db.ForeignKey('category_master.id'))
    category_name = db.Column(db.String(100))  # Denormalized for quick display
    packaging_type = db.Column(db.String(50))  # Jumbo, HDPE 40kg, Loose, Bulk
    size = db.Column(db.String(50))  # Size e.g. 10-40mm, 40-60mm, 0-3mm, 10-50mm, 90%, 95%
    opening_qty = db.Column(db.Float, default=0)  # Opening Qty
    unit_of_measurement = db.Column(db.String(20))  # UOM e.g. MT, Kg, Bags, MT/Bags
    # Stock tracking for combined logic
    loose_stock_mt = db.Column(db.Float, default=0)
    jumbo_mt = db.Column(db.Float, default=0)
    hdpe_mt = db.Column(db.Float, default=0)
    total_stock_mt = db.Column(db.Float, default=0)
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
    production_capacity = db.Column(db.Float)
    lining_installation_date = db.Column(db.String(20))
    health_status = db.Column(db.String(50))
    product_ids = db.Column(db.Text)

class SizingPlantAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    product_ids = db.Column(db.Text)
    production_capacity_per_hour = db.Column(db.Float)
    machineries = db.Column(db.Text)

class HydrationPlantAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    product_ids = db.Column(db.Text)
    production_capacity = db.Column(db.Float)
    machineries = db.Column(db.Text)

# FIXED Stock Yard as per new requirement
class StockYardAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    yard_name = db.Column(db.String(100))  # Yard Name
    product_ids = db.Column(db.Text)  # Product selection from ALL product lists (JSON)
    opening_quantity = db.Column(db.Float, default=0)  # Opening Quantity
    unit_of_measurement = db.Column(db.String(20))  # UOM e.g. MT, Bags
    packaging_type = db.Column(db.String(50))  # Packaging type for finished products e.g. Jumbo 1.2MT, HDPE 40kg, Loose
    yard_type = db.Column(db.String(50), default='Stock Yard')  # Keep for backward
    capacity_mt = db.Column(db.Float, default=0)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vendor_type = db.Column(db.String(50))
    contact = db.Column(db.String(50))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    customer_type = db.Column(db.String(50))
    contact = db.Column(db.String(50))

class PackagingStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bag_type = db.Column(db.String(100))
    closing = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))

class ManufacturingOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mo_no = db.Column(db.String(50), unique=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'))
    mo_type = db.Column(db.String(50))
    output_product = db.Column(db.String(100))
    output_qty_mt = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Done')

with app.app_context():
    db.create_all()
    # Seed Category Master empty but with some defaults if none
    if CategoryMaster.query.count()==0:
        defaults=[
            CategoryMaster(name='Raw - Limestone', category_type='Raw'),
            CategoryMaster(name='Raw - Petcoke', category_type='Raw'),
            CategoryMaster(name='WIP - CaO Loose', category_type='WIP'),
            CategoryMaster(name='Finished - Quicklime', category_type='Finished'),
            CategoryMaster(name='Finished - Hydrated', category_type='Finished'),
            CategoryMaster(name='Finished - Chunna', category_type='Finished'),
        ]
        for c in defaults:
            db.session.add(c)
        db.session.commit()

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html><head><title>Lemon ERP v4.6 - SBU + Products</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--line:#E8E0D5;--gray:#F6F5F3}
*{box-sizing:border-box} body{margin:0;font-family:Inter,Arial;background:var(--gray);color:var(--green);font-size:12.5px}
.topnav{background:var(--green);color:white;padding:0 14px;display:flex;justify-content:space-between;align-items:center;height:44px;position:sticky;top:0;z-index:200}
.topnav .brand{font-weight:900;font-size:14px} .topnav .brand span.l{color:var(--lemon)} .ver{font-size:9px;background:var(--brass);color:var(--green);padding:2px 6px;border-radius:10px;margin-left:6px}
.layout{display:flex}
.sidebar{width:200px;background:white;border-right:1px solid var(--line);padding:10px 0;position:sticky;top:44px;height:calc(100vh - 44px);overflow-y:auto}
.sidebar h4{font-size:10px;color:#888;margin:14px 10px 4px;text-transform:uppercase;letter-spacing:0.6px}
.menu{padding:7px 10px;margin:2px 6px;border-radius:7px;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:12px;color:#444}
.menu:hover{background:var(--alab)} .menu.active{background:var(--green);color:var(--brass)}
.content{flex:1;padding:14px;max-width:1400px}
.card{background:white;border-radius:10px;padding:14px;margin:8px 0;box-shadow:0 2px 6px rgba(0,0,0,0.04);border:1px solid var(--line)}
.card h3{margin:0 0 10px;font-size:13px;font-weight:800;display:flex;align-items:center;gap:8px}
.btn{padding:7px 12px;border-radius:7px;border:none;cursor:pointer;font-weight:700;font-size:11px}
.btn-g{background:var(--green);color:white} .btn-y{background:var(--lemon);color:var(--green)} .btn-w{background:white;color:var(--green);border:1px solid var(--line)} .btn-r{background:#C5221F;color:white}
.badge{padding:3px 8px;border-radius:12px;font-size:10px;font-weight:800}
.ok{background:#E6F4EA;color:#1E7D32} .warn{background:#FEF3CD;color:#9C6F00}
table{width:100%;border-collapse:collapse;font-size:12px} th{background:#F8F6F3;padding:8px 6px;text-align:left;font-weight:700;border-bottom:2px solid var(--line)} td{padding:7px 6px;border-bottom:1px solid #F0EBE2}
input,select,textarea{padding:7px 8px;border-radius:6px;border:1px solid var(--line);width:100%;font-size:12px;margin:3px 0}
.row{display:flex;gap:6px;flex-wrap:wrap}.row>*{flex:1;min-width:120px}
.hidden{display:none}
.form-box{background:var(--alab);padding:12px;border-radius:8px;border:1px dashed var(--brass);margin-bottom:10px}
.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:500;display:flex;align-items:center;justify-content:center;padding:20px}
.modal-content{background:white;border-radius:12px;padding:20px;width:100%;max-width:900px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
.asset-section{background:white;border:1px solid var(--line);border-radius:8px;padding:10px;margin:8px 0}
.sbu-card{border-left:5px solid var(--green)}
.cat-group{border:1px solid var(--line);border-radius:8px;margin:8px 0;overflow:hidden}
.cat-header{background:var(--green);color:var(--brass);padding:8px 12px;font-weight:800;font-size:12px;display:flex;justify-content:space-between}
</style></head><body>
<div class="topnav"><div class="brand">🍋 Lemon ERP <span class="l">v4.6 SBU + Products</span> <span class="ver">v4.4 Base → SBU Fix + Products Refinement</span></div><div><button class="btn btn-y" onclick="location.reload()">Reload</button></div></div>
<div class="layout">
<div class="sidebar">
<h4>Main</h4>
<div class="menu active" onclick="openTab('dash')"><i class="bi bi-speedometer2"></i> Dash</div>
<div class="menu" onclick="openTab('stock')"><i class="bi bi-box-seam"></i> Stock</div>
<h4>Masters - v4.4 Base</h4>
<div class="menu" onclick="openTab('products')" style="background:var(--alab);border:1px solid var(--brass)"><i class="bi bi-bag"></i> Products *Refined</div>
<div class="menu" onclick="openTab('sbus')" style="background:var(--alab);border:1px solid var(--brass)"><i class="bi bi-building"></i> SBUs *Fixed Yard</div>
<div class="menu" onclick="openTab('categories')"><i class="bi bi-tags"></i> Categories *New</div>
<div class="menu" onclick="openTab('vendors')"><i class="bi bi-people"></i> Vendors</div>
<div class="menu" onclick="openTab('customers')"><i class="bi bi-person"></i> Customers</div>
<div class="menu" onclick="openTab('pack')"><i class="bi bi-box"></i> Pack</div>
</div>

<div class="content">
<!-- DASH -->
<div id="dash" class="tabcontent">
<div class="card"><h3><i class="bi bi-speedometer2"></i> Dash - v4.6 - SBU Yard Fixed + Products Refined</h3><p style="font-size:11px">Base v4.4: Empty masters, Short headings | Fix: Stock Yard fields corrected as requested | Products: Category-wise list + Category Master</p>
<div class="row"><div class="card" style="flex:1"><div style="font-size:11px">SBUs</div><div style="font-size:20px;font-weight:900" id="sbuCount">0</div></div><div class="card" style="flex:1"><div style="font-size:11px">Products</div><div style="font-size:20px;font-weight:900" id="prodCount">0</div></div><div class="card" style="flex:1"><div style="font-size:11px">Categories</div><div style="font-size:20px;font-weight:900" id="catCount">0</div></div><div class="card" style="flex:1"><div style="font-size:11px">Date</div><div style="font-size:14px;font-weight:900" id="todayDate"></div></div></div>
</div>
</div>

<!-- PRODUCTS MASTER - REFINED -->
<div id="products" class="tabcontent">
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center"><h3><i class="bi bi-bag"></i> Products - Landing Category-wise - With Add Product Button - Category Master Linked</h3><button class="btn btn-y" onclick="openAddProduct()"><i class="bi bi-plus-lg"></i> Add Product</button></div>
<p style="font-size:11px;color:#666">Refined: Product Name, Category (from Category Master), Packaging Type, Size, Opening Qty, UOM | Category-wise grouped list | Create Category Master for future selection</p>
<div id="productList">Loading products category-wise...</div>
</div>
</div>

<!-- CATEGORIES MASTER - NEW -->
<div id="categories" class="tabcontent hidden">
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center"><h3><i class="bi bi-tags"></i> Categories - Category Master - Create New Category for Future Selection</h3><button class="btn btn-g" onclick="openAddCategory()"><i class="bi bi-plus-lg"></i> Add Category</button></div>
<p style="font-size:11px;color:#666">Create categories like Raw-Limestone, Finished-Quicklime, Hydrated etc. Will appear in Product Category dropdown for future selection</p>
<div class="form-box hidden" id="catFormBox">
<h3 id="catFormTitle">Add New Category</h3>
<input type="hidden" id="cat_id">
<div class="row"><input id="cat_name" placeholder="Category Name e.g. Finished - Quicklime, Raw - Limestone, WIP - CaO Loose, Hydrated 90%"><select id="cat_type"><option>Raw</option><option>WIP</option><option>Finished</option><option>Packaging</option></select><button class="btn btn-g" onclick="saveCategory()">Save Category</button><button class="btn btn-w" onclick="closeCatForm()">Cancel</button></div>
</div>
<div id="categoryList">Loading categories...</div>
</div>
</div>

<!-- SBU MASTER - FIXED YARD -->
<div id="sbus" class="tabcontent hidden">
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center"><h3><i class="bi bi-building"></i> SBUs - With Fixed Stock Yard Fields - Yard Name, Product from ALL lists, Opening Qty, UOM, Packaging Type</h3><button class="btn btn-y" onclick="openAddSBU()"><i class="bi bi-plus-lg"></i> Add SBU</button></div>
<p style="font-size:11px;color:#666">Fixed: Stock Yard now has fields as requested: Yard Name, Add Product from ALL product lists, Opening Quantity, Unit of measurement, Packaging type for finished products</p>
<div id="sbuList">Loading SBUs...</div>
</div>
</div>

<!-- OTHER MASTERS -->
<div id="stock" class="tabcontent hidden"><div class="card"><h3>Stock - Category-wise</h3><div id="stockTbl">Create products first</div></div></div>
<div id="vendors" class="tabcontent hidden"><div class="card"><h3>Vendors</h3><div id="vendorTbl">No vendors</div></div></div>
<div id="customers" class="tabcontent hidden"><div class="card"><h3>Customers</h3><div id="customerTbl">No customers</div></div></div>
<div id="pack" class="tabcontent hidden"><div class="card"><h3>Pack</h3><div id="packTbl">No packs</div></div></div>
</div>
</div>

<!-- ADD PRODUCT MODAL - REFINED -->
<div id="productModal" class="modal hidden">
<div class="modal-content">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><h3 style="margin:0"><i class="bi bi-bag-plus"></i> Add Product - With Category Master + Packaging + Size + Opening + UOM</h3><button class="btn btn-w" onclick="closeAddProduct()">✕ Close</button></div>
<input type="hidden" id="prod_id">
<div class="form-box">
<h3>Product Details - As Requested</h3>
<div class="row"><input id="prod_name" placeholder="Product Name e.g. CaO 10-40mm, Limestone, Hydrated 90%"><select id="prod_category"></select><button class="btn btn-w" style="max-width:140px" onclick="openAddCategoryFromProduct()">+ New Category</button></div>
<div class="row"><select id="prod_pack_type"><option>Loose</option><option>Jumbo 1.2MT</option><option>Jumbo 1.5MT</option><option>HDPE 40kg</option><option>HDPE 25kg</option><option>Bulk</option><option>Bag - Custom</option></select><input id="prod_size" placeholder="Size e.g. 10-40mm, 40-60mm, 0-3mm, 10-50mm, 90%, 95%, 0-100mm"><input id="prod_opening" type="number" placeholder="Opening Qty e.g. 25"></div>
<div class="row"><select id="prod_uom"><option>MT</option><option>Kg</option><option>Bags</option><option>MT + Bags Combined</option><option>Quintals</option></select><input id="prod_location" placeholder="Location e.g. Unit 1 Yard"><input id="prod_sale" type="number" placeholder="Sale Price Rs/MT"><input id="prod_purchase" type="number" placeholder="Purchase Price Rs/MT"></div>
</div>
<div style="display:flex;gap:8px"><button class="btn btn-g" style="flex:1;padding:12px" onclick="saveProduct()"><i class="bi bi-check-lg"></i> Save Product</button><button class="btn btn-w" onclick="closeAddProduct()">Cancel</button></div>
<p style="font-size:10px;color:#666;margin-top:8px">Category from Category Master - Create new categories in Categories tab for future selection | Packaging Type: Jumbo, HDPE, Loose | Size: 10-40mm etc | Opening Qty + UOM</p>
</div>
</div>

<!-- ADD SBU MODAL - FIXED YARD -->
<div id="sbuModal" class="modal hidden">
<div class="modal-content">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><h3 style="margin:0"><i class="bi bi-building-add"></i> Add SBU - With Fixed Stock Yard Fields</h3><button class="btn btn-w" onclick="closeAddSBU()">✕ Close</button></div>
<input type="hidden" id="sbu_id">
<div class="form-box"><h3>SBU Details</h3><div class="row"><input id="sbu_name" placeholder="SBU Name e.g. Unit 1 72MT"><input id="sbu_address" placeholder="Address e.g. Plot 123, Jodhpur"></div></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center"><h4><i class="bi bi-fire"></i> Kilns</h4><button class="btn btn-g" onclick="addKilnField()"><i class="bi bi-plus"></i> Add Kiln</button></div><div id="kilnsContainer"><p style="font-size:11px;color:#888">No kilns - Fields: Kiln No, Capacity, Lining Date, Health, Product from Finished list</p></div></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center"><h4><i class="bi bi-gear"></i> Sizing Plants</h4><button class="btn btn-g" onclick="addSizingField()"><i class="bi bi-plus"></i> Add Sizing Plant</button></div><div id="sizingContainer"><p style="font-size:11px;color:#888">No sizing - Fields: Product from Finished, Capacity/hr, Machineries</p></div></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center"><h4><i class="bi bi-droplet"></i> Hydration Plants</h4><button class="btn btn-g" onclick="addHydrationField()"><i class="bi bi-plus"></i> Add Hydration Plant</button></div><div id="hydrationContainer"><p style="font-size:11px;color:#888">No hydration</p></div></div>

<div class="asset-section" style="border:2px solid var(--brass)"><div style="display:flex;justify-content:space-between;align-items:center"><h4><i class="bi bi-stack"></i> Stock Yards - FIXED - Yard Name, Product from ALL lists, Opening Qty, UOM, Packaging Type</h4><button class="btn btn-y" onclick="addYardField()"><i class="bi bi-plus"></i> Add Stock Yard</button></div><div id="yardsContainer"><p style="font-size:11px;color:#888">Fixed as requested: Yard Name, Add Product from ALL product lists, Opening Quantity, Unit of measurement, Packaging type for finished products</p></div></div>

<div style="margin-top:16px;display:flex;gap:8px"><button class="btn btn-g" style="flex:1;padding:12px" onclick="saveSBU()"><i class="bi bi-check-lg"></i> Save SBU</button><button class="btn btn-w" onclick="closeAddSBU()">Cancel</button></div>
</div>
</div>

<script>
function openTab(id){
 document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));
 document.getElementById(id).classList.remove('hidden');
 document.querySelectorAll('.menu').forEach(e=>e.classList.remove('active'));
 document.querySelectorAll('.menu').forEach(t=>{ if(t.getAttribute('onclick').includes("'"+id+"'")) t.classList.add('active'); });
 if(id==='sbus') loadSBUs();
 if(id==='products') loadProducts();
 if(id==='categories') loadCategories();
 if(id==='stock') loadStock();
}
document.getElementById('todayDate').innerText=new Date().toLocaleDateString('en-IN',{weekday:'short',day:'numeric',month:'short',year:'numeric'});

let kilnCounter=0, sizingCounter=0, hydCounter=0, yardCounter=0;

// CATEGORIES
function openAddCategory(){ document.getElementById('catFormBox').classList.remove('hidden'); document.getElementById('cat_id').value=''; document.getElementById('cat_name').value=''; document.getElementById('catFormTitle').innerText='Add New Category'; }
function closeCatForm(){ document.getElementById('catFormBox').classList.add('hidden'); }
function openAddCategoryFromProduct(){ openTab('categories'); openAddCategory(); }
async function loadCategories(){
 let res=await fetch('/api/categories'); let cats=await res.json();
 document.getElementById('catCount').innerText=cats.length;
 if(cats.length===0){ document.getElementById('categoryList').innerHTML='<p>No categories - Add new category for future selection - Masters empty as per v4.4 base</p>'; return; }
 let h='<table><tr><th>Category Name</th><th>Type (Raw/WIP/Finished)</th><th>Created</th><th>Products Count</th><th>Actions</th></tr>';
 for(let c of cats){
   let prodRes=await fetch('/api/products?category='+encodeURIComponent(c.name));
   let prods=await prodRes.json();
   h+=`<tr><td><b>${c.name}</b></td><td><span class="badge ok">${c.category_type}</span></td><td style="font-size:10px">${c.created_at||'-'}</td><td>${prods.length} products</td><td><button class="btn btn-w" onclick="editCategory(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCategory(${c.id})">Del</button></td></tr>`;
 }
 h+='</table><p style="font-size:10px;color:#666;margin-top:8px">Create categories for future selection in Product Category dropdown - e.g. Raw-Limestone, Finished-Quicklime 10-40mm, Finished-Hydrated 90% etc</p>';
 document.getElementById('categoryList').innerHTML=h;
 // update product category dropdown
 let opts=cats.map(c=>`<option value="${c.id}">${c.name} (${c.category_type})</option>`).join('');
 let prodCat=document.getElementById('prod_category');
 if(prodCat) prodCat.innerHTML=opts || '<option value="">No categories - Create in Categories tab</option>';
}
async function saveCategory(){
 let name=document.getElementById('cat_name').value;
 if(!name){alert('Enter Category Name'); return;}
 let id=document.getElementById('cat_id').value;
 let payload={name:name, category_type:document.getElementById('cat_type').value};
 let url=id?'/api/categories/'+id:'/api/categories';
 let method=id?'PUT':'POST';
 await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 alert(id?'✅ Category Updated':'✅ Category Created: '+name+' - Will appear in Product Category dropdown');
 closeCatForm(); loadCategories();
}
async function editCategory(id){ let res=await fetch('/api/categories/'+id); let c=await res.json(); document.getElementById('cat_id').value=c.id; document.getElementById('cat_name').value=c.name; document.getElementById('cat_type').value=c.category_type; document.getElementById('catFormTitle').innerText='Edit Category - '+c.name; document.getElementById('catFormBox').classList.remove('hidden'); }
async function delCategory(id){ if(!confirm('Delete Category? Products using this category will remain but category name will stay')) return; await fetch('/api/categories/'+id,{method:'DELETE'}); loadCategories(); }

// PRODUCTS - Category-wise landing
function openAddProduct(){ document.getElementById('productModal').classList.remove('hidden'); document.getElementById('prod_id').value=''; ['prod_name','prod_size','prod_opening','prod_location','prod_sale','prod_purchase'].forEach(id=>document.getElementById(id).value=''); loadCategories(); }
function closeAddProduct(){ document.getElementById('productModal').classList.add('hidden'); }
async function loadProducts(){
 let res=await fetch('/api/products'); let prods=await res.json();
 document.getElementById('prodCount').innerText=prods.length;
 if(prods.length===0){ document.getElementById('productList').innerHTML='<div style="text-align:center;padding:30px"><p>No products - Masters empty as per v4.4 base</p><button class="btn btn-y" onclick="openAddProduct()">+ Add First Product</button><p style="font-size:11px;color:#666;margin-top:8px">Add Product with: Product Name, Category (from Category Master), Packaging Type, Size, Opening Qty, UOM</p></div>'; return; }
 // Group by category
 let grouped={};
 prods.forEach(p=>{ let cat=p.category_name||'Uncategorized'; if(!grouped[cat]) grouped[cat]=[]; grouped[cat].push(p); });
 let h='';
 for(let cat in grouped){
   h+=`<div class="cat-group"><div class="cat-header"><span><i class="bi bi-tags"></i> ${cat} - ${grouped[cat].length} Products</span><span style="font-size:10px">${grouped[cat][0].category_type||''}</span></div><div style="padding:8px"><table><tr><th>Product Name</th><th>Packaging Type</th><th>Size</th><th>Opening Qty</th><th>UOM</th><th>Location</th><th>Sale/Purchase</th><th>Actions</th></tr>`;
   grouped[cat].forEach(p=>{
     h+=`<tr><td><b>${p.product_name}</b></td><td><span class="badge ok">${p.packaging_type||'-'}</span></td><td>${p.size||'-'}</td><td><b>${p.opening_qty} ${p.unit_of_measurement||''}</b><br><span style="font-size:9px">Total: ${p.total_stock_mt} MT</span></td><td>${p.unit_of_measurement||'-'}</td><td style="font-size:10px">${p.location||'-'}</td><td>Sale: Rs ${p.sale_price||0}<br>Pur: Rs ${p.purchase_price||0}</td><td><button class="btn btn-w" onclick="editProduct(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProduct(${p.id})">Del</button></td></tr>`;
   });
   h+='</table></div></div>';
 }
 document.getElementById('productList').innerHTML=h;
 // also for stock
 document.getElementById('stockTbl').innerHTML=h;
}
async function saveProduct(){
 let name=document.getElementById('prod_name').value;
 if(!name){alert('Enter Product Name'); return;}
 let catSelect=document.getElementById('prod_category');
 let catId=catSelect.value;
 let catName=catSelect.options[catSelect.selectedIndex]?catSelect.options[catSelect.selectedIndex].text:'';
 let payload={
   product_name:name,
   category_id:catId?parseInt(catId):null,
   category_name:catName,
   packaging_type:document.getElementById('prod_pack_type').value,
   size:document.getElementById('prod_size').value,
   opening_qty:parseFloat(document.getElementById('prod_opening').value||0),
   unit_of_measurement:document.getElementById('prod_uom').value,
   location:document.getElementById('prod_location').value,
   sale_price:parseFloat(document.getElementById('prod_sale').value||0),
   purchase_price:parseFloat(document.getElementById('prod_purchase').value||0)
 };
 let id=document.getElementById('prod_id').value;
 let url=id?'/api/products/'+id:'/api/products';
 let method=id?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json();
 alert(id?'✅ Product Updated':'✅ Product Created: '+d.product_name+' | Category: '+catName+' | Pack: '+payload.packaging_type+' | Size: '+payload.size+' | Opening: '+payload.opening_qty+' '+payload.unit_of_measurement);
 closeAddProduct(); loadProducts(); loadCategories();
}
async function editProduct(id){
 let res=await fetch('/api/products/'+id); let p=await res.json();
 document.getElementById('prod_id').value=p.id;
 document.getElementById('prod_name').value=p.product_name;
 // category
 await loadCategories();
 document.getElementById('prod_category').value=p.category_id||'';
 document.getElementById('prod_pack_type').value=p.packaging_type||'Loose';
 document.getElementById('prod_size').value=p.size||'';
 document.getElementById('prod_opening').value=p.opening_qty||0;
 document.getElementById('prod_uom').value=p.unit_of_measurement||'MT';
 document.getElementById('prod_location').value=p.location||'';
 document.getElementById('prod_sale').value=p.sale_price||0;
 document.getElementById('prod_purchase').value=p.purchase_price||0;
 document.getElementById('productModal').classList.remove('hidden');
}
async function delProduct(id){ if(!confirm('Delete Product?')) return; await fetch('/api/products/'+id,{method:'DELETE'}); loadProducts(); }

// SBU - Fixed Yard
function openAddSBU(){ document.getElementById('sbuModal').classList.remove('hidden'); resetSBUForm(); loadAllProductsForSBU(); }
function closeAddSBU(){ document.getElementById('sbuModal').classList.add('hidden'); }
function resetSBUForm(){
 document.getElementById('sbu_id').value=''; document.getElementById('sbu_name').value=''; document.getElementById('sbu_address').value='';
 document.getElementById('kilnsContainer').innerHTML='<p style="font-size:11px;color:#888">No kilns</p>';
 document.getElementById('sizingContainer').innerHTML='<p style="font-size:11px;color:#888">No sizing</p>';
 document.getElementById('hydrationContainer').innerHTML='<p style="font-size:11px;color:#888">No hydration</p>';
 document.getElementById('yardsContainer').innerHTML='<p style="font-size:11px;color:#888">Fixed: Yard Name, Product from ALL lists, Opening Qty, UOM, Packaging Type for finished</p>';
 kilnCounter=0; sizingCounter=0; hydCounter=0; yardCounter=0;
}
async function loadAllProductsForSBU(){
 let res=await fetch('/api/products'); let ps=await res.json();
 window.allProducts=ps;
 window.finishedProducts=ps.filter(p=> (p.category_name||'').toLowerCase().includes('finish') || p.category_type==='Finished');
}

function addKilnField(data=null){
 let container=document.getElementById('kilnsContainer');
 if(container.innerHTML.includes('No kilns')) container.innerHTML='';
 kilnCounter++;
 let id='kiln_'+kilnCounter;
 let prodOptions=(window.finishedProducts||[]).map(p=>`<option value="${p.id}" ${data && data.product_ids && data.product_ids.includes(p.id)?'selected':''}>${p.product_name} (${p.size||''})</option>`).join('');
 if(prodOptions==='') prodOptions='<option>No finished products - Create in Products tab</option>';
 let html=`<div id="${id}" class="form-box" style="background:white"><div style="display:flex;justify-content:space-between"><b>Kiln ${kilnCounter}</b><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Remove</button></div><div class="row"><input class="k_no" placeholder="Kiln No. e.g. Kiln 1" value="${data?data.kiln_no||'':''}"><input class="k_cap" type="number" placeholder="Production Capacity MT/day" value="${data?data.production_capacity||'':''}"><input class="k_lining" type="date" value="${data?data.lining_installation_date||''}"><select class="k_health"><option ${data&&data.health_status==='Good'?'selected':''}>Good</option><option ${data&&data.health_status==='Needs Repair'?'selected':''}>Needs Repair</option><option ${data&&data.health_status==='Critical'?'selected':''}>Critical</option><option ${data&&data.health_status==='New'?'selected':''}>New</option></select></div><div class="row"><select class="k_products" multiple style="height:60px">${prodOptions}</select></div></div>`;
 container.insertAdjacentHTML('beforeend', html);
}
function addSizingField(data=null){
 let container=document.getElementById('sizingContainer');
 if(container.innerHTML.includes('No sizing')) container.innerHTML='';
 sizingCounter++;
 let id='sizing_'+sizingCounter;
 let prodOptions=(window.finishedProducts||[]).map(p=>`<option value="${p.id}" ${data && data.product_ids && data.product_ids.includes(p.id)?'selected':''}>${p.product_name} (${p.size||''})</option>`).join('');
 let html=`<div id="${id}" class="form-box" style="background:white"><div style="display:flex;justify-content:space-between"><b>Sizing Plant ${sizingCounter}</b><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Remove</button></div><div class="row"><select class="s_products" multiple style="height:60px">${prodOptions}</select><input class="s_cap" type="number" placeholder="Capacity Per Hour MT/hr" value="${data?data.production_capacity_per_hour||'':''}"></div><div class="row"><textarea class="s_mach" placeholder="List of Machineries">${data?data.machineries||'':''}</textarea></div></div>`;
 container.insertAdjacentHTML('beforeend', html);
}
function addHydrationField(data=null){
 let container=document.getElementById('hydrationContainer');
 if(container.innerHTML.includes('No hydration')) container.innerHTML='';
 hydCounter++;
 let id='hyd_'+hydCounter;
 let prodOptions=(window.finishedProducts||[]).map(p=>`<option value="${p.id}" ${data && data.product_ids && data.product_ids.includes(p.id)?'selected':''}>${p.product_name} (${p.size||''})</option>`).join('');
 let html=`<div id="${id}" class="form-box" style="background:white"><div style="display:flex;justify-content:space-between"><b>Hydration Plant ${hydCounter}</b><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Remove</button></div><div class="row"><select class="h_products" multiple style="height:60px">${prodOptions}</select><input class="h_cap" type="number" placeholder="Production Capacity MT/day" value="${data?data.production_capacity||'':''}"></div><div class="row"><textarea class="h_mach" placeholder="List of machineries">${data?data.machineries||'':''}</textarea></div></div>`;
 container.insertAdjacentHTML('beforeend', html);
}
function addYardField(data=null){
 let container=document.getElementById('yardsContainer');
 if(container.innerHTML.includes('Fixed:')) container.innerHTML='';
 yardCounter++;
 let id='yard_'+yardCounter;
 let prodOptions=(window.allProducts||[]).map(p=>`<option value="${p.id}" ${data && data.product_ids && data.product_ids.includes(p.id)?'selected':''}>${p.product_name} (${p.category_name||''}) - ${p.size||''}</option>`).join('');
 if(prodOptions==='') prodOptions='<option>No products - Create in Products tab</option>';
 let html=`<div id="${id}" class="form-box" style="background:white;border:1px solid var(--brass)">
<div style="display:flex;justify-content:space-between"><b>Stock Yard ${yardCounter} - FIXED FIELDS</b><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Remove</button></div>
<div class="row"><input class="y_name" placeholder="Yard Name e.g. Limestone Yard 1, Finished Godown A" value="${data?data.yard_name||'':''}"><select class="y_products" multiple style="height:70px"><option disabled>Product from ALL product lists (as requested)</option>${prodOptions}</select></div>
<div class="row"><input class="y_opening" type="number" placeholder="Opening Quantity e.g. 100" value="${data?data.opening_quantity||''}"><select class="y_uom"><option ${data&&data.unit_of_measurement==='MT'?'selected':''}>MT</option><option ${data&&data.unit_of_measurement==='Bags'?'selected':''}>Bags</option><option ${data&&data.unit_of_measurement==='Kg'?'selected':''}>Kg</option><option ${data&&data.unit_of_measurement==='MT + Bags Combined'?'selected':''}>MT + Bags Combined</option><option ${data&&data.unit_of_measurement==='Quintals'?'selected':''}>Quintals</option></select><select class="y_pack"><option ${data&&data.packaging_type==='Loose'?'selected':''}>Loose</option><option ${data&&data.packaging_type==='Jumbo 1.2MT'?'selected':''}>Jumbo 1.2MT</option><option ${data&&data.packaging_type==='Jumbo 1.5MT'?'selected':''}>Jumbo 1.5MT</option><option ${data&&data.packaging_type==='HDPE 40kg'?'selected':''}>HDPE 40kg</option><option ${data&&data.packaging_type==='HDPE 25kg'?'selected':''}>HDPE 25kg</option><option ${data&&data.packaging_type==='Bulk'?'selected':''}>Bulk</option></select></div>
<p style="font-size:9px;color:#666">As requested: Yard Name, Product from ALL lists, Opening Qty, UOM, Packaging type for finished</p>
</div>`;
 container.insertAdjacentHTML('beforeend', html);
}

async function saveSBU(){
 let sbuName=document.getElementById('sbu_name').value;
 if(!sbuName){alert('Enter SBU Name'); return;}
 let kilns=[]; document.querySelectorAll('#kilnsContainer > div[id^="kiln_"]').forEach(div=>{ kilns.push({kiln_no:div.querySelector('.k_no').value, production_capacity:parseFloat(div.querySelector('.k_cap').value||0), lining_installation_date:div.querySelector('.k_lining').value, health_status:div.querySelector('.k_health').value, product_ids:Array.from(div.querySelector('.k_products').selectedOptions).map(o=>parseInt(o.value))}); });
 let sizings=[]; document.querySelectorAll('#sizingContainer > div[id^="sizing_"]').forEach(div=>{ sizings.push({product_ids:Array.from(div.querySelector('.s_products').selectedOptions).map(o=>parseInt(o.value)), production_capacity_per_hour:parseFloat(div.querySelector('.s_cap').value||0), machineries:div.querySelector('.s_mach').value}); });
 let hydrations=[]; document.querySelectorAll('#hydrationContainer > div[id^="hyd_"]').forEach(div=>{ hydrations.push({product_ids:Array.from(div.querySelector('.h_products').selectedOptions).map(o=>parseInt(o.value)), production_capacity:parseFloat(div.querySelector('.h_cap').value||0), machineries:div.querySelector('.h_mach').value}); });
 let yards=[]; document.querySelectorAll('#yardsContainer > div[id^="yard_"]').forEach(div=>{ yards.push({yard_name:div.querySelector('.y_name').value, product_ids:Array.from(div.querySelector('.y_products').selectedOptions).map(o=>parseInt(o.value)), opening_quantity:parseFloat(div.querySelector('.y_opening').value||0), unit_of_measurement:div.querySelector('.y_uom').value, packaging_type:div.querySelector('.y_pack').value}); });
 let payload={sbu_name:sbuName, address:document.getElementById('sbu_address').value, kilns:kilns, sizing_plants:sizings, hydration_plants:hydrations, stock_yards:yards};
 let sbuId=document.getElementById('sbu_id').value;
 let url=sbuId?'/api/sbus/'+sbuId:'/api/sbus';
 let method=sbuId?'PUT':'POST';
 let res=await fetch(url,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let d=await res.json();
 alert(sbuId?'✅ SBU Updated':'✅ SBU Created: '+d.sbu_name+' with '+kilns.length+' Kilns, '+sizings.length+' Sizing, '+hydrations.length+' Hydration, '+yards.length+' Yards (Fixed fields)');
 closeAddSBU(); loadSBUs();
}

async function loadSBUs(){
 let res=await fetch('/api/sbus'); let sbus=await res.json();
 document.getElementById('sbuCount').innerText=sbus.length;
 if(sbus.length===0){ document.getElementById('sbuList').innerHTML='<div style="text-align:center;padding:30px"><p>No SBUs - Masters empty</p><button class="btn btn-y" onclick="openAddSBU()">+ Add First SBU</button></div>'; return; }
 let h='';
 for(let s of sbus){
   h+=`<div class="card sbu-card"><div style="display:flex;justify-content:space-between"><div><h3 style="font-size:14px"><i class="bi bi-building"></i> ${s.sbu_name}</h3><p style="font-size:11px;color:#666"><i class="bi bi-geo-alt"></i> ${s.address||'No address'}</p><p style="font-size:10px"><span class="badge ok">${(s.kilns||[]).length} Kilns</span> <span class="badge ok">${(s.sizing_plants||[]).length} Sizing</span> <span class="badge ok">${(s.hydration_plants||[]).length} Hydration</span> <span class="badge ok">${(s.stock_yards||[]).length} Yards (Fixed)</span></p></div><div><button class="btn btn-w" onclick="editSBU(${s.id})">Edit</button> <button class="btn btn-r" onclick="delSBU(${s.id})">Del</button></div></div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin-top:10px">
<div><b style="font-size:11px">🔥 Kilns:</b>${(s.kilns||[]).map(k=>`<div style="font-size:11px;background:var(--alab);padding:6px;margin:4px 0;border-radius:6px"><b>${k.kiln_no}</b> - ${k.production_capacity} MT/day<br>Lining: ${k.lining_installation_date||'-'} | Health: ${k.health_status}<br>Products: ${(k.product_names||[]).join(', ')||'-'}</div>`).join('')||'<span style="font-size:11px;color:#888">No kilns</span>'}</div>
<div><b style="font-size:11px">⚙️ Sizing:</b>${(s.sizing_plants||[]).map(sp=>`<div style="font-size:11px;background:var(--alab);padding:6px;margin:4px 0;border-radius:6px">Cap: ${sp.production_capacity_per_hour} MT/hr<br>Products: ${(sp.product_names||[]).join(', ')||'-'}<br>Mach: ${sp.machineries||'-'}</div>`).join('')||'<span style="font-size:11px;color:#888">No sizing</span>'}</div>
<div><b style="font-size:11px">💧 Hydration:</b>${(s.hydration_plants||[]).map(hp=>`<div style="font-size:11px;background:var(--alab);padding:6px;margin:4px 0;border-radius:6px">Cap: ${hp.production_capacity} MT/day<br>Products: ${(hp.product_names||[]).join(', ')||'-'}<br>Mach: ${hp.machineries||'-'}</div>`).join('')||'<span style="font-size:11px;color:#888">No hydration</span>'}</div>
<div><b style="font-size:11px">📦 Stock Yards - FIXED:</b>${(s.stock_yards||[]).map(y=>`<div style="font-size:11px;background:#FFF8E1;padding:6px;margin:4px 0;border-radius:6px;border:1px solid var(--brass)"><b>${y.yard_name}</b><br>Products: ${(y.product_names||[]).join(', ')||'-'}<br>Opening: <b>${y.opening_quantity} ${y.unit_of_measurement}</b><br>Pack: ${y.packaging_type||'-'}</div>`).join('')||'<span style="font-size:11px;color:#888">No yards - Add with Fixed fields</span>'}</div>
</div></div>`;
 }
 document.getElementById('sbuList').innerHTML=h;
}
async function editSBU(id){ let res=await fetch('/api/sbus/'+id); let s=await res.json(); document.getElementById('sbu_id').value=s.id; document.getElementById('sbu_name').value=s.sbu_name; document.getElementById('sbu_address').value=s.address; openAddSBU(); setTimeout(()=>{ document.getElementById('kilnsContainer').innerHTML=''; document.getElementById('sizingContainer').innerHTML=''; document.getElementById('hydrationContainer').innerHTML=''; document.getElementById('yardsContainer').innerHTML=''; (s.kilns||[]).forEach(k=>addKilnField(k)); (s.sizing_plants||[]).forEach(sp=>addSizingField(sp)); (s.hydration_plants||[]).forEach(hp=>addHydrationField(hp)); (s.stock_yards||[]).forEach(y=>addYardField(y)); },400); }
async function delSBU(id){ if(!confirm('Delete SBU?')) return; await fetch('/api/sbus/'+id,{method:'DELETE'}); loadSBUs(); }

loadProducts(); loadCategories(); loadSBUs();
</script>
</body></html>
    """

@app.route('/api/categories', methods=['GET','POST'])
def categories_api():
    if request.method=='POST':
        data=request.json
        c=CategoryMaster(name=data.get('name'), category_type=data.get('category_type','Finished'))
        db.session.add(c)
        db.session.commit()
        return jsonify({'id':c.id,'name':c.name})
    cats=CategoryMaster.query.all()
    return jsonify([{'id':c.id,'name':c.name,'category_type':c.category_type,'created_at':c.created_at} for c in cats])

@app.route('/api/categories/<int:cid>', methods=['GET','PUT','DELETE'])
def category_one(cid):
    c=CategoryMaster.query.get_or_404(cid)
    if request.method=='GET':
        return jsonify({'id':c.id,'name':c.name,'category_type':c.category_type})
    elif request.method=='PUT':
        data=request.json
        c.name=data.get('name',c.name)
        c.category_type=data.get('category_type',c.category_type)
        db.session.commit()
        return jsonify({'status':'updated'})
    else:
        db.session.delete(c)
        db.session.commit()
        return jsonify({'status':'deleted'})

@app.route('/api/products', methods=['GET','POST'])
def products_api():
    if request.method=='POST':
        data=request.json
        cat_name=data.get('category_name','')
        # If category_id provided, get name
        if data.get('category_id'):
            cat=CategoryMaster.query.get(data.get('category_id'))
            if cat:
                cat_name=cat.name
        p=Product(product_name=data.get('product_name'), category_id=data.get('category_id'), category_name=cat_name, packaging_type=data.get('packaging_type'), size=data.get('size'), opening_qty=float(data.get('opening_qty',0)), unit_of_measurement=data.get('unit_of_measurement','MT'), location=data.get('location',''), sale_price=float(data.get('sale_price',0)), purchase_price=float(data.get('purchase_price',0)), loose_stock_mt=float(data.get('opening_qty',0)), total_stock_mt=float(data.get('opening_qty',0)))
        db.session.add(p)
        db.session.commit()
        return jsonify({'id':p.id,'product_name':p.product_name})
    # Filter by category name if query param
    cat_filter=request.args.get('category')
    if cat_filter:
        prods=Product.query.filter_by(category_name=cat_filter).all()
    else:
        prods=Product.query.all()
    return jsonify([{'id':p.id,'product_name':p.product_name,'category_id':p.category_id,'category_name':p.category_name,'category_type': (CategoryMaster.query.get(p.category_id).category_type if p.category_id else 'Finished'), 'packaging_type':p.packaging_type,'size':p.size,'opening_qty':p.opening_qty,'unit_of_measurement':p.unit_of_measurement,'location':p.location,'sale_price':p.sale_price,'purchase_price':p.purchase_price,'loose_stock_mt':p.loose_stock_mt,'total_stock_mt':p.total_stock_mt} for p in prods])

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
def product_one(pid):
    p=Product.query.get_or_404(pid)
    if request.method=='GET':
        return jsonify({'id':p.id,'product_name':p.product_name,'category_id':p.category_id,'category_name':p.category_name,'packaging_type':p.packaging_type,'size':p.size,'opening_qty':p.opening_qty,'unit_of_measurement':p.unit_of_measurement,'location':p.location,'sale_price':p.sale_price,'purchase_price':p.purchase_price})
    elif request.method=='PUT':
        data=request.json
        p.product_name=data.get('product_name',p.product_name)
        if data.get('category_id'):
            p.category_id=data.get('category_id')
            cat=CategoryMaster.query.get(data.get('category_id'))
            if cat:
                p.category_name=cat.name
        if data.get('category_name'):
            p.category_name=data.get('category_name')
        p.packaging_type=data.get('packaging_type',p.packaging_type)
        p.size=data.get('size',p.size)
        p.opening_qty=float(data.get('opening_qty',p.opening_qty))
        p.unit_of_measurement=data.get('unit_of_measurement',p.unit_of_measurement)
        p.location=data.get('location',p.location)
        p.sale_price=float(data.get('sale_price',p.sale_price))
        p.purchase_price=float(data.get('purchase_price',p.purchase_price))
        p.total_stock_mt=p.opening_qty
        p.loose_stock_mt=p.opening_qty
        db.session.commit()
        return jsonify({'status':'updated'})
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
            ka=KilnAsset(sbu_id=sbu.id, kiln_no=k.get('kiln_no'), production_capacity=float(k.get('production_capacity',0)), lining_installation_date=k.get('lining_installation_date',''), health_status=k.get('health_status','Good'), product_ids=json.dumps(k.get('product_ids',[])))
            db.session.add(ka)
        for sp in data.get('sizing_plants',[]):
            sa=SizingPlantAsset(sbu_id=sbu.id, product_ids=json.dumps(sp.get('product_ids',[])), production_capacity_per_hour=float(sp.get('production_capacity_per_hour',0)), machineries=sp.get('machineries',''))
            db.session.add(sa)
        for hp in data.get('hydration_plants',[]):
            ha=HydrationPlantAsset(sbu_id=sbu.id, product_ids=json.dumps(hp.get('product_ids',[])), production_capacity=float(hp.get('production_capacity',0)), machineries=hp.get('machineries',''))
            db.session.add(ha)
        for y in data.get('stock_yards',[]):
            ya=StockYardAsset(sbu_id=sbu.id, yard_name=y.get('yard_name'), product_ids=json.dumps(y.get('product_ids',[])), opening_quantity=float(y.get('opening_quantity',0)), unit_of_measurement=y.get('unit_of_measurement','MT'), packaging_type=y.get('packaging_type','Loose'), capacity_mt=float(y.get('opening_quantity',0)))
            db.session.add(ya)
        db.session.commit()
        return jsonify({'id':sbu.id,'sbu_name':sbu.sbu_name})
    sbus=SBU.query.all()
    result=[]
    all_products={p.id:p.product_name for p in Product.query.all()}
    def resolve(ids_json):
        try:
            ids=json.loads(ids_json) if ids_json else []
            return [all_products.get(i,f'ID {i}') for i in ids]
        except:
            return []
    for s in sbus:
        kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
        sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
        hyds=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
        yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
        result.append({
            'id':s.id,'sbu_name':s.sbu_name,'address':s.address,
            'kilns':[{'kiln_no':k.kiln_no,'production_capacity':k.production_capacity,'lining_installation_date':k.lining_installation_date,'health_status':k.health_status,'product_ids':json.loads(k.product_ids or '[]'),'product_names':resolve(k.product_ids)} for k in kilns],
            'sizing_plants':[{'product_ids':json.loads(sp.product_ids or '[]'),'product_names':resolve(sp.product_ids),'production_capacity_per_hour':sp.production_capacity_per_hour,'machineries':sp.machineries} for sp in sizings],
            'hydration_plants':[{'product_ids':json.loads(hp.product_ids or '[]'),'product_names':resolve(hp.product_ids),'production_capacity':hp.production_capacity,'machineries':hp.machineries} for hp in hyds],
            'stock_yards':[{'yard_name':y.yard_name,'product_ids':json.loads(y.product_ids or '[]'),'product_names':resolve(y.product_ids),'opening_quantity':y.opening_quantity,'unit_of_measurement':y.unit_of_measurement,'packaging_type':y.packaging_type,'capacity_mt':y.capacity_mt} for y in yards]
        })
    return jsonify(result)

@app.route('/api/sbus/<int:sid>', methods=['GET','PUT','DELETE'])
def sbu_one(sid):
    s=SBU.query.get_or_404(sid)
    all_products={p.id:p.product_name for p in Product.query.all()}
    def resolve(ids_json):
        try:
            ids=json.loads(ids_json) if ids_json else []
            return [all_products.get(i,f'ID {i}') for i in ids]
        except:
            return []
    if request.method=='GET':
        kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
        sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
        hyds=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
        yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
        return jsonify({
            'id':s.id,'sbu_name':s.sbu_name,'address':s.address,
            'kilns':[{'kiln_no':k.kiln_no,'production_capacity':k.production_capacity,'lining_installation_date':k.lining_installation_date,'health_status':k.health_status,'product_ids':json.loads(k.product_ids or '[]'),'product_names':resolve(k.product_ids)} for k in kilns],
            'sizing_plants':[{'product_ids':json.loads(sp.product_ids or '[]'),'product_names':resolve(sp.product_ids),'production_capacity_per_hour':sp.production_capacity_per_hour,'machineries':sp.machineries} for sp in sizings],
            'hydration_plants':[{'product_ids':json.loads(hp.product_ids or '[]'),'product_names':resolve(hp.product_ids),'production_capacity':hp.production_capacity,'machineries':hp.machineries} for hp in hyds],
            'stock_yards':[{'yard_name':y.yard_name,'product_ids':json.loads(y.product_ids or '[]'),'product_names':resolve(y.product_ids),'opening_quantity':y.opening_quantity,'unit_of_measurement':y.unit_of_measurement,'packaging_type':y.packaging_type} for y in yards]
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
            ka=KilnAsset(sbu_id=s.id, kiln_no=k.get('kiln_no'), production_capacity=float(k.get('production_capacity',0)), lining_installation_date=k.get('lining_installation_date',''), health_status=k.get('health_status','Good'), product_ids=json.dumps(k.get('product_ids',[])))
            db.session.add(ka)
        for sp in data.get('sizing_plants',[]):
            sa=SizingPlantAsset(sbu_id=s.id, product_ids=json.dumps(sp.get('product_ids',[])), production_capacity_per_hour=float(sp.get('production_capacity_per_hour',0)), machineries=sp.get('machineries',''))
            db.session.add(sa)
        for hp in data.get('hydration_plants',[]):
            ha=HydrationPlantAsset(sbu_id=s.id, product_ids=json.dumps(hp.get('product_ids',[])), production_capacity=float(hp.get('production_capacity',0)), machineries=hp.get('machineries',''))
            db.session.add(ha)
        for y in data.get('stock_yards',[]):
            ya=StockYardAsset(sbu_id=s.id, yard_name=y.get('yard_name'), product_ids=json.dumps(y.get('product_ids',[])), opening_quantity=float(y.get('opening_quantity',0)), unit_of_measurement=y.get('unit_of_measurement','MT'), packaging_type=y.get('packaging_type','Loose'), capacity_mt=float(y.get('opening_quantity',0)))
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

@app.route('/api/health')
def health():
    return jsonify({"status":"LIVE","version":"v4.6 SBU Yard Fixed + Products Category-wise","base":"v4.4 Base Remembered","fix":"Stock Yard fields: Yard Name, Product from ALL lists, Opening Qty, UOM, Packaging Type","refinement":"Products Master: Category-wise landing, Add Product: Name, Category (from Category Master), Packaging Type, Size, Opening Qty, UOM, Category Master create for future selection","url":"https://lemon-erp.onrender.com"})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
