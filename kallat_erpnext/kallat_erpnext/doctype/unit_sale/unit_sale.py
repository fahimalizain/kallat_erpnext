# Copyright (c) 2022, Fahim Ali Zain and contributors
# For license information, please see license.txt

from enum import Enum

# import frappe
from frappe.model.document import Document


class UnitSaleStatuses(Enum):
    BOOKED = "Booked"
    AGREEMENT_SIGNED = "Agreement Signed"
    EMPTY_PLOT = "Empty Plot"
    FOUNDATION_COMPLETED = "Foundation Completed"
    FIRST_FLOOR_SLAB_COMPLETED = "1st Floor Slab Completed"
    STRUCTURE_COMPLETED = "Structure Completed"
    TILING_COMPLETED = "Tiling Completed"
    HAND_OVER_COMPLETED = "Hand Over Completed"


class UnitSale(Document):
    pass
