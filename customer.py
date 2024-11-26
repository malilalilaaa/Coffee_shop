from typing import Any

import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import datetime
import pandas as pd
import seaborn as sns

def top_product_categories(df):
    top_products = df.groupby(['store_location', 'product_detail', 'unit_price'])['transaction_qty'].sum().reset_index()
    top_products_by_location = top_products.loc[top_products.groupby('store_location')['transaction_qty'].idxmax()]
    top_products_by_location = top_products_by_location.sort_values('transaction_qty', ascending=False)

    plt.figure(figsize=(16, 10))
    sns.barplot(data=top_products_by_location, x='store_location', y='transaction_qty', hue='product_detail')
    plt.title('Highest Selling Products by Location')
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(plt)

def transaction_in_hour_basis(store_df):
    transaction_count_by_hour_location = store_df.groupby(['store_location', 'hour'])['transaction_id'].count().unstack(
        fill_value=0)
    num_bars = transaction_count_by_hour_location.shape[0] * transaction_count_by_hour_location.shape[1]
    colors = ['skyblue', 'lightgreen', 'salmon', 'black', 'orange', 'yellow', 'lightpink', 'purple', 'darkcyan',
              'mediumseagreen', 'gold', 'lightsteelblue', 'tomato', 'navy', 'mediumorchid']
    if len(colors) < num_bars:
        colors = (colors * ((num_bars // len(colors)) + 1))[:num_bars]
    st.title("Transactions by Hour of the Day for Each Location")
    fig, ax = plt.subplots(figsize=(10, 6))
    transaction_count_by_hour_location.plot(kind='bar', ax=ax, color=colors)
    ax.set_title('Transactions by Hour of the Day for Each Location')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Number of Transactions')
    ax.set_xticklabels(transaction_count_by_hour_location.index, rotation=0)
    ax.legend(title='Store Location')
    st.pyplot(fig)


def transaction_in_day_basis(store_df):
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])
    store_df['transaction_amount'] = store_df['transaction_qty'] * store_df['unit_price']
    store_df['transaction_day'] = store_df['transaction_date'].dt.floor('D')
    average_transaction_per_day_location = store_df.groupby(['transaction_day', 'store_location'])['transaction_amount'].mean().reset_index()
    st.title("Average Transaction Amount per Day by Store Location")
    st.write("This chart shows the daily average transaction amount for each store location.")
    fig, ax = plt.subplots(figsize=(12, 6))
    for location in average_transaction_per_day_location['store_location'].unique():
        location_data = average_transaction_per_day_location[
            average_transaction_per_day_location['store_location'] == location]
        ax.plot(location_data['transaction_day'], location_data['transaction_amount'], label=location)
    ax.set_title('Average Transaction Amount per Day by Store Location')
    ax.set_xlabel('Transaction Day')
    ax.set_ylabel('Average Transaction Amount')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines[['top', 'right']].set_visible(False)
    plt.xticks(rotation=45)
    plt.legend(title='Store Location')
    plt.tight_layout()
    st.pyplot(fig)

def transaction_in_month_basis(store_df):
    store_df['revenue'] = store_df['transaction_qty'] * store_df['unit_price']
    daily_revenue = store_df.groupby('transaction_date')['revenue'].sum().reset_index()
    store_df['month'] = store_df['transaction_date'].dt.month
    monthly_stats = store_df.groupby('month').agg({
        'revenue': ['sum', 'mean', 'std']
    }).round(2)
    st.header("Monthly Revenue Statistics")
    st.write(monthly_stats)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(monthly_stats.index, monthly_stats[('revenue', 'sum')], color='skyblue')
    ax.set_title('Monthly Revenue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Revenue ($)')
    ax.set_xticks(monthly_stats.index)
    plt.tight_layout()
    st.pyplot(fig)

def average_price_basis(store_df):

    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])

    average_price = store_df['unit_price'].mean()

    store_locations = store_df['store_location'].unique()

    st.write(f"### Overall Average Unit Price: ${average_price:.2f}")

    for location in store_locations:
        location_data = store_df[store_df['store_location'] == location]

        lower_than_average = location_data[location_data['unit_price'] < average_price]
        higher_than_average = location_data[location_data['unit_price'] >= average_price]

        lower_sales = lower_than_average['transaction_qty'].sum()
        higher_sales = higher_than_average['transaction_qty'].sum()

        categories = ['Lower than Average Price', 'Higher than Average Price']
        sales = [lower_sales, higher_sales]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(categories, sales, color=['blue', 'orange'])
        ax.set_title(f'Sales Comparison: Lower vs Higher than Average Price in {location}')
        ax.set_ylabel('Total Sales Quantity')
        ax.set_xlabel('Price Category')

        st.pyplot(fig)

        st.write(f"#### Store Location: {location}")
        st.write(f"Average Unit Price: ${average_price:.2f}")
        st.write(f"Total Sales for Lower than Average Price: {lower_sales}")
        st.write(f"Total Sales for Higher than Average Price: {higher_sales}")
        st.write("---")

def average_category_transaction(store_df):

    end_date = store_df['transaction_date'].max()
    start_date = end_date - pd.DateOffset(months=6)
    filtered_data = store_df[(store_df['transaction_date'] >= start_date) & (store_df['transaction_date'] <= end_date)]

    average_daily_sales = filtered_data.groupby(['store_location', 'product_category'])['transaction_qty'].mean().reset_index()

    max_sales = average_daily_sales.loc[average_daily_sales.groupby('store_location')['transaction_qty'].idxmax()]
    min_sales = average_daily_sales.loc[average_daily_sales.groupby('store_location')['transaction_qty'].idxmin()]

    result = pd.merge(max_sales, min_sales, on='store_location', suffixes=('_max', '_min'))

    st.write("Highest and Lowest Average Sales by Store Location", result)

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.4
    locations = range(len(result))

    ax.bar(
        [pos - bar_width / 2 for pos in locations],
        result['transaction_qty_max'],
        width=bar_width,
        color='skyblue',
        label='Highest Average Sales'
    )

    ax.bar(
        [pos + bar_width / 2 for pos in locations],
        result['transaction_qty_min'],
        width=bar_width,
        color='salmon',
        label='Lowest Average Sales'
    )

    ax.set_xticks(locations)
    ax.set_xticklabels(result['store_location'])
    ax.set_xlabel('Store Location')
    ax.set_ylabel('Average Sold Quantity')
    ax.set_title('Highest and Lowest Average Sold Quantity by Product Category for Each Location')
    plt.legend()

    st.pyplot(fig)

def category_basis_transaction(store_df):
    for col in store_df.columns:
        if 'date' in col.lower():
            store_df[col] = pd.to_datetime(store_df[col], errors='coerce')  # Handle conversion errors gracefully

    for category in store_df['product_category'].unique():
        category_data : Any = store_df[store_df['product_category'] == category]

        product_sales : Any = category_data.groupby('product_detail')['transaction_qty'].sum().sort_values(ascending=True)

        plt.figure(figsize=(12, max(6, len(product_sales) * 0.4)))  # Adjust height dynamically based on the number of products

        bars = plt.barh(product_sales.index, product_sales.values, color='skyblue')

        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height() / 2,
                     f'{int(width):,}',
                     ha='left', va='center', fontweight='bold')

        plt.title(f'Total Sales by Product - {category}')
        plt.xlabel('Total Quantity Sold')
        plt.ylabel('Product Name')

        plt.tight_layout()

        st.pyplot(plt)
        plt.clf()
def category_transaction(store_df):
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])

    end_date = store_df['transaction_date'].max()
    start_date = end_date - pd.DateOffset(months=6)
    filtered_data = store_df[(store_df['transaction_date'] >= start_date) & (store_df['transaction_date'] <= end_date)]

    category_sales = filtered_data.groupby(['store_location', 'product_category'])[
        'transaction_qty'].sum().unstack().fillna(0)

    fig, ax = plt.subplots(figsize=(12, 6))
    category_sales.plot(kind='bar', ax=ax, colormap='tab20')  # Use a colormap for distinct category colors
    ax.set_title('Total Sales Quantity of Each Product Category in Each Location (Last 6 Months)')
    ax.set_xlabel('Store Location')
    ax.set_ylabel('Total Sales Quantity')
    plt.xticks(rotation=45)
    plt.legend(title='Product Category', bbox_to_anchor=(1.05, 1), loc='upper left')  # Place legend outside the plot
    plt.tight_layout()

    st.pyplot(fig)

def revenue_day(store_df):
    store_df['revenue'] = store_df['transaction_qty'] * store_df['unit_price']

    store_df['hour'] = pd.to_datetime(store_df['transaction_time']).dt.hour
    store_df['time_of_day'] = pd.cut(
        store_df['hour'],
        bins=[0, 11, 16, 23],
        labels=['Morning', 'Afternoon', 'Evening']
    )
    lower_manhattan_revenue = store_df[store_df['store_location'] == "Lower Manhattan"].groupby('time_of_day')[
        'revenue'].sum()
    st.write("Lower Manhattan Revenue by Time of Day:")
    st.write(lower_manhattan_revenue)

    sns.set(style='whitegrid')

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=lower_manhattan_revenue.index, y=lower_manhattan_revenue.values, palette='viridis', ax=ax)

    ax.set_title('Lower Manhattan Revenue by Time of Day')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Revenue ($)')

    st.pyplot(fig)


def lowest_sale_product(store_df):
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])

    product_sales = store_df.groupby('product_detail').agg({'transaction_qty': 'sum'}).sort_values('transaction_qty')
    lowest_sales_product = product_sales.index[0]
    lowest_sales_data = store_df[store_df['product_detail'] == lowest_sales_product]

    lowest_sales_time_location = lowest_sales_data.groupby(['store_location', 'transaction_time']).agg(
        {'transaction_qty': 'sum'}).reset_index()
    most_sold_time_by_location = lowest_sales_time_location.loc[
        lowest_sales_time_location.groupby('store_location')['transaction_qty'].idxmax()]

    st.write("### Product with the Lowest Sales:", lowest_sales_product)
    st.write("Most Sold Time by Location for the Product with the Lowest Sales:")
    st.write(most_sold_time_by_location)

    lowest_sales_data['hour'] = pd.to_datetime(lowest_sales_data['transaction_time']).dt.hour

    st.write(f"### Hourly Sales Distribution of {lowest_sales_product} by Location")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=lowest_sales_data, x='hour', y='transaction_qty', hue='store_location', ci=None)
    plt.title(f'Hourly Sales Distribution of {lowest_sales_product} by Location')
    plt.xlabel('Hour of Day')
    plt.ylabel('Quantity Sold')
    plt.ylim(0, 2)  # Set the y-axis range from 1 to 10 to fit your specified range
    plt.legend(title='Location')
    plt.tight_layout()

    st.pyplot(plt)

    st.write("### Total Quantity Sold by Location")
    st.write(lowest_sales_data.groupby('store_location')['transaction_qty'].sum())


def display_barista_revenue(store_df):
    barista_revenue = store_df[store_df['product_detail'] == 'Ouro Brasileiro shot'].groupby("store_location").agg({
        'transaction_qty': 'sum',
        'unit_price': 'first'  
    }).assign(total_revenue=lambda x: x['transaction_qty'] * x['unit_price'])

    barista_revenue = barista_revenue.sort_values('total_revenue', ascending=False)

    st.write("### Total Revenue from Ouro Brasileiro shot by Location")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=barista_revenue.reset_index(), x='store_location', y='total_revenue')
    plt.xticks(rotation=45, ha='right')
    plt.title('Total Revenue from Ouro Brasileiro shot by Location')
    plt.ylabel('Total Revenue ($)')
    plt.tight_layout()

    st.pyplot(plt)
    st.write("### Detailed Revenue Breakdown")
    st.write(barista_revenue[['transaction_qty', 'unit_price', 'total_revenue']])
