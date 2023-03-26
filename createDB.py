from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
db = SQLAlchemy(app)
app.app_context().push()



class Payment(db.Model):
    #crypto payment model
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    address = db.Column(db.String(100))
    key = db.Column(db.String(100))
    txid = db.Column(db.String(100))
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, amount, currency, address, key, txid, status):
        self.amount = amount
        self.currency = currency
        self.address = address
        self.key = key
        self.txid = txid
        self.status = status
        
        
db.create_all()
