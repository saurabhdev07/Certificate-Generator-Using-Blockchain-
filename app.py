import hashlib
import datetime
from flask import Flask, render_template, session, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certificates.db'
db = SQLAlchemy(app)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(80), nullable=False)
    issuer_name = db.Column(db.String(80), nullable=False)
    accomplishment = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, recipient_name, issuer_name, accomplishment, date):
        self.recipient_name = recipient_name
        self.issuer_name = issuer_name
        self.accomplishment = accomplishment
        self.date = date
        self.hash = self.generate_hash()
        print(f"Certificate generated with hash: {self.hash}\n")

    def generate_hash(self):
        sha = hashlib.sha256()
        sha.update(self.recipient_name.encode('utf-8'))
        sha.update(self.issuer_name.encode('utf-8'))
        sha.update(self.accomplishment.encode('utf-8'))
        sha.update(str(self.date).encode('utf-8'))
        return sha.hexdigest()

class Block:
    def __init__(self, timestamp, data, previous_hash=''):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.generate_hash()

    def generate_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.timestamp).encode('utf-8'))
        sha.update(str(self.data).encode('utf-8'))
        sha.update(str(self.previous_hash).encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(datetime.datetime.now(), "Genesis Block", "0")

    def add_block(self, new_block):
        new_block.previous_hash = self.chain[-1].hash
        new_block.hash = new_block.generate_hash()
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.generate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

blockchain = Blockchain()

@app.before_request
def create_tables():
    db.create_all()

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        recipient_name = request.form['t1']
        issuer_name = request.form['issuer']
        accomplishment = request.form['a1']
        date = request.form['d1']

        certificate = Certificate(recipient_name, issuer_name, accomplishment, date)
        blockchain.add_block(Block(datetime.datetime.now(), certificate))

        db.session.add(certificate)
        db.session.commit()

        print(recipient_name)
        print(issuer_name)
        print(accomplishment)
        print(date)
        print(certificate.hash) 
        return render_template('index.html',certificate=certificate)

    return render_template('index3.html')
    
@app.route("/validate.",methods=['POST','GET'])
def validate():
    if request.method == 'POST':
        certificate_hash = request.form['hash']
        certificate_value = validate_certificate(certificate_hash,blockchain)
      
    return render_template('index3.html',certificate_value = certificate_value)

def validate_certificate(certificate_hash, blockchain):
        certificate_exists=False
        certificate_exists = bool(Certificate.query.filter_by(hash=certificate_hash).first())
        if certificate_exists:
            print("Certificate found in the database.")
            return True
        else:
            print("Certificate not found in the database.")
            return False

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
 
