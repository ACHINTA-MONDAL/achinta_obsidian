---
created: 2024-08-11T01:41:31+05:30
modified: 2024-08-11T01:43:35+05:30
tags:
  - Databricks
  - DataEngineering
  - UnityCatalog
---
Databricks has introduced industry’s only unified and open governance solution for data! and that's…

> Unity Catalog

## Before Unity Catalog,

- We used to have access control for each Databricks workspace separately.
- Each workspace would have its own Hive Metastore
- Hive Metastore is an HDFS, so you cannot save objects in that
- Tracking the upstream and downstream of a table (called data lineage) was not possible
- Sharing access to a hive Metastore across Databricks workspaces was not possible
- No Delta Sharing, No external data connection
- No row level or column level security

# Unity Catalog

Unity Catalog is a data governance solution in Databricks which provides a unified way to govern data. let me give you an example:

Say, you have multiple workspaces in Databricks. You also have a database (a schema) to which, all workspaces want access to. This access was not possible till now! 😥

But with Unity Catalog, we have a layer above workspaces which deals with all the access related work.

![](https://miro.medium.com/v2/resize:fit:758/1*LhlIuxpOqJuVwOgfSHLqtg.png)

unity catalog layer above workspace

In Unity, we have a **_Unity Catalog Metastore (UC Metastore)_**, which, unlike HDFS, is an object storage (similar to S3 or ADLS).

One can have multiple workspaces connected to this UC Metastore. Different workspaces can create their own schemas (databases) in UC Metastore and can also ask permissions to access other workspace’s schemas. 😮

Let’s discuss the admins in Unity, and then we’ll jump in the features provided by Unity. 😉

## Types of admin in Unity Catalog

There are 3 different admins in Unity Catalog:

1. **Account admin**: this admin creates and links Metastore to workspaces.
2. **Metastore admin**: this admin is the owner of the Metastore. The only user who can grant privileges to the Metastore. This admin is assigned by Account admin
3. **Workspace admin**: each workspace would have a workspace admin to manage users in workspace

## Object Model in Unity Catalog

![](https://miro.medium.com/v2/resize:fit:1400/1*Zt_uHjg1rtxjlsM1XDUrSA.png)

Under a UC Metastore

- We can have multiple Catalogs
- Each Catalog can have multiple schemas (databases)
- And each schema can have multiple tables/views/volumes(objects)

> Note: To query a table, you have to do catalog.schema.table

Now, if a user wants to query one table, he/she needs to have access to that particular catalog and the schema inside which the table resides. 🧐

# Features of Unity Catalog

## 1. Multiple workspaces can have access to UC Metastore 😲

Once Unity is enabled in your Databricks, go to “Data” tab on your left panel.

![](https://miro.medium.com/v2/resize:fit:1280/1*dH0jYsZgWW9bELjnl84kNQ.png)

There, you would see details of your Metastore, for example, to which storage location the Metastore is connected to (In above image, it's in ADLS) and Metastore’s admins

If you click on “Workspaces”, you will see all the workspaces which has access to the UC Metastore 😱. Each workspace can have its own Catalog. Also, 2 workspaces can have access to one Catalog as well!

Meaning, say we have Catalog1, Catalog2 of workspace 1 and workspace2 respectively. If workspace1 needs access to catalog2, that access can be given instantaneously! 🤯🤯

Similarly, individual users can also be given access to catalogs, tables and schemas. One point to be noted here:

> ANY PERMISSION GIVEN TO A CATALOG, TABLE OR SCHEMA ARE APPLIED TO ALL THE WORKSPACES WHICH HAS THE CATALOG ACCESS

**_Hence, one major drawback_** 🤕 **_(in my opinion) is, let's say:_**

We have User1 who have permission to access table1. The user needs to have permission to access the corresponding catalog1 and schema1 inside which table1 resides.

We also have 2 workspaces which have access to catalog1. Since all the permissions are applied to all the sharing workspaces, user1 would indirectly have access to both the workspaces!

![](https://miro.medium.com/v2/resize:fit:982/1*fNUzIdlu72DCH9qO1vToOQ.jpeg)

## 2. Unity Catalog provides Data Lineage!

Imagine 100s of Notebooks using 100s of tables to create more 100s of tables. 🥴🥴

Yup, and now imagine tracking which table is created in which notebook and is used to create which table😖

Ha!! This big clutter is easily solved by Unity by providing _Data Lineage_.

![](https://miro.medium.com/v2/resize:fit:1400/1*qtdxBoVWbWlEOMBtFTwknw.png)

Lineage tab under tables

“_Lineage_” tab under tables provides which are the downstream and upstream tables, which notebooks and workflows uses these tables and which dashboard is using this table to generate respective KPIs. 😏

For example, lineage of a gold table could look like this:

![](https://miro.medium.com/v2/resize:fit:1400/1*twW_6BzPKRwqmQr3q8X31Q.png)

lineage of a gold table

## 3. One can connect to external Data Source!

Using “storage credentials” and “external location”, one can access external data stored in ADLS or S3.

Also, you can connect to external databases like snowflake, MySQL, Postgres and other workspace catalogs as well! 😱

NO NEED TO MIGRATE YOUR DATA, JUST ESTABLISH A CONNECTION AND QUERY IT! 🤯😱

![](https://miro.medium.com/v2/resize:fit:836/1*Q5IteyBjgh9jZTBeBXqQVQ.png)

All three types of external data ingestion options

## 4. You can store objects in Unity Catalog Metastore

Unlike HDFS, you can store blob objects in UC Metastore (same as S3 and ADLS) 😏

## 5. You can give row and column level security in Unity Catalog

This will allow us to hide or anonymize data based on each user’s permission🫣 (check [this](https://www.youtube.com/watch?v=jAPuAuphwt4) video to know more)

**And many more features….**

Isn’t Unity powerful 🙃 (saw the irony there?)

If you want a visual overview of Unity Catalog, I will highly recommend [this](https://www.youtube.com/watch?v=vwIujIbqEKQ) video.

Databricks is driving Data governance in a very “easy to handle” way, by doing all the heavy liftings! And leaving all the brainy stuff to Data Engineers. 😉

Happy learning! 😆

If you liked the blog, please clap 👏 to make this reach to all the Data Engineers.

Thanks for reading! 😁