Wanting more is not always good! Don’t believe me? Ask that Data Engineer who takes on tasks because he can’t say ‘NO’. (Oh sorry, did I hurt your feelings🙈🤐)

You can also ask that executor who just got 5 more tasks added in the queue because YOU can't figure out the number of executor cores required for your spark job! 🙃

But, seriously, let's say you are given a task to set up a spark cluster which should be able to process 100GBs of data “efficiently”.

How would you start?

Let me show you how the boss does it! 😏

## STEP 1: Number of executor cores required?

We start by deciding how many executor cores we need 🤔

- **One partition is of 128MB of size by default** _— important to remember_
- To calculate number of cores required, you have to calculate total number of partitions you will end up having
- 100GB = 100*1024 MB = 102400MB
- Number of partitions = 102400/128 = 800
- Therefore, 800 executor cores in total are required

![](https://miro.medium.com/v2/resize:fit:524/1*klzSef6h9wS21wJ4PYO4IA.jpeg)

## STEP 2: Number of executors required?

Now that we know how many cores, next we need to find how many executors are required.

- On an average, its recommended to have 2–5 executor cores in one executor
- **If we take number of executors cores in one executor = 4** then, total number of executors = 800/4 = 200
- Therefore, 200 executors are required to perform this task

Obviously, the number will vary depending on how many executor cores do you keep in one executor 😉

## STEP 3: Total executor memory required?

**_Important step_**! how much memory to be assigned to each executor 🤨

- By default, total memory of an executor core should be

> 4 times the (default partition memory) = 4*128 = 512 MB

- Therefore, total executor memory = number of cores*512 = 4*512 = 2GB

## SUMMARIZE: Total memory required to process 100GB of data

We are here! 🥳lets finalize on total memory to be required to process 100GBs of data

- Each executor has 2GB of memory
- We have total of 200 executors

Therefore, 400GB of total minimum memory required to process 100GB of data _completely in parallel._

Meaning, all the tasks will run in parallel 😲

> Say, it takes 5 mins to run one task, how much time it will take to process 100GBs of data? — Answer is 5 mins!! since all tasks will run in parallel

## BONUS STEP: What should be the driver memory?

- This depends on your use case.
- If you do df.collect(), then 100Gbs of driver memory would be required since all of the executors will send their data to driver
- If you just export the output somewhere in cloud/disk, then driver memory can be ideally 2 times the executor memory = 4GB

And that my friend, is how you efficiently process 100GBs of data 😉

One thing to keep in mind, this is an ideal solution which can easily be toned down to fit the budget of a project😇

If project has a tight budget, you can reduce number of executors in half or by one-fourth. Though the time taken to process will definitely increase.

If you liked the blog, please clap 👏 to make this reach to all the Data Engineers.

Thanks for reading! 😁