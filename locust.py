# from locust import HttpUser, between, task

# class WebsiteUser(HttpUser):
#     wait_time = between(5, 15)

#     def on_start(self):
#         response = self.client.post("/login", data={
#             "email": "rani@gmail.com",
#             "password": "Rani@12"
#         })
#         print("Login Response:", response.status_code, response.text)

#     @task
#     def view_todos(self):
#         self.client.get("/todos/1")


# def args_test(*number):
#     return sum(number)

# ttest = args_test(2,4,5,6,7)
# print(ttest)


# def kawargs_Test(**kwargs):
#     return kwargs

# ktest = kawargs_Test(name="Rani", age=24, email="rani@gmail.com", password="Rani@12")
# print(ktest)


# class Dog:
#     species = "Canine"  # Class attribute

#     def __init__(self, name, age):
#         self.name = name
#         self.age = age

# dog1 = Dog("Rani", 24)
# print(dog1.name)
# print(dog1.age)
# print(dog1.species)



# def divide_numbers(a,b):
#     try:
#         result = a / b
#     except ZeroDivisionError:
#         print("Cannot divide by zero")
#     else:
#         print("result is {}".format(result))

#     finally:
#         print("Execution completed")

# divide_numbers(10,2)
# divide_numbers(10,0)



# class NegativeValueError(Exception):
#     def __init__(self, message):
#         self.message = message
#         super().__init__(self.message)

# def check_positive(number):
#     if number < 0:
#         raise NegativeValueError("Number is negative {}".format(number))
#     return "Number is positive {}".format(number)

# try:
#     print(check_positive(1))
#     print(check_positive(-1))
# except NegativeValueError as e:
#     print(e.message)


# def divide(a: int, b: int) -> float | None:
#     try:
#         return a / b
#     except ZeroDivisionError:
#         return "Cannot divide by zero"
    

# print(divide(10,2))
# print(divide(10,0))


# class NegativeValueError(Exception):
#     pass
 
 
# def check_positive(number: int) -> int:
#     if number < 0:
#         raise NegativeValueError("The number is negative.")
#     return number

# try:
#     print(check_positive(1))
#     print(check_positive(-1))
# except NegativeValueError as e:
#     print(e)


# class InvalidQuantityError(Exception):
#     pass
 
 
# class ProductSalesCalculator:
#     def __init__(self, price: float, quantity: int):
#         if quantity <= 0:
#             raise InvalidQuantityError("The quantity must be greater than zero.")
#         self.price = price
#         self.quantity = quantity
 
#     def calculate_total(self) -> float:
#         return self.price * self.quantity
    
# try:
#     calculator = ProductSalesCalculator(10, 3)
#     print("result is {}".format(calculator.calculate_total()))
# except InvalidQuantityError as e:
#     print(e)



# a = 4 | 50
# print(a)
