frappe.query_reports["Miqaat Attendance Details"] = {

    "filters": [
        {
            "fieldname": "miqaat",
            "label": __("Miqaat Name"),
            "fieldtype": "Link",
            "options": "Miqaat"
        },
        {
            "fieldname": "its_no",
            "label": __("ITS No"),
            "fieldtype": "Link",
            "options": "ITS Data"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        // Apply conditional formatting based on 'colour' value
        if (data.colour <4) {
            value = `<span style="background-color: green; color: white;">${value}</span>`;
        }else if (data.colour>4 && data.colour<7 ) {
            value = `<span style="background-color: red; color: white;">${value}</span>`;
        }
		else if (data.colour >7 && data.colour <9) {
            value = `<span style="background-color: yellow; color: white;">${value}</span>`;
        }
		else if (data.colour >9 && data.colour <10) {
            value = `<span style="background-color: pink; color: white;">${value}</span>`;
        }else if (data.colour >10) {
            value = `<span style="background-color: blue; color: white;">${value}</span>`;
        }
        return default_formatter(value, row, column, data);
    },

    "after_datatable_render": function() {
        // Directly access the data attribute of the report
        let all_data = frappe.query_report.data;

        // Log all data rows to the console
        console.log("All Data Rows: ", all_data);

        // Example: Iterate over all data rows and log each row
        all_data.forEach(row => {
            console.log("Row Data: ", row);
        });
    }
};