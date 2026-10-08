from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ============================================================
# TOPIC 1: CLASS AND OBJECT
# TOPIC 2: INSTANCE ATTRIBUTE VS CLASS ATTRIBUTE
# TOPIC 3: INSTANCE METHOD / CLASS METHOD / STATIC METHOD
# ============================================================

class Store:

    # CLASS ATTRIBUTE
    # Shared by every Store object.
    store_name = "Python Shop"
    total_orders = 0

    def __init__(self, owner: str):
        # INSTANCE ATTRIBUTE
        # Every object can have a different owner.
        self.owner = owner

    # INSTANCE METHOD
    # Works with one specific object using self.
    def show_owner(self) -> None:
        print(f"Store owner: {self.owner}")

    # CLASS METHOD
    # Works with the class itself using cls.
    @classmethod
    def change_store_name(cls, new_name: str) -> None:
        cls.store_name = new_name

    # STATIC METHOD
    # Related to Store, but doesn't need self or cls.
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return "@" in email and "." in email


# ============================================================
# TOPIC 4: @property
# TOPIC 5: ENCAPSULATION
# TOPIC 9: MAGIC METHODS
# ============================================================

class Product:

    def __init__(self, name: str, price: float):
        self.name = name

        # IMPORTANT:
        # We are using self.price instead of self._price.
        #
        # Why?
        # Because self.price goes through the setter,
        # so validation happens when the object is created too.
        self.price = price

    # @property controls READING.
    @property
    def price(self) -> float:
        return self._price

    # Setter controls ASSIGNING.
    @price.setter
    def price(self, value: float) -> None:

        if value < 0:
            raise ValueError("Price cannot be negative")

        # Actual internal value is stored here.
        self._price = value

    def delivery_info(self) -> str:
        return "Standard delivery"

    # MAGIC METHOD
    # Runs when:
    #
    # print(product)
    # str(product)
    #
    def __str__(self) -> str:
        return f"{self.name} - ₹{self.price}"

    # MAGIC METHOD
    # Runs when:
    #
    # product1 == product2
    #
    def __eq__(self, other) -> bool:

        if not isinstance(other, Product):
            return False

        return (
            self.name == other.name
            and self.price == other.price
        )


# ============================================================
# TOPIC 6: INHERITANCE + super()
# TOPIC 7: POLYMORPHISM
# ============================================================

class PhysicalProduct(Product):

    def __init__(
        self,
        name: str,
        price: float,
        weight: float
    ):

        # super() calls Product.__init__()
        super().__init__(name, price)

        self.weight = weight

    # Same method name as parent.
    # Different implementation.
    #
    # This is polymorphism.
    def delivery_info(self) -> str:
        return f"Courier delivery. Weight: {self.weight} kg"


class DigitalProduct(Product):

    def __init__(
        self,
        name: str,
        price: float,
        download_link: str
    ):

        super().__init__(name, price)

        self.download_link = download_link

    # Again same method, different behavior.
    def delivery_info(self) -> str:
        return f"Download from: {self.download_link}"


# ============================================================
# TOPIC 7: POLYMORPHISM
# ============================================================

def show_delivery(product: Product) -> None:

    # We don't care whether product is:
    #
    # PhysicalProduct
    # DigitalProduct
    #
    # Python calls the correct implementation automatically.
    print(product.delivery_info())


# ============================================================
# TOPIC 11: DATACLASS
# ============================================================

@dataclass
class Customer:

    # @dataclass automatically gives us things like:
    #
    # __init__()
    # __repr__()
    # __eq__()
    #
    # So we don't need to manually write them.

    name: str
    email: str
    loyalty_points: int = 0


# ============================================================
# TOPIC 8: COMPOSITION
# TOPIC 9: MAGIC METHODS
# ============================================================

class Cart:

    def __init__(self, customer: Customer):

        # COMPOSITION:
        #
        # Cart HAS-A Customer.
        #
        # Cart is NOT a Customer.
        #
        # This is composition.
        self.customer = customer

        # Cart HAS products.
        self.items: list[tuple[Product, int]] = []

    def add_product(
        self,
        product: Product,
        quantity: int = 1
    ) -> None:

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.items.append((product, quantity))

    def total(self) -> float:

        total_amount = 0

        for product, quantity in self.items:
            total_amount += product.price * quantity

        return total_amount

    # MAGIC METHOD
    # Runs when:
    #
    # len(cart)
    #
    def __len__(self) -> int:

        total_quantity = 0

        for _, quantity in self.items:
            total_quantity += quantity

        return total_quantity

    # MAGIC METHOD
    # Runs when:
    #
    # print(cart)
    #
    def __str__(self) -> str:

        return (
            f"Cart of {self.customer.name} | "
            f"Items: {len(self)} | "
            f"Total: ₹{self.total()}"
        )


# ============================================================
# TOPIC 12: ABC - ABSTRACT BASE CLASS
# ============================================================

class PaymentProcessor(ABC):

    # Every child class MUST implement pay().
    @abstractmethod
    def pay(self, amount: float) -> str:
        pass


class UPIPayment(PaymentProcessor):

    def pay(self, amount: float) -> str:
        return f"₹{amount} paid using UPI"


class CardPayment(PaymentProcessor):

    def pay(self, amount: float) -> str:
        return f"₹{amount} paid using Card"


# ============================================================
# ABC + POLYMORPHISM
# ============================================================

def checkout(
    cart: Cart,
    payment_processor: PaymentProcessor
) -> str:

    amount = cart.total()

    # We don't care whether payment_processor is:
    #
    # UPIPayment
    # CardPayment
    #
    # Both obey PaymentProcessor.
    return payment_processor.pay(amount)


# ============================================================
# TOPIC 13: PROTOCOL
# TOPIC 7: DUCK TYPING
# ============================================================

class NotificationService(Protocol):

    # Any object having this method structure
    # can behave like NotificationService.
    def send(self, message: str) -> None:
        ...


class EmailNotifier:

    # Notice:
    # EmailNotifier does NOT inherit NotificationService.
    #
    # But it has send(), so it satisfies the Protocol.
    def send(self, message: str) -> None:
        print(f"EMAIL: {message}")


class SMSNotifier:

    def send(self, message: str) -> None:
        print(f"SMS: {message}")


def send_notification(
    notifier: NotificationService,
    message: str
) -> None:

    # DUCK TYPING:
    #
    # If it has a usable send() method,
    # we can use it.
    notifier.send(message)


# ============================================================
# TOPIC 10: CLASS-BASED CONTEXT MANAGER
# ============================================================

class DatabaseConnection:

    def __enter__(self):

        # Setup/open resource.
        print("Opening database connection")

        # return self becomes:
        #
        # with DatabaseConnection() as db
        #
        # db = self
        return self

    def save_order(
        self,
        customer: Customer,
        cart: Cart,
        payment_result: str
    ) -> None:

        print(
            f"Saving order for {customer.name}, "
            f"total ₹{cart.total()}"
        )

        print(payment_result)

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        # Cleanup runs when with-block finishes.
        print("Closing database connection")

        # False means:
        # if an exception happened,
        # do not silently suppress it.
        return False


# ============================================================
# TOPIC 14: PYDANTIC + FASTAPI BRIDGE
# ============================================================

app = FastAPI()


class OrderRequest(BaseModel):

    # Pydantic validates incoming API data at runtime.

    customer_name: str
    customer_email: str

    product_id: int

    # Must be greater than zero.
    quantity: int = Field(gt=0)

    payment_method: str


# Some products already available in our store.

PRODUCT_CATALOG = {

    1: PhysicalProduct(
        name="Mechanical Keyboard",
        price=3000,
        weight=0.8
    ),

    2: DigitalProduct(
        name="Python Course",
        price=1500,
        download_link="https://example.com/python-course"
    )
}


@app.post("/orders")
def create_order(request: OrderRequest):

    # --------------------------------------------------------
    # STEP 1:
    # Validate email using STATIC METHOD.
    # --------------------------------------------------------

    if not Store.is_valid_email(request.customer_email):

        raise HTTPException(
            status_code=400,
            detail="Invalid email"
        )

    # --------------------------------------------------------
    # STEP 2:
    # Find product.
    # --------------------------------------------------------

    product = PRODUCT_CATALOG.get(request.product_id)

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # --------------------------------------------------------
    # STEP 3:
    # Create DATACLASS object.
    # --------------------------------------------------------

    customer = Customer(
        name=request.customer_name,
        email=request.customer_email
    )

    # --------------------------------------------------------
    # STEP 4:
    # COMPOSITION.
    #
    # Cart receives Customer.
    # --------------------------------------------------------

    cart = Cart(customer)

    cart.add_product(
        product,
        request.quantity
    )

    # --------------------------------------------------------
    # STEP 5:
    # Choose payment implementation.
    # --------------------------------------------------------

    if request.payment_method.lower() == "upi":

        payment_processor: PaymentProcessor = UPIPayment()

    elif request.payment_method.lower() == "card":

        payment_processor = CardPayment()

    else:

        raise HTTPException(
            status_code=400,
            detail="Payment method must be upi or card"
        )

    # --------------------------------------------------------
    # STEP 6:
    # POLYMORPHISM.
    #
    # checkout() doesn't care whether processor is
    # UPI or Card.
    # --------------------------------------------------------

    payment_result = checkout(
        cart,
        payment_processor
    )

    # --------------------------------------------------------
    # STEP 7:
    # CLASS-BASED CONTEXT MANAGER.
    # --------------------------------------------------------

    with DatabaseConnection() as db:

        db.save_order(
            customer,
            cart,
            payment_result
        )

    # --------------------------------------------------------
    # STEP 8:
    # PROTOCOL + DUCK TYPING.
    # --------------------------------------------------------

    notifier: NotificationService = EmailNotifier()

    send_notification(
        notifier,
        "Your order has been created successfully"
    )

    # --------------------------------------------------------
    # STEP 9:
    # CLASS ATTRIBUTE.
    # --------------------------------------------------------

    Store.total_orders += 1

    # --------------------------------------------------------
    # STEP 10:
    # Return API response.
    # --------------------------------------------------------

    return {
        "customer": customer.name,
        "product": product.name,
        "quantity": request.quantity,
        "total": cart.total(),
        "payment": payment_result,
        "delivery": product.delivery_info(),
        "total_orders": Store.total_orders
    }


# ============================================================
# NORMAL PYTHON OBJECT CALLS
# ============================================================

if __name__ == "__main__":

    print("\n--- STORE ---")

    # Creating an OBJECT from Store class.
    store = Store("Akshay")

    # INSTANCE METHOD
    store.show_owner()

    # CLASS ATTRIBUTE
    print(Store.store_name)

    # CLASS METHOD
    Store.change_store_name("AI Engineer Store")

    print(Store.store_name)

    # STATIC METHOD
    print(
        Store.is_valid_email(
            "akshay@example.com"
        )
    )


    print("\n--- PRODUCTS ---")

    keyboard = PhysicalProduct(
        name="Keyboard",
        price=2500,
        weight=0.7
    )

    course = DigitalProduct(
        name="FastAPI Course",
        price=1000,
        download_link="https://example.com/course"
    )

    # __str__() automatically runs.
    print(keyboard)
    print(course)


    print("\n--- PROPERTY / SETTER ---")

    # READING:
    #
    # keyboard.price
    #
    # calls @property.
    print(keyboard.price)

    # ASSIGNING:
    #
    # keyboard.price = 2800
    #
    # calls @price.setter.
    keyboard.price = 2800

    print(keyboard.price)

    # Uncomment this:
    #
    # keyboard.price = -500
    #
    # Setter will reject it.


    print("\n--- POLYMORPHISM ---")

    # Same function.
    # Different object types.
    #
    # Python chooses correct delivery_info().
    show_delivery(keyboard)
    show_delivery(course)


    print("\n--- DATACLASS ---")

    customer = Customer(
        name="Rahul",
        email="rahul@example.com"
    )

    # Dataclass gives us readable representation automatically.
    print(customer)


    print("\n--- COMPOSITION ---")

    # Cart HAS-A Customer.
    cart = Cart(customer)

    # Cart also HAS products.
    cart.add_product(
        keyboard,
        quantity=2
    )

    cart.add_product(
        course,
        quantity=1
    )

    # __str__ automatically runs.
    print(cart)

    # __len__ automatically runs.
    print("Total quantity:", len(cart))

    print("Cart total:", cart.total())


    print("\n--- ABC + POLYMORPHISM ---")

    upi = UPIPayment()

    result = checkout(
        cart,
        upi
    )

    print(result)

    card = CardPayment()

    result = checkout(
        cart,
        card
    )

    print(result)


    print("\n--- PROTOCOL / DUCK TYPING ---")

    email_notifier = EmailNotifier()

    send_notification(
        email_notifier,
        "Payment successful"
    )

    sms_notifier = SMSNotifier()

    send_notification(
        sms_notifier,
        "Order shipped"
    )


    print("\n--- CONTEXT MANAGER ---")

    with DatabaseConnection() as db:

        db.save_order(
            customer,
            cart,
            "Payment completed"
        )


    print("\n--- MAGIC METHOD equality ---")

    product1 = Product(
        "Mouse",
        500
    )

    product2 = Product(
        "Mouse",
        500
    )

    # Calls Product.__eq__()
    print(product1 == product2)