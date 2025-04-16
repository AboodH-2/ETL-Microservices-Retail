"""
Run ETL Pipeline and View Results

This script runs the ETL pipeline and then displays the results from the MySQL database.
"""

import os
import sys
import mysql.connector
from etl_pipeline import run_etl_pipeline

def run_pipeline():
    """Run the ETL pipeline"""
    print("\n" + "="*50)
    print("RUNNING ETL PIPELINE")
    print("="*50)
    
    # CSV file path
    csv_file_path = "in_store_sales.csv"
    
    # Run the ETL pipeline
    run_etl_pipeline(csv_file_path)
    
    print("\n" + "="*50)
    print("ETL PIPELINE COMPLETED")
    print("="*50)

def view_results():
    """Display the results from the MySQL database"""
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            database="retail_dw",
            user="mysql",
            password="mysql"
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute("SELECT * FROM aggregated_sales")
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Print the results
        print("\n" + "="*50)
        print("RESULTS FROM MYSQL DATABASE")
        print("="*50)
        print(f"{'Product ID':<10} | {'Total Quantity':<15} | {'Total Sale Amount':<18}")
        print("-" * 50)
        
        # Calculate totals
        total_quantity = 0
        total_amount = 0
        
        # Print each row
        for row in results:
            print(f"{row[0]:<10} | {row[1]:<15} | ${row[2]:<17.2f}")
            total_quantity += row[1]
            total_amount += row[2]
        
        print("-" * 50)
        print(f"TOTAL:      | {total_quantity:<15} | ${total_amount:<17.2f}")
        print("="*50)
        print(f"Total products: {len(results)}")
        print("="*50)
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"Error accessing MySQL: {e}")
        
def main():
    """Main function to run the pipeline and view results"""
    print("\n" + "="*50)
    print("ETL PIPELINE EXECUTION")
    print("="*50)
    print("This script will:")
    print("1. Run the ETL pipeline to extract, transform, and load data")
    print("2. Display the results from the MySQL database")
    print("="*50)
    
    # Run the pipeline
    run_pipeline()
    
    # View the results
    view_results()
    
    print("\nProcess completed successfully!")

if __name__ == "__main__":
    main() 