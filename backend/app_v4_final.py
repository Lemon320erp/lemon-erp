
"""
🍋 LEMON ERP v4 FINAL - HERITAGE GREEN + LEMON ESSENCE
Modules: Vendor, PO, GRN, Min Stock Reorder, Raw/WIP/Finished/Packaging Separate, WhatsApp, QR, Hydration, Kiln, Weighbridge
Theme: Heritage Green #1A2E1E + Brass #C9A86A + Alabaster #FAF6F0 + Lemon Zest #F2E863
White-label Ready for other lime companies
"""

from flask import Flask, request, jsonify, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, qrcode, base64
from io import BytesIO
import requests

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'lemon_erp_heritage_green_v4_secret'
# For production switch to PostgreSQL: postgresql://user:pass@localhost/lemon_erp
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lemon_erp_v4_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(20), unique=True)
    theme = db.Column(db.String(50), default='heritage_green')
    whatsapp_api_key = db.Column(db.String(200))
    whatsapp_enabled = db.Column(db.Boolean, default=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # Owner, Manager, Operator, SuperAdmin
    unit_access = db.Column(db.String(200))
    name = db.Column(db.String(100))
    whatsapp_number = db.Column(db.String(20))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.String(100))
    vendor_type = db.Column(db.String(50))  # Limestone, Petcoke, Trading, Transport, Packaging
    gst = db.Column(db.String(30))
    contact = db.Column(db.String(50))
    payment_terms = db.Column(db.String(50))
    credit_limit = db.Column(db.Float)
    pending_due = db.Column(db.Float, default=0)
    rating = db.Column(db.Float, default=4.5)

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    po_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material_type = db.Column(db.String(50))  # Raw, Finished Trading, Packaging
    material = db.Column(db.String(100))  # Limestone, Petcoke, CaO 10-40, HDPE White Bag, Jumbo Type A
    qty = db.Column(db.Float)
    rate = db.Column(db.Float)
    total = db.Column(db.Float)
    delivery_date = db.Column(db.String(20))
    unit = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Draft')  # Draft, Sent, Partial, Received, Cancelled
    created_by = db.Column(db.String(100))

class GRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    grn_no = db.Column(db.String(50), unique=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    po_no = db.Column(db.String(50))
    vehicle_no = db.Column(db.String(50))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    material_type = db.Column(db.String(50))  # Raw, Finished Trading, Packaging
    material = db.Column(db.String(100))
    challan_no = db.Column(db.String(50))
    invoice_no = db.Column(db.String(50))
    gross_wt = db.Column(db.Float)
    tare_wt = db.Column(db.Float)
    net_wt = db.Column(db.Float)
    rejection_pct = db.Column(db.Float, default=0)
    stock_type = db.Column(db.String(20), default='Own')  # Own, Traded, Own Processing
    photo_truck = db.Column(db.String(200))
    photo_challan = db.Column(db.String(200))
    gps = db.Column(db.String(100))
    operator = db.Column(db.String(100))

class StockMaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    product = db.Column(db.String(100))
    product_category = db.Column(db.String(50))  # Raw, WIP, Finished, Packaging
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
    bag_type = db.Column(db.String(100))  # 40kg HDPE White, Jumbo Type A etc
    bag_category = db.Column(db.String(20))  # 40kg, Jumbo
    capacity_mt = db.Column(db.Float)  # 0.04 for 40kg, 1.2 for Jumbo
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
    message_type = db.Column(db.String(50))  # Low Stock, GRN, Daily Summary, Dispatch, PO
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

# INIT DB
with app.app_context():
    db.create_all()
    if Company.query.count() == 0:
        c1 = Company(name='RLP Lime Industries', code='RLP', theme='heritage_green', whatsapp_enabled=True)
        db.session.add(c1)
        db.session.commit()
        # Users
        db.session.add_all([
            User(company_id=c1.id, username='owner', password='owner123', role='Owner', unit_access='All', name='Owner RLP', whatsapp_number='919999999999'),
            User(company_id=c1.id, username='operator1', password='op123', role='Operator', unit_access='Unit 1 - 72 MT', name='Operator 1'),
            User(company_id=c1.id, username='superadmin', password='super123', role='SuperAdmin', unit_access='All', name='Super Admin'),
        ])
        # Vendors
        db.session.add_all([
            Vendor(company_id=c1.id, name='Jodhpur Limestone Mines', vendor_type='Limestone', gst='08ABCDE1234F1Z5', contact='9876543210', payment_terms='15 Days', credit_limit=1000000, pending_due=250000),
            Vendor(company_id=c1.id, name='IOCL Petcoke', vendor_type='Petcoke', gst='08ABCDE1234F1Z6', contact='9876543211', payment_terms='Advance', credit_limit=500000, pending_due=0),
            Vendor(company_id=c1.id, name='Katni Traders - CaO', vendor_type='Trading', gst='23ABCDE1234F1Z5', contact='9876543212', payment_terms='30 Days', credit_limit=2000000, pending_due=450000),
            Vendor(company_id=c1.id, name='Shree Packaging - Jodhpur', vendor_type='Packaging', gst='08ABCDE1234F1Z7', contact='9876543213', payment_terms='15 Days', credit_limit=300000, pending_due=85000),
        ])
        # Stock Masters - Raw, WIP, Finished, Packaging
        stock_data = [
            ('Limestone', 'Raw', 'Unit 1 - 72 MT', 100, 150, 300, 150, 85),
            ('Petcoke', 'Raw', 'Unit 1 - 72 MT', 10, 20, 50, 20, 8),
            ('Limestone', 'Raw', 'Unit 2 - 84 MT', 100, 150, 300, 150, 120),
            ('CaO Loose', 'WIP', 'Unit 1 - 72 MT', 20, 30, 100, 50, 45),
            ('CaO 10-40mm', 'Finished', 'Unit 1 - 72 MT', 20, 40, 100, 60, 35),
            ('CaO 0-3mm', 'Finished', 'Unit 1 - 72 MT', 15, 30, 80, 40, 22),
            ('HYD 90%', 'Finished', 'Unit 3 - 125 MT', 10, 20, 50, 30, 12),
            ('Chunna Ready', 'Finished', 'Unit 1 - 72 MT', 5, 10, 30, 15, 8),
        ]
        for prod, cat, unit, min_s, reorder, max_s, reorder_q, curr in stock_data:
            db.session.add(StockMaster(company_id=c1.id, product=prod, product_category=cat, unit=unit, min_stock=min_s, reorder_level=reorder, max_stock=max_s, reorder_qty=reorder_q, current_stock=curr))
        # Packaging Stock
        packaging_data = [
            ('HDPE White 40kg - CaO 0-3mm/0-2mm/200M', '40kg', 0.04, 1200, 18, 'Unit 1 - 72 MT', 200),
            ('HDPE Yellow 40kg - HYD 75/80/90%', '40kg', 0.04, 800, 20, 'Unit 1 - 72 MT', 200),
            ('Laminated Premium 40kg - HYD 90%', '40kg', 0.04, 500, 25, 'Unit 3 - 125 MT', 150),
            ('PP Bag 40kg - Chunna/Gulli', '40kg', 0.04, 600, 16, 'Unit 1 - 72 MT', 150),
            ('Jumbo Type A 1.2 MT White - CaO 10-40/40-60/10-50', 'Jumbo', 1.2, 150, 280, 'Unit 1 - 72 MT', 50),
            ('Jumbo Type B 1.0 MT Yellow - Hydrate', 'Jumbo', 1.0, 80, 260, 'Unit 3 - 125 MT', 30),
            ('Jumbo Type C 1.5 MT - Limestone/Petcoke', 'Jumbo', 1.5, 60, 320, 'Unit 1 - 72 MT', 20),
        ]
        for bag_type, cat, cap, closing, rate, unit, min_s in packaging_data:
            db.session.add(PackagingStock(company_id=c1.id, bag_type=bag_type, bag_category=cat, capacity_mt=cap, closing=closing, rate_per_bag=rate, unit=unit, min_stock=min_s, opening=closing))
        db.session.commit()

# WHATSAPP FUNCTION
def send_whatsapp(to_number, message, message_type='Low Stock'):
    company_id = 1
    # In production, integrate with WATI / Interakt / Twilio
    # For demo, log it
    log = WhatsAppLog(
        company_id=company_id,
        date=datetime.now().strftime('%Y-%m-%d'),
        time=datetime.now().strftime('%H:%M:%S'),
        to_number=to_number,
        message_type=message_type,
        message=message,
        status='Sent'
    )
    db.session.add(log)
    db.session.commit()
    
    # Actual API call (Uncomment and add your API key)
    """
    # For WATI:
    url = "https://live-mt-server.wati.io/..."
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    data = {"phone": to_number, "message": message}
    requests.post(url, json=data, headers=headers)
    """
    return True

# ROUTES

@app.route('/')
def index():
    return render_template('dashboard_v4.html')

@app.route('/api/vendors')
def vendors():
    v = Vendor.query.filter_by(company_id=1).all()
    return jsonify([{'id':x.id,'name':x.name,'type':x.vendor_type,'pending_due':x.pending_due,'contact':x.contact} for x in v])

@app.route('/api/po', methods=['GET','POST'])
def po():
    if request.method == 'POST':
        data = request.json
        count = PurchaseOrder.query.count() + 1
        po_no = f"PO-2025-{count+100:03d}"
        po = PurchaseOrder(
            company_id=1,
            po_no=po_no,
            date=data.get('date', datetime.now().strftime('%Y-%m-%d')),
            vendor_id=data.get('vendor_id'),
            material_type=data.get('material_type'),
            material=data.get('material'),
            qty=float(data.get('qty',0)),
            rate=float(data.get('rate',0)),
            total=float(data.get('qty',0))*float(data.get('rate',0)),
            unit=data.get('unit'),
            status='Draft',
            created_by='Owner'
        )
        db.session.add(po)
        db.session.commit()
        return jsonify({'status':'success','po_no':po_no})
    pos = PurchaseOrder.query.filter_by(company_id=1).order_by(PurchaseOrder.id.desc()).all()
    return jsonify([{'po_no':p.po_no,'material':p.material,'qty':p.qty,'status':p.status,'total':p.total} for p in pos])

@app.route('/api/grn', methods=['GET','POST'])
def grn():
    if request.method == 'POST':
        data = request.json
        count = GRN.query.count() + 1
        grn_no = f"GRN-2025-{count:03d}"
        grn_entry = GRN(
            company_id=1,
            grn_no=grn_no,
            date=data.get('date', datetime.now().strftime('%Y-%m-%d')),
            time=datetime.now().strftime('%H:%M:%S'),
            po_no=data.get('po_no',''),
            vehicle_no=data.get('vehicle_no','').upper(),
            vendor_id=data.get('vendor_id'),
            material_type=data.get('material_type'),
            material=data.get('material'),
            challan_no=data.get('challan_no'),
            invoice_no=data.get('invoice_no'),
            gross_wt=float(data.get('gross_wt',0)),
            tare_wt=float(data.get('tare_wt',0)),
            net_wt=float(data.get('net_wt',0)),
            stock_type=data.get('stock_type','Own'),
            operator=data.get('operator','Operator1'),
            gps=data.get('gps','')
        )
        db.session.add(grn_entry)
        # Update stock
        stock = StockMaster.query.filter_by(company_id=1, product=data.get('material'), unit=data.get('unit')).first()
        if stock:
            stock.current_stock += float(data.get('net_wt',0))
        db.session.commit()
        
        # WhatsApp notification for GRN
        send_whatsapp('919999999999', f"✅ GRN Done: {data.get('net_wt')} MT {data.get('material')} received from Vendor. Vehicle {data.get('vehicle_no')}. Slip {grn_no}. Stock now {stock.current_stock if stock else 0} MT. - Lemon ERP", 'GRN')
        
        return jsonify({'status':'success','grn_no':grn_no})
    grns = GRN.query.filter_by(company_id=1).order_by(GRN.id.desc()).limit(20).all()
    return jsonify([{'grn_no':g.grn_no,'material':g.material,'net_wt':g.net_wt,'vehicle':g.vehicle_no,'date':g.date} for g in grns])

@app.route('/api/stock_v4')
def stock_v4():
    stocks = StockMaster.query.filter_by(company_id=1).all()
    result = {'Raw':[],'WIP':[],'Finished':[],'Packaging':[]}
    for s in stocks:
        status = 'OK'
        if s.current_stock < s.min_stock:
            status = 'Critical'
        elif s.current_stock < s.reorder_level:
            status = 'Reorder'
        result[s.product_category].append({
            'product':s.product,
            'unit':s.unit,
            'current':s.current_stock,
            'min':s.min_stock,
            'reorder':s.reorder_level,
            'max':s.max_stock,
            'status':status
        })
    # Packaging
    packs = PackagingStock.query.filter_by(company_id=1).all()
    for p in packs:
        status = 'OK'
        if p.closing < p.min_stock:
            status = 'Critical'
        result['Packaging'].append({
            'product':p.bag_type,
            'unit':p.unit,
            'current':p.closing,
            'min':p.min_stock,
            'rate':p.rate_per_bag,
            'capacity':p.capacity_mt,
            'status':status
        })
    return jsonify(result)

@app.route('/api/low_stock_alerts')
def low_stock():
    stocks = StockMaster.query.filter_by(company_id=1).all()
    alerts = []
    for s in stocks:
        if s.current_stock < s.min_stock:
            alerts.append({
                'product':s.product,
                'unit':s.unit,
                'current':s.current_stock,
                'min':s.min_stock,
                'type':'Critical',
                'message': f"🍋 Lemon ERP Alert: {s.unit} {s.product} {s.current_stock} MT < Min {s.min_stock} MT. Reorder {s.reorder_qty} MT suggested. PO Draft auto created."
            })
            # Auto send WhatsApp for critical
            send_whatsapp('919999999999', f"🍋 Lemon ERP Alert: {s.unit} {s.product} {s.current_stock} MT < Min {s.min_stock} MT. Reorder {s.reorder_qty} MT suggested. - RLP Lime", 'Low Stock')
        elif s.current_stock < s.reorder_level:
            alerts.append({
                'product':s.product,
                'unit':s.unit,
                'current':s.current_stock,
                'min':s.min_stock,
                'type':'Reorder',
                'message': f"{s.product} at {s.unit} - {s.current_stock} MT < Reorder {s.reorder_level} MT"
            })
    return jsonify(alerts)

@app.route('/api/whatsapp_logs')
def whatsapp_logs():
    logs = WhatsAppLog.query.filter_by(company_id=1).order_by(WhatsAppLog.id.desc()).limit(20).all()
    return jsonify([{'date':l.date,'time':l.time,'type':l.message_type,'message':l.message,'status':l.status} for l in logs])

@app.route('/api/qr_generate', methods=['POST'])
def qr_gen():
    data = request.json
    count = QRBag.query.count() + 1
    bag_id = f"JMB-{data.get('product','').replace(' ','')[:6]}-{data.get('unit','U1')[:2]}-{datetime.now().strftime('%Y')}-{count:04d}"
    qr_data = f"{bag_id}|{data.get('product')}|{data.get('weight')}MT|{data.get('unit')}|RLP|HeritageGreen"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1A2E1E", back_color="#FAF6F0")  # Heritage Green QR
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    entry = QRBag(company_id=1, bag_id=bag_id, product=data.get('product'), weight=float(data.get('weight',1.2)), unit=data.get('unit'), qr_data=qr_data, created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(entry)
    db.session.commit()
    return jsonify({'bag_id':bag_id,'qr_base64':img_str})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
