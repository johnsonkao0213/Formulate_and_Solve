MATH_COT = """
Let's translate mathematical word problems into the system of equations in a careful, formal manner. The system of equations will follow the following solving steps: 
1- Determine what the question is asking.
2- Write down the relevant information in simple statements.
3- Assign symbols (must be an alphabetic character e.g., x, y, z etc.) to unknown values that need to be found.
4- Determine how the statements relate to each other mathematically.
5- Give the system of equations only here, with each equation on a new line.

Q: Mike invested $6000 for one year. He invested part of it at 9% and the rest at 11%. At the end of the year he earned $624 in interest. How much did he invest at each rate?
A: 1- The question is asking for the amount of money Mike invested at each interest rate.
2- Relevant information: 
   - Total investment amount: $6000
   - Interest earned: $624
   - Interest rates: 9% and 11%
3- Assign symbols:
   Let x = amount invested at 9%
   Let y = amount invested at 11%
4- Mathematical relationship:
   The total investment amount is the sum of the amounts invested at each rate: x + y = 6000
   The interest earned is the sum of the interest earned at each rate: 0.09x + 0.11y = 624
5- System of equations:
   x + y = 6000
   0.09x + 0.11y = 624

Q: One pan pizza and two cheesburgers provide 2860 calories. Two pan pizzas and one cheeseburger provide 2990 calories. Find the caloric content of each item.
A: 1- The question is asking for the caloric content of each item.
2- Relevant information:
   - Calories in one pan pizza: x
   - Calories in one cheeseburger: y
   - One pan pizza and two cheeseburgers provide 2860 calories
   - Two pan pizzas and one cheeseburger provide 2990 calories
3- Assign symbols:
   Let x = calories in one pan pizza
   Let y = calories in one cheeseburger
4- Mathematical relationship:
   The total calories from the first statement: x + 2y = 2860
   The total calories from the second statement: 2x + y = 2990
5- System of equations:
   x + 2y = 2860
   2x + y = 2990

Q: A theater sells adult tickets for $8 and children's tickets for $5. If a total of $236 was taken in on sales of 34 total tickets, then how many adult tickets were sold?
A: 1- The question is asking for the number of adult tickets sold.
2- Relevant information:
   - Price of adult ticket: $8
   - Price of children's ticket: $5
   - Total revenue from ticket sales: $236
   - Total number of tickets sold: 34
3- Assign symbols:
   Let a = number of adult tickets sold
   Let c = number of children's tickets sold
4- Mathematical relationship:
   The total revenue from ticket sales: 8a + 5c = 236
   The total number of tickets sold: a + c = 34
5- System of equations:
   8a + 5c = 236
   a + c = 34

Q: The ratio of boys to girls is 9 to 4. You know there are 91 total students. How many of them are boys? How many are girls?
A: 1- The question is asking for the number of boys and girls.
2- Relevant information:
   - Ratio of boys to girls: 9 to 4
   - Total number of students: 91
3- Assign symbols:
   Let b = number of boys
   Let g = number of girls
4- Mathematical relationship:
   The total number of students: b + g = 91
   The ratio of boys to girls: b/g = 9/4
5- System of equations:
   b + g = 91
   b/g = 9/4

Q: A number added to 6 is equal to 30 less than four times the number. what is the number.
A: 1- The question is asking for the value of the number.
2- Relevant information:
   - A number added to 6 is equal to 30 less than four times the number.
3- Assign symbols:
   Let n = the number
4- Mathematical relationship:
   The number added to 6: n + 6
   30 less than four times the number: 4n - 30
   The relationship between the two expressions: n + 6 = 4n - 30
5- System of equations:
   n + 6 = 4n - 30

Q: {question}
A: 
""".strip()

MATH_COT_NEW = """
Let's translate mathematical word problems into the system of equations in a careful, formal manner. The system of equations will follow the following solving steps: 
1- Determine what the question is asking.
2- Write down the relevant information in simple statements.
3- Assign symbols (must be an alphabetic character e.g., x, y, z etc.) to unknown values that need to be found.
4- Determine how the statements relate to each other mathematically.
5- Give the system of equations only here, with each equation on a new line.

Q: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?
A: 1- The question is asking for the number of lollipops Jason gave to Denny.
2- Relevant information: Jason had 20 lollipops, gave some to Denny, and now has 12 lollipops.
3- Assign symbols: Let's use the symbol "x" to represent the number of lollipops Jason gave to Denny.
4- Mathematically, the number of lollipops Jason has after giving some to Denny can be represented as 20 - x = 12.
5- The system of equations:
   20 - x = 12

Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?
A: 1- The question is asking for the number of golf balls Michael had at the end of Wednesday.
2- Relevant information: Michael had 58 golf balls, lost 23 on Tuesday, and lost 2 more on Wednesday.
3- Assign symbols: Let's use the symbol "y" to represent the number of golf balls Michael had at the end of Wednesday.
4- Mathematically, the number of golf balls Michael had at the end of Wednesday can be represented as 58 - 23 - 2 = y.
5- The system of equations:
   58 - 23 - 2 = y

Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?
A: 1- The question is asking for the total number of cars in the parking lot after 2 more cars arrive.
2- Relevant information: There are 3 cars in the parking lot and 2 more cars arrive.
3- Assign symbols: Let's use the symbol "z" to represent the total number of cars in the parking lot after 2 more cars arrive.
4- Mathematically, the total number of cars in the parking lot after 2 more cars arrive can be represented as 3 + 2 = z.
5- The system of equations:
   3 + 2 = z

Q: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?
A: 1- The question is asking for the total number of computers in the server room after the installations.
2- Relevant information: There were 9 computers initially, and 5 more were installed each day from Monday to Thursday.
3- Assign symbols: Let's use the symbol "c" to represent the total number of computers in the server room after the installations.
4- Mathematically, the total number of computers in the server room after the installations can be represented as 9 + 5*4 = c.
5- The system of equations:
   9 + 5*4 = c

Q: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?
A: 1- The question is asking for the amount of money Olivia has left after buying the bagels.
2- Relevant information: Olivia has $23 and bought five bagels for $3 each.
3- Assign symbols: Let's use the symbol "m" to represent the amount of money Olivia has left.
4- Mathematically, the amount of money Olivia has left can be represented as 23 - 5*3 = m.
5- The system of equations:
   23 - 5*3 = m

Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?
A: The system of equations for the given word problem is as follows:
1- The question is asking for the number of trees the grove workers planted today.
2- Relevant information: There are 15 trees in the grove, and after planting, there will be 21 trees.
3- Assign symbols: Let's use the symbol "t" to represent the number of trees the grove workers planted today.
4- Mathematically, the number of trees the grove workers planted today can be represented as 15 + t = 21.
5- The system of equations:
   15 + t = 21

Q: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?
A: The system of equations for the given word problem is as follows:
1- The question is asking for the total number of toys Shawn has now.
2- Relevant information: Shawn has 5 toys, and he got 2 toys each from his mom and dad for Christmas.
3- Assign symbols: Let's use the symbol "s" to represent the total number of toys Shawn has now.
4- Mathematically, the total number of toys Shawn has now can be represented as 5 + 2*2 = s.
5- The system of equations:
   5 + 2*2 = s

Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?
A: The system of equations for the given word problem is as follows:
1- The question is asking for the total number of chocolates Leah and her sister have left after eating 35.
2- Relevant information: Leah had 32 chocolates, her sister had 42, and they ate 35.
3- Assign symbols: Let's use the symbol "c" to represent the total number of chocolates Leah and her sister have left.
4- Mathematically, the total number of chocolates Leah and her sister have left can be represented as 32 + 42 - 35 = c.
5- The system of equations:
   32 + 42 - 35 = c

Q: {question}
A: 
""".strip()
