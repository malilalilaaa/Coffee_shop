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

    # Create the bar plot
    plt.figure(figsize=(16, 10))
    sns.barplot(data=top_products_by_location, x='store_location', y='transaction_qty', hue='product_detail')
    plt.title('Highest Selling Products by Location')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)

def transaction_in_hour_basis(store_df):
    transaction_count_by_hour_location = store_df.groupby(['store_location', 'hour'])['transaction_id'].count().unstack(
        fill_value=0)
    num_bars = transaction_count_by_hour_location.shape[0] * transaction_count_by_hour_location.shape[1]
    # Define a list of colors (make sure you have enough colors to cover all bars)
    colors = ['skyblue', 'lightgreen', 'salmon', 'black', 'orange', 'yellow', 'lightpink', 'purple', 'darkcyan',
              'mediumseagreen', 'gold', 'lightsteelblue', 'tomato', 'navy', 'mediumorchid']
    # If you have fewer colors than bars, you can repeat the list of colors to match the number of bars
    if len(colors) < num_bars:
        colors = (colors * ((num_bars // len(colors)) + 1))[:num_bars]
    # Set the Streamlit title
    st.title("Transactions by Hour of the Day for Each Location")
    # Plotting the result with time labels using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    transaction_count_by_hour_location.plot(kind='bar', ax=ax, color=colors)
    # Set plot labels and title
    ax.set_title('Transactions by Hour of the Day for Each Location')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Number of Transactions')
    ax.set_xticklabels(transaction_count_by_hour_location.index, rotation=0)
    ax.legend(title='Store Location')
    # Display the plot in Streamlit
    st.pyplot(fig)


def transaction_in_day_basis(store_df):
    # Load data into DataFrame (assuming it's already loaded as store_df)
    # store_df = pd.read_csv('Coffee_Shop_Sales.csv')  # Uncomment if loading from a file
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])
    # Calculate the transaction amount for each transaction
    store_df['transaction_amount'] = store_df['transaction_qty'] * store_df['unit_price']
    # Create a new column for the day of the transaction
    store_df['transaction_day'] = store_df['transaction_date'].dt.floor('D')
    # Group by 'transaction_day' and 'store_location' and calculate the average transaction amount per day for each store
    average_transaction_per_day_location = store_df.groupby(['transaction_day', 'store_location'])['transaction_amount'].mean().reset_index()
    # Set up Streamlit app layout and title
    st.title("Average Transaction Amount per Day by Store Location")
    st.write("This chart shows the daily average transaction amount for each store location.")
    # Plot the average transaction amount per day for each store location using matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))
    for location in average_transaction_per_day_location['store_location'].unique():
        location_data = average_transaction_per_day_location[
            average_transaction_per_day_location['store_location'] == location]
        ax.plot(location_data['transaction_day'], location_data['transaction_amount'], label=location)
    # Customize plot
    ax.set_title('Average Transaction Amount per Day by Store Location')
    ax.set_xlabel('Transaction Day')
    ax.set_ylabel('Average Transaction Amount')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines[['top', 'right']].set_visible(False)
    plt.xticks(rotation=45)
    plt.legend(title='Store Location')
    plt.tight_layout()
    # Display plot in Streamlit
    st.pyplot(fig)

def transaction_in_month_basis(store_df):
    # Calculate revenue
    store_df['revenue'] = store_df['transaction_qty'] * store_df['unit_price']
    # Calculate daily revenue
    daily_revenue = store_df.groupby('transaction_date')['revenue'].sum().reset_index()
    # Extract the month and calculate monthly statistics
    store_df['month'] = store_df['transaction_date'].dt.month
    monthly_stats = store_df.groupby('month').agg({
        'revenue': ['sum', 'mean', 'std']
    }).round(2)
    # Display monthly statistics in Streamlit
    st.header("Monthly Revenue Statistics")
    st.write(monthly_stats)
    # Plotting Monthly Revenue
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(monthly_stats.index, monthly_stats[('revenue', 'sum')], color='skyblue')
    ax.set_title('Monthly Revenue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Revenue ($)')
    ax.set_xticks(monthly_stats.index)
    plt.tight_layout()
    # Display the plot in Streamlit
    st.pyplot(fig)

def average_price_basis(store_df):

    # Assuming store_df is already loaded with transaction data
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])

    # Calculate the overall average price across all locations
    average_price = store_df['unit_price'].mean()

    # Get unique store locations
    store_locations = store_df['store_location'].unique()

    # Display average price
    st.write(f"### Overall Average Unit Price: ${average_price:.2f}")

    # Loop over each store location to create a bar plot
    for location in store_locations:
        # Filter data for the specific location
        location_data = store_df[store_df['store_location'] == location]

        # Separate data based on price relative to the average price
        lower_than_average = location_data[location_data['unit_price'] < average_price]
        higher_than_average = location_data[location_data['unit_price'] >= average_price]

        # Calculate total sales quantity for each category
        lower_sales = lower_than_average['transaction_qty'].sum()
        higher_sales = higher_than_average['transaction_qty'].sum()

        # Prepare data for plotting
        categories = ['Lower than Average Price', 'Higher than Average Price']
        sales = [lower_sales, higher_sales]

        # Plotting
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(categories, sales, color=['blue', 'orange'])
        ax.set_title(f'Sales Comparison: Lower vs Higher than Average Price in {location}')
        ax.set_ylabel('Total Sales Quantity')
        ax.set_xlabel('Price Category')

        # Display plot in Streamlit
        st.pyplot(fig)

        # Display details for each location in Streamlit
        st.write(f"#### Store Location: {location}")
        st.write(f"Average Unit Price: ${average_price:.2f}")
        st.write(f"Total Sales for Lower than Average Price: {lower_sales}")
        st.write(f"Total Sales for Higher than Average Price: {higher_sales}")
        st.write("---")

def average_category_transaction(store_df):

    # Filter data for the last 6 months
    end_date = store_df['transaction_date'].max()
    start_date = end_date - pd.DateOffset(months=6)
    filtered_data = store_df[(store_df['transaction_date'] >= start_date) & (store_df['transaction_date'] <= end_date)]

    # Calculate average daily sales
    average_daily_sales = filtered_data.groupby(['store_location', 'product_category'])['transaction_qty'].mean().reset_index()

    # Get the maximum and minimum sales for each store
    max_sales = average_daily_sales.loc[average_daily_sales.groupby('store_location')['transaction_qty'].idxmax()]
    min_sales = average_daily_sales.loc[average_daily_sales.groupby('store_location')['transaction_qty'].idxmin()]

    # Merge the max and min sales data
    result = pd.merge(max_sales, min_sales, on='store_location', suffixes=('_max', '_min'))

    # Display the result table in Streamlit
    st.write("Highest and Lowest Average Sales by Store Location", result)

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.4
    locations = range(len(result))

    # Plot the highest average sales
    ax.bar(
        [pos - bar_width / 2 for pos in locations],
        result['transaction_qty_max'],
        width=bar_width,
        color='skyblue',
        label='Highest Average Sales'
    )

    # Plot the lowest average sales
    ax.bar(
        [pos + bar_width / 2 for pos in locations],
        result['transaction_qty_min'],
        width=bar_width,
        color='salmon',
        label='Lowest Average Sales'
    )

    # Set labels and title
    ax.set_xticks(locations)
    ax.set_xticklabels(result['store_location'])
    ax.set_xlabel('Store Location')
    ax.set_ylabel('Average Sold Quantity')
    ax.set_title('Highest and Lowest Average Sold Quantity by Product Category for Each Location')
    plt.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)

def category_basis_transaction(store_df):
    # Automatically convert any date-related columns to datetime format
    for col in store_df.columns:
        if 'date' in col.lower():
            store_df[col] = pd.to_datetime(store_df[col], errors='coerce')  # Handle conversion errors gracefully

    # Assuming store_df is your DataFrame containing product sales data
    for category in store_df['product_category'].unique():
        # Filter data for this category
        category_data : Any = store_df[store_df['product_category'] == category]

        # Calculate total sales for each product in this category
        product_sales : Any = category_data.groupby('product_detail')['transaction_qty'].sum().sort_values(ascending=True)

        # Create the plot
        plt.figure(figsize=(12, max(6, len(product_sales) * 0.4)))  # Adjust height dynamically based on the number of products

        # Create horizontal bar plot
        bars = plt.barh(product_sales.index, product_sales.values, color='skyblue')

        # Add value labels on the bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height() / 2,
                     f'{int(width):,}',
                     ha='left', va='center', fontweight='bold')

        plt.title(f'Total Sales by Product - {category}')
        plt.xlabel('Total Quantity Sold')
        plt.ylabel('Product Name')

        # Adjust layout
        plt.tight_layout()

        # Display the plot using Streamlit
        st.pyplot(plt)

        # Clear the figure to avoid overlap with the next plot
        plt.clf()
def category_transaction(store_df):
    # Convert 'transaction_date' to datetime format
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])

    # Filter data for the last 6 months
    end_date = store_df['transaction_date'].max()
    start_date = end_date - pd.DateOffset(months=6)
    filtered_data = store_df[(store_df['transaction_date'] >= start_date) & (store_df['transaction_date'] <= end_date)]

    # Calculate total sales quantity for each product category in each location
    category_sales = filtered_data.groupby(['store_location', 'product_category'])[
        'transaction_qty'].sum().unstack().fillna(0)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    category_sales.plot(kind='bar', ax=ax, colormap='tab20')  # Use a colormap for distinct category colors
    ax.set_title('Total Sales Quantity of Each Product Category in Each Location (Last 6 Months)')
    ax.set_xlabel('Store Location')
    ax.set_ylabel('Total Sales Quantity')
    plt.xticks(rotation=45)
    plt.legend(title='Product Category', bbox_to_anchor=(1.05, 1), loc='upper left')  # Place legend outside the plot
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)

def revenue_day(store_df):
    # Calculate revenue
    store_df['revenue'] = store_df['transaction_qty'] * store_df['unit_price']

    # Extract the hour and categorize time of day
    store_df['hour'] = pd.to_datetime(store_df['transaction_time']).dt.hour
    store_df['time_of_day'] = pd.cut(
        store_df['hour'],
        bins=[0, 11, 16, 23],
        labels=['Morning', 'Afternoon', 'Evening']
    )

    # Calculate revenue by time of day for Lower Manhattan
    lower_manhattan_revenue = store_df[store_df['store_location'] == "Lower Manhattan"].groupby('time_of_day')[
        'revenue'].sum()

    # Display the revenue data
    st.write("Lower Manhattan Revenue by Time of Day:")
    st.write(lower_manhattan_revenue)

    # Set up the plot style
    sns.set(style='whitegrid')

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=lower_manhattan_revenue.index, y=lower_manhattan_revenue.values, palette='viridis', ax=ax)

    # Customize plot appearance
    ax.set_title('Lower Manhattan Revenue by Time of Day')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Revenue ($)')

    # Display the plot in Streamlit
    st.pyplot(fig)


def lowest_sale_product(store_df):
    # Convert 'transaction_date' to datetime format
    store_df['transaction_date'] = pd.to_datetime(store_df['transaction_date'])

    # Get the product with the lowest sales
    product_sales = store_df.groupby('product_detail').agg({'transaction_qty': 'sum'}).sort_values('transaction_qty')
    lowest_sales_product = product_sales.index[0]
    lowest_sales_data = store_df[store_df['product_detail'] == lowest_sales_product]

    # Get the most sold time by location for the product with the lowest sales
    lowest_sales_time_location = lowest_sales_data.groupby(['store_location', 'transaction_time']).agg(
        {'transaction_qty': 'sum'}).reset_index()
    most_sold_time_by_location = lowest_sales_time_location.loc[
        lowest_sales_time_location.groupby('store_location')['transaction_qty'].idxmax()]

    # Display the product with the lowest sales and the most sold time by location
    st.write("### Product with the Lowest Sales:", lowest_sales_product)
    st.write("Most Sold Time by Location for the Product with the Lowest Sales:")
    st.write(most_sold_time_by_location)

    # Add hour column for plotting
    lowest_sales_data['hour'] = pd.to_datetime(lowest_sales_data['transaction_time']).dt.hour

    # Plot hourly sales distribution for the lowest sales product
    st.write(f"### Hourly Sales Distribution of {lowest_sales_product} by Location")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=lowest_sales_data, x='hour', y='transaction_qty', hue='store_location', ci=None)
    plt.title(f'Hourly Sales Distribution of {lowest_sales_product} by Location')
    plt.xlabel('Hour of Day')
    plt.ylabel('Quantity Sold')
    plt.ylim(0, 2)  # Set the y-axis range from 1 to 10 to fit your specified range
    plt.legend(title='Location')
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Display total quantity sold by location
    st.write("### Total Quantity Sold by Location")
    st.write(lowest_sales_data.groupby('store_location')['transaction_qty'].sum())


def display_barista_revenue(store_df):
    # Filter for 'Ouro Brasileiro shot' and calculate total revenue by store location
    barista_revenue = store_df[store_df['product_detail'] == 'Ouro Brasileiro shot'].groupby("store_location").agg({
        'transaction_qty': 'sum',
        'unit_price': 'first'  # Assuming unit_price is the same for each store_location-product_detail
    }).assign(total_revenue=lambda x: x['transaction_qty'] * x['unit_price'])

    # Sort by total revenue
    barista_revenue = barista_revenue.sort_values('total_revenue', ascending=False)

    # Plotting the total revenue by store location
    st.write("### Total Revenue from Ouro Brasileiro shot by Location")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=barista_revenue.reset_index(), x='store_location', y='total_revenue')
    plt.xticks(rotation=45, ha='right')
    plt.title('Total Revenue from Ouro Brasileiro shot by Location')
    plt.ylabel('Total Revenue ($)')
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Display the detailed revenue breakdown in Streamlit
    st.write("### Detailed Revenue Breakdown")
    st.write(barista_revenue[['transaction_qty', 'unit_price', 'total_revenue']])
