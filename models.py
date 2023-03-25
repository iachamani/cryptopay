from app import db
import datetime

class Payment(db.Model):
    #crypto payment model
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(100))
    address = db.Column(db.String(100))
    txid = db.Column(db.String(100))
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, amount, currency, address, txid, status):
        self.amount = amount
        self.currency = currency
        self.address = address
        self.txid = txid
        self.status = status
    

