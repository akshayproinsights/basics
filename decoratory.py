import time

def work():
    start = time.time()

    time.sleep(2)

    end = time.time()

    print(end - start)

def work_timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(end - start)
        return result
    return wrapper

# @work_timer
# def add(a, b):
#     time.sleep(2)
#     return a + b

# @work_timer
# def sub(a, b):
#     return a - b

# # print(add(10, 12))
# # print(sub(10, 2))

# @work_timer
# def greet(name):
#     time.sleep(2)
#     return "Hello " + name

# print(greet('Akshay'))

logged_in = True

def login_required(func):    # this is descorator now
    def wrapper():    # this is the actual function that will be called but its wrapper on top of 
        if not logged_in: 
            print("Please login first.")
            return
        return func()
    return wrapper

@login_required
def view_profile():
    print("Showing profile")

@login_required
def view_dashboard():
    print("Showing dashboard")

view_profile()
view_dashboard()

print(view_profile.__name__)
print(view_dashboard.__name__)

def my_security(func):
    def wrapper():
        return func()
    return wrapper

@my_security
def profile():
    print("Profile")

profile()

import time

def logged_time(func):
    def wrapper():
        start = time.time()
        func()
        end = time.time()
        print(end - start)
    return wrapper

@logged_time
def say_hello():
    time.sleep(2)
    print("Hello World")

say_hello()


##########################################################
logged_in = True

def login_required(func):

    @wraps(func)
    def wrapper():
        if not logged_in:
            print("Please login first.")
            return

        return func()

    return wrapper


@login_required
def view_profile():
    print("Showing profile")


@login_required
def view_dashboard():
    print("Showing dashboard")

print(view_profile.__name__)
print(view_dashboard.__name__)