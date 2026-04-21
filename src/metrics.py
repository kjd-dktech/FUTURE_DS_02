# Copyright (c) 2026 Kodjo Jean DEGBEVI.
#====================================
# Metrics
#====================================

import pandas as pd

def calculate_global_churn_rate(df: pd.DataFrame) -> dict:
    """
    Calcule le taux de churn global sur le dataset en pourcentage.
    """
    churn_counts = df['Churn'].value_counts()
    churn_rate = (churn_counts.get('Yes', 0) / len(df)) * 100
    return {
        'total_customers': len(df),
        'churn_rate': churn_rate,
        'churn_counts': churn_counts.to_dict()
    }

def calculate_churn_financial_impact(df: pd.DataFrame) -> dict:
    """
    Calcule l'impact financier mensuel et total du churn.
    """
    df_churners = df[df['Churn'] == 'Yes']
    df_retained = df[df['Churn'] == 'No']
    
    impact = {
        'lost_mrr': df_churners['MonthlyCharges'].sum(),
        'retained_mrr': df_retained['MonthlyCharges'].sum(),
        'lost_total_revenue': df_churners['TotalCharges'].sum(),
        'retained_total_revenue': df_retained['TotalCharges'].sum(),
    }
    return impact
