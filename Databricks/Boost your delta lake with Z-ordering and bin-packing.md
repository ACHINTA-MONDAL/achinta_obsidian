
The speed of the read queries in delta lake is mainly dependent on layout of the data stored. If the delta lake has large number of small files the performance is going to get a hit. Also data skipping plays an important role in increasing the performance of your query. By Z-ordering your data in delta lake,the data skipping can be done more efficiently thus increasing your query performance.

# What is bin-packing?

bin-packing a.k.a. compaction, coalesces the smaller files into bigger ones. We can do the compaction by using the below command:

> [!NOTE]
> OPTIMIZE delta.`/path/to/delta/lake`

Example:

The below location has six smaller files.

![](https://miro.medium.com/v2/resize:fit:1400/1*e-UFj5UHmtnulg49ho41yQ.png)

6 small files

Now lets do the compaction on the above delta path.

![](https://miro.medium.com/v2/resize:fit:1400/1*80azFctZZsm02iXdtOePOA.png)

After doing the optimization you can see that numFilesAdded is 1 and numFilesRemoved is 6 in the metrics. That means 6 smaller files are combined into 1 single file.

If you see the files in the path you still will see those 6 small files along with the newly added file. This is because delta lake preserves the older files for the time travelling functionality. The best to way to see the change is to look into DeltaLog.

![](https://miro.medium.com/v2/resize:fit:1400/1*G4yFdMPi6GVTzvMn_QP42A.png)

You will notice that 6 files are removed and one file is added.

# What is Data Skipping?

DeltaLog stores the minimum and maximum values of all the columns for every file so that the particular file can be skipped if the search value doesn’t fall into that minimum and maximum value range.

**_Z-Ordering_**

Z-Ordering helps to do the data skipping in an efficient way by colocating related information in the same set of files.

> [!NOTE]
> OPTIMIZE delta.`/path/to/delta/lake`  
> ZORDER **BY** (colName)

Let consider the below scenario.

We have 4 small files with fields _id ,name_ and _dept._

Since the size of the files are small we perform compaction. Now these 4 smaller files will be combined into two files.

Let’s query data and select the row where dept=_ccc_. Since the dept column is unordered and _ccc_ values falls into min and max range, both the files will be read. So the data layout is not fully optimized yet.

![](https://miro.medium.com/v2/resize:fit:1400/1*qHnH11Nxmt7cyiQBJkqP5w.png)

Now along with compaction, lets do z-ordering on dept column.

![](https://miro.medium.com/v2/resize:fit:1400/1*UUxjQTXzejUavRP_rqLSDA.png)

After doing compaction and z-ordering on dept column, the dept column will be ordered and stored into two files. The min and max _dept_ value of the first file is _aaa_ and _ddd_ respectively. Similarly, the min and max _dept_ value of the second file is _eee_ and _hhh_ respectively. Since _ccc_ doesn’t fall into min and max range, the second file will be skipped completely.

We can z-order multiple columns by providing the column names in the list. However, the effectiveness decreases with the addition of every column.

# **Conclusion**

I hope this blog gives an idea on how to optimize the layout of data stored and take full advantage of delta lake. Please share your feedback in comments.