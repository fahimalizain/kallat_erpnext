from faker import Faker

import frappe

from .tests import TestFixture


class CustomerFixtures(TestFixture):
    faker = Faker()

    def __init__(self):
        super().__init__()
        self.DEFAULT_DOCTYPE = "Customer"

    def make_dependencies(self):
        for i in range(10):
            customer = frappe.new_doc("Customer")
            customer.update(dict(
                customer_name=self.faker.first_name() + " " + self.faker.last_name(),
                customer_type="Individual",
            ))
            customer.insert()
            self.add_document(customer)
