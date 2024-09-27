from __future__ import unicode_literals
from xml.etree.ElementTree import tostring
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
from datetime import date
import json 

@frappe.whitelist()
def fetch_comments(reference_name,its_no):
	#print("filters",type(filters))
	print("itereference_namems",reference_name)
	comments = frappe.db.sql("""select content from `tabComment` where 
	reference_name=%(reference_name)s""",
	{'reference_name':reference_name}, as_dict=1)
	print("comments",comments)
	contents = [comment['content'] for comment in comments if comment['content'] is not None]
	print("-----",contents)
	for comment in comments:
		if comment['content'] is not None:
			print("comment---", comment['content'])
			comment=comment['content']
			additional_line = '<div>' + reference_name + '</div>'
			comment_with_additional_line = comment + additional_line
			print("comment_with_additional_line",comment_with_additional_line)
			# Create your outer JSON payload
			outerJson_po = {
				"reference_doctype": "ITS Data",
				"doctype": "Comment",
				"comment_type": "Comment",
				"reference_name": its_no,
				"content":comment_with_additional_line
			}
		print("outerJson_po",outerJson_po)
		doc_new_po = frappe.new_doc("Comment")
		print("----------------------------")
		doc_new_po.update(outerJson_po)
		print("++++++++++++")
		doc_new_po.save()
		frappe.db.commit()

@frappe.whitelist()
def create_user_on_approve(email_id, first_name, password, hof_its_number,form_name):
    # Check if the user already exists
    if not frappe.db.exists("User", email_id):
        # Create a new User document
        user = frappe.get_doc({
            "doctype": "User",
            "email": email_id,
            "first_name": first_name,
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": "ITS Member"}],  # Assign ITS Member role
            "new_password": password  # Set the password
        })
        user.insert(ignore_permissions=True)

        # Create User Permission for the ITS number
        user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": email_id,
            "allow": "ITS Data",
            "for_value": hof_its_number,
            "apply_to_all_doctypes": 1
        })
        user_permission.insert(ignore_permissions=True)

        # Check if Contact Details already exist
        if not frappe.db.exists("Contact Details", {"its_number": hof_its_number}):
            # Create Contact Details doctype
            contact_details = frappe.get_doc({
                "doctype": "Contact Details",
                "its_number": hof_its_number,
                # Add more fields here if needed
            })
            contact_details.insert(ignore_permissions=True)
        else:
            frappe.log_error(f"Contact Details for ITS Number {hof_its_number} already exist.")

        # Check if Household Budget already exists
        if not frappe.db.exists("Household Budget Main", {"its_number": hof_its_number}):
            # Create Household Budget doctype
            household_budget = frappe.get_doc({
                "doctype": "Household Budget Main",
                "its_number": hof_its_number,
                # Add more fields here if needed
            })
            household_budget.insert(ignore_permissions=True)
        else:
            frappe.log_error(f"Household Budget for ITS Number {hof_its_number} already exist.")

        # Fetch form details based on ITS number
        form_details = frappe.db.sql("""
            SELECT
                name AS form_name
            FROM
                `tabContact Details`
            WHERE
                its_number = %s
        """, hof_its_number, as_dict=True)

        if form_details:
            name = form_details[0]['form_name']
            # Generate the link to the Muwasaat Form
            form_url = f"https://muwasaat.anjuman-najmi.com/app/contact-details/{hof_its_number}"

            # Send the email
            frappe.sendmail(
                recipients=[email_id],
                subject="Access to Muwasaat Form",
                message=f"""
                Dear {first_name},

                Your account has been created successfully.Please fallow below step to Process your application.
                1.Please click on the link below  and login with credentials provided.
                2.Fill all data provided in Contact Details Application and submit.
                3.Fill all data in Householdhold Budget Main Application and Submit.
                4.Once you click on submit button you will redirect to Muwasaat Form List.
                5.Now click on application you created and fill all sections and save.
                6.After filling all data please check Application Filled checkbox and save again after your application you go for verification.
                7.Once verification is completed,you will receive an email for Application Status.

                <a href="{form_url}">{form_url}</a>

                Use the following credentials to log in:
                Username: {email_id}
                Password: {password}

                Regards,
                
                """
            )

        return "User, related doctypes Created and email sent successfully!"
    else:
        print("user already exist")
        # Fetch form details based on ITS number
        form_details = frappe.db.sql("""
            SELECT
                name AS form_name
            FROM
                `tabMuwasaat Form`
            WHERE
                hof_its_number = %s
        """, hof_its_number, as_dict=True)

        if form_details:
            name = form_details[0]['form_name']
            # Generate the link to the Muwasaat Form
            #form_url = f"http://127.0.0.1:8000/app/contact-details/{its_number}"

            form_url = f"https://muwasaat.anjuman-najmi.com/app/muwasaat-form/{form_name}"

            # Send the email
            frappe.sendmail(
                recipients=[email_id],
                subject="Access to Muwasaat Form",
                message=f"""
                Dear {first_name},

                Your account has been created successfully.Please fallow below step to Process your application.
                1.Please click on the link below  and login with credentials provided.
                2.Fill all data provided in Muwasaat Form Application and submit.
                3.Once verification is completed,you will receive an email for Application Status.

                <a href="{form_url}">{form_url}</a>

                Use the following credentials to log in:
                Username: {email_id}
                Password: {password}

                Regards,
                Your Company
                """
            )
        return "User already exists and sent mail Successfully"


@frappe.whitelist()
def create_tracker(application_id, applicant_its_no):
    # Check if the user already exists
    print("entered in tracker doctype")
    # Create Contact Details doctype
    tracker_details = frappe.get_doc({
        "doctype": "Muwasaat Tracker",
        "application_id":application_id,
        "applicant_its_no": applicant_its_no

        # Add more fields here if needed
    })
    print("created in tracker doctype")
    tracker_details.insert(ignore_permissions=True)

    
@frappe.whitelist()
def check_previous_musawaat_data(purpose, hof_its_number, application_for_the_year):
    # Check if the user already exists
    print("entered in tracker doctype")
    # Create Contact Details doctype
    form_details = frappe.db.sql("""
        SELECT
            name,application_for_the_year,Purpose,hof_its_number
        FROM
            `tabMuwasaat Form`
        WHERE
            purpose = %s AND hof_its_number = %s AND application_for_the_year = %s
        """, (purpose, hof_its_number, application_for_the_year), as_dict=True)
    
    print("check_previous_musawaat_data", form_details)
    return form_details

@frappe.whitelist()
def check_previous_musawaat_data_education(purpose, hof_its_number, application_for_the_year):
    # Check if the user already exists
    print("entered in education_form_details doctype")
    # Create Contact Details doctype
    education_form_details = frappe.db.sql("""
        SELECT c.its,c.parent
        FROM `tabMuwasaat Form` AS m
        JOIN `tabMultiple Children Details` AS c 
        ON m.name = c.parent 
        and m.purpose = %s AND c.its = %s AND m.application_for_the_year = %s
        """, (purpose, hof_its_number, application_for_the_year), as_dict=True)
    
    print("check_previous_musawaat_data_education", education_form_details)
    return education_form_details



        

