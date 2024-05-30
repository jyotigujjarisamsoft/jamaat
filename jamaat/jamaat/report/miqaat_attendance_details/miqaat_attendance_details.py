# Copyright (c) 2024, jyoti and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
from datetime import date
import json 


def execute(filters=None):
	columns, data = [], []
	
	miqaat=filters.get("miqaat")
	print("miqaat",miqaat)
	its_no=filters.get("its_no")
	print("its_no",its_no)
	if its_no is not None and miqaat is not None:
		customer_details = fetching_customer_details(miqaat,its_no)
		columns = get_columns()
		for customers in customer_details:
			data.append([customers['miqaat'],
			customers['its_no'],customers['present_count']
				])
	elif its_no is None and miqaat is not None:
		customer_details = fetching_customer_all_its_details(miqaat)
		columns = get_columns()
		for customers in customer_details:
			data.append([customers['miqaat'],
			customers['its_no'],customers['present_count']
				])
	elif its_no is not None and miqaat is None:
		customer_details = fetching_its_details(its_no)
		columns = get_columns()
		for customers in customer_details:
			data.append([customers['miqaat'],
			customers['its_no'],customers['present_count']
				])

	elif its_no is None and miqaat is None:
		customer_details = fetching_all_miqaat_details()
		print("fetching_all_miqaat_details-----")
		columns = get_columns()
		for customers in customer_details:
			data.append([customers['miqaat'],
			customers['its_no'],customers['present_count']
				])

	return columns, data


			
def fetching_customer_details(miqaat,its_no):
	customer_data = frappe.db.sql("""SELECT 
    miqaat, 
	miqaat_attended_date,
    its_no, 
	attendance,
    COUNT(*) AS present_count
FROM 
    `tabMiqaat Detail`
WHERE 
    attendance = 'Present' and miqaat= %s and its_no = %s
GROUP BY 
    miqaat, 
    its_no """,(miqaat,its_no), as_dict=1)
	print("customer_data",customer_data)
	
	return customer_data

def fetching_all_miqaat_details():
	customer_data = frappe.db.sql("""SELECT 
    miqaat, 
	miqaat_attended_date,
    its_no, 
	attendance,
    COUNT(*) AS present_count
FROM 
    `tabMiqaat Detail`
WHERE 
    attendance = 'Present' 
GROUP BY 
    miqaat, 
    its_no """, as_dict=1)
	print("fetching_all_miqaat_details",customer_data)
	
	return customer_data

def fetching_customer_all_its_details(miqaat):
	customer_data = frappe.db.sql("""SELECT 
    miqaat, 
	miqaat_attended_date,
    its_no, 
	attendance,
    COUNT(*) AS present_count
FROM 
    `tabMiqaat Detail`
WHERE 
    attendance = 'Present' and miqaat= %s 
GROUP BY 
    miqaat, 
    its_no """,(miqaat), as_dict=1)
	print("customer_data",customer_data)
	
	return customer_data

def fetching_its_details(its_no):
	customer_data = frappe.db.sql("""SELECT 
    miqaat, 
	miqaat_attended_date,
    its_no, 
	attendance,
    COUNT(*) AS present_count
FROM 
    `tabMiqaat Detail`
WHERE 
    attendance = 'Present' and its_no= %s 
GROUP BY 
    miqaat, 
    its_no """,(its_no), as_dict=1)
	print("customer_data",customer_data)
	
	return customer_data



def get_columns():
	"""return columns"""
	columns = [
		_("miqaat")+"::200",
		_("its_no")+"::200",
		_("colour")+"::200"

		]
	return columns



