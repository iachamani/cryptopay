import requests
from flask import Flask,jsonify, render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from bit import PrivateKey
import os
import qrcode

WALLET = os.environ.get('WALLET')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dfewfew123213rwd8gert34tgfd1234trgf'
db = SQLAlchemy(app)
app.app_context().push()

@app.route('/payment', methods=['POST'])
def create_payment():
    from forms import PaymentForm
    form = PaymentForm()
    if form.validate_on_submit():
        amount = convert(form.amount.data,form.currency.data)
        if form.currency.data == 'BTC':
            address, key = generate_new_btc_address()
            generate_qr_code(address)
        elif form.currency.data == 'LTC':
            pass
        # Save the payment information in the database
        from models import Payment
        db.session.add(Payment(amount,form.currency.data, address,key,None, 'pending'))
        db.session.commit()
        pay = Payment.query.filter_by(address=address).first()
        return redirect(url_for('payment',payment_id=pay.id))


# display the payment information on the frontend
@app.route('/payment/<payment_id>')
def payment(payment_id):
    # Get the payment information from the database
    # You can use any database of your choice
    # Here we are using a simple dictionary as a placeholder
    from models import Payment
    payment = Payment.query.filter_by(id=payment_id).first()
    return render_template('payment.html', payment=payment)
# check the status of the payment
@app.route('/status/<payment_id>',methods=['POST'])
def status(payment_id):
    response = requests.post(f'http://127.0.0.1:8000/verify/{payment_id}')
    if response.status_code == 200:
        return jsonify({'message': 'Payment successful'}), 200
    return jsonify({'message': 'Payment failed'}), 400


@app.route('/verify/<payment_id>', methods=['POST'])
def handle_webhook(payment_id):
    from models import Payment
    details = Payment.query.filter_by(id=payment_id).first()
    # Verify the transaction
    try:
        if Isconfirmed(details.address) and verify_btc_transaction(details.address, details.amount):
            #Update the payment status to 'completed' in the database
            api_url = f'https://blockstream.info/api/address/{details.address}/txs'
            response = requests.get(api_url)
            tx_details = response.json()[0]
            details.txid = tx_details['txid']
            details.status = 'completed'
            db.session.commit()
            forward_btc_funds(details.key,WALLET,details.amount)
            return jsonify({'message': 'Transaction successful'}), 200
    except:
        return jsonify({'message': 'Transaction failed'}), 400
    return jsonify({'message': 'Transaction failed'}), 400

def generate_new_btc_address():
    # Generate a new Bitcoin testnet address
    key = PrivateKey()
    address = key.address
    return address, key.to_wif()

def verify_btc_transaction(address, amount):
    # Verify the transaction
    api_url = f'https://blockstream.info/api/address/{address}/txs'
    response = requests.get(api_url)
    tx_details = response.json()[0]
    tx_hash = tx_details['txid']
    api_url = f'https://blockstream.info/testnet/api/tx/{tx_hash}'
    response = requests.get(api_url)
    tx_details = response.json()
    for output in tx_details['vout']:
        if output['value'] == int(amount*100000000):
            return True
    return False
    



def forward_btc_funds(private_key,wallet, amount):
    key = PrivateKey(private_key)
    #send the funds to your wallet and return the transaction hash
    #estimate the fee
    fee = key.get_fee()
    amount = amount - fee
    txid = key.send([(wallet, amount)])
    return txid

   


def Isconfirmed(address):
    api_url = f'https://blockstream.info/api/address/{address}/txs'
    response = requests.get(api_url)
    try:
        tx_details = response.json()[0]
    except:
        return False
        
    tx_hash = tx_details['txid']
    api_url = f'https://blockstream.info/api/tx/{tx_hash}'
    response = requests.get(api_url)
    tx_details = response.json()  
    confirmed_count = 0
    while confirmed_count < 2:
        response = requests.get(api_url)
        tx_details = response.json()
        if tx_details['status']['confirmed']:
            confirmed_count += 1
    
    return True
    
   


def convert(amount,currency):
    api_url = 'https://api.coinbase.com/v2/exchange-rates?currency=USD'
    response = requests.get(api_url)
    data = response.json()
    coin = f'{currency}'
    ltc_rate = data['data']['rates'][coin]
    return amount*float(ltc_rate)

def generate_qr_code(address):
    qrcode.make(address).save(f'static/QRs/{address}.png')



@app.route('/checkout')
def checkout():
    from forms import PaymentForm
    form = PaymentForm()
    return render_template('checkout.html', form=form)


