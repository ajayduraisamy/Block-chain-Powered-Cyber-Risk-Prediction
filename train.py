import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from imblearn.over_sampling import SMOTE

# Load dataset
file1 = "datas.csv"
df = pd.read_csv(file1)
df.columns = df.columns.str.strip()

# Handle missing values
for col in df.select_dtypes(include=['object']):
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace('nan', np.nan)
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].mode()[0])

for col in df.select_dtypes(include=['float64', 'int64']):
    df[col] = df[col].fillna(df[col].median())

# Drop unnecessary columns
cols_to_drop = ['Customer ID', 'Policy Start Date', 'Policy Renewal Date']
df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)

# Reduce high-cardinality features
for col in ['Occupation', 'Geographic Information', 'Insurance Products Owned']:
    if col in df.columns:
        counts = df[col].value_counts()
        rare = counts[counts < 50].index
        df[col] = df[col].replace(rare, 'Other')

# Feature engineering
if 'Income' in df.columns and 'Premium Amount' in df.columns:
    df['Income_to_Premium'] = df['Income'] / (df['Premium Amount'] + 1)

if 'Coverage Amount' in df.columns and 'Income' in df.columns:
    df['Coverage_to_Income'] = df['Coverage Amount'] / (df['Income'] + 1)

# Log-transform skewed numeric features
for col in ['Income', 'Coverage Amount', 'Premium Amount', 'Deductible']:
    if col in df.columns:
        df[col] = np.log1p(df[col])

# Encode target
target_column = 'Risk Profile'
if df[target_column].dtype == 'object':
    df[target_column], uniques = pd.factorize(df[target_column])
    print(f"Target classes: {list(uniques)}")

X = df.drop(target_column, axis=1)
y = df[target_column]

# One-hot encode categorical features
X = pd.get_dummies(X)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "scaler.pkl")
joblib.dump(X.columns.tolist(), "trained_columns.pkl")

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X_scaled, y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
)

# Initialize models
models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=300, max_depth=15, class_weight='balanced', random_state=42
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000, class_weight='balanced', random_state=42
    ),
    "Neural Network": MLPClassifier(
        hidden_layer_sizes=(128,64),
        max_iter=1000,
        batch_size=64,
        early_stopping=True,
        random_state=42
    )
}

results = {}

# Train, evaluate, save models
for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    results[name] = acc
    print(f"{name} Accuracy: {acc:.4f}")
    
    # Save model
    joblib.dump(model, f"{name.replace(' ', '_').lower()}_model.pkl")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=np.unique(y))
    disp.plot(cmap=plt.cm.Blues)
    plt.title(f"{name} - Confusion Matrix")
    plt.show()

# Accuracy comparison
plt.figure(figsize=(8,5))
plt.bar(results.keys(), results.values(), color=['blue', 'green', 'red'])
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.ylim(0, 1)
for i, v in enumerate(results.values()):
    plt.text(i, v + 0.02, f"{v:.2f}", ha='center')
plt.show()
