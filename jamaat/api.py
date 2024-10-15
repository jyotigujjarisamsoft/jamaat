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
def create_user_on_approve(email_id, first_name, password, hof_its_number, form_name, purpose):
    # Check if the user already exists
    if not frappe.db.exists("User", email_id):
        # Create a new User document
        all_modules = frappe.get_all('Module Def', fields=['module_name'])

        # Create a list of modules to block (exclude "Jamaat")
        block_modules = [{"module": module.module_name} for module in all_modules if module.module_name != "Jamaat"]

        user = frappe.get_doc({
            "doctype": "User",
            "email": email_id,
            "first_name": first_name,
            "enabled": 1,
            "send_welcome_email": 0,
            "roles": [{"role": "ITS Member"}],  # Assign ITS Member role
            "block_modules": block_modules,  # Block all except "Jamaat"
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
        if not frappe.db.exists("Household Details", {"its_number": hof_its_number}):
            # Create Contact Details doctype
            contact_details = frappe.get_doc({
                "doctype": "Household Details",
                "its_number": hof_its_number,
                # Add more fields here if needed
            })
            contact_details.insert(ignore_permissions=True)
        else:
            frappe.log_error(f"Household Details for ITS Number {hof_its_number} already exist.")

        # Determine Muwasaat form URL based on purpose
        if purpose == "Household":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/household/{form_name}"
        elif purpose == "Education":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/education/{form_name}"
        elif purpose == "Medical":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/medical/{form_name}"
        else:
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/muwasaat-main-application-/{form_name}"

        # Generate the link to the Contact Details
        form_url = f"https://muwasaat.anjuman-najmi.com/webform-application/{hof_its_number}"
        muwasaat_url_app = f"https://muwasaat.anjuman-najmi.com"
        # Send the email
        frappe.sendmail(
            recipients=[email_id],
            subject="AEN Muwasaat Application Account Creation – Next Steps for Application Processing",
            message=f"""
            Dear {first_name},<br><br>

            We are pleased to inform you that your account has been successfully created.<br>
            Your Application is unique to your ITS No. only. Do not share it with anyone else.<br><br>

            Please follow the steps below to proceed with your application:<br>
            1. Click the link below and log in using the credentials provided.<br>
            2. Complete all the required information in the Muwasaat Form and submit your application.<br>
            3. Attach all relevant attachments to the application in a single PDF file. The size of this PDF file should not exceed 1000 KB.<br>
            4. Please verify all entered information accurately. Inaccurate or incomplete applications will be rejected.<br>
            5. After verification, your application will be sent to the Marafiq Burhaniyah Team for further processing, and you will receive an email regarding the status of your application.<br><br>

            <strong>Login Credentials:</strong><br>
            
            Muwasaat URL: <a href="{muwasaat_url_app}">{muwasaat_url_app}</a><br>
            Username: {email_id}<br>
            Password: {password}<br><br>

            If you have any questions or need further assistance, feel free to contact us.<br><br>

            Wassalam,<br>
            Umoor Marafiq Burhaniyah<br>
            Anjuman Najmi, Dubai.
            """
        )

        return "User, related doctypes created and email sent successfully!"
    else:
        # User already exists case
        # Determine Muwasaat form URL based on purpose
        if purpose == "Household":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/household/{form_name}"
        elif purpose == "Education":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/education/{form_name}"
        elif purpose == "Medical":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/medical/{form_name}"
        else:
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/muwasaat-main-application-/{form_name}"
        muwasaat_url_app = f"https://muwasaat.anjuman-najmi.com"
        frappe.sendmail(
            recipients=[email_id],
            subject="AEN Muwasaat Application Created – Next Steps for Application Processing",
            message=f"""
            Dear {first_name},<br><br>

            We are pleased to inform you that your application has been successfully created.<br>
            Your Application is unique to your ITS No. only. Do not share it with anyone else.<br><br>

            Please follow the steps below to proceed with your application:<br>
            1. Click the link below and log in using the credentials provided.<br>
            2. Complete all the required information in the Muwasaat Form and submit your application.<br>
            3. Attach all relevant attachments to the application in a single PDF file. The size of this PDF file should not exceed 1000 KB.<br>
            4. Please verify all entered information accurately. Inaccurate or incomplete applications will be rejected.<br>
            5. After verification, your application will be sent to the Marafiq Burhaniyah Team for further processing, and you will receive an email regarding the status of your application.<br><br>

            <strong>Login Credentials:</strong><br>
            Application URL: <a href="{muwasaat_url_app}">{muwasaat_url_app}</a><br>
            Username: {email_id}<br>
            Password: {password}<br><br>

            If you have any questions or need further assistance, feel free to contact us.<br><br>

            Wassalam,<br>
            Umoor Marafiq Burhaniyah<br>
            Anjuman Najmi, Dubai.
            """
        )
        return "User already exists and mail sent successfully."



@frappe.whitelist()
def create_tracker(application_id, applicant_its_no, purpose, first_name, mohalla, 
                    hof_its_number,
                   application_date, enayat_araz_aed_for_education,
                    enayat_araz_aed_for_medical,
                   enayat_araz_aed_for_household, email_id,hof_mobile_no):
    # Check if the user already exists
    print("Entered in tracker doctype")

    # Fetch specific details from the Mohalla table
    mohalla_details = frappe.db.sql("""
        SELECT mb_team_member_name, rafiq, rafiq_contact_no, rafiq_name, amil_saheb_name,
               amil_saheb, amil_saheb_contact_no, mushrif_name, mushrif_contact_no,
               rafiq_email_id, mb_team_member, amil_saheb_email_id, mb_team_member_email_id,
               mushrif_email_id, mb_team_member_contact_no,
               finance_team_member_its_no,finance_team_member_name,
               finance_team_email_id,finance_team_contact_no
        FROM `tabMohalla` WHERE mohalla=%s
    """, (mohalla,), as_dict=True)
    print("mohalla_details",mohalla_details)

    # Fetch specific details from the KG Details table with additional filters
    kg_details = frappe.db.sql("""
        SELECT its_no, full_name, mobile_no, email_id 
        FROM `tabKG Details` 
        WHERE mohalla=%s AND role='SP Team Leader' AND purpose=%s
    """, (mohalla, purpose), as_dict=True)
    print("kg_details",kg_details)

    if purpose == "Education":
        muwasaat_amount_required = enayat_araz_aed_for_education
    elif purpose == "Household":
        muwasaat_amount_required = enayat_araz_aed_for_household
    elif purpose == "Medical":
        muwasaat_amount_required = enayat_araz_aed_for_medical
    # Create Muwasaat Tracker doctype
    tracker_details = frappe.get_doc({
        "doctype": "Muwasaat Tracker",
        "application_id": application_id,
        "applicant_its_no": applicant_its_no,
        "purpose": purpose,
        "applicant_name": first_name,
        "mohalla": mohalla,
        "application_date": application_date,
        "muwasaat_amount_required": muwasaat_amount_required,
        "email":email_id,
        "applicant_contact_no":hof_mobile_no,

        "amil_saheb_name":mohalla_details[0]['amil_saheb_name'],
        "assigned_mb_team_member":mohalla_details[0]['mb_team_member_name'],
        "rafiq_name":mohalla_details[0]['rafiq_name'],
        
        'rafiq_assigned':mohalla_details[0]['rafiq_name'],
        'rafiq_its_no': mohalla_details[0]['rafiq'],
        'rafiq_assigned_mobile': mohalla_details[0]['rafiq_contact_no'],
        'rafiq_email_id': mohalla_details[0]['rafiq_email_id'],

        'amil_saheb_its_no': mohalla_details[0]['amil_saheb'],
        'amil_saheb_assigned': mohalla_details[0]['amil_saheb_name'],
        'amil_saheb_mobile': mohalla_details[0]['amil_saheb_contact_no'],
        'amil_saheb_email_id': mohalla_details[0]['amil_saheb_email_id'],

        'mushrif_assigned': mohalla_details[0]['mushrif_name'],
        'mushrif_mobile': mohalla_details[0]['mushrif_contact_no'],
        'mushrif_email_id': mohalla_details[0]['mushrif_email_id'],

        'mb_team_member_its_no': mohalla_details[0]['mb_team_member'],
        'mb_team_member_full_name': mohalla_details[0]['mb_team_member_name'],
        'mb_team_member_mobile_no': mohalla_details[0]['mb_team_member_contact_no'],
        'mb_team_member_email_address': mohalla_details[0]['mb_team_member_email_id'],

        'sp_team_lead_name': kg_details[0]['full_name'],
        'sp_team_lead_its_no':  kg_details[0]['its_no'],
        'sp_team_tl_mobile':  kg_details[0]['mobile_no'],
        'mobile_no':  kg_details[0]['email_id'],

        'finance_its_number':mohalla_details[0]['finance_team_member_its_no'],
        'finance_team_member_name':mohalla_details[0]['finance_team_member_name'],
        'finance_mobile_numbe':mohalla_details[0]['finance_team_contact_no'],
        'finance_team_mail_id':mohalla_details[0]['finance_team_email_id'],

        'finance_team_its_no':mohalla_details[0]['finance_team_member_its_no'],
        'finance_membre_name':mohalla_details[0]['finance_team_member_name'],
        'finance_mobile_no':mohalla_details[0]['finance_team_contact_no'],
        'finance_mail_id':mohalla_details[0]['finance_team_email_id'],
        
        # Add more fields here if needed
    })
    
    print("Created in tracker doctype")
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
def check_previous_musawaat_data_education(purpose, its, application_for_the_year):
    # Check if the user already exists
    print("entered in education_form_details doctype")
    # Create Contact Details doctype
    education_form_details = frappe.db.sql("""
        SELECT c.its,c.parent
        FROM `tabMuwasaat Form` AS m
        JOIN `tabMultiple Children Details` AS c 
        ON m.name = c.parent 
        and m.purpose = %s AND c.its = %s AND m.application_for_the_year = %s
        """, (purpose, its, application_for_the_year), as_dict=True)
    
    print("check_previous_musawaat_data_education", education_form_details)
    return education_form_details



        

