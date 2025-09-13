# 🚀 Cyber Insurance Prediction Platform

A **Flask-based web application** for cyber insurance risk prediction with **Machine Learning** and **Ethereum Blockchain integration**.

---

## ✨ Features

- **User Management** – Registration, login, KYC verification, and profile pages.
- **ML-based Risk Prediction** – Predicts insurance risk using a trained Random Forest model.
- **Blockchain Integration**  
  - Automatically generates Ethereum wallets for users upon registration.  
  - Stores policy predictions on Ethereum (Ganache) via a Solidity smart contract.  
  - Keeps immutable records of risk scores and levels.
- **Admin Dashboard** – View users, policies, and generate charts (pie and bar charts).
- **Charts & Analytics** – Visualizes risk distribution, average premium by occupation, and total coverage by geography.

---

## 🛠 Technologies Used

| Layer          | Technology |
|----------------|------------|
| Backend        | Flask, SQLAlchemy, Flask-Login |
| Machine Learning | Scikit-learn, Pandas, NumPy, Joblib |
| Blockchain     | Ethereum (Ganache), Web3.py, Solidity |
| Frontend       | HTML, CSS, Chart.js |
| Database       | SQLite (switchable to PostgreSQL/MySQL) |

---

## 🔗 Blockchain Details

1. **User Wallets** – Every registered user gets a unique Ethereum wallet.  
2. **Smart Contract** – A Solidity contract stores policy risk scores and levels.  
3. **Transaction Management** – Backend account signs and sends transactions, storing the hash in the database.  
4. **Verification** – Admins can track blockchain transactions for audit and immutability.

---
📂 Project Structure

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


## 💻 Installation & Usage

```bash
git clone https://github.com/ajayduraisamy/Block-chain-Powered-Cyber-Risk-Prediction.git
cd Block-chain-Powered-Cyber-Risk-Prediction
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run                      # or python app.py

🔑 Highlights

💼 Generates Ethereum wallets for users

🔒 Stores predictions immutably on blockchain

⚡ Uses smart contracts for secure, transparent risk recording

📊 Dashboard charts: pie & bar for analytics

📜 License

MIT License


👤 Author

Ajay Duraisamy
Cyber Insurance Prediction Platform with ML & Blockchain

---


 


