# Here are some classes I created, which I was going to use but ended up not:

from uuid import uuid4


class Address(object):  # Just a simple struct
    def __init__(self, street, city, state, zip_code, country):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country


class Name(object):  # Just a simple struct
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


class Person(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.id = uuid4().get_hex()

    def __repr__(self):
        return self.name.__dict__, self.address.__dict__, self.id
