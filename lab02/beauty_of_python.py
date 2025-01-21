# Introduce Python Programming
import this

# hack for imports

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parents[1]))
import lab01

# basics
for i in [0, 1, 2, 3]:
  print(i)

colors = ['red', 'green', 'blue', 'yellow']
for i in range(len(colors)):
  print(i, '-->', colors[i])

for color in reversed(colors):
  print(color)

# format strings
name = 'John'
age = 30.01
f'My name is {name:^10} and I am {age:10} years old.'

# list comprehensions and idiomatic Python
squared = [x**2 for x in range(10)]
squared
4 in squared
7 in squared

# dictionary comprehensions
squared_dict = {str(x): x**2 for x in range(10)}
squared_dict
squared_dict['4']

# set comprehensions and set operations
set_a = {1, 2, 3, 4, 5}
set_b = {4, 5, 6, 7, 8}
print(set_a | set_b)
print(set_a & set_b)
print(set_a - set_b)
print(set_a ^ set_b)

difference = set_a - set_b
print(difference <= set_a)

set_a|=set_b
print(set_a)


# map and filter functions demonstrate functional programming

def is_even(x):
    return x % 2 == 0

def square(x):
    return x**2

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squared_evens = map(square, filter(is_even, numbers))
list(squared_evens)

# reduce function
from functools import reduce

def add(x, y):
    return x + y

squared = [x**2 for x in range(10)]
sum_of_squares = reduce(add, squared)

# https://realpython.com/python-reduce-function/#readability-counts

# threading and function objects as parameters
import threading
import time
def print_numbers():
    for i in range(10):
        print(i)
        time.sleep(1)

def run_run_run():
  thread = threading.Thread(target=print_numbers)
  thread.start()
  print('running...')

run_run_run()

#lambda functions 

import threading
import time
def print_numbers(modifier):
    for i in modifier(range(10)):
        print(i)
        time.sleep(1)

def run_run_run():
  rev_function = lambda : print_numbers(reversed) 
  rev_thread = threading.Thread(target=rev_function)

  plain_function = lambda : print_numbers(lambda x: x) #show dictionary map here
  thread = threading.Thread(target=plain_function)

  thread.start()
  print('running thread...')
  time.sleep(5)
  rev_thread.start()
  print('both running now...')
  thread.join()
  print('not waiting for reversed thread')

run_run_run()

# generator functions
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

fib = fibonacci(10)
list(fib)

# generator expressions
for a in fibonacci(10):
    print(a, 'is my favorite number')

# decorators
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

def say_hello():
    print("Hello!")

say_hello = my_decorator(say_hello)
say_hello()

# decorator for timing a function

import time

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Elapsed time: {end_time - start_time}")
        return result
    return wrapper

@timer
def slow_func(num_times):
    for _ in range(num_times):
        time.sleep(1)
    print("Function executed")

slow_func(4)

# decorators with arguments
def repeat(num_times):
    def decorator_repeat(func):
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat

def greet(name):
    print(f"Hello {name}!")

greet = repeat(num_times=4)(greet)

greet('Howard')

@repeat(num_times=4)
def greet(name):
    print(f"Hello {name}!")
