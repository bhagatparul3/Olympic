import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

# Load and preprocess the data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
df = preprocessor.preprocess(df, region_df)

# Sidebar
st.sidebar.title("Olympics Analysis")
st.sidebar.image('https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# Medal Tally Section
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Medal Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} Overall Performance")
    else:
        st.title(f"{selected_country} Performance in {selected_year} Olympics")
    st.table(medal_tally)

# Overall Analysis Section
if user_menu == 'Overall Analysis':
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x="Edition", y="region")
    st.title("Participating Nations Over the Years")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x="Edition", y="Event")
    st.title("Events Over the Years")
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x="Edition", y="Name")
    st.title("Athletes Over the Years")
    st.plotly_chart(fig)

    st.title("Number of Events Over Time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    heatmap_data = x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int)
    sns.heatmap(heatmap_data, annot=True, ax=ax)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox('Select a Sport', sport_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x)

# Country-wise Analysis Section
if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')

    country_list = ['Overall'] + sorted(df['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.title(f"{selected_country} Medal Tally Over the Years")
    if country_df.empty:
        st.warning(f"No medal data available for {selected_country}.")
    else:
        fig = px.line(country_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally Over the Years")
        st.plotly_chart(fig)

    st.title(f"{selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    if pt.empty:
        st.warning(f"No data available for {selected_country} in specific sports.")
    else:
        fig, ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(pt, annot=True, ax=ax)
        st.pyplot(fig)

    st.title(f"Top 10 Athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)
    if top10_df.empty:
        st.warning(f"No athlete data available for {selected_country}.")
    else:
        st.table(top10_df)

# Athlete-wise Analysis Section
if user_menu == 'Athlete-wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'], show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    st.title("Height vs Weight")
    sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(data=temp_df, x='Weight', y='Height', hue='Medal', style='Sex', s=60, ax=ax)
    st.pyplot(fig)

    st.title("Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(
        final,
        x="Year",
        y=["Male", "Female"],
        labels={"value": "Participants", "variable": "Gender"},
        title="Participation of Men vs Women Over the Years",
    )
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
