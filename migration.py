from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

    reviews = relationship('Review', back_populates='restaurant')
    customers = relationship('Customer', secondary='reviews', back_populates='restaurants', overlaps="reviews")

    @classmethod
    def fanciest(cls):
        return max(cls.query.all(), key=lambda r: r.price)

    def all_reviews(self):
        return [review.full_review() for review in self.reviews]


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    reviews = relationship('Review', back_populates='customer', overlaps="customers")
    restaurants = relationship('Restaurant', secondary='reviews', back_populates='customers', overlaps="reviews")

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        if not self.reviews:
            return None
        return max(self.reviews, key=lambda r: r.star_rating).restaurant

    def add_review(self, restaurant, rating):
        new_review = Review(star_rating=rating, restaurant=restaurant, customer=self)
        session.add(new_review)
        session.commit()

    def delete_reviews(self, restaurant):
        reviews_to_delete = [review for review in self.reviews if review.restaurant == restaurant]
        for review in reviews_to_delete:
            session.delete(review)
        session.commit()

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    star_rating = Column(Integer, nullable=False)
    feedback = Column(String(250), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    restaurant = relationship("Restaurant", back_populates="reviews", overlaps="customers,restaurants")
    customer = relationship("Customer", back_populates="reviews", overlaps="customers,restaurants")

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."





# ORM setup
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Create Restaurants
restaurant1 = Restaurant(name="Restaurant A", price=3)
restaurant2 = Restaurant(name="Restaurant B", price=2)
restaurant3 = Restaurant(name="Restaurant C", price=4)

# Create Customers
customer1 = Customer(first_name="John", last_name="Doe")
customer2 = Customer(first_name="Jane", last_name="Smith")
customer3 = Customer(first_name="Bob", last_name="Johnson")

# Add Restaurants and Customers to the session
session.add_all([restaurant1, restaurant2, restaurant3, customer1, customer2, customer3])
session.commit()

# Create Reviews
review1 = Review(star_rating=4, feedback="Good", restaurant=restaurant1, customer=customer1)
review2 = Review(star_rating=5, feedback="Excellent", restaurant=restaurant2, customer=customer1)
review3 = Review(star_rating=3, feedback="Average", restaurant=restaurant3, customer=customer2)
review4 = Review(star_rating=2, feedback="Poor", restaurant=restaurant1, customer=customer3)

# Add Reviews to the session
session.add_all([review1, review2, review3, review4])
session.commit()
