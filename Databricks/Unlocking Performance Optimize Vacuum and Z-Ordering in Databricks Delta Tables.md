---
source: https://medium.com/@amarkrgupta96/unlocking-performance-optimize-vacuum-and-z-ordering-in-databricks-delta-tables-6ce20999f6f5
tags:
  - Databricks
  - DataEngineering
  - CodeOptimization
data: 2024-07-03T01:38:00
---

![](https://miro.medium.com/v2/resize:fit:1188/1*8-b9COpzaJDqmGZWVLYE1A.png)

Databricks Official Logo

Delta Lake is a powerful storage layer that brings ACID transactions to Apache Spark and big data workloads. Delta Lake not only enhances reliability but also introduces various optimization techniques that can significantly boost performance and streamline data workflows.

In this article, we will delve deeper into the inner workings of Delta Lake, shedding light on the mechanics that drive its functionality. Furthermore, we will explore a selection of common optimization techniques applicable to Delta tables within the Databricks environment.

Without further ado, let’s dive right in and begin our exploration.

# **Processing Tables and Data Files in Databricks:**

Let’s create our table, first:

![](https://miro.medium.com/v2/resize:fit:1300/1*-op6I5qgymRnU77o7llWog.png)

Let’s run a SELECT query:

![](https://miro.medium.com/v2/resize:fit:1400/1*Q6c-my3l_JixUa1UuTRRFw.png)

Let’s see how the files are placed in the DBFS (Databricks File System) location:

![](https://miro.medium.com/v2/resize:fit:1400/1*nIyC8D6uxe3BAmJQtS8TBw.png)

As you can see, in the first run only **__delta_log_** folder is created.

If we go inside this folder, we see a json file with the initial snapshot (present state of table):

![](https://miro.medium.com/v2/resize:fit:1400/1*i_C3gDt_55h_WA7YqfJk-A.png)

Let’s insert few records:

![](https://miro.medium.com/v2/resize:fit:1400/1*rM_TO5coMbh1H3QgH3j89w.png)

Each insert will be treated as a separate operation, as a result, three different files will be created, with each containing only one record.

Let’s verify the same:

![](https://miro.medium.com/v2/resize:fit:1400/1*sfY1aKX0qsQ8KlY4-Y5xYQ.png)

Let’s check our **__delta_log_** folder again:

![](https://miro.medium.com/v2/resize:fit:1400/1*LOvktXNhYEzbatLFeD-_2w.png)

In the delta log, since the table state got changed **thrice** (after three insert operations), three more json files got created.

Let’s do three more insert operations to our table:

![](https://miro.medium.com/v2/resize:fit:1400/1*lXC3yNF276fYA3QYQ9q0xQ.png)

So, now we have a total of six data files.

![](https://miro.medium.com/v2/resize:fit:1400/1*Y699a0n0BVU0G2olmH8CdQ.png)

And we’ll have three more json files in our _delta_log folder.

![](https://miro.medium.com/v2/resize:fit:1400/1*bqsQAGWhRxzPdZ49qfZbZA.png)

Let’s again do a SELECT operation on our table:

![](https://miro.medium.com/v2/resize:fit:1400/1*uteru0aXXXLuFfoy1fPH1Q.png)

> **Now let’s see how this SELECT operation ran behind the scenes:**
> 
> _Whenever we run a query on top of our delta table, Databricks first goes to the_ **__delta_log_** _folder, refers the latest json file (in our case it is_ **_0000000000006.json_**_), and gets the info about the_ **_snapshot_** _of that table, that is which files it needs to refer to give an output and accordingly gives the output, after referring those data files._

Now let’s do a delete operation:

![](https://miro.medium.com/v2/resize:fit:1040/1*V_8IlfW8NNVXll4riZoSQA.png)

Let’s see how this impacted our DBFS files:

![](https://miro.medium.com/v2/resize:fit:1400/1*t3vUykpb7dDGTOtn8g7q-A.png)

You’ll see a new json file is created in **__delta_log_** whereas the number of data files remains the same — **SIX**.

> **_Even after a delete operation, the data files have remained same. Why?_**
> 
> The file is not removed immediately. This for the simple reason of time-travelling — an important feature of delta tables. So, instead of removing the file, Databricks will simply mark that file “inactive”. All this info will be present in the latest log file (0000000007.json)

Now let’s do an UPDATE operation on our table:

![](https://miro.medium.com/v2/resize:fit:1306/1*0UXHbv3JiedZCHMMrJNPRg.png)

As expected, a new data file is added along with one additional json file. It will keep the previous file and write the updated record in a new file.

![](https://miro.medium.com/v2/resize:fit:1400/1*g293LZJ1u1NteNjGQLCY3Q.png)

The latest log file (**_000000000008.json_**) will tell Databricks to ignore two files (one as the corresponding record is deleted and other one as it contains an old value of that record).

> **_Now we have a well-framed description of how Delta tables behave behind the scenes, after CRUD operations. :)_**

_(*) As you can see, we have created so many small files and in real-time scenarios, there may be millions of such small files and Delta engine will have to maintain all their metadata as well. This is a process-overhead and it will affect the performance, for sure._

_(*) So, it’s not a good idea to keep so many small files. Instead, we can combine these small files to a single file of optimal size._

_(*) This can be achieved using OPTIMIZE command._

# 1. OPTIMIZE Command:

This is the command to compact smaller sized files. In Big Data processing, having too many small files or too few very big files are not desired. It’s always good to have files with optimal size.

**_As per OPTIMIZE, the default size is 1GB. So, for data files smaller than 1GB, running this command would combine such files to 1gb in size._**

Let’s practically see the OPTIMIZE command in action:

![](https://miro.medium.com/v2/resize:fit:1400/1*8nMN7Mh2VFuMMqbhoX57gQ.png)

If you read the log message, it says in that path, 1 file added and 5 files removed. New file is a combination of those 5 files and hence those 5 files are removed.

> But when it says, 5 files removed, it means that going forward the delta engine would not refer these files and would only refer the latest combined file after OPTIMIZE operation. But those files would remain present in the DBFS location. They are just removed from reference.

If you see the DBFS again, you will see an additional eighth file along with an extra json file in **__delta_log_** folder.

![](https://miro.medium.com/v2/resize:fit:1400/1*ggu68NFSIqQ4pk7RRr0p8g.png)

If you see the history of the table, you will find the following:

![](https://miro.medium.com/v2/resize:fit:1400/1*VQcaodBxFhsG-C6ArYM0ZQ.png)

Here, we can clearly see all the operations that have been done on our delta table. And with every operation, a new snapshot (version) of the table is created.

Let’s move on to the second command that is helpful in optimizing our Delta tables — VACUUM.

# **2. VACUUM Command:**

(*) Delta Tables, by default, keep the history files for time-travelling.

(*) But over a period of time, if we do not clean up those data files, it will continue to pile-up huge amount of data, which is not good from maintenance and storage perspectives.

(*) So, we must clean them periodically and for that we can use the VACUUM command, which helps us to remove the **_obsolete files,_** that are not part of our latest version of our delta table.

Let’s see the files that our present in that path:

![](https://miro.medium.com/v2/resize:fit:1400/1*xHFsNr2NntnF7vRgarTkPQ.png)

We see these many files, but we know after running the OPTIMIZE command, we are just left with one single active file, rest all are inactive.

We can remove the invalidated files which are:

i. Not part of the present version of the table.

ii. Files that have become invalid at least 7 days ago. _(This is configurable)_

> But before we remove these files, it’s always suggested to do a **DRY RUN**. This will list out all the files that will be removed after the actual VACUUM operation.

(*) Since, we have recently added the files, the criteria of 7 day retention period won’t be fulfilled, so we will tweak it a bit:

![](https://miro.medium.com/v2/resize:fit:1400/1*yP2pu4pe1rpR0ifV3Nembg.png)

> But this throws an error, because there’s a **property** set that is mandating a minimum retention period of 168 hours or 7 days for file obsolescence.

![](https://miro.medium.com/v2/resize:fit:1400/1*Id0-1eYDK_2WBQqnRCirKA.png)

(*) Thus, it lists down those files that became inactive in the last 1 hour.

(*) We can also remove all the obsolete files by making **RETAIN 0 HOURS**. This means that even files that were just created or recently modified could be marked for deletion, if they are deemed unnecessary for query processing.

![](https://miro.medium.com/v2/resize:fit:1400/1*lcqz1V_kCq6T0FDFXXPGDQ.png)

Finally let’s execute the VACUUM command.

![](https://miro.medium.com/v2/resize:fit:1196/1*wRSxzlbfoJX5qF0za5EPHg.png)

Let’s see the table-history:

![](https://miro.medium.com/v2/resize:fit:1400/1*FuBN7-AHkwBkj2MHNlMy7w.png)

Let’s run a SELECT query on our table:

![](https://miro.medium.com/v2/resize:fit:1400/1*4taB1NXbxai69N0T0cmDBQ.png)

And, we have only one file in the DBFS location:

![](https://miro.medium.com/v2/resize:fit:1400/1*BQXR2oq6lN7RbsZZA56XGA.png)

# **3. Z-Ordering:**

(*) Z-Ordering is nothing but an extension of OPTIMIZE.

(*) OPTIMIZE, while combining smaller files, does not care about the ordering of data and randomly combines those files. So, if we add Z-Ordering to our OPTIMIZE command, our smaller files will get combined in a specific order as specified in the Z-Order.

# **Example:**

Let’s say, we have an **“Employee”** delta table, that 6 data files — each of size 500 MB.

![](https://miro.medium.com/v2/resize:fit:1400/1*2T-V9E_t6YjvqdEIPq3CFg.png)

Then we perform an **OPTIMIZE** operation, and it results in three files (1GB each):

![](https://miro.medium.com/v2/resize:fit:1400/1*8lTYh5WpBvaf8qQUzSWT0A.png)

(*) Now delta engine maintains some statistics, for all these files, as below:

![](https://miro.medium.com/v2/resize:fit:528/1*dp6zqomA5Scd_AxQ-3Sxbg.png)

(*) Suppose we need to run some queries; this is how **_data skipping_** would work:

![](https://miro.medium.com/v2/resize:fit:1400/1*4oTOEXcDzkGxDugpJpmgeQ.png)

> **1st Query:** It goes to file #1 checks the min and max value of emp_id in that file, there’s a possibility to find 444, hence it adds it to the list of the files that need to be scanned. Similarly, file #2 and file #3 would also fall in the range. And ultimately, the delta engine would need to scan all these 3 files. So, we don’t’t get any advantage of data-skipping here.
> 
> **2nd Query:** For less than 333, it goes to file #1 and file #2 and skips file #3, as it is not in the range. So, here data skipping (scanning only those files where there’s a possibility to find our data), takes place.

# When we have Z-Order in place:

At first, it _sorts all the data_ (based on Z-Order column), and then distributes it into _three files_ (because of OPTIMIZE):

![](https://miro.medium.com/v2/resize:fit:1400/1*8LX0XuW7eNeC1AJd3GTWug.png)

So, the performance of the same 2 queries will be:

![](https://miro.medium.com/v2/resize:fit:1400/1*GiSdUhd6tbkQQMxXDQRV2Q.png)

> **Query1:** From the stats, delta engine will directly go and look into file#2.
> 
> **Query2:** From the stats, delta engine will directly go and look into file#1.

Clearly, data skipping was done in a much better way.

# **Syntax:**

Let’s see the syntax of Z-Order (w.r.t. our previous table)

![](https://miro.medium.com/v2/resize:fit:954/1*E05zWgxGmUyTN7vl0PcTvA.png)

# Summary:

(*) In Big Data processing, it’s always good to have files with optimal size. We should always avoid having too many small files or very few very big files. And we can use OPTIMIZE command for the same.

(*) ==When data files become obsolete, they are automatically removed from the storage locations. And to optimize our storage costs, we can periodically run VACUUM command on our tables. But please make sure to do a DRY RUN before actually executing it.==

(*) Z-Ordering is an extension to OPTIMIZE command, where the data is first sorted based on a particular column’s values and then file compaction happens. This greatly improves performance and enhances data-skipping through sorted compaction.

# Conclusion:

_In the ever-evolving landscape of data management, achieving peak performance is a constant pursuit. And as the final curtain descends, what emerges is a harmonious synergy of Delta optimization techniques. Z-Ordering’s intelligent data arrangement sets the tone, while VACUUM and OPTIMIZE play their parts in creating a refined symphony of performance enhancement. Queries execute gracefully, resources are utilized optimally, and the data ecosystem resonates with efficiency_.
