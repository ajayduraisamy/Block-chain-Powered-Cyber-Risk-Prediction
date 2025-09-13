# Cyber Insurance Prediction Platform

A **Flask-based web application** for cyber insurance risk prediction with **machine learning** and **Ethereum blockchain integration**.

---

## Features

- **User Management**: Registration, login, KYC verification, and profile pages.
- **ML-based Risk Prediction**: Predicts insurance risk using a trained Random Forest model.
- **Blockchain Integration**: 
  - Automatically generates Ethereum wallets for users upon registration.
  - Stores policy predictions on Ethereum (Ganache) via a Solidity smart contract.
  - Keeps immutable records of risk scores and levels.
- **Admin Dashboard**: View users, policies, and generate charts (pie and bar charts).
- **Charts & Analytics**: Visualizes risk distribution, average premium by occupation, and total coverage by geography.

---

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Machine Learning**: Scikit-learn, Pandas, NumPy, Joblib
- **Blockchain**: Ethereum (Ganache), Web3.py, Solidity smart contract
- **Frontend**: HTML, CSS, Chart.js
- **Database**: SQLite (can be switched to PostgreSQL/MySQL)

---

## Blockchain Details

1. **User Wallets**: Every registered user gets a new Ethereum wallet address.
2. **Smart Contract**: A Solidity contract stores policy risk scores and levels.
3. **Transaction Management**: Backend account signs and sends transactions, storing the hash in the database.
4. **Verification**: Admins can track blockchain transactions for audit and immutability.

---

## Installation & Usage

1. Clone repository:

```bash
git clone https://github.com/ajayduraisamy/Block-chain-Powered-Cyber-Risk-Prediction.git
cd Block-chain-Powered-Cyber-Risk-Prediction

---
## flask run or python app.py
---
Open http://127.0.0.1:5000/ in your browser.
---
Project Structure
.
├── app.py                  # Flask app with blockchain & ML integration
├── models.py
├── contracts/
│   └── MyContract.sol      # Solidity smart contract
├── build/
│   └── compiled_contract.json
├── ml_models/
├── templates/
├── static/
├── requirements.txt
└── README.md
---


---

 Now blockchain is **front and center**, showing that your app:  

1. Generates user wallets.  
2. Stores predictions immutably.  
3. Uses Ethereum smart contracts.  

---
