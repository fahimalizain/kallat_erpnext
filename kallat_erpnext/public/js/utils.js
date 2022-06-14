frappe.provide("kallat")

/**
 * Returns if the User can modify the timestamp manually
 * - Used in UnitSale's forms
 * @returns Boolean
 */
kallat.maintenance_mode = function () {
    return !!frappe.boot.kallat_modify_timestamp;
}