
"""
LEMON ERP - MASTER WORKFLOW - v4.4.8
BASE: v1.3.py = v4.4.7 Fixed + Masters reordered
Fixes in v4.4.8:
- Sidebar reorganized: Moved Product Category, Products, SBUs from MAIN to MASTERS in sequence: Product Category first, Products second, SBUs third - to ensure data entry flow Category -> Product -> SBU
- MAIN now only Dashboard
- MASTERS order: Product Category, Products, SBUs, Vendors, Customers, Cost, Mobile
- Everything else 100% unchanged from v1.3.py
DB: lemon_erp_v44_1_category.db single file
File: backend/app_v4_final.py
URL: https://lemon-erp.onrender.com
"""

from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, os, re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lemon-erp-v44-8-masters-reordered'
db_path = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'instance', 'lemon_erp_v44_1_category.db'))
os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(db_path)}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True)
    hsn_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    loose_stock_mt = db.Column(db.Float, default=0)
    jumbo_mt = db.Column(db.Float, default=0)
    hdpe_40kg_mt = db.Column(db.Float, default=0)
    total_stock_mt = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    sale_price = db.Column(db.Float, default=0)
    purchase_price = db.Column(db.Float, default=0)
    location = db.Column(db.String(100), default='')

class SBU(db.Model):
    __tablename__ = 'sbu'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class KilnAsset(db.Model):
    __tablename__ = 'kiln_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    kiln_no = db.Column(db.String(50))
    lining_installation_date = db.Column(db.String(20), default='')
    health_status = db.Column(db.String(50), default='Good')
    products_capacity = db.Column(db.Text) # JSON list

class SizingPlantAsset(db.Model):
    __tablename__ = 'sizing_plant_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    plant_no = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)
    machineries = db.Column(db.Text, default='')

class HydrationPlantAsset(db.Model):
    __tablename__ = 'hydration_plant_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    plant_no = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)
    machineries = db.Column(db.Text, default='')

class StockYardAsset(db.Model):
    __tablename__ = 'stock_yard_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    yard_name = db.Column(db.String(100))
    yard_items = db.Column(db.Text) # JSON

# Other modules - keep same as v4.4.6 minimal schemas
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    gst_no = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    credit_limit = db.Column(db.Float, default=0)
    pending_due = db.Column(db.Float, default=0)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    gst_no = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    pending_receivable = db.Column(db.Float, default=0)

class Packaging(db.Model):
    __tablename__ = 'packaging'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pack_type = db.Column(db.String(100))
    pack_cat = db.Column(db.String(50))
    capacity = db.Column(db.Float, default=0)
    closing = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))

class MO(db.Model):
    __tablename__ = 'manufacturing_order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu = db.Column(db.String(100))
    type = db.Column(db.String(50))
    unit = db.Column(db.String(100))
    limestone_mt = db.Column(db.Float, default=0)
    petcoke_mt = db.Column(db.Float, default=0)
    output_mt = db.Column(db.Float, default=0)
    wastage = db.Column(db.Float, default=0)
    input_product = db.Column(db.String(100))
    output_product = db.Column(db.String(100))
    operator = db.Column(db.String(100))
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class PO(db.Model):
    __tablename__ = 'po'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor = db.Column(db.String(100))
    material = db.Column(db.String(100))
    qty = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))
    status = db.Column(db.String(50))

class GRN(db.Model):
    __tablename__ = 'grn'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_no = db.Column(db.String(100))
    material = db.Column(db.String(100))
    unit = db.Column(db.String(100))
    gross_kg = db.Column(db.Float, default=0)
    tare_kg = db.Column(db.Float, default=0)
    vendor = db.Column(db.String(100))
    net_kg = db.Column(db.Float, default=0)

class Dispatch(db.Model):
    __tablename__ = 'dispatch'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer = db.Column(db.String(100))
    vehicle_no = db.Column(db.String(100))
    product = db.Column(db.String(100))
    qty_mt = db.Column(db.Float, default=0)
    qr_bags = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(100))

class QRBag(db.Model):
    __tablename__ = 'qr_bag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bag_id = db.Column(db.String(100), unique=True)
    product = db.Column(db.String(100))
    weight = db.Column(db.Float)
    unit = db.Column(db.String(100))
    qr_data = db.Column(db.Text)
    qr_base64 = db.Column(db.Text)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

with app.app_context():
    db.create_all()

# Helpers
def generate_product_code(category, count):
    base = ''.join([c for c in category if c.isalnum()])[:4].upper()
    if len(base)<4: base = (base + 'XXXX')[:4]
    return f"{base}-{count:04d}"

def resolve_pc(pc_json):
    try:
        lst = json.loads(pc_json) if isinstance(pc_json, str) else (pc_json or [])
    except:
        lst = []
    res=[]
    for it in lst:
        pid = it.get('product_id')
        prod = Product.query.get(pid) if pid else None
        res.append({
            'product_id': pid,
            'product_name': prod.name if prod else f"ID {pid}",
            'product_code': prod.product_code if prod else '',
            'category': prod.category if prod else '',
            'capacity_per_day': it.get('capacity_per_day') or it.get('capacity') or 0,
            'capacity_per_hour': it.get('capacity_per_hour') or it.get('capacity') or 0,
            'capacity': it.get('capacity') or it.get('capacity_per_day') or it.get('capacity_per_hour') or 0,
            'machineries': it.get('machineries',''),
            'machineries_line': it.get('machineries',''),
        })
    return res

def resolve_yard(yard_json):
    try:
        lst = json.loads(yard_json) if isinstance(yard_json, str) else (yard_json or [])
    except:
        lst=[]
    res=[]
    for it in lst:
        pid = it.get('product_id')
        prod = Product.query.get(pid) if pid else None
        res.append({
            'product_id': pid,
            'product_name': prod.name if prod else f"ID {pid}",
            'product_code': prod.product_code if prod else '',
            'opening_stock': it.get('opening_stock') or it.get('opening') or 0,
        })
    return res

# ========== API ==========
@app.route('/api/health')
def health():
    return jsonify(status='LIVE', version='v4.4.7 - SBUs fixed tabular duplicate', db_file='lemon_erp_v44_1_category.db', url='https://lemon-erp.onrender.com')

# Product Category
@app.route('/api/product_categories', methods=['GET','POST'])
def pc_list():
    if request.method=='GET':
        cats = ProductCategory.query.order_by(ProductCategory.id.desc()).all()
        return jsonify([{'id':c.id,'category_name':c.category_name,'created_at':c.created_at} for c in cats])
    data=request.get_json() or {}
    name=(data.get('category_name') or '').strip()
    if not name: return jsonify(error='Category Name required'),400
    if ProductCategory.query.filter_by(category_name=name).first():
        return jsonify(error='Category already exists'),400
    cat=ProductCategory(category_name=name)
    db.session.add(cat); db.session.commit()
    return jsonify(id=cat.id, category_name=cat.category_name)

@app.route('/api/product_categories/<int:id>', methods=['GET','PUT','DELETE'])
def pc_one(id):
    cat=ProductCategory.query.get_or_404(id)
    if request.method=='GET':
        return jsonify(id=cat.id, category_name=cat.category_name, created_at=cat.created_at)
    if request.method=='PUT':
        data=request.get_json() or {}
        name=(data.get('category_name') or '').strip()
        if not name: return jsonify(error='Required'),400
        exists=ProductCategory.query.filter(ProductCategory.category_name==name, ProductCategory.id!=id).first()
        if exists: return jsonify(error='Exists'),400
        cat.category_name=name; db.session.commit()
        return jsonify(ok=True)
    db.session.delete(cat); db.session.commit()
    return jsonify(ok=True)

# Products
@app.route('/api/products', methods=['GET','POST'])
def prod_list():
    if request.method=='GET':
        prods=Product.query.order_by(Product.id.desc()).all()
        return jsonify([{'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description,'total_stock_mt':p.total_stock_mt} for p in prods])
    data=request.get_json() or {}
    for f in ['name','category','hsn_code','description']:
        if not (data.get(f) or '').strip(): return jsonify(error=f'{f} mandatory'),400
    cnt=Product.query.filter_by(category=data['category']).count()+1
    code=generate_product_code(data['category'], cnt)
    while Product.query.filter_by(product_code=code).first():
        cnt+=1; code=generate_product_code(data['category'], cnt)
    p=Product(name=data['name'].strip(), category=data['category'].strip(), product_code=code, hsn_code=data['hsn_code'].strip(), description=data['description'].strip())
    db.session.add(p); db.session.commit()
    return jsonify(id=p.id, name=p.name, product_code=p.product_code, hsn_code=p.hsn_code, category=p.category)

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
def prod_one(pid):
    p=Product.query.get_or_404(pid)
    if request.method=='GET': return jsonify(id=p.id,name=p.name,category=p.category,product_code=p.product_code,hsn_code=p.hsn_code,description=p.description)
    if request.method=='PUT':
        data=request.get_json() or {}
        for f in ['name','category','hsn_code','description']:
            if not (data.get(f) or '').strip(): return jsonify(error=f'{f} mandatory'),400
        p.name=data['name'].strip(); p.category=data['category'].strip(); p.hsn_code=data['hsn_code'].strip(); p.description=data['description'].strip()
        db.session.commit(); return jsonify(ok=True)
    db.session.delete(p); db.session.commit(); return jsonify(ok=True)

# SBUs - v4.4.7 FINAL
@app.route('/api/sbus', methods=['GET','POST'])
def sbu_list():
    if request.method=='GET':
        sbus=SBU.query.order_by(SBU.id.desc()).all()
        out=[]
        all_prods={pr.id: pr for pr in Product.query.all()}
        for s in sbus:
            kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
            sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
            hydrations=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
            yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
            def res_k(k):
                pcs=[]
                try: raw=json.loads(k.products_capacity) if k.products_capacity else []
                except: raw=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else f"ID {it.get('product_id")}', 'product_code':prod.product_code if prod else '', 'capacity_per_day': it.get('capacity_per_day') or it.get('capacity') or 0, 'capacity': it.get('capacity_per_day') or 0})
                return {'id':k.id,'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':pcs,'products_capacity_raw':k.products_capacity}
            def res_sz(sp):
                try: raw=json.loads(sp.products_capacity) if sp.products_capacity else []
                except: raw=[]
                pcs=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else f"ID {it.get('product_id")}', 'product_code':prod.product_code if prod else '', 'capacity_per_hour':it.get('capacity_per_hour') or it.get('capacity') or 0, 'capacity':it.get('capacity_per_hour') or 0, 'machineries':it.get('machineries','')})
                return {'id':sp.id,'plant_no':sp.plant_no,'products_capacity':pcs,'products_capacity_raw':sp.products_capacity,'machineries':sp.machineries}
            def res_hy(h):
                try: raw=json.loads(h.products_capacity) if h.products_capacity else []
                except: raw=[]
                pcs=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else '', 'product_code':prod.product_code if prod else '', 'capacity_per_hour':it.get('capacity_per_hour') or 0, 'machineries':it.get('machineries','')})
                return {'id':h.id,'plant_no':h.plant_no,'products_capacity':pcs,'products_capacity_raw':h.products_capacity,'machineries':h.machineries}
            def res_y(y):
                try: raw=json.loads(y.yard_items) if y.yard_items else []
                except: raw=[]
                items=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    items.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else '', 'product_code':prod.product_code if prod else '', 'opening_stock':it.get('opening_stock') or it.get('opening') or 0})
                return {'id':y.id,'yard_name':y.yard_name,'yard_items':items,'yard_items_raw':y.yard_items}
            out.append({'id':s.id,'sbu_name':s.sbu_name,'address':s.address,'kilns':[res_k(k) for k in kilns],'sizing_plants':[res_sz(sp) for sp in sizings],'hydration_plants':[res_hy(h) for h in hydrations],'stock_yards':[res_y(y) for y in yards]})
        return jsonify(out)
    # POST
    data=request.get_json() or {}
    sbu_name=(data.get('sbu_name') or '').strip()
    if not sbu_name: return jsonify(error='SBU Name required'),400
    s=SBU(sbu_name=sbu_name, address=data.get('address',''))
    db.session.add(s); db.session.flush()
    for k in data.get('kilns',[]):
        db.session.add(KilnAsset(sbu_id=s.id, kiln_no=k.get('kiln_no',''), lining_installation_date=k.get('lining_installation_date') or k.get('lining_date') or '', health_status=k.get('health_status','Good'), products_capacity=json.dumps(k.get('products_capacity',[]))))
    for sp in data.get('sizing_plants',[]):
        db.session.add(SizingPlantAsset(sbu_id=s.id, plant_no=sp.get('plant_no',''), products_capacity=json.dumps(sp.get('products_capacity',[])), machineries=sp.get('machineries','')))
    for hp in data.get('hydration_plants',[]):
        db.session.add(HydrationPlantAsset(sbu_id=s.id, plant_no=hp.get('plant_no',''), products_capacity=json.dumps(hp.get('products_capacity',[])), machineries=hp.get('machineries','')))
    for y in data.get('stock_yards',[]):
        db.session.add(StockYardAsset(sbu_id=s.id, yard_name=y.get('yard_name',''), yard_items=json.dumps(y.get('yard_items',[]))))
    db.session.commit()
    return jsonify(id=s.id, sbu_name=s.sbu_name)

@app.route('/api/sbus/<int:sid>', methods=['GET','PUT','DELETE'])
def sbu_one(sid):
    s=SBU.query.get_or_404(sid)
    if request.method=='GET':
        kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
        sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
        hydrations=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
        yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
        return jsonify(id=s.id, sbu_name=s.sbu_name, address=s.address,
                       kilns=[{'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':json.loads(k.products_capacity) if k.products_capacity else [],'products_capacity_raw':k.products_capacity} for k in kilns],
                       sizing_plants=[{'plant_no':sp.plant_no,'products_capacity':json.loads(sp.products_capacity) if sp.products_capacity else [],'products_capacity_raw':sp.products_capacity,'machineries':sp.machineries} for sp in sizings],
                       hydration_plants=[{'plant_no':h.plant_no,'products_capacity':json.loads(h.products_capacity) if h.products_capacity else [],'products_capacity_raw':h.products_capacity,'machineries':h.machineries} for h in hydrations],
                       stock_yards=[{'yard_name':y.yard_name,'yard_items':json.loads(y.yard_items) if y.yard_items else [],'yard_items_raw':y.yard_items} for y in yards])
    if request.method=='PUT':
        data=request.get_json() or {}
        s.sbu_name=(data.get('sbu_name') or s.sbu_name).strip()
        s.address=data.get('address', s.address)
        KilnAsset.query.filter_by(sbu_id=s.id).delete()
        SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
        HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
        StockYardAsset.query.filter_by(sbu_id=s.id).delete()
        for k in data.get('kilns',[]):
            db.session.add(KilnAsset(sbu_id=s.id, kiln_no=k.get('kiln_no',''), lining_installation_date=k.get('lining_installation_date') or k.get('lining_date') or '', health_status=k.get('health_status','Good'), products_capacity=json.dumps(k.get('products_capacity',[]))))
        for sp in data.get('sizing_plants',[]):
            db.session.add(SizingPlantAsset(sbu_id=s.id, plant_no=sp.get('plant_no',''), products_capacity=json.dumps(sp.get('products_capacity',[])), machineries=sp.get('machineries','')))
        for hp in data.get('hydration_plants',[]):
            db.session.add(HydrationPlantAsset(sbu_id=s.id, plant_no=hp.get('plant_no',''), products_capacity=json.dumps(hp.get('products_capacity',[])), machineries=hp.get('machineries','')))
        for y in data.get('stock_yards',[]):
            db.session.add(StockYardAsset(sbu_id=s.id, yard_name=y.get('yard_name',''), yard_items=json.dumps(y.get('yard_items',[]))))
        db.session.commit()
        return jsonify(ok=True)
    # DELETE
    KilnAsset.query.filter_by(sbu_id=s.id).delete()
    SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
    HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
    StockYardAsset.query.filter_by(sbu_id=s.id).delete()
    db.session.delete(s); db.session.commit()
    return jsonify(ok=True)

# Other modules API minimal to keep UI working
@app.route('/api/inventory/combined')
def inv_combined():
    prods=Product.query.all()
    raw=[{'product_code':p.product_code,'hsn_code':p.hsn_code,'name':p.name,'total_mt':p.total_stock_mt,'status':'OK'} for p in prods if 'raw' in p.category.lower() or 'lime' in p.category.lower()]
    finished=[{'product_code':p.product_code,'hsn_code':p.hsn_code,'name':p.name,'total_mt':p.total_stock_mt,'status':'OK'} for p in prods]
    return jsonify(raw=raw, wip=[], finished=finished, total_value_lakh=sum([p.total_stock_mt*1000/100000 for p in prods]))

@app.route('/api/vendors', methods=['GET','POST'])
def vendors_api():
    if request.method=='GET': return jsonify([{'id':v.id,'name':v.name,'type':v.type,'gst_no':v.gst_no,'contact':v.contact} for v in Vendor.query.all()])
    d=request.get_json() or {}; v=Vendor(name=d.get('name'), type=d.get('type'), gst_no=d.get('gst_no'), contact=d.get('contact')); db.session.add(v); db.session.commit(); return jsonify(ok=True)

@app.route('/api/vendors/<int:id>', methods=['PUT','DELETE'])
def vendor_one(id):
    v=Vendor.query.get_or_404(id)
    if request.method=='DELETE': db.session.delete(v); db.session.commit(); return jsonify(ok=True)
    d=request.get_json() or {}; v.name=d.get('name',v.name); db.session.commit(); return jsonify(ok=True)

@app.route('/api/customers', methods=['GET','POST'])
def customers_api():
    if request.method=='GET': return jsonify([{'id':c.id,'name':c.name,'type':c.type} for c in Customer.query.all()])
    d=request.get_json() or {}; c=Customer(name=d.get('name'), type=d.get('type')); db.session.add(c); db.session.commit(); return jsonify(ok=True)

@app.route('/api/customers/<int:id>', methods=['PUT','DELETE'])
def cust_one(id):
    c=Customer.query.get_or_404(id)
    if request.method=='DELETE': db.session.delete(c); db.session.commit(); return jsonify(ok=True)
    return jsonify(ok=True)

@app.route('/api/manufacturing_orders', methods=['GET','POST'])
def mo_api():
    if request.method=='GET': return jsonify([{'id':m.id,'unit':m.unit} for m in MO.query.all()])
    d=request.get_json() or {}; m=MO(sbu=d.get('sbu'), type=d.get('type'), unit=d.get('unit')); db.session.add(m); db.session.commit(); return jsonify(ok=True)

@app.route('/api/mo/total')
def mo_total(): return jsonify(total=MO.query.count())

@app.route('/api/po', methods=['GET','POST'])
def po_api():
    if request.method=='GET': return jsonify([])
    return jsonify(ok=True)

@app.route('/api/grn', methods=['GET','POST'])
def grn_api():
    if request.method=='GET': return jsonify([])
    return jsonify(ok=True)

@app.route('/api/dispatch', methods=['GET','POST'])
def disp_api():
    if request.method=='GET': return jsonify([])
    return jsonify(ok=True)

@app.route('/api/packaging', methods=['GET','POST'])
def pack_api():
    if request.method=='GET': return jsonify([])
    return jsonify(ok=True)

@app.route('/api/qr_generate', methods=['POST'])
def qr_gen():
    import qrcode, io, base64
    d=request.get_json() or {}
    cnt=QRBag.query.count()+1
    bag_id=f"JMB-{d.get('product','PROD')}-2026-{cnt:05d}"
    qr_data=f"{bag_id}|{d.get('product')}|{d.get('weight')} MT|{d.get('unit')}"
    qr=qrcode.QRCode(box_size=8, border=3); qr.add_data(qr_data); qr.make(fit=True)
    img=qr.make_image(fill_color="#1A2E1E", back_color="#FAF6F0")
    buf=io.BytesIO(); img.save(buf, format='PNG'); b64=base64.b64encode(buf.getvalue()).decode()
    qb=QRBag(bag_id=bag_id, product=d.get('product'), weight=d.get('weight'), unit=d.get('unit'), qr_data=qr_data, qr_base64=b64)
    db.session.add(qb); db.session.commit()
    return jsonify(bag_id=bag_id, qr_data=qr_data, qr_base64=b64)

@app.route('/api/qr_list')
def qr_list(): return jsonify([{'bag_id':q.bag_id,'product':q.product} for q in QRBag.query.order_by(QRBag.id.desc()).all()])

# ========== FRONTEND HTML - v4.4.7 ==========
HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemon ERP v4.4.7 - SBUs Fixed Tabular Duplicate</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--line:#E8E0D5;--gray:#F6F5F3}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui;background:var(--gray)}
.topnav{background:var(--green);color:white;padding:0 14px;display:flex;justify-content:space-between;align-items:center;height:44px;position:sticky;top:0;z-index:200}
.brand{font-weight:900;font-size:15px} .brand span{color:var(--lemon)}
.layout{display:flex}
.sidebar{width:210px;background:white;border-right:1px solid var(--line);padding:10px 0;position:sticky;top:44px;height:calc(100vh - 44px);overflow-y:auto}
.sidebar h4{font-size:10px;color:#888;margin:14px 10px 4px;text-transform:uppercase;letter-spacing:0.6px}
.menu{padding:7px 10px;margin:2px 6px;border-radius:7px;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:12px;color:#444}
.menu:hover{background:var(--alab)} .menu.active{background:var(--green);color:var(--brass)}
.content{flex:1;padding:14px;max-width:1500px}
.card{background:white;border-radius:10px;padding:14px;margin:8px 0;box-shadow:0 2px 6px rgba(0,0,0,0.04);border:1px solid var(--line)}
.card h3{margin:0 0 10px;font-size:13px;font-weight:800}
.kpi{border-left:4px solid var(--brass);padding:12px} .kpi .val{font-size:20px;font-weight:900}
.btn{padding:7px 12px;border-radius:7px;border:none;cursor:pointer;font-weight:700;font-size:11px}
.btn-g{background:var(--green);color:white} .btn-y{background:var(--lemon);color:var(--green)} .btn-w{background:white;color:var(--green);border:1px solid var(--line)} .btn-r{background:#C5221F;color:white} .btn-b{background:#E8F0FE;color:#1A2E1E;border:1px solid #C2D6FF} .btn-o{background:#FFF3E0;color:#8C6B2A;border:1px solid var(--brass)}
.badge{padding:3px 8px;border-radius:12px;font-size:10px;font-weight:800}
.ok{background:#E6F4EA;color:#1E7D32} .warn{background:#FEF3CD;color:#9C6F00} .crit{background:#FCE8E6;color:#C5221F} .brass{background:#FFFBEB;color:#8C6B2A;border:1px solid var(--brass)}
table{width:100%;border-collapse:collapse;font-size:12px} th{background:#F8F6F3;padding:8px 6px;text-align:left;font-weight:700;border-bottom:2px solid var(--line)} td{padding:7px 6px;border-bottom:1px solid #F0EBE2;vertical-align:top}
input,select,textarea{padding:8px 10px;border-radius:7px;border:1.5px solid var(--line);width:100%;font-size:12px;margin:4px 0}
.row{display:flex;gap:8px;flex-wrap:wrap} .row>*{flex:1;min-width:140px}
.hidden{display:none !important}
.form-box{background:var(--alab);padding:12px;border-radius:8px;border:1px dashed var(--brass);margin-bottom:10px}
.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(26,46,30,0.65);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(4px)}
.modal-content{background:white;border-radius:14px;width:100%;max-width:1000px;max-height:94vh;display:flex;flex-direction:column;box-shadow:0 24px 64px rgba(0,0,0,0.35);border:1px solid var(--brass);animation:slideUp 0.25s ease}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal-header{padding:16px 20px;border-bottom:2px solid var(--line);display:flex;justify-content:space-between;align-items:center;background:var(--alab);border-radius:14px 14px 0 0;position:sticky;top:0;z-index:2}
.modal-body{padding:16px 20px;overflow-y:auto;flex:1}
.modal-footer{padding:14px 20px;border-top:2px solid var(--line);background:var(--alab);border-radius:0 0 14px 14px;display:flex;gap:10px;position:sticky;bottom:0;z-index:2}
.close-x{background:white;border:1.5px solid var(--line);border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:900;font-size:18px}
.close-x:hover{background:#FCE8E6;color:#C5221F;border-color:#C5221F}
.asset-section{background:white;border:1.5px solid var(--line);border-radius:12px;padding:14px;margin:14px 0}
.kiln-line{background:#FFFBEB;border:1.5px solid var(--brass);border-radius:10px;padding:12px;margin:10px 0}
.product-line{background:white;border:1px dashed var(--brass);border-radius:8px;padding:10px;margin:8px 0;margin-left:12px;border-left:4px solid var(--brass)}
.tooltip{position:relative;display:inline-block}
.tooltip .tip{visibility:hidden;width:260px;background:var(--green);color:white;border-radius:8px;padding:10px;position:absolute;bottom:125%;left:50%;margin-left:-130px;z-index:10;font-size:11px}
.tooltip:hover .tip{visibility:visible}
.sbu-card{border:1.5px solid var(--line);border-radius:12px;padding:14px;margin:12px 0;background:white}
</style></head>
<body>
<div class="topnav"><div class="brand">🍋 LEMON <span>ERP</span> v4.4.8 - Masters Reordered Category→Products→SBUs - Base v1.3.py</div><button class="btn btn-y" onclick="location.reload()">Reload</button></div>
<div class="layout">
<div class="sidebar">
<h4>MAIN</h4>
<div class="menu active" onclick="openTab('dash')"><i class="bi bi-speedometer2"></i> Dashboard</div>
<h4>OPERATIONS</h4>
<div class="menu" onclick="openTab('stock')"><i class="bi bi-box-seam"></i> Stock</div>
<div class="menu" onclick="openTab('make')"><i class="bi bi-gear"></i> Make</div>
<div class="menu" onclick="openTab('buy')"><i class="bi bi-cart"></i> Buy</div>
<div class="menu" onclick="openTab('sell')"><i class="bi bi-truck"></i> Sell</div>
<div class="menu" onclick="openTab('pack')"><i class="bi bi-box"></i> Pack</div>
<div class="menu" onclick="openTab('qr')"><i class="bi bi-qr-code"></i> QR</div>
<h4>MASTERS</h4>
<div class="menu" onclick="openTab('product_category')"><i class="bi bi-tags"></i> Product Category</div>
<div class="menu" onclick="openTab('products')"><i class="bi bi-bag"></i> Products</div>
<div class="menu" onclick="openTab('sbus')"><i class="bi bi-building"></i> SBUs</div>
<div class="menu" onclick="openTab('vendors')"><i class="bi bi-people"></i> Vendors</div>
<div class="menu" onclick="openTab('customers')"><i class="bi bi-person"></i> Customers</div>
<div class="menu" onclick="openTab('cost')"><i class="bi bi-currency-rupee"></i> Cost</div>
<div class="menu" onclick="openTab('mobile')"><i class="bi bi-phone"></i> Mobile</div>
</div>
<div class="content">
<!-- DASH -->
<div id="dash" class="tabcontent">
<div class="card"><h3>Dashboard - v4.4.8 Masters Reordered - Category → Products → SBUs - Base v1.3.py</h3>
<div class="row"><div class="card kpi"><div>Total Value</div><div class="val" id="totalVal">Rs 0 Lakh</div></div><div class="card kpi"><div>SBUs</div><div class="val" id="sbuCountDash">0</div></div><div class="card kpi"><div>Products</div><div class="val" id="prodCountDash">0</div></div><div class="card kpi"><div>Categories</div><div class="val" id="catCountDash">0</div></div></div>
<div class="card"><b>v4.4.8 Changes:</b> Sidebar reorganized - MAIN only Dashboard, MASTERS sequence: 1) Product Category 2) Products 3) SBUs 4) Vendors 5) Customers 6) Cost 7) Mobile - Flow: Category → Product → SBU - Everything else unchanged from v1.3.py / v4.4.7 Fixed Tabular</div>
<div id="alerts"></div>
</div></div>

<!-- PRODUCT CATEGORY -->
<div id="product_category" class="tabcontent hidden">
<div class="card" style="text-align:center"><h1 style="font-size:22px;font-weight:900">Product Category Master - DB File for Further Use - v4.4.3 Unchanged</h1><p style="font-size:11px;color:#666">DB File: lemon_erp_v44_1_category.db - Table: product_category</p>
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass);text-align:left;max-width:600px;margin:12px auto"><b>Add Product Category - 1 Input Field</b><input type="hidden" id="cat_id"><div style="margin-top:8px">Category Name *<input id="category_name" placeholder="Category Name e.g. Raw - Limestone, Finished - Quicklime 10-40mm"></div><div class="row" style="margin-top:8px"><button class="btn btn-g" onclick="saveCategory()">Save Category</button><button class="btn btn-w" onclick="resetCat()">Reset</button></div></div>
<table><thead><tr><th>#</th><th>Category Name</th><th>Created At</th><th>DB File</th><th>Actions</th></tr></thead><tbody id="catTbl"></tbody></table>
</div></div>

<!-- PRODUCTS -->
<div id="products" class="tabcontent hidden">
<div class="card" style="text-align:center"><h1 style="font-size:22px;font-weight:900;text-align:center"><i class="bi bi-bag"></i> Products</h1><p style="font-size:11px;color:#666;text-align:center">Landing Page Heading Products centrally aligned - HSN + Description + Auto Code + Category-wise + Hover narration - v4.4.3 Unchanged - 11px gray #666</p><button class="btn btn-y" style="padding:12px 28px;font-size:14px;font-weight:800" onclick="openAddProductPopup()">Add New Product</button>
<div id="prodList"></div></div></div>

<!-- SBUS v4.4.7 -->
<div id="sbus" class="tabcontent hidden active">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 14px;text-align:center"><i class="bi bi-building"></i> Strategic Business Units</h1>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddSBU()">Add New SBU</button>
</div>
<div id="sbuList">Loading SBUs...</div>
</div>

<!-- STOCK -->
<div id="stock" class="tabcontent hidden"><div class="card"><h3>Stock - v4.4 Unchanged</h3><div class="row"><select id="fUnit"><option>All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="loadStock()">Filter</button></div><div id="rawTbl"></div><div id="wipTbl"></div><div id="finTbl"></div></div></div>
<div id="make" class="tabcontent hidden"><div class="card"><h3>Make</h3><p>Make module v4.4 Unchanged</p><div id="moList"></div></div></div>
<div id="buy" class="tabcontent hidden"><div class="card"><h3>Buy</h3><p>Buy module v4.4 Unchanged</p></div></div>
<div id="sell" class="tabcontent hidden"><div class="card"><h3>Sell</h3><p>Sell module v4.4 Unchanged</p></div></div>
<div id="vendors" class="tabcontent hidden"><div class="card"><h3>Vendors</h3><table><tbody id="vendorTbl"></tbody></table></div></div>
<div id="customers" class="tabcontent hidden"><div class="card"><h3>Customers</h3><table><tbody id="customerTbl"></tbody></table></div></div>
<div id="pack" class="tabcontent hidden"><div class="card"><h3>Pack</h3><p>Pack v4.4</p></div></div>
<div id="qr" class="tabcontent hidden"><div class="card"><h3>QR</h3><p>QR module</p><div id="qrList"></div></div></div>
<div id="cost" class="tabcontent hidden"><div class="card"><h3>Cost</h3><div id="costVal"></div><div id="costTbl"></div></div></div>
<div id="mobile" class="tabcontent hidden"><div class="card"><h3>Mobile - Placeholder</h3></div></div>
</div></div>

<!-- PRODUCT MODAL -->
<div id="productModal" class="modal hidden" onclick="if(event.target===this) closeProductPopup()"><div class="modal-content" style="max-width:620px"><div class="modal-header"><b>Add Product - HSN + Description + Auto Code - v4.4.3</b><button class="close-x" onclick="closeProductPopup()">×</button></div><div class="modal-body"><input type="hidden" id="prod_id"><div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">Product Name *<input id="prod_name">Product Category *<select id="prod_cat"></select><p style="font-size:10px;color:#888">DB File: lemon_erp_v44_1_category.db - Table: product_category</p><div class="row"><div>HSN Code *<input id="prod_hsn" placeholder="2522"></div><div>Product Code (Auto)<input id="prod_code_preview" disabled style="background:var(--alab);font-weight:800"></div></div>Product Description *<textarea id="prod_desc" placeholder="Product Description - Mandatory - Shows narration when roll mouse over name in list"></textarea></div></div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:13px" onclick="saveProduct()">Save Product - Auto Code Generate</button><button class="btn btn-w" onclick="closeProductPopup()">Cancel</button></div></div></div>

<!-- SBU MODAL v4.4.7 FIXED -->
<div id="sbuModal" class="modal hidden" onclick="if(event.target===this) closeAddSBU()"><div class="modal-content" style="max-width:1000px"><div class="modal-header"><b>Add SBU - Strategic Business Units - v4.4.7 Fixed</b><button class="close-x" onclick="closeAddSBU()">×</button></div><div class="modal-body">
<input type="hidden" id="sbu_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>SBU Details</b><div style="margin-top:8px">SBU Name - e.g. Unit 1 72MT, Jodhpur Plant *<input id="sbu_name" placeholder="SBU Name"></div>Address - Full address field<textarea id="sbu_address" placeholder="Address - Full address field e.g. Plot 123, RIICO Industrial Area, Jodhpur, Rajasthan 342001"></textarea></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>🔥 Kilns - v4.4.7 Fixed - Lining & Health once per kiln</h4><button class="btn btn-y" onclick="addKilnField()">Add Kiln</button></div><p style="font-size:10px;color:#666">When clicked Add Kiln - Add new line: *Kiln No. *Lining Date *Health Status *Products and Capacity *Add Product Button *Delete button. Products only ask Product + Capacity/Day.</p><div id="kilnsContainer"><p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p></div></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>⚙ Sizing Plants</h4><button class="btn btn-y" onclick="addSizingField()">Add Sizing Plant</button></div><div id="sizingContainer"><p style="text-align:center;color:#888">No sizing plants</p></div></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>💧 Hydration Plants</h4><button class="btn btn-y" onclick="addHydrationField()">Add Hydration Plant</button></div><div id="hydrationContainer"><p style="text-align:center;color:#888">No hydration plants</p></div></div>

<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>📦 Stock Yards</h4><button class="btn btn-y" onclick="addYardField()">Add Stock Yard</button></div><p style="font-size:10px;color:#666">Add Stock Yard Button - when clicked: *Yard Name *Add Yard Items - dropdown from all categories, Opening stock.</p><div id="yardsContainer"><p style="text-align:center;color:#888">No stock yards</p></div></div>

</div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="saveSBU()">Save SBU - Strategic Business Units</button><button class="btn btn-w" onclick="closeAddSBU()">Cancel</button></div></div></div>

<script>
function openTab(id){document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));document.getElementById(id).classList.remove('hidden');document.querySelectorAll('.menu').forEach(m=>m.classList.remove('active')); if(id==='product_category') loadCategories(); if(id==='products') loadProducts(); if(id==='sbus') loadSBUs(); if(id==='dash') loadDash(); if(id==='stock') loadStock();}

let allProducts=[], finishedProducts=[]; let kilnCounter=0;
async function loadAllProductsForSBU(){
 let r=await fetch('/api/products'); let d=await r.json(); allProducts=d;
 finishedProducts=d.filter(p=>{let c=(p.category||'').toLowerCase(); return c.includes('finish')||c.includes('quicklime')||c.includes('cao')||c.includes('hydrat')||c.includes('sizing');}); if(finishedProducts.length===0) finishedProducts=d;
}
function getFinishedProductOptions(sel){let h='<option value="">Select Finished Product</option>'; finishedProducts.forEach(p=>{h+=`<option value="${p.id}" ${sel==p.id?'selected':''}>${p.name} (${p.product_code}) - ${p.category}</option>`}); return h;}
function getAllProductOptions(sel){let h='<option value="">Select Product</option>'; allProducts.forEach(p=>{h+=`<option value="${p.id}" ${sel==p.id?'selected':''}>${p.name} (${p.product_code}) - ${p.category}</option>`}); return h;}

// Category
async function loadCategories(){let r=await fetch('/api/product_categories'); let d=await r.json(); let tb=document.getElementById('catTbl'); tb.innerHTML=''; d.forEach((c,i)=>{tb.innerHTML+=`<tr><td>${i+1}</td><td>${c.category_name}</td><td>${c.created_at}</td><td>lemon_erp_v44_1_category.db / product_category / ${c.id}</td><td><button class="btn btn-b" onclick="editCat(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCat(${c.id})">Del</button></td></tr>`}); document.getElementById('catCountDash').innerText=d.length;}
async function saveCategory(){let id=document.getElementById('cat_id').value; let name=document.getElementById('category_name').value.trim(); if(!name) return alert('Required'); let url=id?`/api/product_categories/${id}`:'/api/product_categories'; let m=id?'PUT':'POST'; let res=await fetch(url,{method:m,headers:{'Content-Type':'application/json'},body:JSON.stringify({category_name:name})}); let j=await res.json(); if(res.ok){resetCat(); loadCategories(); loadProdCatOptions();} else alert(j.error);}
function resetCat(){document.getElementById('cat_id').value=''; document.getElementById('category_name').value='';}
async function editCat(id){let r=await fetch(`/api/product_categories/${id}`); let c=await r.json(); document.getElementById('cat_id').value=c.id; document.getElementById('category_name').value=c.category_name;}
async function delCat(id){if(!confirm('Delete?'))return; await fetch(`/api/product_categories/${id}`,{method:'DELETE'}); loadCategories();}

// Products
async function loadProdCatOptions(){let r=await fetch('/api/product_categories'); let d=await r.json(); let sel=document.getElementById('prod_cat'); if(!sel) return; sel.innerHTML='<option value="">Select Category</option>'; d.forEach(c=>{sel.innerHTML+=`<option value="${c.category_name}">${c.category_name}</option>`});}
async function loadProducts(){await loadAllProductsForSBU(); await loadProdCatOptions(); let r=await fetch('/api/products'); let d=await r.json(); let groups={}; d.forEach(p=>{if(!groups[p.category]) groups[p.category]=[]; groups[p.category].push(p);}); let html=''; for(let cat in groups){html+=`<div style="border:1.5px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden"><div style="background:var(--green);color:var(--brass);padding:10px 14px;font-weight:800;font-size:12px">${cat} - ${groups[cat].length} Products</div><table><thead><tr><th>Product Code</th><th>HSN</th><th>Product Name - Hover for Narration</th><th>Description</th><th>Actions</th></tr></thead><tbody>`; groups[cat].forEach(p=>{html+=`<tr><td><span style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line)">${p.product_code}</span></td><td><span class="badge ok">${p.hsn_code}</span></td><td><div class="tooltip">${p.name}<span class="tip">Code: ${p.product_code}<br>HSN: ${p.hsn_code}<br>Cat: ${p.category}<br>Desc: ${p.description}</span></div></td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px">${p.description}</td><td><button class="btn btn-b" onclick="editProd(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProd(${p.id})">Del</button></td></tr>`}); html+='</tbody></table></div>';} document.getElementById('prodList').innerHTML=html||'<p>No products</p>'; document.getElementById('prodCountDash').innerText=d.length;}
function openAddProductPopup(){document.getElementById('productModal').classList.remove('hidden');}
function closeProductPopup(){document.getElementById('productModal').classList.add('hidden'); document.getElementById('prod_id').value=''; document.getElementById('prod_name').value=''; document.getElementById('prod_hsn').value=''; document.getElementById('prod_desc').value=''; document.getElementById('prod_code_preview').value='';}
async function saveProduct(){let id=document.getElementById('prod_id').value; let payload={name:document.getElementById('prod_name').value, category:document.getElementById('prod_cat').value, hsn_code:document.getElementById('prod_hsn').value, description:document.getElementById('prod_desc').value}; if(!payload.name||!payload.category||!payload.hsn_code||!payload.description) return alert('All fields mandatory'); let url=id?`/api/products/${id}`:'/api/products'; let m=id?'PUT':'POST'; let res=await fetch(url,{method:m,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let j=await res.json(); if(res.ok){closeProductPopup(); loadProducts();} else alert(j.error);}
async function editProd(id){let r=await fetch(`/api/products/${id}`); let p=await r.json(); openAddProductPopup(); document.getElementById('prod_id').value=p.id; document.getElementById('prod_name').value=p.name; document.getElementById('prod_cat').value=p.category; document.getElementById('prod_hsn').value=p.hsn_code; document.getElementById('prod_desc').value=p.description; document.getElementById('prod_code_preview').value=p.product_code;}
async function delProd(id){if(!confirm('Delete?'))return; await fetch(`/api/products/${id}`,{method:'DELETE'}); loadProducts();}

// SBU v4.4.7 FIXED
function openAddSBU(){document.getElementById('sbuModal').classList.remove('hidden'); document.getElementById('sbu_id').value=''; document.getElementById('sbu_name').value=''; document.getElementById('sbu_address').value=''; document.getElementById('kilnsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p>'; document.getElementById('sizingContainer').innerHTML='<p style="text-align:center;color:#888">No sizing plants</p>'; document.getElementById('hydrationContainer').innerHTML='<p style="text-align:center;color:#888">No hydration plants</p>'; document.getElementById('yardsContainer').innerHTML='<p style="text-align:center;color:#888">No stock yards</p>'; loadAllProductsForSBU();}
function closeAddSBU(){document.getElementById('sbuModal').classList.add('hidden');}

function addKilnField(data=null){
 let c=document.getElementById('kilnsContainer'); if(c.innerHTML.includes('No kilns')) c.innerHTML='';
 kilnCounter++; let id=`kiln_${kilnCounter}_${Date.now()}`;
 let lining=data?.lining_installation_date||data?.lining_date||''; let health=data?.health_status||'Good';
 let html=`<div id="${id}" class="kiln-line"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px"><b>Kiln Line - *Kiln No. *Lining Date *Health + Products</b><div><button class="btn btn-b" onclick="addKilnProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete Kiln</button></div></div>
 <div class="row" style="margin-top:8px"><div>*Kiln No. e.g. Kiln 1, K-01<input class="k_no" placeholder="Kiln No." value="${data?.kiln_no||''}"></div><div>*Lining Installation Date<input type="date" class="k_lining" value="${lining}"></div><div>*Health Status<select class="k_health"><option ${health==='Good'?'selected':''}>Good</option><option ${health==='Needs Repair'?'selected':''}>Needs Repair</option><option ${health==='Critical'?'selected':''}>Critical</option><option ${health==='New'?'selected':''}>New</option></select></div></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Products and Capacity - v4.4.7 Fixed (Product + Capacity only)</b><div id="${id}-products" class="kiln-products-container">${data?.products_capacity?.length? '' : '<p style="font-size:10px;color:#888">No products - Click Add Product → Inset Product name, Capacity/Day, Delete - 10px gray</p>'}</div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let prodContainer=document.getElementById(`${id}-products`);
 if(data?.products_capacity){ data.products_capacity.forEach(pc=>{ prodContainer.insertAdjacentHTML('beforeend', renderKilnProductLine(pc)); });}
}
function renderKilnProductLine(pc){
 let id=`kprod_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line"><div class="row" style="align-items:end"><div>Product name (Finished List)<select class="kp_product">${getFinishedProductOptions(pc.product_id||pc.product_id)}</select></div><div>Capacity/Day MT/day e.g. 15<input type="number" class="kp_capacity" placeholder="Capacity/Day - MT/day e.g. 15" value="${pc.capacity_per_day||pc.capacity||''}"></div><div><button class="btn btn-r" style="margin-top:18px" onclick="document.getElementById('${id}').remove()">Delete</button></div></div></div>`;
}
function addKilnProduct(kilnId){
 let cont=document.getElementById(`${kilnId}-products`)||document.querySelector(`#${kilnId} .kiln-products-container`); if(!cont) return; if(cont.innerHTML.includes('No products')) cont.innerHTML=''; cont.insertAdjacentHTML('beforeend', renderKilnProductLine({}));
}

function addSizingField(data=null){
 let c=document.getElementById('sizingContainer'); if(c.innerHTML.includes('No sizing')) c.innerHTML='';
 kilnCounter++; let id=`sizing_${kilnCounter}_${Date.now()}`;
 let html=`<div id="${id}" class="kiln-line" style="background:#F6FFF6;border-color:#C5E1C5"><div style="display:flex;justify-content:space-between"><b>Sizing Plant - *Plant No. *Products and Capacity</b><div><button class="btn btn-b" onclick="addSizingProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div>
 <div class="row" style="margin-top:8px"><div>*Plant No. e.g. Sizing 1, SP-01<input class="s_no" placeholder="Plant No." value="${data?.plant_no||''}"></div></div>
 <div style="margin-top:8px"><b>Whole Plant Machineries</b><textarea class="s_mach" placeholder="List of Machineries - Whole plant - e.g. Crusher, Vibrating Screen 10-40mm, Conveyor 20m, Dust Collector">${data?.machineries||''}</textarea></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Products and Capacity</b><div id="${id}-products" class="sizing-products-container"></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let pc=document.getElementById(`${id}-products`);
 if(data?.products_capacity){ data.products_capacity.forEach(p=>{ pc.insertAdjacentHTML('beforeend', renderSizingProductLine(p)); });}
}
function renderSizingProductLine(pc){
 let id=`sprod_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line" style="border-left-color:#C5E1C5"><div class="row" style="align-items:end"><div>Product<select class="sp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div>Capacity/hour<input type="number" class="sp_capacity" placeholder="Capacity/hour" value="${pc.capacity_per_hour||pc.capacity||''}"></div><div>List Machineries for this product line<textarea class="sp_mach_line" placeholder="Machineries">${pc.machineries||pc.machineries_line||''}</textarea></div><div><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Del</button></div></div></div>`;
}
function addSizingProduct(pid){ let cont=document.getElementById(`${pid}-products`); if(!cont) return; cont.insertAdjacentHTML('beforeend', renderSizingProductLine({}));}

function addHydrationField(data=null){
 let c=document.getElementById('hydrationContainer'); if(c.innerHTML.includes('No hydration')) c.innerHTML='';
 kilnCounter++; let id=`hyd_${kilnCounter}_${Date.now()}`;
 let html=`<div id="${id}" class="kiln-line" style="background:#F0F8FF;border-color:#C2D6FF"><div style="display:flex;justify-content:space-between"><b>Hydration Plant</b><div><button class="btn btn-b" onclick="addHydrationProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div>
 <div class="row"><div>*Plant No.<input class="h_no" value="${data?.plant_no||''}"></div></div>
 <div><b>Whole Plant Machineries</b><textarea class="h_mach">${data?.machineries||''}</textarea></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><div id="${id}-products" class="hydration-products-container"></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let pc=document.getElementById(`${id}-products`);
 if(data?.products_capacity){ data.products_capacity.forEach(p=>{ pc.insertAdjacentHTML('beforeend', renderHydrationProductLine(p)); });}
}
function renderHydrationProductLine(pc){
 let id=`hprod_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line" style="border-left-color:#C2D6FF"><div class="row"><div>Product<select class="hp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div>Capacity/hour<input type="number" class="hp_capacity" value="${pc.capacity_per_hour||pc.capacity||''}"></div><div>Line Machineries<textarea class="hp_mach_line">${pc.machineries||''}</textarea></div><div><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Del</button></div></div></div>`;
}
function addHydrationProduct(pid){ let cont=document.getElementById(`${pid}-products`); cont.insertAdjacentHTML('beforeend', renderHydrationProductLine({}));}

function addYardField(data=null){
 let c=document.getElementById('yardsContainer'); if(c.innerHTML.includes('No stock yards')) c.innerHTML='';
 kilnCounter++; let id=`yard_${kilnCounter}_${Date.now()}`;
 let html=`<div id="${id}" class="kiln-line"><div style="display:flex;justify-content:space-between"><b>Stock Yard - *Yard Name *Add Yard Items</b><div><button class="btn btn-b" onclick="addYardItem('${id}')">Add Yard Items</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete Yard</button></div></div>
 <div class="row"><div>*Yard Name e.g. Limestone Yard 1<input class="y_name" placeholder="Yard Name" value="${data?.yard_name||''}"></div></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Add Yard Items - dropdown from all category, Opening stock</b><div id="${id}-items" class="yard-items-container"></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let cont=document.getElementById(`${id}-items`);
 if(data?.yard_items){ data.yard_items.forEach(yi=>{ cont.insertAdjacentHTML('beforeend', renderYardItemLine(yi)); });}
}
function renderYardItemLine(yi){
 let id=`yitem_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line"><div class="row" style="align-items:end"><div>Product (All)<select class="yi_product">${getAllProductOptions(yi.product_id)}</select></div><div>Opening stock - e.g. 150 MT<input type="number" class="yi_opening" placeholder="Opening stock - e.g. 150 MT" value="${yi.opening_stock||yi.opening||''}"></div><div><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Del</button></div></div></div>`;
}
function addYardItem(yardId){ let cont=document.getElementById(`${yardId}-items`); cont.insertAdjacentHTML('beforeend', renderYardItemLine({}));}

async function saveSBU(){
 let sbuName=document.getElementById('sbu_name').value.trim(); if(!sbuName) return alert('SBU Name required');
 let kilns=[]; document.querySelectorAll('#kilnsContainer > div[id^="kiln_"]').forEach(div=>{
   let pcs=[]; div.querySelectorAll('.kiln-products-container > div[id^="kprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.kp_product').value; let cap=pdiv.querySelector('.kp_capacity').value;
     if(pid) pcs.push({product_id:parseInt(pid), capacity_per_day:parseFloat(cap)||0, capacity:parseFloat(cap)||0});
   });
   let k_no=div.querySelector('.k_no').value; let k_lining=div.querySelector('.k_lining').value; let k_health=div.querySelector('.k_health').value;
   kilns.push({kiln_no:k_no, lining_installation_date:k_lining, lining_date:k_lining, health_status:k_health, products_capacity:pcs});
 });
 let sizings=[]; document.querySelectorAll('#sizingContainer > div[id^="sizing_"]').forEach(div=>{
   let pcs=[]; div.querySelectorAll('.sizing-products-container > div[id^="sprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.sp_product').value; let cap=pdiv.querySelector('.sp_capacity').value; let ml=pdiv.querySelector('.sp_mach_line').value;
     if(pid) pcs.push({product_id:parseInt(pid), capacity_per_hour:parseFloat(cap)||0, capacity:parseFloat(cap)||0, machineries:ml});
   });
   sizings.push({plant_no:div.querySelector('.s_no').value, products_capacity:pcs, machineries:div.querySelector('.s_mach').value});
 });
 let hydrations=[]; document.querySelectorAll('#hydrationContainer > div[id^="hyd_"]').forEach(div=>{
   let pcs=[]; div.querySelectorAll('.hydration-products-container > div[id^="hprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.hp_product').value; let cap=pdiv.querySelector('.hp_capacity').value; let ml=pdiv.querySelector('.hp_mach_line')?.value||'';
     if(pid) pcs.push({product_id:parseInt(pid), capacity_per_hour:parseFloat(cap)||0, machineries:ml});
   });
   hydrations.push({plant_no:div.querySelector('.h_no').value, products_capacity:pcs, machineries:div.querySelector('.h_mach').value});
 });
 let yards=[]; document.querySelectorAll('#yardsContainer > div[id^="yard_"]').forEach(div=>{
   let items=[]; div.querySelectorAll('.yard-items-container > div[id^="yitem_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.yi_product').value; let op=pdiv.querySelector('.yi_opening').value;
     if(pid) items.push({product_id:parseInt(pid), opening_stock:parseFloat(op)||0, opening:parseFloat(op)||0});
   });
   yards.push({yard_name:div.querySelector('.y_name').value, yard_items:items});
 });
 let payload={sbu_name:sbuName, address:document.getElementById('sbu_address').value, kilns, sizing_plants:sizings, hydration_plants:hydrations, stock_yards:yards};
 let sbuId=document.getElementById('sbu_id').value;
 let url=sbuId?`/api/sbus/${sbuId}`:'/api/sbus'; let method=sbuId?'PUT':'POST';
 let res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let j=await res.json();
 if(res.ok){alert(`SBU ${sbuId?'Updated':'Created'} - ${kilns.length} Kilns, ${sizings.length} Sizing, ${hydrations.length} Hyd, ${yards.length} Yards`); closeAddSBU(); loadSBUs(); loadDash();}
 else alert(j.error||'Error');
}

async function loadSBUs(){
 let r=await fetch('/api/sbus'); let sbus=await r.json();
 document.getElementById('sbuCountDash').innerText=sbus.length;
 let list=document.getElementById('sbuList');
 if(sbus.length===0){
   list.innerHTML=`<div style="text-align:center;padding:30px"><p>No SBUs - Masters empty - Strategic Business Units - Forget v4.4.4 and v4.4.5 - Take v4.4.3 as base</p><button class="btn btn-y" onclick="openAddSBU()">Add First SBU</button></div>`;
   return;
 }
 let h='';
 sbus.forEach(s=>{
   let kilnBadge=`${s.kilns.length} Kilns`; let sizBadge=`${s.sizing_plants.length} Sizing`; let hydBadge=`${s.hydration_plants.length} Hydration`; let yardBadge=`${s.stock_yards.length} Yards`;
   h+=`<div class="sbu-card"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px"><div><h3 style="font-size:16px;margin:0"><i class="bi bi-building"></i> ${s.sbu_name}</h3><p style="font-size:11px;color:#666;margin:2px 0"><i class="bi bi-geo-alt"></i> ${s.address||''}</p><p style="font-size:10px;margin-top:6px"><span class="badge brass">${kilnBadge}</span> <span class="badge brass">${sizBadge}</span> <span class="badge brass">${hydBadge}</span> <span class="badge brass">${yardBadge}</span></p></div><div style="display:flex;gap:6px;align-items:start"><button class="btn btn-b" onclick="editSBU(${s.id})">Edit</button><button class="btn btn-o" onclick="duplicateSBU(${s.id})">Duplicate</button><button class="btn btn-r" onclick="delSBU(${s.id})">Delete</button></div></div>`;
   // Tabular clean
   h+=`<div style="margin-top:10px">`;
   // Kilns Table
   if(s.kilns.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:var(--green);color:white;padding:8px 10px;font-weight:800;font-size:11px">🔥 Kilns - ${s.kilns.length}</div><table><thead><tr><th>Kiln No</th><th>Lining Date</th><th>Health</th><th>Products + Capacity/Day</th></tr></thead><tbody>`;
     s.kilns.forEach(k=>{
       let healthClass=k.health_status==='Good'?'ok':k.health_status==='Critical'?'crit':'warn';
       let prodHtml=k.products_capacity.length? k.products_capacity.map(pc=>`<span style="display:block;background:white;padding:4px 6px;border-radius:4px;margin:3px 0;border:1px solid var(--line)"><b>${pc.product_name}</b> - ${pc.capacity_per_day||pc.capacity||0} MT/day <small style="color:#888">(${pc.product_code})</small></span>`).join('') : '<small>No products</small>';
       h+=`<tr><td><b>${k.kiln_no}</b></td><td>${k.lining_installation_date||k.lining_date||''}</td><td><span class="badge ${healthClass}">${k.health_status}</span></td><td>${prodHtml}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   if(s.sizing_plants.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:#1A2E1E;color:#C5E1C5;padding:8px 10px;font-weight:800;font-size:11px">⚙ Sizing Plants - ${s.sizing_plants.length}</div><table><thead><tr><th>Plant No</th><th>Machineries (Whole)</th><th>Products + Capacity/Hour</th></tr></thead><tbody>`;
     s.sizing_plants.forEach(sp=>{
       let prodHtml=sp.products_capacity.map(pc=>`<span style="display:block;background:#F6FFF6;padding:4px 6px;border-radius:4px;margin:3px 0;border:1px solid #C5E1C5"><b>${pc.product_name}</b> - ${pc.capacity_per_hour||0} MT/hr ${pc.machineries?'<br><small>Mach: '+pc.machineries+'</small>':''}</span>`).join('');
       h+=`<tr><td><b>${sp.plant_no}</b></td><td style="font-size:10px">${sp.machineries||''}</td><td>${prodHtml}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   if(s.hydration_plants.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:#0F2A44;color:#C2D6FF;padding:8px 10px;font-weight:800;font-size:11px">💧 Hydration Plants - ${s.hydration_plants.length}</div><table><thead><tr><th>Plant No</th><th>Machineries</th><th>Products</th></tr></thead><tbody>`;
     s.hydration_plants.forEach(hp=>{
       let prodHtml=hp.products_capacity.map(pc=>`<span style="display:block;background:#F0F8FF;padding:4px 6px;border-radius:4px;margin:3px 0"><b>${pc.product_name}</b> - ${pc.capacity_per_hour||0} MT/hr</span>`).join('');
       h+=`<tr><td><b>${hp.plant_no}</b></td><td style="font-size:10px">${hp.machineries||''}</td><td>${prodHtml}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   if(s.stock_yards.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:var(--alab);padding:8px 10px;font-weight:800;font-size:11px;border-bottom:1px solid var(--line)">📦 Stock Yards - ${s.stock_yards.length}</div><table><thead><tr><th>Yard Name</th><th>Items - Product + Opening Stock</th></tr></thead><tbody>`;
     s.stock_yards.forEach(y=>{
       let items=y.yard_items.map(yi=>`<span style="display:block;background:white;padding:4px 6px;border-radius:4px;margin:3px 0;border:1px solid var(--line)"><b>${yi.product_name}</b> - ${yi.opening_stock} MT</span>`).join('');
       h+=`<tr><td><b>${y.yard_name}</b></td><td>${items}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   h+=`</div><p style="font-size:10px;color:#888;margin-top:10px">SBU card with SBU Name + Address + Badges: ${kilnBadge}, ${sizBadge}, ${hydBadge}, ${yardBadge} / Edit / Duplicate / Delete buttons for each SBU - Base v4.4.3 Products refined kept - v4.4.7 Tabular</p></div>`;
 });
 list.innerHTML=h;
}

async function editSBU(id){
 let r=await fetch(`/api/sbus/${id}`); let s=await r.json();
 openAddSBU(); // open first - fixed bug
 setTimeout(()=>{
   document.getElementById('sbu_id').value=s.id;
   document.getElementById('sbu_name').value=s.sbu_name;
   document.getElementById('sbu_address').value=s.address||'';
   document.getElementById('kilnsContainer').innerHTML='';
   document.getElementById('sizingContainer').innerHTML='';
   document.getElementById('hydrationContainer').innerHTML='';
   document.getElementById('yardsContainer').innerHTML='';
   (s.kilns||[]).forEach(k=> addKilnField(k));
   (s.sizing_plants||[]).forEach(sp=> addSizingField(sp));
   (s.hydration_plants||[]).forEach(hp=> addHydrationField(hp));
   (s.stock_yards||[]).forEach(y=> addYardField(y));
   if(!s.kilns?.length) document.getElementById('kilnsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p>';
   if(!s.sizing_plants?.length) document.getElementById('sizingContainer').innerHTML='<p style="text-align:center;color:#888">No sizing plants</p>';
   if(!s.hydration_plants?.length) document.getElementById('hydrationContainer').innerHTML='<p style="text-align:center;color:#888">No hydration plants</p>';
   if(!s.stock_yards?.length) document.getElementById('yardsContainer').innerHTML='<p style="text-align:center;color:#888">No stock yards</p>';
 }, 600);
}

async function duplicateSBU(id){
 if(!confirm('Duplicate SBU? Creates copy with - Copy suffix')) return;
 let r=await fetch(`/api/sbus/${id}`); let s=await r.json();
 let payload={
   sbu_name: s.sbu_name + ' - Copy',
   address: s.address,
   kilns: (s.kilns||[]).map(k=> ({kiln_no: (k.kiln_no||'Kiln')+' - Copy', lining_installation_date:k.lining_installation_date||k.lining_date||'', lining_date:k.lining_installation_date||k.lining_date||'', health_status:k.health_status||'Good', products_capacity: (k.products_capacity||[]).map(pc=> ({product_id:pc.product_id, capacity_per_day:pc.capacity_per_day||pc.capacity||0, capacity:pc.capacity_per_day||pc.capacity||0}))})),
   sizing_plants: (s.sizing_plants||[]).map(sp=> ({plant_no: (sp.plant_no||'Sizing')+' - Copy', products_capacity: (sp.products_capacity||[]).map(pc=> ({product_id:pc.product_id, capacity_per_hour:pc.capacity_per_hour||pc.capacity||0, capacity:pc.capacity_per_hour||0, machineries:pc.machineries||''})), machineries: sp.machineries||''})),
   hydration_plants: (s.hydration_plants||[]).map(hp=> ({plant_no: (hp.plant_no||'Hyd')+' - Copy', products_capacity: (hp.products_capacity||[]).map(pc=> ({product_id:pc.product_id, capacity_per_hour:pc.capacity_per_hour||0})), machineries: hp.machineries||''})),
   stock_yards: (s.stock_yards||[]).map(y=> ({yard_name: (y.yard_name||'Yard')+' - Copy', yard_items: (y.yard_items||[]).map(yi=> ({product_id:yi.product_id, opening_stock:yi.opening_stock||yi.opening||0, opening:yi.opening_stock||0}))}))
 };
 let res=await fetch('/api/sbus',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 if(res.ok){alert('SBU Duplicated: '+payload.sbu_name); loadSBUs();} else alert('Duplicate failed');
}

async function delSBU(id){ if(!confirm('Delete SBU? Strategic Business Units')) return; await fetch(`/api/sbus/${id}`,{method:'DELETE'}); loadSBUs();}

async function loadDash(){ let r=await fetch('/api/inventory/combined'); let d=await r.json(); document.getElementById('totalVal').innerText='Rs '+(d.total_value_lakh||0).toFixed(2)+' Lakh'; let rc=await fetch('/api/product_categories'); let cats=await rc.json(); document.getElementById('catCountDash').innerText=cats.length; let rp=await fetch('/api/products'); let prods=await rp.json(); document.getElementById('prodCountDash').innerText=prods.length; let rs=await fetch('/api/sbus'); let sbus=await rs.json(); document.getElementById('sbuCountDash').innerText=sbus.length;}
async function loadStock(){ let r=await fetch('/api/inventory/combined'); let d=await r.json(); document.getElementById('rawTbl').innerHTML='<h4>Raw</h4><table><tr><th>Code</th><th>Name</th><th>MT</th></tr>'+d.raw.map(x=>`<tr><td>${x.product_code}</td><td>${x.name}</td><td>${x.total_mt}</td></tr>`).join('')+'</table>'; document.getElementById('finTbl').innerHTML='<h4>Finished</h4><table><tr><th>Code</th><th>Name</th><th>MT</th></tr>'+d.finished.map(x=>`<tr><td>${x.product_code}</td><td>${x.name}</td><td>${x.total_mt}</td></tr>`).join('')+'</table>';}
loadDash(); loadAllProductsForSBU(); loadProdCatOptions();
</script>
</body></html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
