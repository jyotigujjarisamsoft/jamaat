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
def create_user_on_approve(email_id, first_name, password, its_number):
    # Check if the user already exists
    if not frappe.db.exists("User", email_id):
        # Create a new User document
        user = frappe.get_doc({
            "doctype": "User",
            "email": email_id,
            "first_name": first_name,
            "enabled": 1,
            "send_welcome_email":0,
            "roles": [{"role": "ITS Member"}],  # Assign ITS Member role
            "new_password": password  # Set the password
        })
        user.insert(ignore_permissions=True)

        # Create User Permission for the ITS number
        user_permission = frappe.get_doc({
            "doctype": "User Permission",
            "user": email_id,
            "allow": "ITS Data",  # Change this if the doctype is different
            "for_value": its_number,  # Set the ITS number here
            "apply_to_all_doctypes": 1  # Apply to all document types
        })
        user_permission.insert(ignore_permissions=True)
        form_details = frappe.db.sql("""
        SELECT
            name AS form_name
            
        FROM
            `tabMuwasaat Form`
        
        WHERE
            its_no = '"""+its_number+"""'
    """, as_dict=True)
        print("form_details",form_details[0]['form_name'])
        name=form_details[0]['form_name']
        # Generate the link to the Muwasaat Form
        form_url = f"https://dubaijamaat.frappe.cloud/app/muwasaat-form/{name}"

        # Send the email
        frappe.sendmail(
            recipients=[email_id],
            subject="Access to Muwasaat Form",
            message=f"""
            Dear {first_name},

            Your account has been created successfully. You can now access the Muwasaat Form by clicking the link below:

            <a href="{form_url}">{form_url}</a>

            Use the following credentials to log in:
            Username: {email_id}
            Password: {password}

            Regards,
            Your Company
            """
        )

        return "User created and email sent successfully!"

        

