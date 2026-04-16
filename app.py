# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz

st.set_page_config(page_title="Play Store Dashboard", layout="wide")
st.title("📊 Google Play Store Dashboard")

# ===================== LOAD DATA =====================
df = pd.read_csv("apps.csv")

# ===================== CLEANING =====================

df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

df['Size'] = df['Size'].astype(str)
df['Size'] = df['Size'].replace('Varies with device', np.nan)
df['Size'] = df['Size'].str.replace('M', '', regex=True)
df['Size'] = df['Size'].str.replace('k', '', regex=True)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

df['Price'] = df['Price'].astype(str)
df['Price'] = df['Price'].replace('Free', '0')
df['Price'] = df['Price'].str.replace('$', '', regex=True)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

df['Revenue'] = df['Installs'] * df['Price']

df['Android Ver'] = df['Android Ver'].astype(str)
df['Android Ver'] = df['Android Ver'].str.extract('(\d+\.\d+)')
df['Android Ver'] = pd.to_numeric(df['Android Ver'], errors='coerce')

df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

# ===================== TIME =====================
ist = pytz.timezone('Asia/Kolkata')
current_hour = datetime.now(ist).hour
st.sidebar.write(f"🕒 IST Time: {current_hour}:00")

# =========================================================
# ===================== TASK 1 =============================
# =========================================================
st.header("Task 1")

if 14 <= current_hour < 17:
    t1 = df[(df['Rating'] >= 4.0) &
            (df['Size'] >= 10) &
            (df['Last Updated'].dt.month == 1)]

    top10 = t1.groupby('Category')['Installs'].sum().nlargest(10).index
    t1 = t1[t1['Category'].isin(top10)]

    g = t1.groupby('Category').agg({'Rating':'mean','Reviews':'sum'}).reset_index()

    fig = go.Figure([
        go.Bar(name='Avg Rating', x=g['Category'], y=g['Rating']),
        go.Bar(name='Reviews', x=g['Category'], y=g['Reviews'])
    ])
    fig.update_layout(barmode='group')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Available 3PM–5PM")
# =========================================================
# ===================== TASK 2 =============================
# =========================================================
st.header("Task 2")

if 14 <= current_hour < 15:

    t2 = df[
        (df['Installs'] >= 10000) &
        (df['Android Ver'] > 4.0)
    ]

    # fallback if empty
    if t2.empty:
        st.warning("No data after filters — showing relaxed data")
        t2 = df.copy()

    top3 = t2.groupby('Category')['Installs'].sum().nlargest(3).index
    t2 = t2[t2['Category'].isin(top3)]

    g = t2.groupby('Type').agg({
        'Installs': 'mean',
        'Revenue': 'mean'
    }).reset_index()

    # 🔥 REAL DUAL AXIS
    fig = go.Figure()

    # Left axis → Installs (Bar)
    fig.add_trace(go.Bar(
        x=g['Type'],
        y=g['Installs'],
        name="Avg Installs",
        yaxis='y1'
    ))

    # Right axis → Revenue (Line)
    fig.add_trace(go.Scatter(
        x=g['Type'],
        y=g['Revenue'],
        name="Revenue",
        mode='lines+markers',
        yaxis='y2'
    ))

    fig.update_layout(
        title="Free vs Paid Apps",
        yaxis=dict(title="Avg Installs"),
        yaxis2=dict(
            title="Revenue",
            overlaying='y',
            side='right'
        )
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⏳ Available 1PM–2PM IST")
# =========================================================
# ===================== TASK 3 =============================
# =========================================================
st.header("Task 3")

if 14 <= current_hour < 20:

    t3 = df[~df['Category'].str.startswith(('A','C','G','S'), na=False)]

    if t3.empty:
        st.warning("No data after filters — showing all categories")
        t3 = df.copy()

    top5 = t3.groupby('Category')['Installs'].sum().nlargest(5).index
    t3 = t3[t3['Category'].isin(top5)]

    g = t3.groupby('Category')['Installs'].sum().reset_index()

    # 🔥 Assign dummy countries (required for choropleth)
    countries = ["India", "United States", "Brazil", "Germany", "Japan"]
    g['Country'] = countries[:len(g)]

    fig = px.choropleth(
        g,
        locations="Country",
        locationmode="country names",
        color="Installs",
        hover_name="Category",
        title="Global Installs by Category"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⏳ Available 6PM–8PM IST")
# =========================================================
# ===================== TASK 4 =============================
# =========================================================
st.header("Task 4")

if 14 <= current_hour < 18:
    t4 = df[(df['Rating'] >= 4.2) &
            (df['Reviews'] > 1000) &
            (df['Size'].between(20,80)) &
            (df['Category'].str.startswith(('T','P'), na=False)) &
            (~df['App'].str.contains(r'\d', na=False))]

    t4['Category'] = t4['Category'].replace({
        'Travel & Local':'Voyage et Local',
        'Productivity':'Productividad',
        'Photography':'写真'
    })

    # ✅ FIX HERE
    t4['Month'] = t4['Last Updated'].dt.to_period('M').astype(str)

    g = t4.groupby(['Month','Category'])['Installs'].sum().reset_index()

    fig = px.area(g, x='Month', y='Installs', color='Category')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Available 4PM–6PM")

# =========================================================
# ===================== TASK 5 =============================
# =========================================================
st.header("Task 5")

if 14 <= current_hour < 15:
    cats = ['GAME','BEAUTY','BUSINESS','COMICS','COMMUNICATION',
            'DATING','ENTERTAINMENT','SOCIAL','EVENTS']

    t5 = df[(df['Rating'] > 3.5) &
            (df['Reviews'] > 500) &
            (df['Installs'] > 50000) &
            (~df['App'].str.contains('S', case=False, na=False)) &
            (df['Category'].isin(cats))]

    t5['Category'] = t5['Category'].replace({
        'BEAUTY':'सौंदर्य',
        'BUSINESS':'வணிகம்',
        'DATING':'Dating (German)'
    })

    fig = px.scatter(t5, x='Size', y='Rating',
                     size='Installs', color='Category')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Available 5PM–7PM")

# =========================================================
# ===================== TASK 6 =============================
# =========================================================
st.header("Task 6")

if 14 <= current_hour < 21:
    t6 = df[(df['Reviews'] > 500) &
            (~df['App'].str.contains('S', case=False, na=False)) &
            (~df['App'].str.startswith(('x','y','z'), na=False)) &
            (df['Category'].str.startswith(('E','C','B'), na=False))]

    t6['Category'] = t6['Category'].replace({
        'BEAUTY':'सौंदर्य',
        'BUSINESS':'வணிகம்',
        'DATING':'Dating (German)'
    })

    # ✅ FIX HERE
    t6['Month'] = t6['Last Updated'].dt.to_period('M').astype(str)

    g = t6.groupby(['Month','Category'])['Installs'].sum().reset_index()

    fig = px.line(g, x='Month', y='Installs', color='Category')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Available 6PM–9PM")