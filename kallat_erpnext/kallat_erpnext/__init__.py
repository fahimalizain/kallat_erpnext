from enum import Enum


class KallatPlotStatus(Enum):
    EMPTY_PLOT = "Empty Plot"
    BOOKED = "Booked"
    WIP = "Work In Progress"
    COMPLETED = "Completed"


class UnitSaleStatus(Enum):
    NONE = ""
    BOOKED = "Booked"
    AGREEMENT_SIGNED = "Agreement Signed"
    WIP = "Work In Progress"
    HANDED_OVER = "Handed Over"
    COMPLETED = "Completed"


class UnitWorkStatus(Enum):
    NOT_STARTED = "Not Started"
    FOUNDATION_COMPLETED = "Foundation Completed"
    FIRST_FLOOR_SLAB_COMPLETED = "1st Floor Slab Completed"
    STRUCTURE_COMPLETED = "Structure Completed"
    TILING_COMPLETED = "Tiling Completed"


class UnitSaleEventType(Enum):
    UNIT_SALE_UPDATE = "Unit Sale Update"
    WORK_STATUS_UPDATE = "Work Status Update"
    PAYMENT_RECEIPT = "Payment Receipt"
    LATE_FEE_APPLIED = "Late Fee Applied"
    ADD_EXTRA_WORK = "Add Extra Work"
