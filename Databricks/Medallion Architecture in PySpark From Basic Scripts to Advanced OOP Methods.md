

In this article, I will introduce you to the **Medallion Architecture** approach to organizing data processing tasks into manageable layers, from **basic scripting to advanced techniques**.

> The Medallion Architecture is a layered approach to data processing that organizes workflows into bronze, silver, and gold stages, facilitating the transformation of raw data into insightful, actionable information.
> 
> ==Bronze = unprocessed raw data.  
> Silver = Cleaned and conformed data.  
> Gold = Aggregated, business-level data.==

![](https://miro.medium.com/v2/resize:fit:1400/1*Gpny59pjTPL1WheeyvyNbQ.jpeg)

DallE generated image

The objective is to load sample data, clean it, and aggregate it.  
I’m using a sample dataset from Databricks. If you are using a non-Databricks environment, [use this link to download](https://raw.githubusercontent.com/gchandra10/filestorage/main/people_data.csv) the sample data.

**Approach 1: Basic Scripting approach**

  
```
## Load Delta into Dataframe  
bronze_df = spark.read.format("delta").load("dbfs:/databricks-datasets/learning-spark-v2/people/people-10m.delta")  
bronze_df.show(4,truncate=False)  
  
## Drop duplicate  
silver_df = bronze_df.dropDuplicates()  
silver_df.show(4,truncate=False)  
  
## Transform column names to lower case and replace any spaces with underscores  
for col in silver_df.columns:  
    silver_df = silver_df.withColumnRenamed(col, col.replace(" ", "_").lower())  
silver_df.show(4,truncate=False)  
  
  
from pyspark.sql.functions import col,date_format,mask  
  
## Format birthdate to yyyy-MM-dd format  
cols_changes={"birthdate":date_format(col("birthdate"),"yyyy-MM-dd"), "ssn":mask(col("ssn"))}  
silver_df1 = silver_df.withColumns(cols_changes)  
silver_df1.show(4,truncate=False)  
  
## Aggregate the data  
from pyspark.sql.functions import sum,count  
  
gold_df = (silver_df.groupBy("gender")  
                    .agg(  
                        sum("salary").alias("total_salary")  
                        ,count("id").alias("gender_count")  
                        )  
)  
  
## Display final output  
gold_df.show(4,truncate=False)  
  
## Write data to table  
gold_df.write.mode('overwrite').saveAsTable("gold_people")
```

The above script is okay to start but unsuitable for sustained reporting.

**Bronze Data**

![](https://miro.medium.com/v2/resize:fit:1400/1*KR2ZitslS6lTgBOJx8molw.png)

Bronze Data

**Silver Data**

![](https://miro.medium.com/v2/resize:fit:1400/1*a9KPWSZx048kJ9Fm1ce9Mw.png)

Silver Data

**Gold Data**

![](https://miro.medium.com/v2/resize:fit:1400/1*MUaDpQW8zr01a397hfd_xw.png)

Gold Data

**Approach 2: Object-Oriented Approach**

This approach has various advantages, such as

- Modularity.
- Reusability.
- Error Handling and Expansion.
- Automation friendly.
- Testing (Unit/Integration) friendly.

The script given below might look intimidating, but it's straightforward.

**Function setup_logging():** This is the standard code to capture the Log. You will reuse the same code 99% of the time with a change to the filename (PeopleDemoLogger).

**Class DataLoader:** This class loads data from a given URL. Writing it this way makes it easy for Unit Testing and expanding various Input sources under one module.

**Class DataProcessor**: Same as above, helps in Unit Testing and expansion.

This also has Doc Strings, which helps in Documentation.

```
### Rotating Log Handler to avoid log large log files.  
  
from pyspark.sql import SparkSession, DataFrame  
from pyspark.sql import functions as F  
from typing import Any  
  
import logging  
from logging.handlers import RotatingFileHandler  
  
def setup_logging():  
    """Configure logging with rotation."""  
    logger = logging.getLogger('PeopleDemoLogger')  
    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG to capture all types of logs  
  
    # Create a file handler which logs even debug messages  
    fh = RotatingFileHandler('people_demo.log', maxBytes=1024*1024*5, backupCount=5)  
    fh.setLevel(logging.DEBUG)  
  
    # Create console handler with a higher log level  
    ch = logging.StreamHandler()  
    ch.setLevel(logging.ERROR)  # Change to INFO or DEBUG as needed for console output  
  
    # Create formatter and add it to the handlers  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter)  
  
    # Add the handlers to the logger  
    logger.addHandler(fh)  
    logger.addHandler(ch)  
  
    return logger  
  
logger = setup_logging()  
  
  
## Class definition for Loading data  
  
class DataLoader:  
    """Responsible for loading data from a specified source."""  
      
    def __init__(self, url: str):  
        """Initialize the DataLoader with a data URL."""  
        self.data_url = url  
  
    def load_data(self) -> DataFrame:  
        """Load data from the specified URL into a DataFrame."""  
        try:  
            df = spark.read.format("delta").load(self.data_url)  
            logger.info("Data loaded successfully.")  
            return df  
        except Exception as e:  
            logger.error(f"Error loading data: {e}", exc_info=True)  
            raise  
  
  
## Class definition for Processing data  
  
class DataProcessor:  
    """Handles data processing including cleaning and transformations."""  
      
    def generate_silver(self, df: DataFrame) -> DataFrame:  
        """Generate the silver layer by deduplicating and transforming the input DataFrame."""  
        try:  
            df = df.dropDuplicates()  
            for col in df.columns:  
                df = df.withColumnRenamed(col, col.replace(" ", "_").lower())  
  
            cols_changes = {  
                "birthdate": F.date_format(F.col("birthdate"), "yyyy-MM-dd"),  
                "ssn": F.mask(F.col("ssn"))  
            }  
            df = df.withColumns(cols_changes)  
            logger.info("Silver data processed successfully.")  
            return df  
        except Exception as e:  
            logger.error(f"Error processing silver data: {e}", exc_info=True)  
            raise  
  
    def process_gold(self, df: DataFrame) -> DataFrame:  
        """Aggregate the silver DataFrame to generate the gold layer, focusing on key metrics."""  
        try:  
            df = df.groupBy("gender").agg(  
                F.sum("salary").alias("total_salary"),  
                F.count("id").alias("gender_count")  
            )  
            logger.info("Gold data processed successfully.")  
            return df  
        except Exception as e:  
            logger.error(f"Error processing gold data: {e}", exc_info=True)  
            raise  
  
  
## Main Module  
  
if __name__ == "__main__":  
    spark = SparkSession.builder.appName("PeopleDemo").getOrCreate()  
  
    data_loader = DataLoader("dbfs:/databricks-datasets/learning-spark-v2/people/people-10m.delta")  
      
    data_processor = DataProcessor()  
  
    try:  
        bronze_df = data_loader.load_data()  
        silver_df = data_processor.generate_silver(bronze_df)  
        gold_df = data_processor.process_gold(silver_df)  
  
        gold_df.write.mode('overwrite').saveAsTable("gold_people")  
        logger.info("Data processing complete. Results saved.")  
    except Exception as e:  
        logger.error(f"An error occurred in the main processing block: {e}", exc_info=True)
```