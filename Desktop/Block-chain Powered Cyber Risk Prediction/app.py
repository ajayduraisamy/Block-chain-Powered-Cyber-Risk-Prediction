# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Policy
from eth_account import Account
import joblib
import numpy as np
import pandas as pd
from web3 import Web3
import json
import os
from collections import Counter

# -----------------------
# Initialize Flask App
# -----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
dats = "Medium"
# -----------------------
# Initialize Extensions
# -----------------------
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    if user:
        print(f"Loaded user: {user.username}, Role: {user.role}")
    return user



# -----------------------------
# Web3 & Contract Setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
if not w3.is_connected():
    raise Exception("Cannot connect to Ganache. Make sure Ganache is running!")

# Backend account (to pay gas)
backend_private_key = "0xb70168b6e74d4b332733b10a895ab7d14a0b735c3fef4cd55172de6864d07df3"
backend_account = Account.from_key(backend_private_key)

# Check balance
balance = w3.eth.get_balance(backend_account.address)
print("Backend balance:", w3.from_wei(balance, 'ether'), "ETH")
backend_account = w3.eth.account.from_key(backend_private_key)

# Load contract ABI and bytecode
with open(os.path.join(BASE_DIR, 'build', 'compiled_contract.json'), 'r') as f:
    compiled_contract = json.load(f)
    # Adjust path to your ABI in JSON
    if 'abi' in compiled_contract:
        contract_abi = compiled_contract['abi']
        contract_bytecode = compiled_contract.get('bytecode', None)
    else:
        # Hardhat/Truffle format
        contract_abi = compiled_contract['contracts']['MyContract.sol']['MyContract']['abi']
        contract_bytecode = compiled_contract['contracts']['MyContract.sol']['MyContract']['evm']['bytecode']['object']

# Set your deployed contract address here

contract_address = '0xD1c2eA2810F2623BE4702BfA764b1FcacC3Eb52E'  # Replace with actual deployed contract address


# If contract address is empty, deploy
if contract_address == '' or contract_address.lower() == '0xyourdeployedcontractaddressonganache':
    Contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    tx_hash = Contract.constructor().transact({'from': backend_account.address})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = receipt.contractAddress
    print("Contract deployed at:", contract_address)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# -----------------------
# Routes
# -----------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login or use a different email.', 'warning')
            return redirect(url_for('register'))

        # Generate Ethereum wallet for the user (private key never stored)
        acct = Account.create()
        wallet_address = acct.address
        balance = w3.eth.get_balance(backend_account.address)
        print("Backend balance:", Web3.from_wei(balance, 'ether'), "ETH")

        # Hash password only
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Save user in DB
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            wallet_address=wallet_address,
            kyc_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Call smart contract from backend account
        nonce = w3.eth.get_transaction_count(backend_account.address)
        tx = contract.functions.registerUser(wallet_address, username).build_transaction({
        'from': backend_account.address,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': Web3.to_wei('20', 'gwei'),
        'value': 0 })


        signed_tx = w3.eth.account.sign_transaction(tx, backend_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        

        print(f"Registration transaction sent: {tx_hash.hex()}")

        flash('Registration successful! Wallet created and registered on blockchain.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))  # Admin route
            else:
                return redirect(url_for('predict_risk'))  # Customer route

        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# -----------------------
# Load ML models
# -----------------------
scaler = joblib.load("ml_models/scaler.pkl")
trained_columns = joblib.load("ml_models/trained_columns.pkl")
rf_model = joblib.load("ml_models/random_forest_model.pkl")
risk_map = {0: "Low", 1: "Medium", 2: "High"}

def preprocess_input(input_data):
    df = pd.DataFrame([input_data])
    for col in ['Income', 'Coverage Amount', 'Premium Amount', 'Deductible']:
        if col in df.columns:
            df[col] = np.log1p(df[col])
    if 'Income' in df.columns and 'Premium Amount' in df.columns:
        df['Income_to_Premium'] = df['Income'] / (df['Premium Amount'] + 1)
    if 'Coverage Amount' in df.columns and 'Income' in df.columns:
        df['Coverage_to_Income'] = df['Coverage Amount'] / (df['Income'] + 1)
    df = pd.get_dummies(df)
    missing_cols = [col for col in trained_columns if col not in df.columns]
    if missing_cols:
        df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing_cols)], axis=1)
    df = df[trained_columns]
    return scaler.transform(df)


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict_risk():
    result = None

    # Check KYC status first
    if not current_user.kyc_verified:
        result = {"error": "Your KYC is not verified yet. Please wait for verification to make predictions."}
        return render_template("predict.html", result=result)

    if request.method == 'POST':
        try:
            # Collect input data from form
            income = float(request.form.get("income", 0))
            coverage = float(request.form.get("coverage", 0))
            premium = float(request.form.get("premium", 0))
            deductible = float(request.form.get("deductible", 0))
            occupation = request.form.get("occupation", "Other")
            geo = request.form.get("geo", "Other")
            products = request.form.get("products", "Other")

            input_data = {
                "Income": income,
                "Coverage Amount": coverage,
                "Premium Amount": premium,
                "Deductible": deductible,
                "Occupation": occupation,
                "Geographic Information": geo,
                "Insurance Products Owned": products
            }

            # Preprocess and predict
            X_scaled = preprocess_input(input_data)
            pred_class = rf_model.predict(X_scaled)[0]
            pred_prob = rf_model.predict_proba(X_scaled)[0]
            risk_percentage = round(float(pred_prob[pred_class]) * 100, 2)
            risk_level = risk_map.get(pred_class, map)

            # Save prediction to DB first
            new_policy = Policy(
                user_id=current_user.id,
                income=income,
                coverage_amount=coverage,
                premium_amount=premium,
                deductible=deductible,
                occupation=occupation,
                geographic_info=geo,
                insurance_products=products,
                risk_score=risk_percentage,
                risk_level=risk_level,
               
                blockchain_txn=None
            )
            db.session.add(new_policy)
            db.session.commit()

            # -------------------------
            # Blockchain integration
            # -------------------------
            try:
                # Ensure the smart contract has a matching function
              
                txn = contract.functions.storePolicy(
                    int(risk_percentage), risk_level
                ).build_transaction({
                    'from': backend_account.address,
                    'nonce': w3.eth.get_transaction_count(backend_account.address),
                    'gas': 3000000,
                    'gasPrice': w3.to_wei('50', 'gwei')
                })

                # Sign the transaction using Web3.py v6+
                signed_txn = w3.eth.account.sign_transaction(txn, backend_private_key)

                # Send raw transaction
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

                # Wait for transaction receipt
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                print(tx_receipt)
                # Save transaction hash in DB
                new_policy.blockchain_txn = tx_hash.hex()
                db.session.commit()
                print(f"Contract created: {new_policy.blockchain_txn}")

            except Exception as e:
                print("Blockchain error:", e)
                result = {"error": f"Prediction saved in DB, but blockchain error: {e}"}
                return render_template("predict.html", result=result)

            # Return results to frontend
            result = {
                "risk_level": risk_level,
                "risk_score": f"{risk_percentage}%",
                "blockchain_txn": new_policy.blockchain_txn
            }

        except Exception as e:
            db.session.rollback()
            print("Prediction error:", e)
            result = {"error": "Error in processing prediction."}

    return render_template("predict.html", result=result)







@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'customer':
        flash("Admins do not have a profile page.", "warning")
        return redirect(url_for('dashboard'))

    policies = None
    if request.method == 'POST':
      
        policies = Policy.query.filter_by(user_id=current_user.id).all()

    return render_template('profile.html', user=current_user, policies=policies)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/policies')
@login_required
def admin_policies():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
  
    else:
       
        policies = Policy.query.all()
    return render_template('admin_policies.html', policies=policies)









@app.route('/verify_kyc/<int:user_id>')
@login_required
def verify_kyc(user_id):
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    user.kyc_verified = True
    db.session.commit()
    flash(f'KYC verified for {user.username}.', 'success')
    return redirect(url_for('admin_dashboard'))




@app.route('/admin/chart', methods=['GET'])
def get_policies():
    policies = Policy.query.all()

  
    risk_counts = Counter([p.risk_level for p in policies])

    
    occupation_premiums = {}
    for p in policies:
        if p.occupation:
            occupation_premiums.setdefault(p.occupation, []).append(p.premium_amount)
    avg_premiums = {occ: sum(vals)/len(vals) for occ, vals in occupation_premiums.items()}

    
    geo_coverage = {}
    for p in policies:
        if p.geographic_info:
            geo_coverage[p.geographic_info] = geo_coverage.get(p.geographic_info, 0) + p.coverage_amount

    return render_template(
        'chart.html',
        risk_counts=risk_counts,
        avg_premiums=avg_premiums,
        geo_coverage=geo_coverage
    )
    
# -----------------------
# Initialize DB
# -----------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
