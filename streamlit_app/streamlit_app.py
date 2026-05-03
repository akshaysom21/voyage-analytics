# ============================================================
# VOYAGE ANALYTICS - STREAMLIT APP
# streamlit_app/streamlit_app.py
# ============================================================

# Section 1 - Page Config + Imports

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Page Config
st.set_page_config(
    page_title = "Voyage Analytics",
    page_icon = "✈️",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
MODELS_DIR = os.path.join(ROOT_DIR, 'models')
DATA_DIR = os.path.join(ROOT_DIR, 'data')


# Section 2 - Load Data & Models

# Load Data
@st.cache_data
def load_data():
    users = pd.read_csv(os.path.join(DATA_DIR, 'users.csv'))
    hotels = pd.read_csv(os.path.join(DATA_DIR, 'hotels.csv'))
    flights = pd.read_csv(os.path.join(DATA_DIR, 'flights.csv'))
    return users, hotels, flights

# Load Models
@st.cache_resource
def load_models():
    hotel_sim = joblib.load(os.path.join(MODELS_DIR, 'hotel_similarity.pkl'))
    collab_mat = joblib.load(os.path.join(MODELS_DIR, 'collaborative_matrix.pkl'))
    user_hotel = joblib.load(os.path.join(MODELS_DIR, 'user_hotel_matrix.pkl'))
    user_prof = joblib.load(os.path.join(MODELS_DIR, 'user_profiles.pkl'))
    hotel_feat = joblib.load(os.path.join(MODELS_DIR, 'hotel_features.pkl'))
    flight_model = joblib.load(os.path.join(MODELS_DIR, 'flight_price_model.pkl'))
    flight_columns = joblib.load(os.path.join(MODELS_DIR, 'feature_columns.pkl'))
    return (hotel_sim, collab_mat, user_hotel,
            user_prof, hotel_feat,
            flight_model, flight_columns)



# Section 3 - Recommendation Functions

# Content-Based Recommend
def content_based_recommend(user_code, hotels_df, hotel_sim_df, n=5):
    user_hotels = hotels_df[hotels_df['userCode'] == user_code]['name'].unique()

    if len(user_hotels) == 0 or len(user_hotels) >= 9:
        popular = hotels_df['name'].value_counts().head(n).index.tolist()
        return pd.DataFrame({
            'Hotel' : popular,
            'Avg Price' : [round(hotels_df[hotels_df['name']==h]['price'].mean(), 2) for h in popular],
            'Score' : [1.0] * len(popular),
            'Reason' : ['🔥 Popular hotel'] * len(popular)
        })

    sim_scores = pd.Series(0.0, index=hotel_sim_df.columns)
    for hotel in user_hotels:
        if hotel in hotel_sim_df.index:
            sim_scores += hotel_sim_df[hotel]
    sim_scores = sim_scores / len(user_hotels)
    sim_scores = sim_scores.drop(
        labels=[h for h in user_hotels if h in sim_scores.index],
        errors='ignore'
    )
    top = sim_scores.sort_values(ascending=False).head(n)

    return pd.DataFrame({
        'Hotel' : top.index,
        'Avg Price' : [round(hotels_df[hotels_df['name']==h]['price'].mean(), 2) for h in top.index],
        'Score' : top.values.round(4),
        'Reason' : ['📍 Similar to past stays'] * len(top)
    })


# Collaborative Recommend
def collaborative_recommend(user_code, collab_df, user_hotel_matrix, hotels_df, n=5):
    if user_code not in collab_df.index:
        popular = hotels_df['name'].value_counts().head(n).index.tolist()
        return pd.DataFrame({
            'Hotel' : popular,
            'Avg Price' : [round(hotels_df[hotels_df['name']==h]['price'].mean(), 2) for h in popular],
            'Score' : [1.0] * len(popular),
            'Reason' : ['👥 Popular'] * len(popular)
        })

    user_scores = collab_df.loc[user_code].copy()
    already = user_hotel_matrix.loc[user_code]
    already = already[already > 0].index
    user_scores = user_scores.drop(labels=already, errors='ignore')
    top = user_scores.sort_values(ascending=False).head(n)

    return pd.DataFrame({
        'Hotel' : top.index,
        'Avg Price' : [round(hotels_df[hotels_df['name']==h]['price'].mean(), 2) for h in top.index],
        'Score' : top.values.round(4),
        'Reason' : ['👥 Loved by similar users'] * len(top)
    })


# Hybrid Recommend
def hybrid_recommend(user_code, hotels_df, hotel_sim_df,
                     collab_df, user_hotel_matrix, n=5):
    c = content_based_recommend(user_code, hotels_df, hotel_sim_df, n=n*2)
    cf = collaborative_recommend(user_code, collab_df, user_hotel_matrix, hotels_df, n=n*2)

    def norm(s):
        mn, mx = s.min(), s.max()
        return (s - mn)/(mx - mn + 1e-9)

    c['norm'] = norm(c['Score']) * 0.5
    cf['norm'] = norm(cf['Score']) * 0.5

    combined = pd.concat([c, cf], ignore_index=True)
    combined = combined.groupby('Hotel').agg(
        Avg_Price = ('Avg Price', 'first'),
        Score = ('norm', 'sum'),
        Reason = ('Reason', lambda x: ' + '.join(x.unique()))
    ).reset_index()
    combined = combined.sort_values('Score', ascending=False).head(n)
    combined.columns = ['Hotel', 'Avg Price ($)', 'Score', 'Why Recommended']
    return combined.reset_index(drop=True)


# Flight Price Predictor
def predict_flight_price(distance, flight_type, agency,
                         month, dow, model, feature_columns):
    FLIGHT_TYPE_MAP = {'economic': 0, 'premium': 1, 'firstClass': 2}
    features = {
        'distance' : float(distance),
        'month' : int(month),
        'day_of_week' : int(dow),
        'flightType_encoded' : FLIGHT_TYPE_MAP[flight_type],
        'agency_CloudFy' : 1 if agency == 'CloudFy' else 0,
        'agency_FlyingDrops' : 1 if agency == 'FlyingDrops' else 0,
        'agency_Rainbow' : 1 if agency == 'Rainbow' else 0,
    }
    input_df = pd.DataFrame([features])[feature_columns]
    return round(float(model.predict(input_df)[0]), 2)



# Section 4 - Main Function + Sidebar

# MAIN APP
def main():
    # Load data and models
    users, hotels, flights = load_data()
    (hotel_sim, collab_mat, user_hotel,
     user_prof, hotel_feat,
     flight_model, flight_columns) = load_models()

    # Sidebar
    st.sidebar.title("✈️ Voyage Analytics")
    st.sidebar.markdown("*Integrating MLOps in Travel*")
    st.sidebar.divider()

    page = st.sidebar.radio("Navigate",
        ["🏠 Dashboard",
         "🏨 Hotel Recommendations",
         "💰 Flight Price Predictor",
         "📊 Data Insights"]
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Model Performance**")
    st.sidebar.metric("Regression R²", "0.9067")
    st.sidebar.metric("Classification", "40.30%")
    st.sidebar.metric("Rec Coverage", "100%")
    st.sidebar.divider()
    st.sidebar.markdown("*Built by Akshay Som*")

    # Section 5 - Dashboard Page

    # PAGE 1 — DASHBOARD
    if page == "🏠 Dashboard":
        st.title("✈️ Voyage Analytics Dashboard")
        st.markdown("### Integrating MLOps in Travel - Productionization of ML Systems")
        st.divider()

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Total Users", f"{users.shape[0]:,}")
        col2.metric("✈️ Total Flights", f"{flights.shape[0]:,}")
        col3.metric("🏨 Hotel Bookings", f"{hotels.shape[0]:,}")
        col4.metric("📍 Unique Places", f"{hotels['place'].nunique()}")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✈️ Flight Type Distribution")
            fig, ax = plt.subplots(figsize=(6, 4))
            flights['flightType'].value_counts().plot(
                kind = 'pie', ax = ax, autopct = '%1.1f%%',
                colors = ['#7C3AED', '#06B6D4', '#10B981'],
                startangle = 90
            )
            ax.set_ylabel('')
            st.pyplot(fig)
            plt.close()

        with col2:
            st.subheader("👥 Gender Distribution")
            fig, ax = plt.subplots(figsize=(6, 4))
            users['gender'].value_counts().plot(
                kind = 'bar', ax = ax,
                color = ['#E91E63', '#2196F3', '#9E9E9E'],
                edgecolor = 'black', alpha = 0.85
            )
            ax.set_xlabel('Gender')
            ax.set_ylabel('Count')
            ax.tick_params(axis='x', rotation=0)
            st.pyplot(fig)
            plt.close()

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Avg Flight Price by Class")
            fig, ax = plt.subplots(figsize=(6, 4))
            flights.groupby('flightType')['price'].mean().sort_values().plot(
                kind = 'barh', ax = ax,
                color = ['#10B981', '#06B6D4', '#7C3AED'],
                edgecolor = 'black'
            )
            ax.set_xlabel('Avg Price ($)')
            st.pyplot(fig)
            plt.close()

        with col2:
            st.subheader("🏨 Top Booked Hotels")
            fig, ax = plt.subplots(figsize=(6, 4))
            hotels['name'].value_counts().plot(
                kind = 'bar', ax = ax,
                color = '#06B6D4',
                edgecolor = 'black', alpha = 0.85
            )
            ax.set_xlabel('Hotel')
            ax.set_ylabel('Bookings')
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
            plt.close()

    
    # Section 6 - Hotel Recommendations Page

    # PAGE 2 — HOTEL RECOMMENDATIONS

    elif page == "🏨 Hotel Recommendations":
        st.title("🏨 Hotel Recommendation Engine")
        st.markdown("Get personalized hotel recommendations based on your travel history.")
        st.divider()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Select User")
            user_options = users.apply(
                lambda r: f"{r['code']} — {r['name']} ({r['company']})", axis=1
            ).tolist()
            selected = st.selectbox("Choose a user:", user_options)
            user_code = int(selected.split("—")[0].strip())

            method = st.radio("Recommendation Method:",
                ["🔀 Hybrid (Best)",
                 "📍 Content-Based",
                 "👥 Collaborative"]
            )

            n_recs = st.slider("Number of recommendations:", 3, 9, 5)
            recommend_btn = st.button("🚀 Get Recommendations", type="primary")

        with col2:
            if recommend_btn:
                user_info = users[users['code'] == user_code].iloc[0]

                st.subheader(f"👤 {user_info['name']}")
                m1, m2, m3 = st.columns(3)
                m1.metric("Company", user_info['company'])
                m2.metric("Gender", user_info['gender'])
                m3.metric("Age", user_info['age'])

                past = hotels[hotels['userCode'] == user_code]
                st.markdown(f"**Past hotel stays:** {len(past)}")
                st.divider()

                st.subheader("🌟 Your Recommendations")
                with st.spinner("Finding best hotels for you..."):
                    if method == "🔀 Hybrid (Best)":
                        recs = hybrid_recommend(
                            user_code, hotels, hotel_sim,
                            collab_mat, user_hotel, n=n_recs
                        )
                    elif method == "📍 Content-Based":
                        recs = content_based_recommend(
                            user_code, hotels, hotel_sim, n=n_recs
                        )
                    else:
                        recs = collaborative_recommend(
                            user_code, collab_mat,
                            user_hotel, hotels, n=n_recs
                        )

                st.dataframe(recs, use_container_width=True)

                # Price chart
                fig, ax = plt.subplots(figsize=(8, 4))
                price_col = 'Avg Price ($)' if 'Avg Price ($)' in recs.columns else 'Avg Price'
                ax.barh(recs['Hotel'], recs[price_col],
                        color='#7C3AED', edgecolor='black', alpha=0.85)
                ax.set_xlabel('Avg Price per Night ($)')
                ax.set_title('Recommended Hotels - Price Comparison')
                st.pyplot(fig)
                plt.close()

    
    # Section 7 - Flight Price Predictor Page

    # PAGE 3 — FLIGHT PRICE PREDICTOR

    elif page == "💰 Flight Price Predictor":
        st.title("💰 Flight Price Predictor")
        st.markdown("Predict flight prices using our Random Forest model (R² = 0.9067)")
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✈️ Flight Details")
            distance = st.number_input("Distance (km):",
                            min_value=1.0, max_value=5000.0, value=676.53)
            flight_type = st.selectbox("Flight Type:",
                            ["economic", "premium", "firstClass"])
            agency = st.selectbox("Agency:",
                            ["CloudFy", "Rainbow", "FlyingDrops"])
            month = st.slider("Month:", 1, 12, 10)
            dow = st.slider("Day of Week (0=Mon, 6=Sun):", 0, 6, 2)
            predict_btn = st.button("💰 Predict Price", type="primary")

        with col2:
            st.subheader("📊 Prediction Result")
            if predict_btn:
                with st.spinner("Predicting..."):
                    price = predict_flight_price(
                        distance, flight_type, agency, month, dow,
                        flight_model, flight_columns
                    )

                st.success(f"### Predicted Price: **${price:,.2f}**")

                # Context
                avg_by_type = flights.groupby('flightType')['price'].mean()
                m1, m2 = st.columns(2)
                m1.metric(
                    "Avg for this class",
                    f"${avg_by_type.get(flight_type, 0):.2f}",
                    delta=f"${price - avg_by_type.get(flight_type, 0):.2f}"
                )
                m2.metric("Model R² Score", "0.9067")

                st.divider()
                st.markdown("**Input Summary**")
                st.json({
                    "distance" : distance,
                    "flightType" : flight_type,
                    "agency" : agency,
                    "month" : month,
                    "day_of_week" : dow,
                    "predicted_price" : price
                })


    # Section 8 - Data Insights Page + Run App

    # PAGE 4 - DATA INSIGHTS

    elif page == "📊 Data Insights":
        st.title("📊 Data Insights")
        st.divider()

        tab1, tab2, tab3 = st.tabs(["✈️ Flights", "🏨 Hotels", "👥 Users"])

        with tab1:
            st.subheader("Flight Price Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Price", f"${flights['price'].mean():.2f}")
            col2.metric("Min Price", f"${flights['price'].min():.2f}")
            col3.metric("Max Price", f"${flights['price'].max():.2f}")

            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            flights['price'].hist(bins=50, ax=axes[0],
                color='#7C3AED', edgecolor='black', alpha=0.85)
            axes[0].set_title('Flight Price Distribution')
            axes[0].set_xlabel('Price ($)')

            flights.groupby('agency')['price'].mean().plot(
                kind='bar', ax=axes[1],
                color='#06B6D4', edgecolor='black', alpha=0.85
            )
            axes[1].set_title('Avg Price by Agency')
            axes[1].tick_params(axis='x', rotation=0)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with tab2:
            st.subheader("Hotel Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Price/Night", f"${hotels['price'].mean():.2f}")
            col2.metric("Avg Stay", f"{hotels['days'].mean():.1f} days")
            col3.metric("Avg Total Spend", f"${hotels['total'].mean():.2f}")

            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            hotels['place'].value_counts().plot(
                kind='barh', ax=axes[0],
                color='#10B981', edgecolor='black', alpha=0.85
            )
            axes[0].set_title('Bookings by Place')

            hotels['days'].value_counts().sort_index().plot(
                kind='bar', ax=axes[1],
                color='#7C3AED', edgecolor='black', alpha=0.85
            )
            axes[1].set_title('Stay Duration Distribution')
            axes[1].tick_params(axis='x', rotation=0)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with tab3:
            st.subheader("User Analysis")
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots(figsize=(6, 4))
                users['age'].hist(bins=20, ax=ax,
                    color='#06B6D4', edgecolor='black', alpha=0.85)
                ax.set_title('User Age Distribution')
                ax.set_xlabel('Age')
                st.pyplot(fig)
                plt.close()

            with col2:
                fig, ax = plt.subplots(figsize=(6, 4))
                users['company'].value_counts().plot(
                    kind='pie', ax=ax, autopct='%1.1f%%',
                    colors=['#7C3AED', '#06B6D4', '#10B981',
                            '#F59E0B', '#EF4444']
                )
                ax.set_ylabel('')
                ax.set_title('Users by Company')
                st.pyplot(fig)
                plt.close()


# Entry Point
if __name__ == '__main__':
    main()