from enum import Enum


class KallatPlotStatus(Enum):
    EMPTY_PLOT = "Empty Plot"
    BOOKED = "Booked"
    WIP = "Work In Progress"
    COMPLETED = "Completed"

    # The following are to be deprecated / moved somewhere else
    FOUNDATION_COMPLETED = "Foundation Completed"
    FIRST_FLOOR_SLAB_COMPLETED = "1st Floor Slab Completed"
    STRUCTURE_COMPLETED = "Structure Completed"
    TILING_COMPLETED = "Tiling Completed"
    HAND_OVER_COMPLETED = "Hand Over Completed"


class UnitSaleStatus(Enum):
    BOOKED = "Booked"
    AGREEMENT_SIGNED = "Agreement Signed"
    WIP = "Work In Progress"
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
