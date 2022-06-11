frappe.provide("kallat")

/**
 * Returns if the User can modify the timestamp manually
 * - Used in UnitSale's forms
 * @returns Boolean
 */
kallat.can_modify_timestamp = function () {
    return !!frappe.boot.kallat_modify_timestamp;
}