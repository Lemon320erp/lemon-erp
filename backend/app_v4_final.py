
"""
LEMON ERP - MASTER WORKFLOW - v4.4.10.1
BASE: v1.3.py = v4.4.7 Fixed Tabular Duplicate + Vendor Master Enhanced
Fixes in v4.4.10:
- ONLY Vendor master enhanced - Added on top of v4.4.9.1 - Nothing removed - No other module changed
- A. Compliance: MSME Certificate No + Expiry + Upload, GST Registration Type Regular/Composition/Unregistered/SEZ/Deemed Export, TDS Section 194C 194J 194Q 194H 194I etc, Vendor Rating 1-5 stars + Last Audit Date, Document uploads GST Cert PAN Card Cancelled Cheque MSME Cert ISO Cert (base64 storage)
- B. Opening Balance Dr/Cr for migration + Ledger Group Sundry Creditors etc
- E. Departments in contacts + Primary contact flag is_primary checkbox
- F. Created By/At Updated By/At auto + Approval Workflow Draft Pending Approved Rejected + Last Transaction Date + Total Business Value sum of POs (po value = qty*rate)
- All previous fields kept: VEND-0001, Station, State, GST PAN TAN Legal Status Vendor Category Bank Details single dropdown searchable + Contacts
- Filters enhanced with Approval Status, Rating
- List shows new fields in tooltip and badges
- Bank single dropdown fix kept from v4.4.9.1
Fixes in v4.4.9.1:
- Fixed Bank Details form had 2 fields for bank selection - Now single searchable dropdown only - Removed extra select vb_bank_sel - Keep only input list datalist
- Rest locked to v4.4.9
Fixes in v4.4.9:
- ONLY Vendor module changed, rest locked to v4.4.8 FIXED
- Vendor Master redesigned: Heading + Add New Vendor button top after heading + Filters + Search bar
- Fields: Vendor Code Auto VEND-0001, Vendor Name text, Station text, Address text, State text for GST, GST No text, PAN No text, TAN No text, Legal Status dropdown (hidden master), Vendor Category dropdown (hidden master MSE/MSME etc), Bank Details Add Bank Account button with lines: Select Bank searchable dropdown nationalised banks India + Other (hidden bank master), Branch Name, Account Name, IFSC, Account No, Transaction Limit, Add Contact button with lines: Name, Designation dropdown hidden master, Mobile No, Whatsapp No, Land Line, Extension No, Email
- Bank master hidden database: 35+ nationalised/private banks seeded
- Legal Status master hidden: Proprietor, Partnership, LLP, Private Limited, Public Limited, HUF, Trust, Society, Govt, Others
- Vendor Category master: MSE, MSME, SSI, Small, Medium, Large, Non-MSE, Govt, Trader, Others
- Designation master: Proprietor, Partner, Director, Managing Director, Manager, Purchase Manager, Accounts Manager, Owner, CEO, AGM, DGM, Executive, Accountant, Others
- Vendor model expanded: vendor_code UNIQUE, name, station, address, state, gst_no, pan_no, tan_no, legal_status, vendor_category, bank_details JSON, contacts JSON, status Active/Inactive/Blocked, created_at + old fields compatibility
- List: Tabular clean with filters: Search by name/GST/PAN/Station/State, Type filters Legal Status, Vendor Category, State, Bank, Status, plus PO/GRN counts (yes for productivity)
- Credit varies PO to PO so not fixed - removed credit limit fixed, showing PO counts
- Duplicate NO
- Everything else 100% unchanged from v4.4.8 FIXED
DB: lemon_erp_v44_1_category.db single file persistent path via DATABASE_PATH env
File: backend/app_v4_final.py
URL: https://lemon-erp.onrender.com
"""

from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, os, re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lemon-erp-v44-10-1-vendor-docs-dragdrop'
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
    products_capacity = db.Column(db.Text)

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
    yard_items = db.Column(db.Text)

# Hidden Masters for Vendor
class LegalStatusMaster(db.Model):
    __tablename__ = 'legal_status_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)

class VendorCategoryMaster(db.Model):
    __tablename__ = 'vendor_category_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)

class DesignationMaster(db.Model):
    __tablename__ = 'designation_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)

class BankMaster(db.Model):
    __tablename__ = 'bank_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bank_name = db.Column(db.String(200), unique=True)
    bank_code = db.Column(db.String(20))

# Vendor Master Enhanced v4.4.9
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor_code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200), nullable=False)
    station = db.Column(db.String(100))
    address = db.Column(db.Text)
    state = db.Column(db.String(100))
    gst_no = db.Column(db.String(50))
    pan_no = db.Column(db.String(20))
    tan_no = db.Column(db.String(20))
    legal_status = db.Column(db.String(100))
    vendor_category = db.Column(db.String(100))
    bank_details = db.Column(db.Text)  # JSON list
    contacts = db.Column(db.Text)  # JSON list - now includes department, is_primary
    status = db.Column(db.String(20), default='Active')
    # old compatibility
    type = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    credit_limit = db.Column(db.Float, default=0)
    pending_due = db.Column(db.Float, default=0)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # v4.4.10 new fields - Compliance
    msme_cert_no = db.Column(db.String(100), default='')
    msme_expiry = db.Column(db.String(20), default='')
    msme_upload = db.Column(db.Text, default='')  # base64 or filename
    gst_reg_type = db.Column(db.String(50), default='Regular')  # Regular/Composition/Unregistered/SEZ/Deemed Export
    tds_section = db.Column(db.String(50), default='194C')
    vendor_rating = db.Column(db.Integer, default=0)  # 1-5 stars
    last_audit_date = db.Column(db.String(20), default='')
    # Document uploads JSON: {gst_cert, pan_card, cancelled_cheque, msme_cert, iso_cert} base64
    documents = db.Column(db.Text, default='{}')
    # B. Financial migration
    opening_balance = db.Column(db.Float, default=0)
    opening_balance_type = db.Column(db.String(10), default='Dr')  # Dr/Cr
    ledger_group = db.Column(db.String(100), default='Sundry Creditors')
    # F. Audit & Workflow
    created_by = db.Column(db.String(100), default='Admin')
    updated_by = db.Column(db.String(100), default='Admin')
    updated_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    approval_status = db.Column(db.String(20), default='Draft')  # Draft/Pending/Approved/Rejected
    last_transaction_date = db.Column(db.String(30), default='')
    total_business_value = db.Column(db.Float, default=0)

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
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
    material = db.Column(db.String(100))
    qty = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))
    status = db.Column(db.String(50))
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class GRN(db.Model):
    __tablename__ = 'grn'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_no = db.Column(db.String(100))
    material = db.Column(db.String(100))
    unit = db.Column(db.String(100))
    gross_kg = db.Column(db.Float, default=0)
    tare_kg = db.Column(db.Float, default=0)
    vendor = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
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
    # Seed hidden masters if empty
    if LegalStatusMaster.query.count()==0:
        for name in ["Proprietor","Partnership","LLP","Private Limited","Public Limited","HUF","Trust","Society","Government","OPC","One Person Company","Co-operative Society","Others"]:
            db.session.add(LegalStatusMaster(name=name))
    if VendorCategoryMaster.query.count()==0:
        for name in ["MSE","MSME","SSI","Small","Medium","Large","Non-MSE","Government","Trader","Importer","Service Provider","Manufacturer","Distributor","Others"]:
            db.session.add(VendorCategoryMaster(name=name))
    if DesignationMaster.query.count()==0:
        for name in ["Proprietor","Partner","Director","Managing Director","Manager","Purchase Manager","Accounts Manager","Owner","CEO","AGM","DGM","Executive","Accountant","Sales Manager","General Manager","Chairman","Secretary","Others"]:
            db.session.add(DesignationMaster(name=name))
    if BankMaster.query.count()==0:
        banks = [
            ("State Bank of India","SBI"), ("Punjab National Bank","PNB"), ("Bank of Baroda","BOB"), ("Canara Bank","CAN"), ("Union Bank of India","UBI"),
            ("Bank of India","BOI"), ("Indian Bank","INDIAN"), ("Central Bank of India","CBI"), ("Indian Overseas Bank","IOB"), ("UCO Bank","UCO"),
            ("Bank of Maharashtra","BOM"), ("Punjab & Sind Bank","PSB"), ("HDFC Bank","HDFC"), ("ICICI Bank","ICICI"), ("Axis Bank","AXIS"),
            ("Kotak Mahindra Bank","KOTAK"), ("IndusInd Bank","INDUS"), ("Yes Bank","YES"), ("IDBI Bank","IDBI"), ("IDFC First Bank","IDFC"),
            ("Federal Bank","FED"), ("South Indian Bank","SIB"), ("Karnataka Bank","KTK"), ("Karur Vysya Bank","KVB"), ("City Union Bank","CUB"),
            ("RBL Bank","RBL"), ("Bandhan Bank","BANDHAN"), ("Jammu & Kashmir Bank","JKB"), ("Dhanlaxmi Bank","DLB"), ("Nainital Bank","NTB"),
            ("Ujjivan Small Finance Bank","UJJIVAN"), ("AU Small Finance Bank","AU"), ("Equitas Small Finance Bank","EQUITAS"), ("Other Bank","OTHER")
        ]
        for bname, bcode in banks:
            db.session.add(BankMaster(bank_name=bname, bank_code=bcode))
    try:
        db.session.commit()
    except:
        db.session.rollback()

def generate_product_code(category, count):
    base = ''.join([c for c in category if c.isalnum()])[:4].upper()
    if len(base)<4: base = (base + 'XXXX')[:4]
    return f"{base}-{count:04d}"

def generate_vendor_code(count):
    return f"VEND-{count:04d}"

# ========== API ==========
@app.route('/api/health')
def health():
    return jsonify(status='LIVE', version='v4.4.9 Vendor Master Enhanced', db_file='lemon_erp_v44_1_category.db', url='https://lemon-erp.onrender.com')

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

# SBUs API - v4.4.7 fixed + v4.4.8 masters reordered (unchanged)
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
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else f"ID {it.get('product_id')}", 'product_code':prod.product_code if prod else '', 'capacity_per_day': it.get('capacity_per_day') or it.get('capacity') or 0, 'capacity': it.get('capacity_per_day') or 0})
                return {'id':k.id,'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':pcs,'products_capacity_raw':k.products_capacity}
            def res_sz(sp):
                try: raw=json.loads(sp.products_capacity) if sp.products_capacity else []
                except: raw=[]
                pcs=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else f"ID {it.get('product_id')}", 'product_code':prod.product_code if prod else '', 'capacity_per_hour':it.get('capacity_per_hour') or it.get('capacity') or 0, 'capacity':it.get('capacity_per_hour') or 0, 'machineries':it.get('machineries','')})
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
    KilnAsset.query.filter_by(sbu_id=s.id).delete()
    SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
    HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
    StockYardAsset.query.filter_by(sbu_id=s.id).delete()
    db.session.delete(s); db.session.commit()
    return jsonify(ok=True)

# Vendor Masters API - hidden
@app.route('/api/vendor_masters')
def vendor_masters_api():
    legal=[{'id':l.id,'name':l.name} for l in LegalStatusMaster.query.order_by(LegalStatusMaster.name).all()]
    vcat=[{'id':v.id,'name':v.name} for v in VendorCategoryMaster.query.order_by(VendorCategoryMaster.name).all()]
    desg=[{'id':d.id,'name':d.name} for d in DesignationMaster.query.order_by(DesignationMaster.name).all()]
    banks=[{'id':b.id,'bank_name':b.bank_name,'bank_code':b.bank_code} for b in BankMaster.query.order_by(BankMaster.bank_name).all()]
    return jsonify(legal_status=legal, vendor_category=vcat, designations=desg, banks=banks)

@app.route('/api/vendor_masters/<string:mtype>', methods=['GET','POST'])
def vendor_master_type(mtype):
    mapping={'legal_status':LegalStatusMaster,'vendor_category':VendorCategoryMaster,'designation':DesignationMaster,'bank':BankMaster}
    Model=mapping.get(mtype)
    if not Model: return jsonify(error='Invalid type'),400
    if request.method=='GET':
        if mtype=='bank':
            return jsonify([{'id':b.id,'bank_name':b.bank_name,'bank_code':b.bank_code,'name':b.bank_name} for b in Model.query.order_by(Model.bank_name).all()])
        return jsonify([{'id':x.id,'name':x.name} for x in Model.query.order_by(Model.name).all()])
    data=request.get_json() or {}
    name=(data.get('name') or data.get('bank_name') or '').strip()
    if not name: return jsonify(error='Name required'),400
    if mtype=='bank':
        if BankMaster.query.filter_by(bank_name=name).first(): return jsonify(error='Exists'),400
        obj=BankMaster(bank_name=name, bank_code=data.get('bank_code','OTHER'))
    else:
        if Model.query.filter_by(name=name).first(): return jsonify(error='Exists'),400
        obj=Model(name=name)
    db.session.add(obj); db.session.commit()
    return jsonify(ok=True, id=obj.id)

# Vendor Enhanced API v4.4.9
@app.route('/api/vendors', methods=['GET','POST'])
def vendors_api():
    if request.method=='GET':
        q=request.args.get('search','').lower()
        type_f=request.args.get('type','')
        cat_f=request.args.get('category','')
        status_f=request.args.get('status','')
        state_f=request.args.get('state','')
        approval_f=request.args.get('approval','')
        rating_f=request.args.get('rating','')
        vendors=Vendor.query.order_by(Vendor.id.desc()).all()
        result=[]
        for v in vendors:
            po_list=PO.query.filter((PO.vendor_id==v.id) | (PO.vendor==v.name)).all()
            po_count=len(po_list)
            grn_count=GRN.query.filter((GRN.vendor_id==v.id) | (GRN.vendor==v.name)).count()
            # calc business value and last transaction
            total_val=sum([(p.qty or 0)*(p.rate or 0) for p in po_list])
            last_trans = max([p.created_at for p in po_list if p.created_at], default='') if po_list else v.last_transaction_date
            try:
                banks=json.loads(v.bank_details) if v.bank_details else []
            except:
                banks=[]
            try:
                contacts=json.loads(v.contacts) if v.contacts else []
            except:
                contacts=[]
            try:
                docs=json.loads(v.documents) if v.documents else {}
            except:
                docs={}
            if q and not (q in (v.name or '').lower() or q in (v.vendor_code or '').lower() or q in (v.gst_no or '').lower() or q in (v.pan_no or '').lower() or q in (v.station or '').lower() or q in (v.state or '').lower() or q in (v.msme_cert_no or '').lower()):
                continue
            if type_f and v.legal_status!=type_f: continue
            if cat_f and v.vendor_category!=cat_f: continue
            if status_f and v.status!=status_f: continue
            if state_f and v.state!=state_f: continue
            if approval_f and v.approval_status!=approval_f: continue
            if rating_f and str(v.vendor_rating)!=str(rating_f): continue
            result.append({
                'id':v.id,'vendor_code':v.vendor_code,'name':v.name,'station':v.station,'address':v.address,'state':v.state,
                'gst_no':v.gst_no,'pan_no':v.pan_no,'tan_no':v.tan_no,'legal_status':v.legal_status,'vendor_category':v.vendor_category,
                'bank_details':banks,'contacts':contacts,'status':v.status,
                'msme_cert_no':v.msme_cert_no,'msme_expiry':v.msme_expiry,'msme_upload':bool(v.msme_upload),
                'gst_reg_type':v.gst_reg_type,'tds_section':v.tds_section,'vendor_rating':v.vendor_rating,'last_audit_date':v.last_audit_date,
                'documents':docs,'has_docs':len(docs)>0,
                'opening_balance':v.opening_balance,'opening_balance_type':v.opening_balance_type,'ledger_group':v.ledger_group,
                'created_by':v.created_by,'created_at':v.created_at,'updated_by':v.updated_by,'updated_at':v.updated_at,
                'approval_status':v.approval_status,'last_transaction_date':last_trans or v.last_transaction_date,'total_business_value':total_val or v.total_business_value,
                'po_count':po_count,'grn_count':grn_count,
                'type':v.legal_status or v.type,'gst':v.gst_no,'contact':contacts[0]['name'] if contacts else ''
            })
        return jsonify(result)
    data=request.get_json() or {}
    name=(data.get('name') or '').strip()
    if not name: return jsonify(error='Vendor Name mandatory'),400
    cnt=Vendor.query.count()+1
    code=generate_vendor_code(cnt)
    while Vendor.query.filter_by(vendor_code=code).first():
        cnt+=1; code=generate_vendor_code(cnt)
    v=Vendor(
        vendor_code=code,
        name=name,
        station=data.get('station',''),
        address=data.get('address',''),
        state=data.get('state',''),
        gst_no=data.get('gst_no',''),
        pan_no=data.get('pan_no',''),
        tan_no=data.get('tan_no',''),
        legal_status=data.get('legal_status',''),
        vendor_category=data.get('vendor_category',''),
        bank_details=json.dumps(data.get('bank_details',[])),
        contacts=json.dumps(data.get('contacts',[])),
        status=data.get('status','Active'),
        msme_cert_no=data.get('msme_cert_no',''),
        msme_expiry=data.get('msme_expiry',''),
        msme_upload=data.get('msme_upload',''),
        gst_reg_type=data.get('gst_reg_type','Regular'),
        tds_section=data.get('tds_section','194C'),
        vendor_rating=int(data.get('vendor_rating') or 0),
        last_audit_date=data.get('last_audit_date',''),
        documents=json.dumps(data.get('documents',{})),
        opening_balance=float(data.get('opening_balance') or 0),
        opening_balance_type=data.get('opening_balance_type','Dr'),
        ledger_group=data.get('ledger_group','Sundry Creditors'),
        created_by=data.get('created_by','Admin'),
        updated_by=data.get('created_by','Admin'),
        approval_status=data.get('approval_status','Draft'),
        type=data.get('legal_status',''),
        contact=data.get('contacts',[{}])[0].get('name','') if data.get('contacts') else ''
    )
    db.session.add(v); db.session.commit()
    return jsonify(id=v.id, vendor_code=v.vendor_code, name=v.name)

@app.route('/api/vendors/<int:vid>', methods=['GET','PUT','DELETE'])
def vendor_one(vid):
    v=Vendor.query.get_or_404(vid)
    if request.method=='GET':
        try:
            banks=json.loads(v.bank_details) if v.bank_details else []
        except:
            banks=[]
        try:
            contacts=json.loads(v.contacts) if v.contacts else []
        except:
            contacts=[]
        try:
            docs=json.loads(v.documents) if v.documents else {}
        except:
            docs={}
        po_list=PO.query.filter((PO.vendor_id==v.id) | (PO.vendor==v.name)).all()
        po_count=len(po_list)
        grn_count=GRN.query.filter((GRN.vendor_id==v.id) | (GRN.vendor==v.name)).count()
        total_val=sum([(p.qty or 0)*(p.rate or 0) for p in po_list])
        last_trans = max([p.created_at for p in po_list if p.created_at], default='') if po_list else v.last_transaction_date
        return jsonify(id=v.id, vendor_code=v.vendor_code, name=v.name, station=v.station, address=v.address, state=v.state, gst_no=v.gst_no, pan_no=v.pan_no, tan_no=v.tan_no, legal_status=v.legal_status, vendor_category=v.vendor_category, bank_details=banks, contacts=contacts, status=v.status, msme_cert_no=v.msme_cert_no, msme_expiry=v.msme_expiry, msme_upload=v.msme_upload, gst_reg_type=v.gst_reg_type, tds_section=v.tds_section, vendor_rating=v.vendor_rating, last_audit_date=v.last_audit_date, documents=docs, opening_balance=v.opening_balance, opening_balance_type=v.opening_balance_type, ledger_group=v.ledger_group, created_by=v.created_by, created_at=v.created_at, updated_by=v.updated_by, updated_at=v.updated_at, approval_status=v.approval_status, last_transaction_date=last_trans or v.last_transaction_date, total_business_value=total_val or v.total_business_value, po_count=po_count, grn_count=grn_count)
    if request.method=='PUT':
        data=request.get_json() or {}
        name=(data.get('name') or '').strip()
        if not name: return jsonify(error='Vendor Name mandatory'),400
        v.name=name
        v.station=data.get('station', v.station)
        v.address=data.get('address', v.address)
        v.state=data.get('state', v.state)
        v.gst_no=data.get('gst_no', v.gst_no)
        v.pan_no=data.get('pan_no', v.pan_no)
        v.tan_no=data.get('tan_no', v.tan_no)
        v.legal_status=data.get('legal_status', v.legal_status)
        v.vendor_category=data.get('vendor_category', v.vendor_category)
        v.bank_details=json.dumps(data.get('bank_details', []))
        v.contacts=json.dumps(data.get('contacts', []))
        v.status=data.get('status', v.status)
        v.msme_cert_no=data.get('msme_cert_no', v.msme_cert_no)
        v.msme_expiry=data.get('msme_expiry', v.msme_expiry)
        if data.get('msme_upload'): v.msme_upload=data.get('msme_upload')
        v.gst_reg_type=data.get('gst_reg_type', v.gst_reg_type)
        v.tds_section=data.get('tds_section', v.tds_section)
        v.vendor_rating=int(data.get('vendor_rating') or v.vendor_rating or 0)
        v.last_audit_date=data.get('last_audit_date', v.last_audit_date)
        if data.get('documents'): v.documents=json.dumps(data.get('documents'))
        v.opening_balance=float(data.get('opening_balance') or v.opening_balance or 0)
        v.opening_balance_type=data.get('opening_balance_type', v.opening_balance_type)
        v.ledger_group=data.get('ledger_group', v.ledger_group)
        v.updated_by=data.get('updated_by','Admin')
        v.updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        v.approval_status=data.get('approval_status', v.approval_status)
        v.type=v.legal_status
        db.session.commit()
        return jsonify(ok=True)
    db.session.delete(v); db.session.commit()
    return jsonify(ok=True)

# Other modules API minimal
@app.route('/api/inventory/combined')
def inv_combined():
    prods=Product.query.all()
    raw=[{'product_code':p.product_code,'hsn_code':p.hsn_code,'name':p.name,'total_mt':p.total_stock_mt,'status':'OK'} for p in prods if 'raw' in p.category.lower() or 'lime' in p.category.lower()]
    finished=[{'product_code':p.product_code,'hsn_code':p.hsn_code,'name':p.name,'total_mt':p.total_stock_mt,'status':'OK'} for p in prods]
    return jsonify(raw=raw, wip=[], finished=finished, total_value_lakh=sum([p.total_stock_mt*1000/100000 for p in prods]))

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
    if request.method=='GET': return jsonify([{'id':p.id,'vendor':p.vendor,'material':p.material,'qty':p.qty,'status':p.status} for p in PO.query.order_by(PO.id.desc()).all()])
    return jsonify(ok=True)

@app.route('/api/grn', methods=['GET','POST'])
def grn_api():
    if request.method=='GET': return jsonify([{'id':g.id,'vehicle_no':g.vehicle_no,'material':g.material,'vendor':g.vendor} for g in GRN.query.order_by(GRN.id.desc()).all()])
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

# ========== FRONTEND HTML - v4.4.9 Vendor Master Enhanced ==========
HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemon ERP v4.4.10.1 - Vendor Docs Drag Drop + File Select</title>
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
.filter-bar{background:white;border:1.5px solid var(--line);border-radius:10px;padding:10px;margin:10px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:end}
.search-input{position:relative} .search-input i{position:absolute;left:8px;top:50%;transform:translateY(-50%);color:#888}
.search-input input{padding-left:28px}

/* v4.4.10.1 Drag & Drop Document Upload Styles - ONLY Vendor Docs */
.drop-zone{border:2px dashed var(--brass);border-radius:10px;padding:16px;text-align:center;background:#FFFBEB;cursor:pointer;transition:all 0.2s;min-height:90px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}
.drop-zone:hover{background:#FFF8E1;border-color:#1A2E1E}
.drop-zone.dragover{background:#E8F0FE;border-color:#1A2E1E;transform:scale(1.02);box-shadow:0 4px 12px rgba(26,46,30,0.15)}
.drop-zone i{font-size:28px;color:var(--brass)}
.drop-zone .dz-title{font-size:11px;font-weight:800;color:#1A2E1E}
.drop-zone .dz-hint{font-size:9px;color:#888}
.drop-zone .dz-file{font-size:10px;font-weight:700;color:#1A2E1E;background:white;padding:4px 8px;border-radius:6px;border:1px solid var(--line);margin-top:4px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.drop-zone .dz-clear{font-size:9px;color:#B33;background:none;border:none;cursor:pointer;text-decoration:underline;margin-top:4px}
.doc-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:700px){.doc-grid{grid-template-columns:1fr}}

</style></head>
<body>
<div class="topnav"><div class="brand">🍋 LEMON <span>ERP</span> v4.4.10.1 - Vendor Docs Drag Drop + File Select - Base v1.3.py</div><button class="btn btn-y" onclick="location.reload()">Reload</button></div>
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
<div class="card"><h3>Dashboard - v4.4.10.1 Vendor Docs Drag Drop + File Select - Single Dropdown - Base v1.3.py</h3>
<div class="row"><div class="card kpi"><div>Total Value</div><div class="val" id="totalVal">Rs 0 Lakh</div></div><div class="card kpi"><div>SBUs</div><div class="val" id="sbuCountDash">0</div></div><div class="card kpi"><div>Products</div><div class="val" id="prodCountDash">0</div></div><div class="card kpi"><div>Categories</div><div class="val" id="catCountDash">0</div></div></div>
<div class="card"><b>v4.4.10 Changes:</b> ONLY Vendor Master Enhanced - A MSME Cert No+Expiry+Upload GST Reg Type Regular/Composition/Unregistered/SEZ TDS 194C/194J/194Q/194H Rating 1-5 + Last Audit + Docs GST Cert PAN Cheque MSME ISO + B Opening Bal Dr/Cr Ledger Group Sundry Creditors + E Dept + Primary flag + F CreatedBy/At UpdatedBy/At Approval Draft/Pending/Approved/Rejected Last Trans Date Total Business Value - Bank single dropdown fix kept - Nothing removed - Heading + Add Vendor Button top + Filters + Search bar + Auto Code VEND-0001 + Station/State/GST/PAN/TAN/Legal Status/Vendor Category hidden masters + Bank Details Add Bank Account (Bank searchable nationalised banks + Branch/Account Name/IFSC/Account No/Transaction Limit) + Add Contact (Name/Designation hidden master/Mobile/Whatsapp/Land Line/Ext/Email) + PO/GRN counts - Everything else locked to v4.4.8 FIXED</div>
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
<div class="card" style="text-align:center"><h1 style="font-size:22px;font-weight:900;text-align:center"><i class="bi bi-bag"></i> Products</h1><p style="font-size:11px;color:#666;text-align:center">Landing Page Heading Products centrally aligned - HSN + Description + Auto Code + Category-wise + Hover narration - v4.4.3 Unchanged</p><button class="btn btn-y" style="padding:12px 28px;font-size:14px;font-weight:800" onclick="openAddProductPopup()">Add New Product</button>
<div id="prodList"></div></div></div>

<!-- SBUS -->
<div id="sbus" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 14px;text-align:center"><i class="bi bi-building"></i> Strategic Business Units</h1>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddSBU()">Add New SBU</button>
</div>
<div id="sbuList">Loading SBUs...</div>
</div>

<!-- VENDORS v4.4.10 COMPLIANCE + DOCS + OPENING + WORKFLOW -->
<div id="vendors" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 6px;text-align:center"><i class="bi bi-people"></i> Vendor Master</h1>
<p style="font-size:11px;color:#666;text-align:center;margin:0 0 14px">Vendor Master - VEND-0001 + Compliance MSME GST Reg TDS Rating + Docs GST PAN Cheque MSME ISO + Opening Bal Dr/Cr Ledger + Dept Primary + Workflow Draft/Pending/Approved + Business Value - v4.4.10 - Base v1.3.py</p>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddVendorPopup()">Add New Vendor</button>
</div>

<div class="filter-bar">
<div class="search-input" style="flex:2;min-width:200px"><i class="bi bi-search"></i><input id="vendorSearch" placeholder="Search Name, Code, Station, State, GST, PAN, MSME Cert..." onkeyup="loadVendors()"></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">Legal Status</label><select id="vendorLegalFilter" onchange="loadVendors()"><option value="">All Legal Status</option></select></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">Category</label><select id="vendorCatFilter" onchange="loadVendors()"><option value="">All Categories</option></select></div>
<div style="flex:1;min-width:100px"><label style="font-size:10px;font-weight:700">State</label><select id="vendorStateFilter" onchange="loadVendors()"><option value="">All States</option></select></div>
<div style="flex:1;min-width:100px"><label style="font-size:10px;font-weight:700">Status</label><select id="vendorStatusFilter" onchange="loadVendors()"><option value="">All Status</option><option value="Active">Active</option><option value="Inactive">Inactive</option><option value="Blocked">Blocked</option></select></div>
<div style="flex:1;min-width:110px"><label style="font-size:10px;font-weight:700">Approval</label><select id="vendorApprovalFilter" onchange="loadVendors()"><option value="">All Approval</option><option value="Draft">Draft</option><option value="Pending">Pending</option><option value="Approved">Approved</option><option value="Rejected">Rejected</option></select></div>
<div style="flex:1;min-width:80px"><label style="font-size:10px;font-weight:700">Rating</label><select id="vendorRatingFilter" onchange="loadVendors()"><option value="">All Rating</option><option value="5">5★</option><option value="4">4★</option><option value="3">3★</option><option value="2">2★</option><option value="1">1★</option></select></div>
<div style="display:flex;gap:6px;align-items:end"><button class="btn btn-g" onclick="loadVendors()">Filter</button><button class="btn btn-w" onclick="resetVendorFilters()">Reset</button></div>
</div>

<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h3>Vendors List - Compliance + Docs + Business Value - v4.4.10</h3><span id="vendorCountBadge" class="badge brass">0 Vendors</span></div>
<div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Code | Name</th><th>Station | State | GST Reg</th><th>MSME | Rating | Audit</th><th>Opening | Ledger | TDS</th><th>Banks | Contacts (Dept+Primary)</th><th>POs | GRNs | Value | Last Trans</th><th>Docs | Approval | Status | Created</th><th>Actions</th></tr></thead><tbody id="vendorTbl"></tbody></table></div>
</div>
</div>

<!-- STOCK etc -->
<div id="stock" class="tabcontent hidden"><div class="card"><h3>Stock - v4.4 Unchanged</h3><div class="row"><select id="fUnit"><option>All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="loadStock()">Filter</button></div><div id="rawTbl"></div><div id="wipTbl"></div><div id="finTbl"></div></div></div>
<div id="make" class="tabcontent hidden"><div class="card"><h3>Make</h3><p>Make module v4.4 Unchanged</p><div id="moList"></div></div></div>
<div id="buy" class="tabcontent hidden"><div class="card"><h3>Buy</h3><p>Buy module v4.4 Unchanged</p></div></div>
<div id="sell" class="tabcontent hidden"><div class="card"><h3>Sell</h3><p>Sell module v4.4 Unchanged</p></div></div>
<div id="customers" class="tabcontent hidden"><div class="card"><h3>Customers</h3><table><tbody id="customerTbl"></tbody></table></div></div>
<div id="pack" class="tabcontent hidden"><div class="card"><h3>Pack</h3><p>Pack v4.4</p></div></div>
<div id="qr" class="tabcontent hidden"><div class="card"><h3>QR</h3><p>QR module</p><div id="qrList"></div></div></div>
<div id="cost" class="tabcontent hidden"><div class="card"><h3>Cost</h3><div id="costVal"></div><div id="costTbl"></div></div></div>
<div id="mobile" class="tabcontent hidden"><div class="card"><h3>Mobile - Placeholder</h3></div></div>
</div></div>

<!-- PRODUCT MODAL -->
<div id="productModal" class="modal hidden" onclick="if(event.target===this) closeProductPopup()"><div class="modal-content" style="max-width:620px"><div class="modal-header"><b>Add Product - HSN + Description + Auto Code - v4.4.3</b><button class="close-x" onclick="closeProductPopup()">×</button></div><div class="modal-body"><input type="hidden" id="prod_id"><div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">Product Name *<input id="prod_name">Product Category *<select id="prod_cat"></select><p style="font-size:10px;color:#888">DB File: lemon_erp_v44_1_category.db - Table: product_category</p><div class="row"><div>HSN Code *<input id="prod_hsn" placeholder="2522"></div><div>Product Code (Auto)<input id="prod_code_preview" disabled style="background:var(--alab);font-weight:800"></div></div>Product Description *<textarea id="prod_desc" placeholder="Product Description - Mandatory - Shows narration when roll mouse over name in list"></textarea></div></div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:13px" onclick="saveProduct()">Save Product - Auto Code Generate</button><button class="btn btn-w" onclick="closeProductPopup()">Cancel</button></div></div></div>

<!-- SBU MODAL -->
<div id="sbuModal" class="modal hidden" onclick="if(event.target===this) closeAddSBU()"><div class="modal-content" style="max-width:1000px"><div class="modal-header"><b>Add SBU - Strategic Business Units - v4.4.9</b><button class="close-x" onclick="closeAddSBU()">×</button></div><div class="modal-body">
<input type="hidden" id="sbu_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>SBU Details</b><div style="margin-top:8px">SBU Name - e.g. Unit 1 72MT, Jodhpur Plant *<input id="sbu_name" placeholder="SBU Name"></div>Address - Full address field<textarea id="sbu_address" placeholder="Address - Full address field e.g. Plot 123, RIICO Industrial Area, Jodhpur, Rajasthan 342001"></textarea></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>🔥 Kilns - v4.4.7 Fixed - Lining & Health once per kiln</h4><button class="btn btn-y" onclick="addKilnField()">Add Kiln</button></div><p style="font-size:10px;color:#666">When clicked Add Kiln - Add new line: *Kiln No. *Lining Date *Health Status *Products and Capacity *Add Product Button *Delete button. Products only ask Product + Capacity/Day.</p><div id="kilnsContainer"><p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p></div></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>⚙ Sizing Plants</h4><button class="btn btn-y" onclick="addSizingField()">Add Sizing Plant</button></div><div id="sizingContainer"><p style="text-align:center;color:#888">No sizing plants</p></div></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>💧 Hydration Plants</h4><button class="btn btn-y" onclick="addHydrationField()">Add Hydration Plant</button></div><div id="hydrationContainer"><p style="text-align:center;color:#888">No hydration plants</p></div></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>📦 Stock Yards</h4><button class="btn btn-y" onclick="addYardField()">Add Stock Yard</button></div><p style="font-size:10px;color:#666">Add Stock Yard Button - when clicked: *Yard Name *Add Yard Items - dropdown from all categories, Opening stock.</p><div id="yardsContainer"><p style="text-align:center;color:#888">No stock yards</p></div></div>
</div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="saveSBU()">Save SBU - Strategic Business Units</button><button class="btn btn-w" onclick="closeAddSBU()">Cancel</button></div></div></div>

<!-- VENDOR MODAL v4.4.10 COMPLIANCE + DOCS + OPENING + WORKFLOW -->
<div id="vendorModal" class="modal hidden" onclick="if(event.target===this) closeAddVendorPopup()"><div class="modal-content" style="max-width:1200px"><div class="modal-header"><b>Add Vendor - v4.4.10 Compliance Docs Opening Bal Workflow - VEND-0001 + Banks + Contacts + Dept Primary</b><button class="close-x" onclick="closeAddVendorPopup()">×</button></div><div class="modal-body">
<input type="hidden" id="vend_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>Vendor Details - Mandatory Fields * - v4.4.10</b>
<div class="row"><div>Vendor Name *<input id="vend_name" placeholder="Vendor Name e.g. Rajasthan Limestone Suppliers"></div><div>Station - Text field<input id="vend_station" placeholder="Station e.g. Jodhpur, Gotan, Beawar"></div></div>
<div>Address - Text<textarea id="vend_address" placeholder="Full Address"></textarea></div>
<div class="row"><div>State - Text (for identifying GST code)<input id="vend_state" placeholder="State e.g. Rajasthan - RJ" list="stateList"><datalist id="stateList"><option value="Rajasthan"><option value="Gujarat"><option value="Madhya Pradesh"><option value="Maharashtra"><option value="Uttar Pradesh"><option value="Andhra Pradesh"><option value="Karnataka"><option value="Tamil Nadu"><option value="Haryana"><option value="Punjab"><option value="Delhi"><option value="West Bengal"><option value="Bihar"><option value="Odisha"><option value="Chhattisgarh"></datalist></div><div>GST No. - Text<input id="vend_gst" placeholder="22AAAAA0000A1Z5"></div></div>
<div class="row"><div>PAN No. - Text<input id="vend_pan" placeholder="AAAAA0000A"></div><div>TAN No. - Text<input id="vend_tan" placeholder="AAAA00000A"></div></div>
<div class="row"><div>Legal Status - Dropdown<input type="hidden" id="vend_legal_status"><select id="vend_legal_status_sel" onchange="document.getElementById('vend_legal_status').value=this.value"><option value="">Select Legal Status</option></select><p style="font-size:9px;color:#888">Hidden master: Proprietor, Partnership, Private Limited etc</p></div><div>Vendor Category - Dropdown<input type="hidden" id="vend_category"><select id="vend_category_sel" onchange="document.getElementById('vend_category').value=this.value"><option value="">Select Category</option></select><p style="font-size:9px;color:#888">Hidden master: MSE, MSME, SSI, Large etc</p></div></div>
<div class="row"><div>Vendor Code - Auto Generated<input id="vend_code_preview" disabled style="background:var(--alab);font-weight:800" placeholder="VEND-0001 Auto when saved"></div><div>Status<select id="vend_status"><option value="Active">Active</option><option value="Inactive">Inactive</option><option value="Blocked">Blocked</option></select></div></div>
</div>

<div class="asset-section"><h4>📋 Compliance - MSME + GST Reg Type + TDS + Rating + Audit - v4.4.10</h4>
<div class="row"><div>MSME Certificate No<input id="vend_msme_no" placeholder="MSME Cert No e.g. UDYAM-RJ-..."></div><div>MSME Expiry Date<input type="date" id="vend_msme_expiry"></div><div>MSME Upload (File name / base64)<input id="vend_msme_upload" placeholder="Paste base64 or file name - GST Cert upload section below for all docs"></div></div>
<div class="row"><div>GST Registration Type<select id="vend_gst_reg_type"><option value="Regular">Regular</option><option value="Composition">Composition</option><option value="Unregistered">Unregistered</option><option value="SEZ">SEZ</option><option value="Deemed Export">Deemed Export</option><option value="Overseas">Overseas</option></select></div><div>TDS Section<select id="vend_tds_section"><option value="194C">194C - Contractors</option><option value="194J">194J - Professional</option><option value="194Q">194Q - Purchase >50L</option><option value="194H">194H - Commission</option><option value="194I">194I - Rent</option><option value="192">192 - Salary</option><option value="None">None</option></select></div></div>
<div class="row"><div>Vendor Rating 1-5 stars<select id="vend_rating"><option value="0">0 - Not Rated</option><option value="1">1★ - Poor</option><option value="2">2★ - Average</option><option value="3">3★ - Good</option><option value="4">4★ - Very Good</option><option value="5">5★ - Excellent</option></select></div><div>Last Audit Date<input type="date" id="vend_last_audit"></div></div>
</div>

<div class="asset-section"><h4>📄 Document Uploads - Drag & Drop + File Select - GST, PAN, Cheque, MSME, ISO - v4.4.10.1</h4><p style="font-size:10px;color:#666">Select file from computer - Drag & Drop supported - Stored as base64 in documents JSON - {gst_cert, pan_card, cancelled_cheque, msme_cert, iso_cert, other} - Preview file name + size - Click to select or drag file onto zone - Supports PDF, JPG, PNG</p>
<div class="doc-grid">
<div><label style="font-size:10px;font-weight:700">GST Certificate</label><div class="drop-zone" id="dz_gst_cert" onclick="document.getElementById('file_gst_cert').click()" ondragover="handleDragOver(event,'dz_gst_cert')" ondragleave="handleDragLeave(event,'dz_gst_cert')" ondrop="handleDrop(event,'gst_cert')"><i class="bi bi-cloud-arrow-up"></i><div class="dz-title">GST Certificate</div><div class="dz-hint">Click to select file or drag & drop here<br>PDF, JPG, PNG up to 5MB</div><div class="dz-file" id="dz_file_gst_cert" style="display:none"></div><button class="dz-clear" id="dz_clear_gst_cert" style="display:none" onclick="clearDoc('gst_cert',event)">Clear</button></div><input type="file" id="file_gst_cert" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'gst_cert')"><input type="hidden" id="doc_gst_cert"><small style="font-size:9px;color:#888" id="doc_gst_cert_info">No file selected - will store base64</small></div>
<div><label style="font-size:10px;font-weight:700">PAN Card</label><div class="drop-zone" id="dz_pan_card" onclick="document.getElementById('file_pan_card').click()" ondragover="handleDragOver(event,'dz_pan_card')" ondragleave="handleDragLeave(event,'dz_pan_card')" ondrop="handleDrop(event,'pan_card')"><i class="bi bi-card-image"></i><div class="dz-title">PAN Card</div><div class="dz-hint">Click to select or drag & drop<br>PDF, JPG, PNG</div><div class="dz-file" id="dz_file_pan_card" style="display:none"></div><button class="dz-clear" id="dz_clear_pan_card" style="display:none" onclick="clearDoc('pan_card',event)">Clear</button></div><input type="file" id="file_pan_card" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'pan_card')"><input type="hidden" id="doc_pan_card"><small style="font-size:9px;color:#888" id="doc_pan_card_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">Cancelled Cheque</label><div class="drop-zone" id="dz_cancelled_cheque" onclick="document.getElementById('file_cancelled_cheque').click()" ondragover="handleDragOver(event,'dz_cancelled_cheque')" ondragleave="handleDragLeave(event,'dz_cancelled_cheque')" ondrop="handleDrop(event,'cancelled_cheque')"><i class="bi bi-bank"></i><div class="dz-title">Cancelled Cheque</div><div class="dz-hint">Click to select or drag & drop</div><div class="dz-file" id="dz_file_cancelled_cheque" style="display:none"></div><button class="dz-clear" id="dz_clear_cancelled_cheque" style="display:none" onclick="clearDoc('cancelled_cheque',event)">Clear</button></div><input type="file" id="file_cancelled_cheque" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'cancelled_cheque')"><input type="hidden" id="doc_cancelled_cheque"><small style="font-size:9px;color:#888" id="doc_cancelled_cheque_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">MSME Certificate</label><div class="drop-zone" id="dz_msme_cert" onclick="document.getElementById('file_msme_cert').click()" ondragover="handleDragOver(event,'dz_msme_cert')" ondragleave="handleDragLeave(event,'dz_msme_cert')" ondrop="handleDrop(event,'msme_cert')"><i class="bi bi-award"></i><div class="dz-title">MSME Certificate</div><div class="dz-hint">Click to select or drag & drop</div><div class="dz-file" id="dz_file_msme_cert" style="display:none"></div><button class="dz-clear" id="dz_clear_msme_cert" style="display:none" onclick="clearDoc('msme_cert',event)">Clear</button></div><input type="file" id="file_msme_cert" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'msme_cert')"><input type="hidden" id="doc_msme_cert"><small style="font-size:9px;color:#888" id="doc_msme_cert_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">ISO Certificate</label><div class="drop-zone" id="dz_iso_cert" onclick="document.getElementById('file_iso_cert').click()" ondragover="handleDragOver(event,'dz_iso_cert')" ondragleave="handleDragLeave(event,'dz_iso_cert')" ondrop="handleDrop(event,'iso_cert')"><i class="bi bi-patch-check"></i><div class="dz-title">ISO Certificate</div><div class="dz-hint">Click to select or drag & drop</div><div class="dz-file" id="dz_file_iso_cert" style="display:none"></div><button class="dz-clear" id="dz_clear_iso_cert" style="display:none" onclick="clearDoc('iso_cert',event)">Clear</button></div><input type="file" id="file_iso_cert" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'iso_cert')"><input type="hidden" id="doc_iso_cert"><small style="font-size:9px;color:#888" id="doc_iso_cert_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">Other Document</label><div class="drop-zone" id="dz_other" onclick="document.getElementById('file_other').click()" ondragover="handleDragOver(event,'dz_other')" ondragleave="handleDragLeave(event,'dz_other')" ondrop="handleDrop(event,'other')"><i class="bi bi-file-earmark-plus"></i><div class="dz-title">Other Document</div><div class="dz-hint">Click to select or drag & drop - Any file</div><div class="dz-file" id="dz_file_other" style="display:none"></div><button class="dz-clear" id="dz_clear_other" style="display:none" onclick="clearDoc('other',event)">Clear</button></div><input type="file" id="file_other" hidden accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onchange="handleFileSelect(event,'other')"><input type="hidden" id="doc_other"><small style="font-size:9px;color:#888" id="doc_other_info">No file selected</small></div>
</div>
<p style="font-size:9px;color:#1A2E1E;background:#F0F8FF;padding:6px;border-radius:6px;margin-top:8px">💡 v4.4.10.1 - Select file from computer with drag & drop - File stored as base64 data URI - Max 5MB per file - Previous version only had text input - Now enhanced with file select + drag drop + preview + clear - No other module changed</p>
</div>

<div class="asset-section"><h4>💰 Opening Balance + Ledger Group - For Migration - v4.4.10</h4>
<div class="row"><div>Opening Balance - Number<input type="number" id="vend_opening_bal" placeholder="Opening Balance e.g. 150000"></div><div>Dr/Cr<select id="vend_opening_type"><option value="Dr">Dr - Receivable from vendor (Advance paid)</option><option value="Cr">Cr - Payable to vendor (Due)</option></select></div></div>
<div class="row"><div>Ledger Group<input id="vend_ledger_group" list="ledgerList" placeholder="Sundry Creditors" value="Sundry Creditors"><datalist id="ledgerList"><option value="Sundry Creditors"><option value="Sundry Debtors"><option value="Trade Creditors"><option value="MSME Creditors"><option value="Non-MSME Creditors"><option value="Service Creditors"></datalist></div><div>Total Business Value (Auto from POs - qty*rate)<input id="vend_total_business" disabled style="background:var(--alab);font-weight:800" placeholder="Auto calculated from POs"></div></div>
</div>

<div class="asset-section"><h4>🏦 Bank Details - Add Bank Account Button - Single Searchable Dropdown - v4.4.10</h4><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-size:10px;color:#666">When clicked on Add Bank Account - Add new line: Select Bank searchable dropdown nationalised banks + Other bank hidden bank master + Branch + Account Name + IFSC + Account No + Transaction Limit</span><button class="btn btn-y" onclick="addVendorBankField()">Add Bank Account</button></div><div id="vendorBanksContainer"><p style="text-align:center;color:#888;padding:12px">No bank accounts - Click Add Bank Account Button</p></div></div>

<div class="asset-section"><h4>👤 Contacts - Add Contact Button - Dept + Primary Flag - v4.4.10</h4><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-size:10px;color:#666">When clicked on Add Contact - Add new line: Name + Designation hidden master + Department + Primary flag + Mobile + Whatsapp + Land Line + Ext + Email</span><button class="btn btn-y" onclick="addVendorContactField()">Add Contact</button></div><div id="vendorContactsContainer"><p style="text-align:center;color:#888;padding:12px">No contacts - Click Add Contact Button</p></div></div>

<div class="asset-section"><h4>✅ Approval Workflow + Audit - v4.4.10</h4>
<div class="row"><div>Approval Status<select id="vend_approval_status"><option value="Draft">Draft</option><option value="Pending">Pending Approval</option><option value="Approved">Approved</option><option value="Rejected">Rejected</option></select></div><div>Created By<input id="vend_created_by" placeholder="Admin" value="Admin"></div></div>
<div class="row"><div>Last Transaction Date (Auto from POs)<input id="vend_last_trans" disabled style="background:var(--alab)" placeholder="Auto from POs"></div><div>Updated By<input id="vend_updated_by" placeholder="Admin" value="Admin"></div></div>
<p style="font-size:10px;color:#888">Created At / Updated At auto - Total Business Value = Sum of PO qty*rate - Last Transaction = Max PO date - Approval workflow Draft→Pending→Approved→Rejected</p>
</div>

</div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="saveVendor()">Save Vendor - v4.4.10 Compliance + Docs + Opening + Workflow</button><button class="btn btn-w" onclick="closeAddVendorPopup()">Cancel</button></div></div></div>

<script>
function openTab(id){document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));document.getElementById(id).classList.remove('hidden');document.querySelectorAll('.menu').forEach(m=>m.classList.remove('active')); if(id==='product_category') loadCategories(); if(id==='products') loadProducts(); if(id==='sbus') loadSBUs(); if(id==='dash') loadDash(); if(id==='stock') loadStock(); if(id==='vendors') loadVendors();}

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
async function loadProdCatOptions(){let r=await fetch('/api/product_categories'); let d=await r.json(); let sel=document.getElementById('prod_cat'); if(!sel) return; sel.innerHTML='<option value="">Select Category</option>'; d.forEach(c=>{sel.innerHTML+=`<option value="${c.category_name}">${c.category_name}</option>`});}

// Products
async function loadProducts(){await loadAllProductsForSBU(); await loadProdCatOptions(); let r=await fetch('/api/products'); let d=await r.json(); let groups={}; d.forEach(p=>{if(!groups[p.category]) groups[p.category]=[]; groups[p.category].push(p);}); let html=''; for(let cat in groups){html+=`<div style="border:1.5px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden"><div style="background:var(--green);color:var(--brass);padding:10px 14px;font-weight:800;font-size:12px">${cat} - ${groups[cat].length} Products</div><table><thead><tr><th>Product Code</th><th>HSN</th><th>Product Name - Hover for Narration</th><th>Description</th><th>Actions</th></tr></thead><tbody>`; groups[cat].forEach(p=>{html+=`<tr><td><span style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line)">${p.product_code}</span></td><td><span class="badge ok">${p.hsn_code}</span></td><td><div class="tooltip">${p.name}<span class="tip">Code: ${p.product_code}<br>HSN: ${p.hsn_code}<br>Cat: ${p.category}<br>Desc: ${p.description}</span></div></td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px">${p.description}</td><td><button class="btn btn-b" onclick="editProd(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProd(${p.id})">Del</button></td></tr>`}); html+='</tbody></table></div>';} document.getElementById('prodList').innerHTML=html||'<p>No products</p>'; document.getElementById('prodCountDash').innerText=d.length;}
function openAddProductPopup(){document.getElementById('productModal').classList.remove('hidden');}
function closeProductPopup(){document.getElementById('productModal').classList.add('hidden'); document.getElementById('prod_id').value=''; document.getElementById('prod_name').value=''; document.getElementById('prod_hsn').value=''; document.getElementById('prod_desc').value=''; document.getElementById('prod_code_preview').value='';}
async function saveProduct(){let id=document.getElementById('prod_id').value; let payload={name:document.getElementById('prod_name').value, category:document.getElementById('prod_cat').value, hsn_code:document.getElementById('prod_hsn').value, description:document.getElementById('prod_desc').value}; if(!payload.name||!payload.category||!payload.hsn_code||!payload.description) return alert('All fields mandatory'); let url=id?`/api/products/${id}`:'/api/products'; let m=id?'PUT':'POST'; let res=await fetch(url,{method:m,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let j=await res.json(); if(res.ok){closeProductPopup(); loadProducts();} else alert(j.error);}
async function editProd(id){let r=await fetch(`/api/products/${id}`); let p=await r.json(); openAddProductPopup(); document.getElementById('prod_id').value=p.id; document.getElementById('prod_name').value=p.name; document.getElementById('prod_cat').value=p.category; document.getElementById('prod_hsn').value=p.hsn_code; document.getElementById('prod_desc').value=p.description; document.getElementById('prod_code_preview').value=p.product_code;}
async function delProd(id){if(!confirm('Delete?'))return; await fetch(`/api/products/${id}`,{method:'DELETE'}); loadProducts();}

// SBU v4.4.7 FIXED kept
function openAddSBU(){document.getElementById('sbuModal').classList.remove('hidden'); document.getElementById('sbu_id').value=''; document.getElementById('sbu_name').value=''; document.getElementById('sbu_address').value=''; document.getElementById('kilnsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p>'; document.getElementById('sizingContainer').innerHTML='<p style="text-align:center;color:#888">No sizing plants</p>'; document.getElementById('hydrationContainer').innerHTML='<p style="text-align:center;color:#888">No hydration plants</p>'; document.getElementById('yardsContainer').innerHTML='<p style="text-align:center;color:#888">No stock yards</p>'; loadAllProductsForSBU();}
function closeAddSBU(){document.getElementById('sbuModal').classList.add('hidden');}
function addKilnField(data=null){
 let c=document.getElementById('kilnsContainer'); if(c.innerHTML.includes('No kilns')) c.innerHTML='';
 kilnCounter++; let id=`kiln_${kilnCounter}_${Date.now()}`;
 let lining=data?.lining_installation_date||data?.lining_date||''; let health=data?.health_status||'Good';
 let html=`<div id="${id}" class="kiln-line"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px"><b>Kiln Line - *Kiln No. *Lining Date *Health + Products</b><div><button class="btn btn-b" onclick="addKilnProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete Kiln</button></div></div>
 <div class="row" style="margin-top:8px"><div>*Kiln No. e.g. Kiln 1, K-01<input class="k_no" placeholder="Kiln No." value="${data?.kiln_no||''}"></div><div>*Lining Installation Date<input type="date" class="k_lining" value="${lining}"></div><div>*Health Status<select class="k_health"><option ${health==='Good'?'selected':''}>Good</option><option ${health==='Needs Repair'?'selected':''}>Needs Repair</option><option ${health==='Critical'?'selected':''}>Critical</option><option ${health==='New'?'selected':''}>New</option></select></div></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Products and Capacity - v4.4.7 Fixed (Product + Capacity only)</b><div id="${id}-products" class="kiln-products-container">${data?.products_capacity?.length? '' : '<p style="font-size:10px;color:#888">No products - Click Add Product → Inset Product name, Capacity/Day, Delete</p>'}</div></div></div>`;
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
   list.innerHTML=`<div style="text-align:center;padding:30px"><p>No SBUs - Masters empty - Strategic Business Units</p><button class="btn btn-y" onclick="openAddSBU()">Add First SBU</button></div>`;
   return;
 }
 let h='';
 sbus.forEach(s=>{
   let kilnBadge=`${s.kilns.length} Kilns`; let sizBadge=`${s.sizing_plants.length} Sizing`; let hydBadge=`${s.hydration_plants.length} Hydration`; let yardBadge=`${s.stock_yards.length} Yards`;
   h+=`<div class="sbu-card"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px"><div><h3 style="font-size:16px;margin:0"><i class="bi bi-building"></i> ${s.sbu_name}</h3><p style="font-size:11px;color:#666;margin:2px 0"><i class="bi bi-geo-alt"></i> ${s.address||''}</p><p style="font-size:10px;margin-top:6px"><span class="badge brass">${kilnBadge}</span> <span class="badge brass">${sizBadge}</span> <span class="badge brass">${hydBadge}</span> <span class="badge brass">${yardBadge}</span></p></div><div style="display:flex;gap:6px;align-items:start"><button class="btn btn-b" onclick="editSBU(${s.id})">Edit</button><button class="btn btn-o" onclick="duplicateSBU(${s.id})">Duplicate</button><button class="btn btn-r" onclick="delSBU(${s.id})">Delete</button></div></div>`;
   h+=`<div style="margin-top:10px">`;
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
   h+=`</div></div>`;
 });
 list.innerHTML=h;
}
async function editSBU(id){
 let r=await fetch(`/api/sbus/${id}`); let s=await r.json();
 openAddSBU();
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

// Vendor v4.4.10 Compliance + Docs + Opening + Workflow - Enhanced
let vendorBanks=[], vendorContacts=[], vendorMasters={banks:[], legal_status:[], vendor_category:[], designations:[]};

async function loadVendorMasters(){
 let r=await fetch('/api/vendor_masters'); let d=await r.json(); vendorMasters=d;
 let legalSel=document.getElementById('vendorLegalFilter'); let catSel=document.getElementById('vendorCatFilter');
 let legalModalSel=document.getElementById('vend_legal_status_sel'); let catModalSel=document.getElementById('vend_category_sel');
 if(legalSel) {legalSel.innerHTML='<option value="">All Legal Status</option>'; }
 if(catSel) catSel.innerHTML='<option value="">All Categories</option>';
 if(legalModalSel) legalModalSel.innerHTML='<option value="">Select Legal Status</option>';
 if(catModalSel) catModalSel.innerHTML='<option value="">Select Category</option>';
 d.legal_status.forEach(ls=>{ if(legalSel) legalSel.innerHTML+=`<option value="${ls.name}">${ls.name}</option>`; if(legalModalSel) legalModalSel.innerHTML+=`<option value="${ls.name}">${ls.name}</option>`; });
 d.vendor_category.forEach(vc=>{ if(catSel) catSel.innerHTML+=`<option value="${vc.name}">${vc.name}</option>`; if(catModalSel) catModalSel.innerHTML+=`<option value="${vc.name}">${vc.name}</option>`; });
}

function getBankOptions(selected){
 let h='<option value="">Select Bank - Searchable - Nationalised Banks</option>';
 (vendorMasters.banks||[]).forEach(b=>{ h+=`<option value="${b.bank_name}" ${selected===b.bank_name?'selected':''}>${b.bank_name} (${b.bank_code})</option>`; });
 return h;
}
function getDesignationOptions(selected){
 let h='<option value="">Select Designation</option>';
 (vendorMasters.designations||[]).forEach(d=>{ h+=`<option value="${d.name}" ${selected===d.name?'selected':''}>${d.name}</option>`; });
 return h;
}
function getDepartmentOptions(selected){
 let depts=["Purchase","Accounts","Sales","Logistics","Management","Quality","HR","Finance","Operations","Admin","Others"];
 let h='<option value="">Select Department</option>';
 depts.forEach(dp=>{ h+=`<option value="${dp}" ${selected===dp?'selected':''}>${dp}</option>`; });
 return h;
}

// v4.4.10.1 Drag & Drop Document Upload - ONLY Vendor Docs - File Select from Computer
function handleDragOver(e, zoneId){
 e.preventDefault(); e.stopPropagation();
 document.getElementById(zoneId).classList.add('dragover');
}
function handleDragLeave(e, zoneId){
 e.preventDefault(); e.stopPropagation();
 document.getElementById(zoneId).classList.remove('dragover');
}
function handleDrop(e, docType){
 e.preventDefault(); e.stopPropagation();
 document.getElementById('dz_'+docType).classList.remove('dragover');
 let files=e.dataTransfer.files;
 if(files.length>0) processVendorDocFile(files[0], docType);
}
function handleFileSelect(e, docType){
 let file=e.target.files[0];
 if(file) processVendorDocFile(file, docType);
}
function processVendorDocFile(file, docType){
 if(file.size>5*1024*1024) return alert('File too large - Max 5MB - Selected: '+(file.size/1024/1024).toFixed(2)+'MB');
 let reader=new FileReader();
 reader.onload=function(ev){
   let base64=ev.target.result;
   document.getElementById('doc_'+docType).value=base64;
   let fileDiv=document.getElementById('dz_file_'+docType);
   let infoDiv=document.getElementById('doc_'+docType+'_info');
   let clearBtn=document.getElementById('dz_clear_'+docType);
   fileDiv.style.display='block';
   fileDiv.innerHTML=`📎 ${file.name} (${(file.size/1024).toFixed(1)}KB)`;
   if(infoDiv) infoDiv.innerHTML=`✅ File ready: ${file.name} - ${base64.substring(0,30)}...`;
   if(clearBtn) clearBtn.style.display='inline-block';
   // Update drop zone title to show selected
   let zone=document.getElementById('dz_'+docType);
   zone.style.borderColor='#1A2E1E';
   zone.style.background='#F6FFF6';
 };
 reader.readAsDataURL(file);
}
function clearDoc(docType, e){
 if(e){ e.preventDefault(); e.stopPropagation(); }
 document.getElementById('doc_'+docType).value='';
 let fileInput=document.getElementById('file_'+docType);
 if(fileInput) fileInput.value='';
 let fileDiv=document.getElementById('dz_file_'+docType);
 let infoDiv=document.getElementById('doc_'+docType+'_info');
 let clearBtn=document.getElementById('dz_clear_'+docType);
 if(fileDiv){ fileDiv.style.display='none'; fileDiv.innerHTML=''; }
 if(infoDiv) infoDiv.innerHTML='No file selected - will store base64';
 if(clearBtn) clearBtn.style.display='none';
 let zone=document.getElementById('dz_'+docType);
 if(zone){ zone.style.borderColor='var(--brass)'; zone.style.background='#FFFBEB'; }
}
function setDocFromExisting(docType, base64Value){
 // Called during edit - if base64 exists, show preview
 if(!base64Value) return;
 document.getElementById('doc_'+docType).value=base64Value;
 let fileDiv=document.getElementById('dz_file_'+docType);
 let infoDiv=document.getElementById('doc_'+docType+'_info');
 let clearBtn=document.getElementById('dz_clear_'+docType);
 if(fileDiv){
   fileDiv.style.display='block';
   // Try to extract file name from base64 if it's just file name
   if(base64Value.startsWith('data:')){
     fileDiv.innerHTML=`📎 Existing file loaded (${(base64Value.length/1024).toFixed(1)}KB base64)`;
   } else {
     fileDiv.innerHTML=`📎 ${base64Value}`;
   }
 }
 if(infoDiv) infoDiv.innerHTML=`✅ Loaded: ${base64Value.substring(0,40)}...`;
 if(clearBtn) clearBtn.style.display='inline-block';
}


function addVendorBankField(data=null){
 let c=document.getElementById('vendorBanksContainer'); if(c.innerHTML.includes('No bank accounts')) c.innerHTML='';
 let id=`vbank_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 let html=`<div id="${id}" class="product-line" style="border-left-color:#1A2E1E"><div class="row"><div>Select Bank - Searchable dropdown (Single field fixed)<input list="bankList_${id}" class="vb_bank" placeholder="Type to search bank e.g. SBI, HDFC - Choose from list" value="${data?.bank_name||''}"><datalist id="bankList_${id}">${(vendorMasters.banks||[]).map(b=>`<option value="${b.bank_name}">${b.bank_name} (${b.bank_code})</option>`).join('')}</datalist><p style="font-size:9px;color:#888">Single field - Start typing SBI, PNB, HDFC - 34 banks + Other</p></div><div>Branch Name<input class="vb_branch" placeholder="Branch Name" value="${data?.branch_name||''}"></div></div>
 <div class="row"><div>Account Name<input class="vb_acc_name" placeholder="Account Name e.g. M/s Rajasthan Lime" value="${data?.account_name||''}"></div><div>IFSC Code<input class="vb_ifsc" placeholder="IFSC e.g. SBIN0001234" value="${data?.ifsc_code||''}"></div></div>
 <div class="row"><div>Account No<input class="vb_acc_no" placeholder="Account No" value="${data?.account_no||''}"></div><div>Transaction Limit<input type="number" class="vb_limit" placeholder="Limit e.g. 500000" value="${data?.transaction_limit||''}"></div><div style="max-width:80px"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
}
function addVendorContactField(data=null){
 let c=document.getElementById('vendorContactsContainer'); if(c.innerHTML.includes('No contacts')) c.innerHTML='';
 let id=`vcont_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 let isPrimary=data?.is_primary?'checked':'';
 let dept=data?.department||'';
 let html=`<div id="${id}" class="product-line" style="border-left-color:#C9A86A"><div class="row"><div>Name<input class="vc_name" placeholder="Contact Person Name" value="${data?.name||''}"></div><div>Designation<select class="vc_designation">${getDesignationOptions(data?.designation||'')}</select></div><div>Department<select class="vc_department">${getDepartmentOptions(dept)}</select><p style="font-size:9px;color:#888">E. Add departments</p></div><div style="max-width:90px">Primary?<br><input type="checkbox" class="vc_primary" ${isPrimary} style="width:20px;height:20px"><p style="font-size:9px">Primary contact flag</p></div></div>
 <div class="row"><div>Mobile<input type="number" class="vc_mobile" placeholder="Mobile No" value="${data?.mobile_no||''}"></div><div>Whatsapp<input type="number" class="vc_whatsapp" placeholder="Whatsapp No" value="${data?.whatsapp_no||''}"></div></div>
 <div class="row"><div>Land Line<input type="number" class="vc_landline" placeholder="Land Line" value="${data?.landline||''}"></div><div>Ext No<input type="number" class="vc_ext" placeholder="Ext No" value="${data?.ext_no||''}"></div><div>Email<input type="email" class="vc_email" placeholder="Email" value="${data?.email||''}"></div><div style="max-width:80px"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
}

function openAddVendorPopup(){
 document.getElementById('vendorModal').classList.remove('hidden');
 document.getElementById('vend_id').value=''; document.getElementById('vend_name').value=''; document.getElementById('vend_station').value=''; document.getElementById('vend_address').value=''; document.getElementById('vend_state').value=''; document.getElementById('vend_gst').value=''; document.getElementById('vend_pan').value=''; document.getElementById('vend_tan').value=''; document.getElementById('vend_legal_status').value=''; document.getElementById('vend_legal_status_sel').value=''; document.getElementById('vend_category').value=''; document.getElementById('vend_category_sel').value=''; document.getElementById('vend_code_preview').value=''; document.getElementById('vend_status').value='Active';
 document.getElementById('vend_msme_no').value=''; document.getElementById('vend_msme_expiry').value=''; document.getElementById('vend_msme_upload').value=''; document.getElementById('vend_gst_reg_type').value='Regular'; document.getElementById('vend_tds_section').value='194C'; document.getElementById('vend_rating').value='0'; document.getElementById('vend_last_audit').value='';
 // v4.4.10.1 clear doc file inputs + drop zones
 ['gst_cert','pan_card','cancelled_cheque','msme_cert','iso_cert','other'].forEach(dt=>{
   let hid=document.getElementById('doc_'+dt); if(hid) hid.value='';
   let fileIn=document.getElementById('file_'+dt); if(fileIn) fileIn.value='';
   let fileDiv=document.getElementById('dz_file_'+dt); if(fileDiv){ fileDiv.style.display='none'; fileDiv.innerHTML=''; }
   let infoDiv=document.getElementById('doc_'+dt+'_info'); if(infoDiv) infoDiv.innerHTML='No file selected - will store base64';
   let clearBtn=document.getElementById('dz_clear_'+dt); if(clearBtn) clearBtn.style.display='none';
   let zone=document.getElementById('dz_'+dt); if(zone){ zone.style.borderColor=''; zone.style.background=''; zone.classList.remove('dragover'); }
 });
 document.getElementById('vend_opening_bal').value=''; document.getElementById('vend_opening_type').value='Dr'; document.getElementById('vend_ledger_group').value='Sundry Creditors'; document.getElementById('vend_total_business').value=''; document.getElementById('vend_approval_status').value='Draft'; document.getElementById('vend_created_by').value='Admin'; document.getElementById('vend_updated_by').value='Admin'; document.getElementById('vend_last_trans').value='';
 document.getElementById('vendorBanksContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No bank accounts - Click Add Bank Account Button</p>';
 document.getElementById('vendorContactsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No contacts - Click Add Contact Button</p>';
 loadVendorMasters();
}
function closeAddVendorPopup(){document.getElementById('vendorModal').classList.add('hidden');}

async function saveVendor(){
 let name=document.getElementById('vend_name').value.trim(); if(!name) return alert('Vendor Name mandatory');
 let banks=[]; document.querySelectorAll('#vendorBanksContainer > div[id^="vbank_"]').forEach(div=>{
   let bank_name=div.querySelector('.vb_bank').value;
   let branch=div.querySelector('.vb_branch').value; let acc_name=div.querySelector('.vb_acc_name').value; let ifsc=div.querySelector('.vb_ifsc').value; let acc_no=div.querySelector('.vb_acc_no').value; let limit=div.querySelector('.vb_limit').value;
   if(bank_name) banks.push({bank_name, branch_name:branch, account_name:acc_name, ifsc_code:ifsc, account_no:acc_no, transaction_limit:parseFloat(limit)||0});
 });
 let contacts=[]; document.querySelectorAll('#vendorContactsContainer > div[id^="vcont_"]').forEach(div=>{
   let cname=div.querySelector('.vc_name').value; let desg=div.querySelector('.vc_designation').value; let dept=div.querySelector('.vc_department').value; let isPrimary=div.querySelector('.vc_primary').checked; let mob=div.querySelector('.vc_mobile').value; let wapp=div.querySelector('.vc_whatsapp').value; let land=div.querySelector('.vc_landline').value; let ext=div.querySelector('.vc_ext').value; let email=div.querySelector('.vc_email').value;
   if(cname) contacts.push({name:cname, designation:desg, department:dept, is_primary:isPrimary, mobile_no:mob, whatsapp_no:wapp, landline:land, ext_no:ext, email});
 });
 let docs={
   gst_cert:document.getElementById('doc_gst_cert').value,
   pan_card:document.getElementById('doc_pan_card').value,
   cancelled_cheque:document.getElementById('doc_cancelled_cheque').value,
   msme_cert:document.getElementById('doc_msme_cert').value,
   iso_cert:document.getElementById('doc_iso_cert').value,
   other:document.getElementById('doc_other').value
 };
 let payload={
   name:name,
   station:document.getElementById('vend_station').value,
   address:document.getElementById('vend_address').value,
   state:document.getElementById('vend_state').value,
   gst_no:document.getElementById('vend_gst').value,
   pan_no:document.getElementById('vend_pan').value,
   tan_no:document.getElementById('vend_tan').value,
   legal_status:document.getElementById('vend_legal_status').value || document.getElementById('vend_legal_status_sel').value,
   vendor_category:document.getElementById('vend_category').value || document.getElementById('vend_category_sel').value,
   bank_details:banks,
   contacts:contacts,
   status:document.getElementById('vend_status').value,
   msme_cert_no:document.getElementById('vend_msme_no').value,
   msme_expiry:document.getElementById('vend_msme_expiry').value,
   msme_upload:document.getElementById('vend_msme_upload').value,
   gst_reg_type:document.getElementById('vend_gst_reg_type').value,
   tds_section:document.getElementById('vend_tds_section').value,
   vendor_rating:parseInt(document.getElementById('vend_rating').value)||0,
   last_audit_date:document.getElementById('vend_last_audit').value,
   documents:docs,
   opening_balance:parseFloat(document.getElementById('vend_opening_bal').value)||0,
   opening_balance_type:document.getElementById('vend_opening_type').value,
   ledger_group:document.getElementById('vend_ledger_group').value,
   approval_status:document.getElementById('vend_approval_status').value,
   created_by:document.getElementById('vend_created_by').value,
   updated_by:document.getElementById('vend_updated_by').value
 };
 let vid=document.getElementById('vend_id').value;
 let url=vid?`/api/vendors/${vid}`:'/api/vendors'; let method=vid?'PUT':'POST';
 let res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let j=await res.json();
 if(res.ok){alert(`Vendor ${vid?'Updated':'Created'}: ${j.vendor_code||payload.name} - ${banks.length} Banks, ${contacts.length} Contacts - Rating ${payload.vendor_rating}★ - Approval ${payload.approval_status}`); closeAddVendorPopup(); loadVendors();} else alert(j.error||'Error');
}

async function loadVendors(){
 await loadVendorMasters();
 let search=document.getElementById('vendorSearch')?.value||'';
 let legal=document.getElementById('vendorLegalFilter')?.value||'';
 let cat=document.getElementById('vendorCatFilter')?.value||'';
 let state=document.getElementById('vendorStateFilter')?.value||'';
 let status=document.getElementById('vendorStatusFilter')?.value||'';
 let approval=document.getElementById('vendorApprovalFilter')?.value||'';
 let rating=document.getElementById('vendorRatingFilter')?.value||'';
 let params=new URLSearchParams({search, type:legal, category:cat, state, status, approval, rating});
 let r=await fetch(`/api/vendors?${params}`); let vendors=await r.json();
 document.getElementById('vendorCountBadge').innerText=`${vendors.length} Vendors`;
 let tb=document.getElementById('vendorTbl'); tb.innerHTML='';
 let statesSet=new Set();
 vendors.forEach(v=>{ if(v.state) statesSet.add(v.state); });
 let stateSel=document.getElementById('vendorStateFilter'); let curState=stateSel?stateSel.value:'';
 if(stateSel && stateSel.options.length<=1){
   statesSet.forEach(st=>{ stateSel.innerHTML+=`<option value="${st}" ${curState===st?'selected':''}>${st}</option>`; });
 }
 if(vendors.length===0){ tb.innerHTML=`<tr><td colspan="9" style="text-align:center;padding:20px;color:#888">No vendors - Add New Vendor Button above heading - v4.4.10 Compliance</td></tr>`; return; }
 vendors.forEach((v,i)=>{
   let banksHtml=(v.bank_details||[]).length? v.bank_details.map(b=>`<span style="display:block;background:#FFFBEB;padding:3px 6px;border-radius:4px;margin:2px 0;border:1px solid var(--brass);font-size:10px"><b>${b.bank_name}</b> - ${b.account_no} - IFSC ${b.ifsc_code}</span>`).join('') : '<small style="color:#888">No banks</small>';
   let contactsHtml=(v.contacts||[]).length? v.contacts.map(c=>`<span style="display:block;background:white;padding:3px 6px;border-radius:4px;margin:2px 0;border:1px solid var(--line);font-size:10px"><b>${c.name}</b> ${c.is_primary?'⭐Primary':''} (${c.designation}) [${c.department||''}] - M:${c.mobile_no} W:${c.whatsapp_no} <br><small>${c.email||''}</small></span>`).join('') : '<small style="color:#888">No contacts</small>';
   let statusClass=v.status==='Active'?'ok':v.status==='Blocked'?'crit':'warn';
   let approvalClass=v.approval_status==='Approved'?'ok':v.approval_status==='Rejected'?'crit':v.approval_status==='Pending'?'warn':'brass';
   let ratingStars='★'.repeat(v.vendor_rating||0)+'☆'.repeat(5-(v.vendor_rating||0));
   let docsCount=v.documents?Object.values(v.documents).filter(x=>x).length:0;
   let docsBadge=docsCount>0?`<span class="badge ok">${docsCount} Docs</span>`:'<small style="color:#888">No docs</small>';
   tb.innerHTML+=`<tr><td>${i+1}</td><td><span style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line);font-weight:800">${v.vendor_code}</span><br><div class="tooltip"><b>${v.name}</b><span class="tip">Code: ${v.vendor_code}<br>Station: ${v.station}<br>State: ${v.state}<br>GST: ${v.gst_no} (${v.gst_reg_type})<br>PAN: ${v.pan_no}<br>TAN: ${v.tan_no}<br>Legal: ${v.legal_status}<br>Cat: ${v.vendor_category}<br>MSME: ${v.msme_cert_no} Exp: ${v.msme_expiry}<br>TDS: ${v.tds_section}<br>Rating: ${v.vendor_rating}★ Audit: ${v.last_audit_date}<br>Opening: ${v.opening_balance} ${v.opening_balance_type} Ledger: ${v.ledger_group}<br>Approval: ${v.approval_status}<br>Created: ${v.created_by} ${v.created_at}<br>Updated: ${v.updated_by} ${v.updated_at}<br>Last Trans: ${v.last_transaction_date}<br>Business Value: Rs ${v.total_business_value}<br>Address: ${v.address}</span></div><br><small style="color:#888">${v.station||''}</small></td>
   <td><b>${v.station||''}</b><br><small>${v.state||''}</small><br><span class="badge brass" style="font-size:9px">${v.gst_reg_type||''}</span></td>
   <td><small>MSME: ${v.msme_cert_no||''}<br>Exp: ${v.msme_expiry||''}</small><br><span style="color:#C9A86A;font-weight:800">${ratingStars}</span> ${v.vendor_rating?`(${v.vendor_rating})`:''}<br><small>Audit: ${v.last_audit_date||''}</small></td>
   <td><small>Opening: ${v.opening_balance||0} ${v.opening_balance_type}<br>Ledger: ${v.ledger_group||''}<br>TDS: ${v.tds_section||''}</small></td>
   <td><small>Banks: ${v.bank_details.length} | Contacts: ${v.contacts.length}</small><div style="max-height:80px;overflow-y:auto;margin-top:4px">${banksHtml}<hr style="margin:4px 0">${contactsHtml}</div></td>
   <td><span class="badge ok">POs: ${v.po_count}</span><br><span class="badge" style="background:#F6FFF6;color:#1A2E1E;border:1px solid #C5E1C5;margin-top:4px;display:inline-block">GRNs: ${v.grn_count}</span><br><small>Value: Rs ${(v.total_business_value||0).toFixed(0)}</small><br><small style="font-size:9px">Last: ${v.last_transaction_date||''}</small></td>
   <td>${docsBadge}<br><span class="badge ${approvalClass}">${v.approval_status}</span><br><span class="badge ${statusClass}">${v.status}</span><br><small style="font-size:9px">${v.created_by} ${v.created_at?.slice(0,10)||''}</small></td>
   <td><button class="btn btn-b" onclick="editVendor(${v.id})">Edit</button> <button class="btn btn-r" onclick="delVendor(${v.id})">Del</button></td></tr>`;
 });
}

function resetVendorFilters(){
 document.getElementById('vendorSearch').value=''; document.getElementById('vendorLegalFilter').value=''; document.getElementById('vendorCatFilter').value=''; document.getElementById('vendorStateFilter').value=''; document.getElementById('vendorStatusFilter').value=''; let af=document.getElementById('vendorApprovalFilter'); if(af) af.value=''; let rf=document.getElementById('vendorRatingFilter'); if(rf) rf.value=''; loadVendors();
}

async function editVendor(id){
 let r=await fetch(`/api/vendors/${id}`); let v=await r.json();
 openAddVendorPopup();
 setTimeout(()=>{
   document.getElementById('vend_id').value=v.id;
   document.getElementById('vend_name').value=v.name;
   document.getElementById('vend_station').value=v.station||'';
   document.getElementById('vend_address').value=v.address||'';
   document.getElementById('vend_state').value=v.state||'';
   document.getElementById('vend_gst').value=v.gst_no||'';
   document.getElementById('vend_pan').value=v.pan_no||'';
   document.getElementById('vend_tan').value=v.tan_no||'';
   document.getElementById('vend_legal_status').value=v.legal_status||'';
   document.getElementById('vend_legal_status_sel').value=v.legal_status||'';
   document.getElementById('vend_category').value=v.vendor_category||'';
   document.getElementById('vend_category_sel').value=v.vendor_category||'';
   document.getElementById('vend_code_preview').value=v.vendor_code;
   document.getElementById('vend_status').value=v.status||'Active';
   document.getElementById('vend_msme_no').value=v.msme_cert_no||'';
   document.getElementById('vend_msme_expiry').value=v.msme_expiry||'';
   document.getElementById('vend_msme_upload').value=v.msme_upload||'';
   document.getElementById('vend_gst_reg_type').value=v.gst_reg_type||'Regular';
   document.getElementById('vend_tds_section').value=v.tds_section||'194C';
   document.getElementById('vend_rating').value=v.vendor_rating||0;
   document.getElementById('vend_last_audit').value=v.last_audit_date||'';
   // v4.4.10.1 - Set docs with drag-drop preview
   setDocFromExisting('gst_cert', v.documents?.gst_cert||'');
   setDocFromExisting('pan_card', v.documents?.pan_card||'');
   setDocFromExisting('cancelled_cheque', v.documents?.cancelled_cheque||'');
   setDocFromExisting('msme_cert', v.documents?.msme_cert||'');
   setDocFromExisting('iso_cert', v.documents?.iso_cert||'');
   setDocFromExisting('other', v.documents?.other||'');
   // Also keep hidden inputs for backward compat
   document.getElementById('doc_gst_cert').value=v.documents?.gst_cert||'';
   document.getElementById('doc_pan_card').value=v.documents?.pan_card||'';
   document.getElementById('doc_cancelled_cheque').value=v.documents?.cancelled_cheque||'';
   document.getElementById('doc_msme_cert').value=v.documents?.msme_cert||'';
   document.getElementById('doc_iso_cert').value=v.documents?.iso_cert||'';
   document.getElementById('doc_other').value=v.documents?.other||'';
   document.getElementById('vend_opening_bal').value=v.opening_balance||0;
   document.getElementById('vend_opening_type').value=v.opening_balance_type||'Dr';
   document.getElementById('vend_ledger_group').value=v.ledger_group||'Sundry Creditors';
   document.getElementById('vend_total_business').value=v.total_business_value||0;
   document.getElementById('vend_approval_status').value=v.approval_status||'Draft';
   document.getElementById('vend_created_by').value=v.created_by||'Admin';
   document.getElementById('vend_updated_by').value=v.updated_by||'Admin';
   document.getElementById('vend_last_trans').value=v.last_transaction_date||'';
   document.getElementById('vendorBanksContainer').innerHTML='';
   document.getElementById('vendorContactsContainer').innerHTML='';
   (v.bank_details||[]).forEach(b=> addVendorBankField(b));
   (v.contacts||[]).forEach(c=> addVendorContactField(c));
   if(!v.bank_details?.length) document.getElementById('vendorBanksContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No bank accounts - Click Add Bank Account Button</p>';
   if(!v.contacts?.length) document.getElementById('vendorContactsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No contacts - Click Add Contact Button</p>';
 }, 600);
}

async function delVendor(id){ if(!confirm('Delete Vendor?')) return; await fetch(`/api/vendors/${id}`,{method:'DELETE'}); loadVendors();}

async function loadDash(){ let r=await fetch('/api/inventory/combined'); let d=await r.json(); document.getElementById('totalVal').innerText='Rs '+(d.total_value_lakh||0).toFixed(2)+' Lakh'; let rc=await fetch('/api/product_categories'); let cats=await rc.json(); document.getElementById('catCountDash').innerText=cats.length; let rp=await fetch('/api/products'); let prods=await rp.json(); document.getElementById('prodCountDash').innerText=prods.length; let rs=await fetch('/api/sbus'); let sbus=await rs.json(); document.getElementById('sbuCountDash').innerText=sbus.length;}
async function loadStock(){ let r=await fetch('/api/inventory/combined'); let d=await r.json(); document.getElementById('rawTbl').innerHTML='<h4>Raw</h4><table><tr><th>Code</th><th>Name</th><th>MT</th></tr>'+d.raw.map(x=>`<tr><td>${x.product_code}</td><td>${x.name}</td><td>${x.total_mt}</td></tr>`).join('')+'</table>'; document.getElementById('finTbl').innerHTML='<h4>Finished</h4><table><tr><th>Code</th><th>Name</th><th>MT</th></tr>'+d.finished.map(x=>`<tr><td>${x.product_code}</td><td>${x.name}</td><td>${x.total_mt}</td></tr>`).join('')+'</table>';}
loadDash(); loadAllProductsForSBU(); loadProdCatOptions(); loadVendorMasters();
</script>
</body></html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
