// Copyright (c) 2022, Fahim Ali Zain and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Kallat Fund Flow"] = {
	"filters": [
		{
			label: "Month",
			fieldtype: "Select",
			options: "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			fieldname: "month",
			default: moment().format("MMMM"),
		},
		{
			label: "Year",
			fieldtype: "Int",
			fieldname: "year",
			default: moment().format("YYYY"),
		}
	]
};
