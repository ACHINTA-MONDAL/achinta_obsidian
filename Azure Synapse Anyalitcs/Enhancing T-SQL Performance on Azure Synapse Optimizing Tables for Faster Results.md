-
> (18 May 2024) This post talks about how to optimize TSQL stored procedures on Azure Synapse.

Crafting T-SQL stored procedures on Azure Synapse presents an efficient way for data transformation and analysis. However, the efficacy of these procedures hinges significantly on the optimization of underlying tables to ensure swift and optimal query execution. In this article, we delve into strategies aimed at elevating T-SQL performance, unraveling the keys to unlocking enhanced efficiency.

**Factors:**

1. **Incorrect Distribution:** In Azure Synapse, with its 64 compute nodes, how you store and retrieve data greatly impacts performance. Azure Synapse offers three distribution methods, each with its own benefits. Let’s break down these methods to help you optimize your queries and achieve faster results.

**a. Replicate:** It mirrors all table data across all 64 nodes, ideal for tables under 2GB and with infrequent updates. This method excels in data retrieval speed. Note: If more than 2 create tables are requested, Synapse triggers creation for the first 2 tables, queuing subsequent replicate table requests, resulting in slower pipeline performance.

Create table dbo.testTable  
(  
column1 varchar(100) null,  
column2 bigint not null,  
)  
with (distribution=REPLICATE,  
heap)

**b. Round Robin:** It is the default distribution on Azure Synapse, spreads data evenly across all compute nodes. While simple and automatic, it’s not optimized for data retrieval, especially in joins where heavy move operations can hamper performance.

**c. Hash:** It uses a hash function to distribute the table rows across all the compute nodes. Basically, the function takes each row and distributed to one node based on the hash. Since identical values always hash to the same distribution, SQL Analytics has built-in knowledge of the row locations. In dedicated SQL pool this knowledge is used to minimize data movement during queries, which improves query performance. This is the most optimized distribution technique.

**2. Incorrect Indexing:** Indexing tables plays crucial part while querying the table, so lets explore on which index to use for best optimization. Synapse analytics provides different indexing options to create table with indexing, like clustered columnstore index(CCI), clustered index and heap (non-clustered index). Lets explore on each one these:

**a. Clustered Columnstore Index (CCI):** By default synapse creates all tables as CCI if not defined. It offers highest level of data compression and best query performance. This indexing option is to be chosen when there are more than 60million rows in the table, like in case of fact tables.

Create table dbo.testTable  
(  
column1 varchar(100) null,  
column2 bigint not null,  
)  
with (clustered columnstore index)

**b. Heap:** This type of indexing is fast when creating a temporary table or a table with less than 60million rows as it allows subsequent reading from the cache.

Create table dbo.testTable  
(  
column1 varchar(100) null,  
column2 bigint not null,  
)  
with (heap)

**c. Clustered Index:** This type of indexing is preferred when single or very few lookup is required. It gives best performance on retrieval and can be used for dims.

Create table dbo.testTable  
(  
column1 varchar(100) null,  
column2 bigint not null,  
)  
with (clustered index (column2))

**3. Incorrect hash key:** When creating a table, it’s important to define the right hash key. While defining the hash key, consider the following factors:

a. The column should have unique values. If not, a combination of columns should be unique, as Synapse supports defining multiple columns in the hash key.

b. The column should not contain null values or should have very few nulls.

c. The column should not be a date column.

**4. Defining Proper Joins:** While joining tables, for best query performance and less shuffle movement, its recommended to use the hash defined field in the join and

**Example1:** You have a table with 200mil records with frequent insert/updates happening in the table. Its primary key is ID.

**Solution:** In this case case the right distribution and indexing should be hash and CCI with hashkey defined on ID.

Create table dbo.exampleTable1  
(  
ID bigint not null,  
column2 varchar(100) null,  
column3 varchar(100) null,  
)  
with (distribution=hash(ID), Clustered Columnstore Index)

**Example 2:** You have a table with 10mil records which is used in joins by many tables with daily inserts/updates happening in tables. Its primary key is ID

**Solution:** Since, its used by downstream than suitable indexing option is heap and suitable distribution is hash.

Create table dbo.exampleTable2  
(  
ID bigint not null,  
column2 varchar(100) null,  
column3 varchar(100) null,  
)  
with (distribution=hash(ID), heap)

**Example 3:** A dimensional table with 0.5mil records with rare updates.

**Solution:** Replicate table with heap as its indexing option.

Create table dbo.exampleTable3  
(  
ID bigint not null,  
column2 varchar(100) null,  
column3 varchar(100) null,  
)  
with (dsitribution=Replicate, heap)

Congrats!! You have learned about optimizing T-SQL tables and stored procedures on Azure Synapse.