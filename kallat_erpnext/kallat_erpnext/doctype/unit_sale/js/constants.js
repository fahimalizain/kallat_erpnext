frappe.provide("kallat.unit_sale")

kallat.unit_sale.UNIT_SALE_TYPE = {
    PAYMENT_RECEIPT: "Payment Receipt",
    UNIT_SALE_UPDATE: "Unit Sale Update",
    WORK_STATUS_UPDATE: "Work Status Update",
};

kallat.unit_sale.UNIT_SALE_STATUS = {
    BOOKED: "Booked",
    AGREEMENT_SIGNED: "Agreement Signed",
    WIP: "Work In Progress",
    HANDED_OVER: "Handed Over",
    COMPLETED: "Completed",
};

kallat.unit_sale.WORK_STATUS = {
    NOT_STARTED: "Not Started",
    FOUNDATION_COMPLETED: "Foundation Completed",
    FIRST_FLOOR_SLAB_COMPLETED: "1st Floor Slab Completed",
    STRUCTURE_COMPLETED: "Structure Completed",
    TILING_COMPLETED: "Tiling Completed",
    HAND_OVER_COMPLETED: "Hand Over Completed",
};

kallat.unit_sale.WORK_STATUSES = Object.values(kallat.unit_sale.WORK_STATUS);
