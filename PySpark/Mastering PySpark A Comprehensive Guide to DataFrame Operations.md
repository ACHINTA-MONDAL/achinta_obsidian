---
created: 2024-08-19T01:12:03+05:30
modified: 2024-08-19T01:12:56+05:30
---
# **Introduction:**

DataFrames in PySpark are designed to handle and process large volumes of structured data, providing a data structure similar to the one you’d find in pandas or SQL tables. This data structure makes PySpark an excellent tool for data scientists and engineers to perform complex data analysis and processing tasks.

This article is a one-stop guide to numerous DataFrame operations in PySpark. It touches on important operations like data loading, data manipulation, filtering, aggregation, and joining, among others. Each part of this guide includes code examples along with comprehensive explanations, aimed at improving your understanding and implementation of these operations in your PySpark tasks.

We have set up an initial DataFrame, as demonstrated below.

from pyspark.sql import SparkSession  
from pyspark.sql.types import StructType, StructField, StringType, IntegerType  
  
# Create a SparkSession  
spark = SparkSession.builder \  
    .appName('Dataframe_Operations') \  
    .getOrCreate()  
  
# Define the schema for our data  
schema = StructType([  
    StructField('Brand', StringType(), True),  
    StructField('Model', StringType(), True),  
    StructField('Memory', StringType(), True),  
    StructField('Processor', StringType(), True),  
    StructField('Price', IntegerType(), True)  
])  
  
# Create a list of tuples representing data  
data = [  
    ('Brand1', 'Model1', '8GB', 'Intel i5', 7000),  
    ('Brand2', 'Model2', '16GB', 'Intel i7', 9000),  
    ('Brand3', 'Model3', '8GB', 'AMD Ryzen 5', 6500),  
    ('Brand4', 'Model4', '16GB', 'Intel i9', 12000),  
    ('Brand5', 'Model5', '32GB', 'AMD Ryzen 7', 15000),  
    ('Brand6', 'Model6', '16GB', 'Intel i7', 11000),  
    ('Brand7', 'Model7', '8GB', 'Intel i5', 8000),  
    ('Brand8', 'Model8', '16GB', 'Intel i7', 9500),  
    ('Brand9', 'Model9', '32GB', 'AMD Ryzen 5', 13000),  
    ('Brand10', 'Model10', '16GB', 'Intel i7', 11500)  
]  
  
# Create DataFrame  
df = spark.createDataFrame(data, schema)  
  
# Show DataFrame  
df.show()  
  
# Print Schema  
df.printSchema()

![](https://miro.medium.com/v2/resize:fit:1112/1*zUX3vWlRq21a9UbD71XSMQ.png)

**Input Dataframe**

![](https://miro.medium.com/v2/resize:fit:1052/1*SrZz0CzuhvWoIXk-hhA0Qw.png)

**Schema Details of the input Dataframe**

1. **Select Specific Columns from an existing dataframe**

# Column Selection  
df_selected = df.select("Brand", "Processor", "Price")  
df_selected.show()

![](https://miro.medium.com/v2/resize:fit:752/1*YW2MLjYVyXo_IDYQkoQ1Sw.png)

**Dataframe After Selecting Specific Columns**

**2**. **Filtering Rows**

# Filtering rows in the DataFrame df where the value in the 'Price' column is greater than 10000  
df_filtered = df.filter(df['Price'] > 10000)  
df_filtered.show()

![](https://miro.medium.com/v2/resize:fit:1128/1*V96vD5sj4MBlCSpRGsXUig.png)

**Filtered Dataframe**

**3. Adding a new Column in existing dataframe**

from pyspark.sql.functions import col  
  
# Adding a new Column 'Discounted_Price'  
df_modified = df.withColumn('Discounted_Price', col('Price')*0.9)  
df_modified.show()

![](https://miro.medium.com/v2/resize:fit:1400/1*OJ3BuDJb-FIFqWFRrIZS2g.png)

**4. Add a constant column**

from pyspark.sql.functions import lit  
  
# Add a constant column 'Warranty_Years' with value '2'  
df_constant_column = df.withColumn('Warranty_Years', lit(2))  
df_constant_column.show()

![](https://miro.medium.com/v2/resize:fit:1400/1*sVErb_vT1y1qq2hPv9ZY4Q.png)

**After adding a constant Column**

**5. Renaming a Column**

# Renaming a Column 'Discounted_Price' to 'Sale_Price'  
df_renamed = df_modified.withColumnRenamed('Discounted_Price', 'Sale_Price')  
df_renamed.show()

![](https://miro.medium.com/v2/resize:fit:1388/1*sOz1WLzmShKwm3vSCn0ibw.png)

**6. Data Type of a Column**

# Get data type of 'Price' column  
price_type = [dtype for name, dtype in df.dtypes if name == 'Price'][0]  
print(f"The data type of 'Price' column is {price_type}.")

![](https://miro.medium.com/v2/resize:fit:1016/1*m_5smoXgXy8rjX_gBH6YAw.png)

**7. Convert Data Types**

# Convert 'Price' column to double  
df_converted = df.withColumn("Price", df["Price"].cast("double"))  
  
# Get data type of modified 'Price' column in df_converted dataframe  
price_type = [dtype for name, dtype in df_converted.dtypes if name == 'Price'][0]  
print(f"The data type of 'Price' column is {price_type}.")

![](https://miro.medium.com/v2/resize:fit:1212/1*AXC5gXOm-l6gw__12Zeeag.png)

**8. Deriving a new column from existing columns**

from pyspark.sql.functions import col  
from pyspark.sql.functions import lit, concat  
  
# Concatenate 'Brand' and 'Model' columns into a new column "Full_Name"  
df_concate = df.withColumn('Full_Name', concat(col('Brand'), lit(' '), col('Model')))  
df_concate.show()

![](https://miro.medium.com/v2/resize:fit:1400/1*dYNpBosaBlAGngpC3r6qKA.png)

**9.** **Dropping a Column**

df_dropped = df_concate.drop('Full_Name')  
df_dropped.show()

![](https://miro.medium.com/v2/resize:fit:1120/1*aMftpiKLXGDcRSCOuMQv8A.png)

**10. Describe Data**

df.describe().show()

![](https://miro.medium.com/v2/resize:fit:1400/1*EVdbNfWll-oQg3GhAYVElA.png)

**11. Sorting rows**

# Sort rows by Price in descending order  
df_ordered_desc = df.orderBy(df['Price'].desc())  
df_ordered_desc.show()  
  
# Sort rows by Price in ascending order  
df_ordered_asc = df.orderBy(df['Price'].asc())  
df_ordered_asc.show()

![](https://miro.medium.com/v2/resize:fit:1104/1*u5w5HraQ5_k69KuqCeCXmg.png)

**Descending Order**

![](https://miro.medium.com/v2/resize:fit:1112/1*xUFEQiBPbpDzTog2_FLVZQ.png)

**Ascending Order**

**12. Grouping and Aggregating the data**

from pyspark.sql.functions import avg  
  
# Group by 'Brand' and calculate average 'Price'  
df_grouped = df.groupBy('Brand').agg(avg('Price').alias('Average_Price'))  
df_grouped.orderBy(df_grouped["Brand"].asc()).show()

![](https://miro.medium.com/v2/resize:fit:632/1*ls7vSXfX4Ffflpsp9sX38w.png)

**Aggregated Dataframe**

**13.** **Joining Dataframes**

- **Create another small DataFrame**

brands_data = [("Brand1", "USA"), ("Brand2", "China"), ("Brand3", "USA"), ("Brand4", "Japan"), ("Brand5", "Germany")]  
brands_schema = ["Brand", "Country"]  
brands_df = spark.createDataFrame(brands_data, brands_schema)  
brands_df.show()

![](https://miro.medium.com/v2/resize:fit:432/1*Li-_ynXx7Jrh4Uq0j9YRwg.png)

**Dataframe 2**

- **Join the DataFrames on ‘Brand’**

df_joined_inner = df.join(brands_df, on='Brand', how='inner')  
  
# Show DataFrame  
df_joined_inner.show()  
  
df_joined_left = df.join(brands_df, on='Brand', how='left')  
  
# Show DataFrame  
df_joined_left.show()

![](https://miro.medium.com/v2/resize:fit:1400/1*AcULGSYni9EEtdIbUOsCNQ.png)

**Joined Dataframe (Inner Join)**

![](https://miro.medium.com/v2/resize:fit:1316/1*xIbKDxpA3RGfMIVpXnseOA.png)

**Joined Dataframe (left Outer)**

**14.** **UDFs (User-Defined Functions)**

from pyspark.sql.functions import udf  
from pyspark.sql.types import IntegerType  
  
# Define your UDF function  
def double_price(price):  
    return price * 2  
  
# Register your UDF function with DoubleType output  
double_price_udf = udf(lambda price: double_price(price), IntegerType())  
  
# Assuming 'df' is your DataFrame and 'Price' is one of the columns in df  
df_udf = df.withColumn("Double_Price", double_price_udf(df["Price"]))  
  
# Display the DataFrame  
df_udf.show()

In this code, we first define a Python function `double_price(price)` that returns double the input price. We then register this function as a UDF named `double_price_udf` with an output type of `IntegerType()`. Finally, we use `withColumn` to apply the UDF to the 'Price' column of the DataFrame `df` and create a new column "Double_Price" with the doubled values. The updated DataFrame is then displayed with `df_udf.show()`.

![](https://miro.medium.com/v2/resize:fit:1400/1*sKM6CVEZIIoUq8O1yRnVFA.png)

# Handling Missing/Null Values:

In PySpark, handling missing or null values is an essential part of the data preprocessing stage. Missing or null values can often lead to inaccurate analyses and errors in your data processing pipeline.

PySpark provides several methods to deal with these missing or null values.

We have created a DataFrame to showcase the methods.

from pyspark.sql import SparkSession  
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, NullType  
  
  
# Create a SparkSession  
spark = SparkSession.builder \  
    .appName('Handling_Missing_Data') \  
    .getOrCreate()  
# Define data with some null values  
data = [(1, "John Doe", "Plan A", 12),  
        (2, "Jane Doe", "Plan B", 24),  
        (3, None, "Plan A", None),  
        (4, "Mark", None, 18),  
        (5, "Lucy", "Plan C", 24),  
        (6, "Tom", "Plan B", None),  
        (7, "Jerry", None, 12),  
        (8, None, "Plan C", 24),  
        (9, "Oscar", "Plan A", 18),  
        (10, "Olivia", None, None)]  
  
# Define the schema  
schema = StructType([  
    StructField("ID", IntegerType(), True),  
    StructField("Customer", StringType(), True),  
    StructField("Plan", StringType(), True),  
    StructField("Duration", IntegerType(), True)  
])  
  
# Create DataFrame  
telecom_df = spark.createDataFrame(data, schema)  
  
# Show DataFrame  
telecom_df.show()

![](https://miro.medium.com/v2/resize:fit:908/1*y_IyCrP7hz7FZ9hIvNi_bQ.png)

Telecom dataframe

1. **Drop rows with null values**

telecom_df_no_nulls = telecom_df.dropna()  
telecom_df_no_nulls.show()

![](https://miro.medium.com/v2/resize:fit:876/1*rUB5iisBEPiuYKWPZlmrNQ.png)

**2. Fill null with values**

# you can fill null values with a specific value, for example, 'unknown' for string columns and 0 for numeric columns  
telecom_df_filled = telecom_df.fillna({'Customer': 'unknown', 'Plan': 'unknown', 'Duration': 0})  
telecom_df_filled.show()

![](https://miro.medium.com/v2/resize:fit:920/1*7hSqapuvgbrVcFaI0WqU5w.png)

**3. Replace specific values in a DataFrame**

# we want to replace all occurrences of 'Unknown' in the 'Plan' column with 'Not Specified'  
telecom_df_replaced = telecom_df_filled.na.replace('unknown', 'Not Specified', subset=['Plan'])  
  
# Display the updated DataFrame  
telecom_df_replaced.show()

![](https://miro.medium.com/v2/resize:fit:1080/1*LBF32FbJMKclCbLyAq0MVg.png)

# Handling duplicate rows:

Managing duplicate rows is a common task when working with data in PySpark. Duplicate rows can skew your data analysis and lead to misleading results.

PySpark provides several methods for handling duplicates:

- **Create a dataframe with some duplicate rows**

# Define data with some duplicate rows  
emp_data = [("John", "Doe", 30),  
        ("Jane", "Doe", 25),  
        ("John", "Doe", 30),  
        ("Mark", "Smith", 40),  
        ("Jane", "Doe", 25),  
        ("Mark", "Smith", 40)]  
  
# Define the schema  
emp_schema = StructType([  
    StructField("FirstName", StringType(), True),  
    StructField("LastName", StringType(), True),  
    StructField("Age", IntegerType(), True)  
])  
  
# Create DataFrame  
emp_df = spark.createDataFrame(emp_data, emp_schema)  
  
# Show DataFrame  
emp_df.show()

![](https://miro.medium.com/v2/resize:fit:720/1*l_6nGu6tuR0mzb-OP1P5vA.png)

Employee Dataframe with duplicate rows

**1. Remove duplicates using distinct()**

emp_df.distinct().show()

![](https://miro.medium.com/v2/resize:fit:712/1*8pKGoJMM2kZvGUkZATPqGQ.png)

**2. Remove duplicates using dropDuplicates()**

emp_df.dropDuplicates().show()

![](https://miro.medium.com/v2/resize:fit:724/1*esyzgag_0n4k6pNmK7_3Fw.png)

# Conclusion:

PySpark provides an extensive selection of operations for manipulating and processing data in DataFrames. It allows for efficient handling of large-scale data, providing functionalities for data ingestion, manipulation, filtering, aggregation, joining and handling missing or null values.

We’ve also seen how PySpark allows for custom operations using User Defined Functions (UDFs). This makes PySpark a highly flexible for data analysis that can be customized to handle a wide variety of data processing tasks.