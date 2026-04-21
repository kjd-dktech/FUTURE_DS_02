# Copyright (c) 2026 Kodjo Jean DEGBEVI.
#====================================
# Data Cleaning
#====================================

import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le dataset Telco Customer Churn.
    - Remplace les espaces vides de TotalCharges par 0
    - Convertit la colonne TotalCharges en float
    - Positionne customerID comme index
    - Harmonise SeniorCitizen en Yes/No
    """
    df_clean = df.copy()
    
    df_clean['TotalCharges'] = pd.to_numeric(df_clean['TotalCharges'], errors='coerce')
    df_clean['TotalCharges'] = df_clean['TotalCharges'].fillna(0.0)
    
    if 'customerID' in df_clean.columns:
        df_clean = df_clean.set_index('customerID')
        
    if 'SeniorCitizen' in df_clean.columns:
        df_clean['SeniorCitizen'] = df_clean['SeniorCitizen'].replace({0: 'No', 1: 'Yes'})
    
    return df_clean

def create_tenure_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Catégorise la variable 'tenure' (mois) en cohortes d'ancienneté.
    """
    df_out = df.copy()
    bins = [-1, 12, 24, 48, 60, 100]
    labels = ['0-12 mois', '12-24 mois', '24-48 mois', '48-60 mois', '60+ mois']
    df_out['tenure_group'] = pd.cut(df_out['tenure'], bins=bins, labels=labels)
    return df_out
