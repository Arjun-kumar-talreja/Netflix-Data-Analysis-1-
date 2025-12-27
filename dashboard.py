import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# --- 1. Page Configuration ---
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

st.title("🎬 Netflix Data Analysis Dashboard")
st.markdown("This dashboard analyzes Netflix content trends, release patterns, and genres to help Executives make production decisions.")

# --- 2. Data Loading & Cleaning Function ---
@st.cache_data # Yeh data ko memory mein rakhta hai taake baar baar load na ho
def load_data():
    df = pd.read_csv('netflix_titles.csv') # File ka naam check kar lein
    
    # Cleaning Steps (Jo humne pehle kiye)
    df['director'] = df['director'].fillna('No Director')
    df['cast'] = df['cast'].fillna('No Cast')
    df['country'] = df['country'].fillna('Unknown Country')
    df.dropna(subset=['date_added', 'rating', 'duration'], inplace=True)
    
    # Date Format
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip())
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month_name()
    
    return df

# Data Load karna
try:
    df = load_data()
    st.sidebar.success("Data Loaded Successfully!")
except FileNotFoundError:
    st.error("Error: 'netflix_titles.csv' file nahi mili. Please file usi folder mein rakhein jahan app.py hai.")
    st.stop()

# --- 3. Sidebar Filters ---
st.sidebar.header("🔍 Filters")
selected_type = st.sidebar.radio("Select Content Type", ["All", "Movie", "TV Show"])

if selected_type != "All":
    filtered_df = df[df['type'] == selected_type]
else:
    filtered_df = df

# --- 4. KPI Metrics (Top Row) ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", filtered_df.shape[0])
col2.metric("Total Movies", df[df['type'] == 'Movie'].shape[0])
col3.metric("Total TV Shows", df[df['type'] == 'TV Show'].shape[0])

st.markdown("---") # Divider Line

# --- 5. Tabs Layout ---
tab1, tab2, tab3 = st.tabs(["📈 Growth Trends", "🔥 Best Time to Release", "🌍 Market Insights"])

# === TAB 1: MOVIES vs TV SHOWS ===
with tab1:
    st.subheader("Yearly Content Growth")
    
    # Data grouping
    trend_data = df.groupby(['year_added', 'type']).size().reset_index(name='count')
    
    # Plotly Interactive Chart (Streamlit mein Plotly acha chalta hai)
    fig_trend = px.line(trend_data, x='year_added', y='count', color='type',
                        title='Movies vs TV Shows Added Per Year',
                        color_discrete_map={'Movie': 'red', 'TV Show': 'black'})
    st.plotly_chart(fig_trend, use_container_width=True)

# === TAB 2: THE HEATMAP (The Trick) ===
with tab2:
    st.subheader("Heatmap: Content Release Density")
    st.write("Darker red areas indicate months with the most releases.")
    
    # Heatmap Data Preparation
    heatmap_data = df.groupby(['year_added', 'month_added']).size().reset_index(name='count')
    heatmap_matrix = heatmap_data.pivot(index='month_added', columns='year_added', values='count')
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    heatmap_matrix = heatmap_matrix.reindex(month_order)
    
    # Seaborn Heatmap in Streamlit
    fig_heat, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(heatmap_matrix, annot=True, fmt='.0f', cmap='Reds', linewidths=.5, ax=ax)
    st.pyplot(fig_heat)

# === TAB 3: INSIGHTS (Genre, Country, Rating) ===
with tab3:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Top 10 Genres")
        filtered_genres = df.set_index('title').listed_in.str.split(', ', expand=True).stack().reset_index(level=1, drop=True)
        top_genres = filtered_genres.value_counts().head(10)
        
        fig_genre, ax = plt.subplots()
        sns.barplot(x=top_genres.values, y=top_genres.index, palette='Reds_r', ax=ax)
        st.pyplot(fig_genre)
        
    with col_b:
        st.subheader("Top Producing Countries")
        top_countries = df['country'].value_counts().head(10)
        
        fig_country, ax = plt.subplots()
        sns.barplot(x=top_countries.values, y=top_countries.index, palette='viridis', ax=ax)
        st.pyplot(fig_country)

    st.markdown("---")
    st.subheader("Target Audience (Ratings)")
    fig_rating, ax = plt.subplots(figsize=(10, 4))
    sns.countplot(data=df, x='rating', order=df['rating'].value_counts().index, palette='coolwarm', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig_rating)

# --- 6. Footer ---
st.sidebar.markdown("---")
st.sidebar.info("Created by: Expert Data Scientist (You) 🚀")