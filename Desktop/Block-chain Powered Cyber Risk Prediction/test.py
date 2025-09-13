import joblib
import numpy as np
import pandas as pd

# Load models and preprocessing
scaler = joblib.load("ml_models/scaler.pkl")
trained_columns = joblib.load("ml_models/trained_columns.pkl")
rf_model = joblib.load("ml_models/random_forest_model.pkl")

risk_map = {0: "Low", 1: "Medium", 2: "High"}

def preprocess_input(input_data):
    df = pd.DataFrame([input_data])
    
    # Log-transform numeric features
    for col in ['Income', 'Coverage Amount', 'Premium Amount', 'Deductible']:
        if col in df.columns:
            df[col] = np.log1p(df[col])
    
    # Feature engineering
    if 'Income' in df.columns and 'Premium Amount' in df.columns:
        df['Income_to_Premium'] = df['Income'] / (df['Premium Amount'] + 1)
    if 'Coverage Amount' in df.columns and 'Income' in df.columns:
        df['Coverage_to_Income'] = df['Coverage Amount'] / (df['Income'] + 1)
    
    # One-hot encode
    df = pd.get_dummies(df)
    
    # Add missing columns at once
    missing_cols = [col for col in trained_columns if col not in df.columns]
    if missing_cols:
        df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing_cols)], axis=1)
    
    # Reorder columns
    df = df[trained_columns]
    
    return scaler.transform(df)

def get_input(prompt, default=None, numeric=False):
    while True:
        value = input(prompt)
        if not value.strip() and default is not None:
            return default
        if numeric:
            try:
                return float(value)
            except ValueError:
                print("Please enter a valid number.")
        else:
            return value.strip()

def main():
    print("Enter the following details one by one:")
    
    income = get_input("Income: ", numeric=True)
    coverage = get_input("Coverage Amount: ", numeric=True)
    premium = get_input("Premium Amount: ", numeric=True)
    deductible = get_input("Deductible: ", numeric=True)
    occupation = get_input("Occupation: ", default="Other")
    geo = get_input("Geographic Information: ", default="Other")
    products = get_input("Insurance Products Owned: ", default="Other")
    
    input_data = {
        "Income": income,
        "Coverage Amount": coverage,
        "Premium Amount": premium,
        "Deductible": deductible,
        "Occupation": occupation,
        "Geographic Information": geo,
        "Insurance Products Owned": products
    }
    
    X_scaled = preprocess_input(input_data)
    pred_class = rf_model.predict(X_scaled)[0]
    pred_prob = rf_model.predict_proba(X_scaled)[0]
    
    risk_percentage = round(float(pred_prob[pred_class]) * 100, 2)
    
    # Print two lines
    risk_level = risk_map.get(pred_class, f"Unknown ({pred_class})")
    print(f"Risk Level: {risk_level}")
    print(f"Risk Score = {risk_percentage}%")
if __name__ == "__main__":
    main()
