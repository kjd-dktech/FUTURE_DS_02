import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ==========================================
# CONFIGURATION ET STYLE
# ==========================================
st.set_page_config(
    page_title="Telco Churn Dashboard",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

import plotly.io as pio
pio.templates.default = "plotly_white"

# ==========================================
# CHARGEMENT DES DONNÉES
# ==========================================
@st.cache_data
def load_data():
    current_dir = Path(__file__).parent
    df = pd.read_csv(current_dir / 'telco_churn_processed.csv')
    return df

df = load_data()

# ==========================================
# SIDEBAR / NAVIGATION
# ==========================================
st.sidebar.title("📉 Churn Dashboard")
st.sidebar.markdown("*Outil de diagnostic et de pilotage stratégique.*")

page = st.sidebar.radio(
    "Navigation :",
    [
        "Vue d'Ensemble",
        "Analyse de Survie",
        "Moteurs de Fuite",
        "Segmentation Démographique",
        "Recommandations Stratégiques"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtres Globaux")
gender_filter = st.sidebar.multiselect("Sexe", options=df['gender'].unique(), default=df['gender'].unique())
senior_filter = st.sidebar.multiselect("Senior", options=df['SeniorCitizen'].unique(), default=df['SeniorCitizen'].unique())
df_filtered = df[(df['gender'].isin(gender_filter)) & (df['SeniorCitizen'].isin(senior_filter))]

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================
def get_churn_rate(data, col):
    return data.groupby(col, observed=False)['Churn'].apply(lambda x: (x == 'Yes').mean() * 100).reset_index(name='Churn Rate (%)')

# ==========================================
# PAGE 1 : VUE D'ENSEMBLE
# ==========================================
if page == "Vue d'Ensemble (KPI)":
    st.title("📊 Executive Summary")
    st.markdown("Aperçu global de l'impact de l'attrition sur la base clientèle filtrée.")
    
    # KPIs
    total_clients = len(df_filtered)
    churners = len(df_filtered[df_filtered['Churn'] == 'Yes'])
    churn_rate = (churners / total_clients * 100) if total_clients > 0 else 0

    mrr_lost = df_filtered[df_filtered['Churn'] == 'Yes']['MonthlyCharges'].sum()
    ltv_lost = df_filtered[df_filtered['Churn'] == 'Yes']['TotalCharges'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clients", f"{total_clients:,}")
    with col2:
        st.metric("Taux de Churn", f"{churn_rate:.1f}%", "- Critique" if churn_rate > 20 else "Stable", delta_color="inverse")
    with col3:
        st.metric("MRR Perdu ($/mois)", f"${mrr_lost:,.0f}")
    with col4:
        st.metric("LTV Perdue (Total $)", f"${ltv_lost:,.0f}")

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        fig_pie = px.pie(
            names=['Restés (No)', 'Partis (Yes)'],
            values=[total_clients - churners, churners],
            title="Proportion des clients (Volume)",
            color_discrete_sequence=['#2ecc71', '#e74c3c'],
            hole=0.4
        )
        st.plotly_chart(fig_pie, width='stretch')

    with c2:
        mrr_retained = df_filtered[df_filtered['Churn'] == 'No']['MonthlyCharges'].sum()
        fig_bar = go.Figure(data=[
            go.Bar(name='Conservé', x=['MRR ($)'], y=[mrr_retained], marker_color='#2ecc71'),
            go.Bar(name='Perdu', x=['MRR ($)'], y=[mrr_lost], marker_color='#e74c3c')
        ])
        fig_bar.update_layout(title="Impact Financier Mensuel", barmode='stack')
        st.plotly_chart(fig_bar, width='stretch')

# ==========================================
# PAGE 2 : ANALYSE DE SURVIE
# ==========================================
elif page == "Analyse de Survie (Ancienneté)":
    st.title("⏳ Cohortes d'Ancienneté")
    st.markdown("Quand nos clients décident-ils de nous quitter ? Analyse de l'effet d'ancrage.")
    
    cohort_data = df_filtered.groupby('tenure_group', observed=False).agg(
        Total=('Churn', 'count'),
        Churners=('Churn', lambda x: (x == 'Yes').sum())
    ).reset_index()
    cohort_data['Churn Rate (%)'] = (cohort_data['Churners'] / cohort_data['Total']) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=cohort_data['tenure_group'], y=cohort_data['Total'], name="Volume Clients", marker_color='#3498db', opacity=0.6),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=cohort_data['tenure_group'], y=cohort_data['Churn Rate (%)'], name="Taux d'Attrition (%)", 
            mode='lines+markers+text', text=cohort_data['Churn Rate (%)'].apply(lambda x: f'{x:.1f}%'),
            textposition="top center", marker=dict(color='#e74c3c', size=12), line=dict(width=3)
        ),
        secondary_y=True,
    )

    fig.update_layout(title="Volume & Risque par Tranche d'Ancienneté", hovermode="x unified")
    fig.update_yaxes(title_text="Volume", secondary_y=False)
    fig.update_yaxes(title_text="Churn Rate (%)", showgrid=False, secondary_y=True)

    st.plotly_chart(fig, width='stretch')
    
    st.info("Près de 50\\% des clients de la première année (0-12 mois) coupent leur abonnement. L'urgence se situe dans le processus d'Onboarding.")

# ==========================================
# PAGE 3 : MOTEURS DE FUITE
# ==========================================
elif page == "Moteurs de Fuite (Contrat & Services)":
    st.title("🔌 Frictions Administratives & Vendor Lock-in")
    
    st.markdown("### 1. L'impact de l'Engagement")
    c1, c2 = st.columns(2)
    
    contract_churn = get_churn_rate(df_filtered, 'Contract')
    fig_contract = px.bar(
        contract_churn, x='Contract', y='Churn Rate (%)', text='Churn Rate (%)',
        title="Type de Contrat", color='Contract', 
        color_discrete_map={"Month-to-month": "#e74c3c", "One year": "#f39c12", "Two year": "#2ecc71"}
    )
    fig_contract.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    c1.plotly_chart(fig_contract, width='stretch')
    
    payment_churn = get_churn_rate(df_filtered, 'PaymentMethod')
    fig_pay = px.bar(
        payment_churn, x='PaymentMethod', y='Churn Rate (%)', text='Churn Rate (%)',
        title="Moyen de Paiement", color='PaymentMethod',
        color_discrete_map={"Electronic check": "#e74c3c"} # Met en rouge le chèque élec
    )
    fig_pay.update_layout(showlegend=False)
    fig_pay.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_color=['#e74c3c' if x == 'Electronic check' else '#95a5a6' for x in payment_churn['PaymentMethod']])
    c2.plotly_chart(fig_pay, width='stretch')

    st.markdown("---")
    st.markdown("### 2. Le Paradoxe de la Fibre et l'Enfermement")
    
    c3, c4 = st.columns(2)
    
    services_churn = get_churn_rate(df_filtered[df_filtered['InternetService'] != 'No'], 'Total_Services')
    fig_svc = px.bar(services_churn, x='Total_Services', y='Churn Rate (%)', title="Nombre de services additionnels (Lock-in)")
    fig_svc.update_traces(marker_color='#3498db')
    c3.plotly_chart(fig_svc, width='stretch')
    
    fiber_df = df_filtered[df_filtered['InternetService'] == 'Fiber optic']
    fiber_sup_churn = get_churn_rate(fiber_df, 'TechSupport')
    fig_fib = px.bar(fiber_sup_churn, x='TechSupport', y='Churn Rate (%)', title="Fibre Optique : Impact du TechSupport")
    fig_fib.update_traces(marker_color=['#e74c3c', '#2ecc71'])
    c4.plotly_chart(fig_fib, width='stretch')

# ==========================================
# PAGE 4 : SEGMENTATION
# ==========================================
elif page == "Segmentation Démographique":
    st.title("👨‍👩‍👧 Profils Démographiques & Risques")
    st.markdown("Identifier les Personas les plus instables.")
    
    fam_churn = get_churn_rate(df_filtered, 'Family_Stability')
    sen_churn = get_churn_rate(df_filtered, 'SeniorCitizen')
    
    c1, c2 = st.columns(2)
    
    fig_fam = px.bar(fam_churn, x='Family_Stability', y='Churn Rate (%)', text='Churn Rate (%)', title="Stabilité Familiale (0=Solo, 2=Famille)")
    fig_fam.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_color=['#e74c3c', '#f39c12', '#2ecc71'])
    c1.plotly_chart(fig_fam, width='stretch')
    
    fig_sen = px.bar(sen_churn, x='SeniorCitizen', y='Churn Rate (%)', text='Churn Rate (%)', title="Client Senior")
    fig_sen.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_color=['#2ecc71', '#e74c3c'])
    c2.plotly_chart(fig_sen, width='stretch')

# ==========================================
# PAGE 5 : RECOMMANDATIONS (Q6)
# ==========================================
elif page == "Recommandations Stratégiques":
    st.title("🎯 Plan d'action pour la Direction")
    st.markdown("---")
    
    st.success("### 1. Verrouiller l'Engagement Contractuel")
    st.write("""
    - **Abolir les facilités de départ :** Le contrat *Month-to-month* (42.7% d'attrition) doit être découragé par une politique de "pricing" agressive qui favorise l'engagement sur 1 ou 2 ans.
    - **Automatiser la trésorerie :** Le paiement manuel (*Electronic check*) génère une friction majeure (+45% de départ). Appliquer une remise symbolique pour obliger le passage au prélèvement automatique (*Auto-pay*).
    """)
    
    st.error("### 2. Opération Sauvetage 'Fibre Optique'")
    st.write("""
    - **Le Paradoxe Premium :** L'offre Fibre est chère ($91/mois en moyenne) et suscite de lourdes attentes. Sans *TechSupport*, 1 client Fibre sur 2 part (49.4%).
    - **Stratégie immédiate :** Rendre le service d'assistance premium (`TechSupport`) totalement **gratuit et inclus par défaut** pour les offres Fibre.
    """)
    
    st.warning("### 3. Surveiller l'Onboarding des Profils Isolés")
    st.write("""
    - **Période de mort (0-12 mois) :** 47% des pertes complètes d'utilisateurs arrivent durant la première année d'ancienneté.
    - **Personas à cibler :** Concentrer l'effort du Service Client humain sur les jeunes célibataires (profil isolé) et les seniors. Un appel d'accompagnement à J+15 et J+90 est fortement recommandé.
    """)
    
    st.info("### 4. Politique de Cross-Selling (Vendor Lock-in)")
    st.write("""
    - **Multiplier les couches technologiques :** Un client ne consommant que de l'accès Internet (sans sécurité ni sauvegarde) s'en ira dès la première meilleure offre concurrente.
    - Dès qu'un client possède plus de 3 services optionnels (*Online Backup, Device Protection, etc.*), son inertie technologique garantit sa présence sur le long terme (attrition < 15%). 
    """)