---
created: 2024-08-11T01:33:47+05:30
modified: 2024-08-11T01:41:23+05:30
tags:
  - Databricks
  - PySpark
  - DataEngineering
---
# Data Skewness

## Finding if its present? 🤔

When you are trying to optimize your spark code, always start with checking if there are any partitions which are taking longer execution time compared to others.

You can go to “spark UI” in your spark cluster and then navigate to “Event Timeline” tab.

![](https://miro.medium.com/v2/resize:fit:1400/1*9H4BSUtjc1p6Krok2A0SHQ.png)

event Timeline is highlighted in back box

Once you are there, observe the timeline. Does it look like this:

![](https://miro.medium.com/v2/resize:fit:1400/1*fzMi6as4m1IYmdjq1LSqmg.png)

X axis is time and Y axis is different partitions.

If it's anything remotely similar to the above image, you can move on to the next task on your optimization check list. 😊 **NO DATA SKEWNESS**

But if it looks like this:

![](https://miro.medium.com/v2/resize:fit:1400/1*uPT2Acl_Ul9aEM0L2zUY6w.png)

skewed partition event timeline

Then you found out the cause of all your problems (which is not you surprisingly! 🥲). Data is indeed skewed!!

Next step: what causes this data skewness?

## Cause of data skewness🧐

Spark divides data in partitions (DUH! 🤷‍♂️) and assigns these partitions to executors. Now executors assign a core to each partition. Do you see the case here? 🤨

If data is divided in partition in such a way that one partition is hugeee, then the core getting that partition is cursed for its life! ☠️It has to work probably 10x times compared to other cores, while its friends sit and relax. And that is what causing your spark code to take long time.

You might ask, why that huge partition is created in the first place?

**_Operations that create big sized partitions:_**

1. Assume your data has 1 million rows. You are trying to group the data on one column and that column (assume “country” column) contains one value which has 950k rows 🤯. Obviously if you do a row count after group by, it will look something like this:

![](https://miro.medium.com/v2/resize:fit:964/1*_3eiJBGGOndt23ywZygtcA.jpeg)

C4 value has 850k rows which is highly skewed

> **Note:** this C4 value is called **skewed key**

Now, this skewed key will go to one partition, and you know how it goes…

2. If you join this skewed key with some other table (big or small doesn't matter), this will also create an oversized partition and…. (I hope you got the pattern till now 🤐)

# Salting: Fixing data skewness

![](https://miro.medium.com/v2/resize:fit:722/1*K0x4033DdNJ4-5pJRxuB3Q.jpeg)

salt that datashit bro!

Only way to fix data skewness is to somehow, divide that huge partition in smaller partitions. 🤔That would mean, divide that skewed key (C4 value in Country column in our case) in smaller chunks.

What if, we add a new column with values (0,1,2) and randomly assign these to skewed key in country column elements. like this:

![](https://miro.medium.com/v2/resize:fit:382/1*cR3XsktmEyyxFsExqSCA5Q.jpeg)

randomly assigned salting values to skewed key of the country column

This is called **_SALTING._** 😏

> Salting: It's a process of adding a random value to each record. By adding randomness, you can distribute skewed keys across multiple partitions, reducing the impact of data skew.

Furthermore, if you have to join this table (table1) with some other table (table2) using this “country” column, you have to join on **[country, salt] (join keys) columns.**

This would create not one big partition, but 3 equally divided, smaller partitions due to salt column! 😲😲😲

But for this, you should have “salt” column in table2 as well, isn't it! 😵‍💫

## Adding salt column in table2

**Step 1**: Add a column to table2 which will contain list of salt values

![](https://miro.medium.com/v2/resize:fit:426/1*cAA7BGAXZXwVnUgwzlRDdw.png)

adding a list of salt as new col for country (join key)

Step 2: EXPLODE THE SALT COLUMN (yup, you read it right! 😵)

![](https://miro.medium.com/v2/resize:fit:1142/1*gxPIo7mZMh4COTP4dw7vfw.jpeg)

Now, if you join this with table1 on **[country, salt],** you will get what you desire

Did you notice a HUGE drawback here? 🤨

If you have 5 keys in country column, you will have 15 keys (5x3 salt values) after exploding. Imagine if you had 50k keys. 🙃

**_This is one of the drawbacks. You are increasing the dataset by 3 folds here._**

It's just a small price to pay for data skewness. 🥹

If you liked the blog, please clap 👏 to make this reach to all the Data Engineers.

Thanks for reading! 😁