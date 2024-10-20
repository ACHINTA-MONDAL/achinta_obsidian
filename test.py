sentence = "Hello World"

sen_split=[]
sen_split= sentence.split(' ')

print(sen_split[1])


ist_part =sen_split[0]


numbers = [1, 2, 3, 4, 5, 6]


even_num = [ i for i in numbers if i%2==0]

print(even_num)


df = spark.read.csv.option('header','true').load('/path')

df.write.format('delta').option('mergeschema',true).option('mode','overwrite').saveAsTable('table')


Write a SQL query to find the top 5 highest-paid employees in each department using a window function.
Sample Data:
EmployeeID	EmployeeName	Salary	Department
1	John	5000	HR
2	Jane	6000	HR
3	Mike	8000	IT
4	Alice	7500	IT
5	Bob	6500	IT
6	Emma	4500	HR
7	Sam	7000	IT
8	David	5500	HR
Expected Output:
This query should return the top 5 highest salaries in each department.
 
EmployeeID	EmployeeName	Salary	Department
2	Jane	6000	HR
1	John	5000	HR
8	David	5500	HR
3	Mike	8000	IT
4	Alice	7500	IT
7	Sam	7000	IT
5	Bob	6500	IT



WITH CTE AS(
SELECT EmployeeID,	EmployeeName,Salary,Department, DENSE RANK() OVER(PARTITION BY Department ORDER BY Salary desc) as rnk
FROM EMP
)

SELECT EmployeeID,	EmployeeName,Salary,Department FROM CTE WHERE rnk <= 5



Using the table employee_salaries with columns employee_id, salary, and effective_date, write a query to identify the dates when an employee’s salary changed. 
List the employee_id, effective_date, salary, and the previous_salary.
Sample Input Data (employee_salaries table):
employee_id	salary	effective_date
101	5000	2023-01-01
101	5500	2023-04-01
101	5500	2023-07-01
102	6000	2023-02-01
102	6200	2023-05-01
102	6400	2023-08-01
Expected Output:
The query should return rows where the salary has changed for each employee.
 
employee_id	effective_date	salary	previous_salary  
101	2023-04-01	5500	5000
102	2023-05-01	6200	6000
102	2023-08-01	6400	6200

WITH CTE AS (
SELECT employee_id,	salary,effective_date, LAG(salary) OVER(ORDER BY effective_date) as previous_salary

FROM employee_salaries
),
sal_diff(

    SELECT employee_id,effective_date,salary, previous_salary, (salary-previous_salary) as sal_diff
    FROM CTE ORDER BY effective_date
)

SELECT * FROM sal_diff WHERE sal_diff >0

5000 NULL
5500 5000
 