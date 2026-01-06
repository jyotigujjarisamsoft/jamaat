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
        elif purpose == "Others":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/others/{form_name}"
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
        elif purpose == "Others":
            muwasaat_url = f"https://muwasaat.anjuman-najmi.com/others/{form_name}"
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
                    enayat_araz_aed_for_medical,enayat_araz_aed_for_others,
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
        WHERE role='SP Team Leader' AND purpose=%s
    """, (purpose), as_dict=True)
    print("kg_details",kg_details)

    if purpose == "Education":
        muwasaat_amount_required = enayat_araz_aed_for_education
    elif purpose == "Household":
        muwasaat_amount_required = enayat_araz_aed_for_household
    elif purpose == "Medical":
        muwasaat_amount_required = enayat_araz_aed_for_medical
    elif purpose == "Others":
        muwasaat_amount_required = enayat_araz_aed_for_others
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
def check_previous_musawaat_data_education(purpose, its_no, application_for_the_year):
    # Check if the user already exists
    print("entered in education_form_details doctype")
    # Create Contact Details doctype
    education_form_details = frappe.db.sql("""
        SELECT c.its_no,c.parent
        FROM `tabMuwasaat Form` AS m
        JOIN `tabtest` AS c 
        ON m.name = c.parent  
        and m.purpose = %s AND c.its_no = %s AND m.application_for_the_year = %s
        """, (purpose, its_no, application_for_the_year), as_dict=True)
    
    print("check_previous_musawaat_data_education", education_form_details)
    return education_form_details


@frappe.whitelist()
def get_combined_data():
    query = """
        SELECT
            hd.its_number,
            hd.name AS household_name,
            hd.please_check_this_if_you_filled_all_data_before_submit AS household_status,
            mf.name AS muwasaat_name,
            mf.purpose AS muwasaat_purpose,
            mf.application_for_the_year AS muwasaat_application_year,
            mf.application_date,
            mf.docstatus,
            mf.please_check_this_before_submit AS muwasaat_status,
            mf.mohalla,
            mf.first_name,
            mf.hof_mobile_no
        FROM
            `tabHousehold Details` AS hd
        LEFT JOIN
            `tabMuwasaat Form` AS mf
        ON
            hd.its_number = mf.hof_its_number
    """
    data = frappe.db.sql(query, as_dict=True)
    return data

@frappe.whitelist()
def old_create_mbi_house_survey_form(hof_its_no):
    # Check if the MBI House Survey Form already exists for the given ITS number
    if not frappe.db.exists("MBI House Survey Form", {"hof_its_no": hof_its_no}):
        # Create new MBI House Survey Form
        its_details = frappe.get_doc({
            "doctype": "MBI House Survey Form",
            "hof_its_no": hof_its_no
        })
        its_details.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "message": "MBI House Survey Form created successfully."}
    else:
        frappe.log_error(f"MBI House Survey Form for ITS No {hof_its_no} already exists.")
        return {"status": "error", "message": f"MBI House Survey Form for ITS No {hof_its_no} already exists."}
        
@frappe.whitelist()
def create_mbi_house_survey_form(hof_its_no, full_name=None, email_address=None, mobile_no=None, mohalla=None):
    """
    Create or update MBI House Survey Form for the given ITS number.
    If record exists, update the provided fields; otherwise, create a new record.
    """
    existing = frappe.db.get_value("MBI House Survey Form", {"hof_its_no": hof_its_no}, ["name"], as_dict=True)

    if existing:
        # Update existing record
        doc = frappe.get_doc("MBI House Survey Form", existing["name"])
        doc.full_name = full_name or doc.full_name
        doc.email_address = email_address or doc.email_address
        doc.mobile_no = mobile_no or doc.mobile_no
        doc.mohalla = mohalla or doc.mohalla
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "message": "MBI House Survey Form already exists. Updated successfully."}

    else:
        # Create new record
        doc = frappe.new_doc("MBI House Survey Form")
        doc.hof_its_no = hof_its_no
        doc.full_name = full_name or ""
        doc.email_address = email_address or ""
        doc.mobile_no = mobile_no or ""
        doc.mohalla = mohalla or ""
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "message": "MBI House Survey Form created successfully."}

@frappe.whitelist()
def create_household_details_doctype(hof_its_no, full_name=None, email_address=None, mobile_no=None, mohalla=None):
    """
    Create or update MBI House Survey Form for the given ITS number.
    If record exists, update the provided fields; otherwise, create a new record.
    """
    existing = frappe.db.get_value("Household Details", {"its_number": hof_its_no}, ["name"], as_dict=True)

    if existing:
        # Update existing record
        doc = frappe.get_doc("Household Details", existing["name"])
        doc.full_name = full_name or doc.full_name
        doc.email_id = email_address or doc.email_address
        doc.mobile_number = mobile_no or doc.mobile_no
        doc.mohalla = mohalla or doc.mohalla
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "message": "Household Details already exists. Updated successfully."}

    else:
        # Create new record
        doc = frappe.new_doc("Household Details")
        doc.its_number = hof_its_no
        doc.full_name = full_name or ""
        doc.email_id = email_address or ""
        doc.mobile_number = mobile_no or ""
        doc.mohalla = mohalla or ""
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "message": "Household Details doctype created successfully."}

@frappe.whitelist()
def create_mbi_family_form(hof_its_no):
    # Fetch ITS data associated with the given hof_its_no
    its_data = frappe.db.sql("""
        SELECT *
        FROM `tabITS Data`
        WHERE hof_its_no = %s
    """, (hof_its_no,), as_dict=True)

    # Initialize a response dictionary
    response = {"messages": []}

    # Loop through each entry in the ITS data
    for entry in its_data:
        its_no = entry.get('name')  # Assuming 'name' is the unique identifier for each family member

        # Check if the MBI House Survey Form already exists for the given ITS number
        if not frappe.db.exists("MBI Form - Family", {"its_no": its_no}):
            # Create new MBI House Survey Form
            its_details = frappe.get_doc({
                "doctype": "MBI Form - Family",
                "its_no": its_no,
                "hof_its_no": hof_its_no,
                "relation_with_hof": entry.get('relation_with_hof'),
                "full_name": entry.get('full_name'),
                "email_id": entry.get('email_address'),
                "mobile_no": entry.get('mobile_no'),
                "mohalla": entry.get('mohalla')
                # Add other fields as required
            })
            its_details.insert(ignore_permissions=True)
            frappe.db.commit()
            response["messages"].append(f"Form created for ITS No: {its_no}.")
        else:
            response["messages"].append(f"Form for ITS No: {its_no} already exists.")

    # Finalize response
    if response["messages"]:
        return {"status": "success", "messages": response["messages"]}
    else:
        return {"status": "error", "messages": ["No operations performed."]}


@frappe.whitelist()
def get_session_user_sp_member():
    user_info = frappe.get_doc("User", frappe.session.user)
    email_id = user_info.email
    print("email_id",email_id)
    
    query = """
        SELECT
            *
        FROM
            `tabMuwasaat Tracker`
        WHERE
            mobile_no = %s
    """
    data = frappe.db.sql(query, (email_id), as_dict=True)
    print("data",data)
    return data

@frappe.whitelist()
def get_session_user_sp_lead():
    user_info = frappe.get_doc("User", frappe.session.user)
    email_id = user_info.email
    

    query = """
        SELECT
            *
        FROM
            `tabMuwasaat Tracker`
        WHERE
            sp_mobile_no = %s
    """
    data = frappe.db.sql(query, (email_id), as_dict=True)
    print("data",data)
    return data

@frappe.whitelist()
def fetch_family_details(application_id, hof_its_no, mohalla):
    if not application_id or not hof_its_no or not mohalla:
        frappe.throw("Application ID, HoF ITS Number, and Mohalla are required")

    # Fetch Family Details based on Application ID, HoF ITS Number, and Mohalla
    family_details = frappe.get_all(
        "Family Details",
        filters={
            "application_id": application_id,
            "hof_its_no": hof_its_no,
            "mohalla": mohalla
        },
        fields=["name", "application_id", "hof_its_no", "mohalla"]
    )
    print("family_details",family_details)
    parent_name = family_details[0].name
    if not family_details:
        return "No matching family details found."

    family_members = frappe.get_all(
        "Members Details",
        filters={"parent": parent_name},
        fields=["*"]  # Fetch all fields
    )
    print("family_members",family_members)

    # Create ITS Data for each family member
    for member in family_members:
        

        fts_data=frappe.new_doc("MBI Form - Family")
        fts_data.hof_its_no = hof_its_no
        fts_data.mohalla = mohalla
        fts_data.its_no = member.get("its_no")
        fts_data.full_name = member.get("full_name")
        fts_data.age = member.get("age")
        fts_data.gender = member.get("gender")
        fts_data.mobile_no = member.get("mobile_no")
        fts_data.email_id = member.get("email_address")
        fts_data.select_this_persons_relationship_with_hof = member.get("relation_with_hof")
        
        
        # Save the new ITS Data record
        fts_data.insert()
        fts_data.save()

    hof_data = frappe.get_doc("ITS Data", {"hof_its_no": hof_its_no, "its_no": hof_its_no})
    print("hof_data",hof_data)
    if hof_data:
        hof_mbi_form = frappe.new_doc("MBI Form - Family")
        hof_mbi_form.hof_its_no = hof_its_no
        hof_mbi_form.mohalla = mohalla
        hof_mbi_form.its_no = hof_data.its_no
        hof_mbi_form.full_name = hof_data.full_name
        hof_mbi_form.age = hof_data.age
        hof_mbi_form.gender = hof_data.gender
        hof_mbi_form.mobile_no = hof_data.mobile_no
        hof_mbi_form.email_id = hof_data.email_address
        hof_mbi_form.select_this_persons_relationship_with_hof = "HOF"
        hof_mbi_form.insert()
        hof_mbi_form.save()


    return family_details

@frappe.whitelist()
def create_its_data_and_details(data):
    import json
    from frappe import msgprint

    data = json.loads(data) if isinstance(data, str) else data
    hof = data.get("hof")
    family_members = data.get("family_members", [])

    if not hof:
        msgprint("Missing HOF data.")
        return

    hof_its_no = hof.get("its_no")
    if not hof_its_no:
        msgprint("HOF its_no is required.")
        return

    # --- Step 1: Sync with ITS Details (Parent Doctype) ---
    existing_details_name = frappe.db.get_value("ITS Data and Form Creation", {"hof_its_id": hof_its_no}, "name")

    if existing_details_name:
        details_doc = frappe.get_doc("ITS Data and Form Creation", existing_details_name)
        details_doc.hof_full_name = hof.get("full_name")
        details_doc.email_address = hof.get("email_address")
        details_doc.mohalla = hof.get("mohalla")
        details_doc.mobile_no = hof.get("mobile_no")
        details_doc.jamaat_clearance = hof.get("jamaat_clearance")
        details_doc.save(ignore_permissions=True)
        msgprint(f"ITS Data updated: {details_doc.name}")
    else:
        details_doc = frappe.new_doc("ITS Data and Form Creation")
        details_doc.hof_its_id = hof_its_no
        details_doc.hof_full_name = hof.get("full_name")
        details_doc.email_address = hof.get("email_address")
        details_doc.mohalla = hof.get("mohalla")
        details_doc.mobile_no = hof.get("mobile_no")
        details_doc.jamaat_clearance = hof.get("jamaat_clearance")
        details_doc.insert(ignore_permissions=True)
        msgprint(f"ITS Details created: {details_doc.name}")

    # --- Step 2: Sync with ITS Data for HOF ---
    existing_hof_name = frappe.db.get_value("ITS Data", {"its_no": hof_its_no}, "name")

    if existing_hof_name:
        hof_doc = frappe.get_doc("ITS Data", existing_hof_name)
        hof_doc.full_name = hof.get("full_name")
        hof_doc.mohalla = hof.get("mohalla")
        hof_doc.mobile_no = hof.get("mobile_no")
        hof_doc.email_address = hof.get("email_address")
        hof_doc.hof_fm_type = hof.get("hof_or_family_member")
        hof_doc.sabeel_clearance = hof.get("jamaat_clearance")
        hof_doc.hof_its_no = hof_its_no
        hof_doc.save(ignore_permissions=True)
        msgprint(f"HOF in ITS Data updated: {hof_doc.name}")
    else:
        hof_doc = frappe.new_doc("ITS Data")
        hof_doc.its_no = hof_its_no
        hof_doc.full_name = hof.get("full_name")
        hof_doc.mohalla = hof.get("mohalla")
        hof_doc.mobile_no = hof.get("mobile_no")
        hof_doc.email_address = hof.get("email_address")
        hof_doc.hof_fm_type = hof.get("hof_or_family_member")
        hof_doc.sabeel_clearance = hof.get("jamaat_clearance")
        hof_doc.hof_its_no = hof_its_no
        hof_doc.insert(ignore_permissions=True)
        msgprint(f"HOF in ITS Data created: {hof_doc.name}")

    # --- Step 3: Sync Family Members in ITS Data ---
    for member in family_members:
        fm_its_no = member.get("its_no")
        if not fm_its_no:
            continue  # skip blank rows

        existing_fm_name = frappe.db.get_value("ITS Data", {"its_no": fm_its_no}, "name")

        if existing_fm_name:
            fm_doc = frappe.get_doc("ITS Data", existing_fm_name)
            fm_doc.full_name = member.get("full_name")
            fm_doc.mobile_no = member.get("mobile_no")
            fm_doc.email_address = member.get("email_address")
            fm_doc.hof_fm_type = member.get("hof_or_family_member")
            fm_doc.relation_with_hof = member.get("relation_with_hof")
            # Inherit from HOF
            fm_doc.mohalla = hof.get("mohalla")
            fm_doc.sabeel_clearance = hof.get("jamaat_clearance")
            fm_doc.hof_its_no = hof_its_no
            fm_doc.save(ignore_permissions=True)
            msgprint(f"Family Member in ITS Data updated: {fm_doc.name}")
        else:
            fm_doc = frappe.new_doc("ITS Data")
            fm_doc.its_no = fm_its_no
            fm_doc.full_name = member.get("full_name")
            fm_doc.mobile_no = member.get("mobile_no")
            fm_doc.email_address = member.get("email_address")
            fm_doc.hof_fm_type = member.get("hof_or_family_member")
            fm_doc.relation_with_hof = member.get("relation_with_hof")
            # Inherit from HOF
            fm_doc.mohalla = hof.get("mohalla")
            fm_doc.sabeel_clearance = hof.get("jamaat_clearance")
            fm_doc.hof_its_no = hof_its_no
            fm_doc.insert(ignore_permissions=True)
            msgprint(f"Family Member in ITS Data created: {fm_doc.name}")

    frappe.db.commit()

    return {"status": "success", "hof": hof_doc.name, "details": details_doc.name}


@frappe.whitelist()
def get_its_data_by_id(its_id):
    """
    Fetches HOF details and all associated family members from the ITS Data DocType.
    
    :param its_id: The ITS ID to search for the HOF.
    :return: A dictionary with 'hof_data' and 'family_members_data' lists.
    """
    
    try:
        # Fetch the HOF record
        # The frappe.get_list method is used to get a list of documents
        # that match the specified filters.
        hof_data = frappe.get_list(
            "ITS Data", 
            filters={
                "its_no": its_id,
                "hof_fm_type": "HOF"
            },
            fields=["*"]  # Fetch all fields
        )
        # Print the HOF data to the console for debugging
        print(f"HOF Data for ITS ID {its_id}: {hof_data}")

        # Fetch all family members associated with the HOF
        family_members_data = frappe.get_list(
            "ITS Data",
            filters={
                "hof_its_no": its_id,
                "hof_fm_type": "FM"
            },
            fields=["*"] # Fetch all fields
        )
        # Print the family members data to the console for debugging
        print(f"Family Members Data for HOF ITS ID {its_id}: {family_members_data}")

        # Provide a pop-up message with the results
        #frappe.msgprint(f"HOF Data: {hof_data}\n\nFamily Members Data: {family_members_data}")

        return {
            "hof_data": hof_data,
            "family_members_data": family_members_data
        }
            
    except Exception as e:
        # Handle any exceptions that might occur
        frappe.log_error(str(e), "ITS Data Fetch Error")
        frappe.msgprint(f"An error occurred: {str(e)}")
        return {
            "hof_data": [],
            "family_members_data": []
        }

        
@frappe.whitelist()
def create_muwasaat_form(year_of_araz, date, email_id, first_name, hof_its_number, mohalla, hof_mobile_no, purpose):
    # Only validate duplicates if purpose is "Education"
    if purpose == "Education":
        existing_form = frappe.db.exists(
            "Muwasaat Form",
            {
                "application_for_the_year": year_of_araz,
                "purpose": purpose,
                "hof_its_number": hof_its_number
            }
        )
        if existing_form:
            return {"error": f"Muwasaat Form already exists: {existing_form}"}

    # Create new form (always allowed if purpose != Education)
    doc = frappe.new_doc("Muwasaat Form")
    doc.application_for_the_year = year_of_araz
    doc.application_date = date
    doc.hof_email_id = email_id
    doc.first_name = first_name
    doc.hof_its_number = hof_its_number
    doc.mohalla = mohalla
    doc.hof_mobile_no = hof_mobile_no
    doc.purpose = purpose
    doc.insert(ignore_permissions=True)
    doc.save()

    return {"muwasaat_form_name": doc.name}
    
    
  
@frappe.whitelist()
def create_mbi_form_family(data):
    import json
    from frappe import msgprint

    data = json.loads(data) if isinstance(data, str) else data

    hof_its_id = data.get("hof_its_id")
    if not hof_its_id:
        msgprint("HOF ITS No is required.")
        return

    created_or_updated = []

    # --- Create or Update MBI Form for HOF ---
    if frappe.db.exists("MBI Form - Family", {"its_no": hof_its_id}):
        hof_doc = frappe.get_doc("MBI Form - Family", {"its_no": hof_its_id})
    else:
        hof_doc = frappe.new_doc("MBI Form - Family")

    hof_doc.hof_its_no = hof_its_id
    hof_doc.its_no = hof_its_id
    hof_doc.full_name = data.get("hof_full_name")
    hof_doc.email_id = data.get("email_address")
    hof_doc.mohalla = data.get("mohalla")
    hof_doc.mobile_no = data.get("mobile_no")
    hof_doc.select_this_persons_relationship_with_hof = "HOF"
    hof_doc.age = data.get("age")

    hof_doc.save(ignore_permissions=True)
    created_or_updated.append(hof_doc.name)

    # --- Handle Family Members ---
    for member in data.get("its_family_details", []):
        fm_its_no = member.get("family_member_its_id")
        if not fm_its_no:
            continue  # skip blank rows

        # --- Create or Update separate MBI Form for each family member ---
        if frappe.db.exists("MBI Form - Family", {"its_no": fm_its_no}):
            fm_doc = frappe.get_doc("MBI Form - Family", {"its_no": fm_its_no})
        else:
            fm_doc = frappe.new_doc("MBI Form - Family")

        fm_doc.hof_its_no = hof_its_id
        fm_doc.its_no = fm_its_no
        fm_doc.full_name = member.get("family_member_full_name")
        fm_doc.email_id = member.get("email_address")
        fm_doc.mobile_no = member.get("mobile_no")
        fm_doc.age = member.get("age")
        fm_doc.select_this_persons_relationship_with_hof = member.get("relation_with_hof")
        fm_doc.mohalla = data.get("mohalla")  # same mohalla as parent

        fm_doc.save(ignore_permissions=True)
        created_or_updated.append(fm_doc.name)

    frappe.db.commit()

    return {"status": "success"}

import frappe
import requests
import json
from datetime import datetime

@frappe.whitelist()
def send_muwasaat_to_jms(docname):
    try:
        doc = frappe.get_doc("Muwasaat Tracker", docname)

        # Prevent duplicate sync
        if doc.jms_synced:
            return {"status": "skipped", "message": "Already synced"}

        

        payload = {
            "strkey": "dubaijms53*$",
            "ITSID": str(doc.applicant_its_no),
            "EnayatYear": str(doc.cheque_collected_date.year),
            "MuwasaatAmount": str(doc.cheque_amount)
            "Purpose": str(doc.purpose)
        }

        url = "https://api-jms-portal.azurewebsites.net//api/Accounts/PostMuwasaatData"
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            timeout=20
        )

        resp_json = response.json()

        # Store response
        doc.jms_response = json.dumps(resp_json, indent=2)

        if resp_json.get("Status") == 1:
            doc.jms_synced = 1

        doc.save(ignore_permissions=True)

        return {
            "status": "success",
            "response": resp_json
        }

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "JMS Muwasaat API Error"
        )
        return {"status": "failed"}




