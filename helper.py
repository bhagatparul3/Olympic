import numpy as np
import pandas as pd

def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall':
        temp_df = medal_df[medal_df['region'] == country]
    elif country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[
            (medal_df['Year'] == int(year)) & (medal_df['region'] == country)
        ]

    x = temp_df.groupby('Year' if country != 'Overall' else 'region').sum(
    )[['Gold', 'Silver', 'Bronze']].reset_index()
    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    for col in ['Gold', 'Silver', 'Bronze', 'total']:
        x[col] = x[col].astype(int)

    return x


def country_year_list(df):
    years = sorted(df['Year'].unique().tolist())
    years.insert(0, 'Overall')

    countries = sorted(df['region'].dropna().unique().tolist())
    countries.insert(0, 'Overall')

    return years, countries


def data_over_time(df, col):
    nations_over_time = (
        df.drop_duplicates(['Year', col])
        .groupby('Year')
        .size()
        .reset_index(name=col)
    )
    nations_over_time.rename(columns={'Year': 'Edition'}, inplace=True)
    return nations_over_time


def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal']).copy()
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    athlete_counts = temp_df['Name'].value_counts().reset_index(name='Medals')
    athlete_counts.rename(columns={'index': 'Name'}, inplace=True)

    merged_df = athlete_counts.merge(
        df[['Name', 'Sport', 'region']], on='Name', how='left'
    ).drop_duplicates('Name')

    return merged_df[['Name', 'Medals', 'Sport', 'region']].head(15)


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal']).drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    if country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]
    
    if temp_df.empty:
        return pd.DataFrame()

    final_df = temp_df.groupby('Year').count()['Medal'].reset_index()
    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal']).drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    if country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]
    
    if temp_df.empty:
        return pd.DataFrame()

    pt = temp_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    if country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]
    
    if temp_df.empty:
        return pd.DataFrame()

    athlete_counts = temp_df['Name'].value_counts().reset_index(name='Medals')
    athlete_counts.rename(columns={'index': 'Name'}, inplace=True)

    merged_df = athlete_counts.merge(
        df[['Name', 'Sport']], on='Name', how='left'
    ).drop_duplicates('Name')

    return merged_df[['Name', 'Medals', 'Sport']].head(10)


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region']).copy()
    athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')
    if sport != 'Overall':
        return athlete_df[athlete_df['Sport'] == sport]
    return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region']).copy()
    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='outer', suffixes=('_Male', '_Female')).fillna(0)

    final['Male'] = final['Name_Male'].astype(int)
    final['Female'] = final['Name_Female'].astype(int)

    return final[['Year', 'Male', 'Female']]
