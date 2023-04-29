import datetime
import uuid

from company import getParameterInfo


def createPosReceipt(
        branch_id,
        customer_id,
        location_id,
        receipt_cash_amount,
        receipt_bank_amount,
        receipt_mobile_money,
        receipt_total_amount,
        shift_id,
        staff_id,
        till_id,
        cart):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """insert into pos_receipts (
    receipt_id,
    bill_printed,
    branch_id,
    cancelled,
    comments,
    customer_id,
    location_id,
    receipt_card_amount,
    receipt_cash_amount,
    receipt_cheque_amount,
    receipt_code,
    receipt_date,
    receipt_discount,
    receipt_mobile_money,
    receipt_paid,
    receipt_ref,
    receipt_time,
    receipt_total_amount,
    receipt_voucher_amount,
    service_customer_id,
    shift_id,
    staff_id,
    till_id,
    updated)
values (
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
   )
;"""
    paramInfo = getParameterInfo(branch_id)
    if "value" in paramInfo:
        code = str(paramInfo.get("value") + 1).zfill(6)
    else:
        code = str(paramInfo.get("invoice_no")).zfill(6)
    rId = uuid.uuid4()
    data = (rId, 'N', branch_id, 'N', "POS Sale", customer_id, location_id,
            receipt_bank_amount, receipt_cash_amount, '0', code, datetime.date.today(), '0', receipt_mobile_money,
            'Y', code, datetime.datetime.now().strftime("%H:%M:%S"), receipt_total_amount, '0', customer_id, shift_id,
            staff_id, till_id,
            'N',)
    cursor.execute(query, data)
    sql = """UPDATE parameter_file SET invoice_no=%s WHERE branch_id=%s"""
    cursor.execute(sql, (int(code) + 1, branch_id,))
    mysql.connection.commit()
    cursor.close()
    addPosReceiptDetails(branch_id, cart, rId, location_id, code)


def addPosReceiptDetails(
        branch_id,
        cartItem,
        receipt_id,
        location, code):
    query = """insert into pos_receipt_details (
    receipt_details_id,
    branch_id,
    cancelled,
    discount,
    linenum,
    location_product_id,
    product_bp,
    product_sp,
    receipt_id,
    trans_quantity,
    uom_code,
    updated)
values (
   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
;"""
    from main import mysql
    cursor = mysql.connection.cursor()
    count = 1
    for item in cartItem:
        product = item["product"]
        print(product["location_product_quantity"])
        data = (uuid.uuid4(), branch_id, 'N', '0', count, product["location_product_id"],
                product["product_bp"], item["unitPrice"], receipt_id, float(item["quantity"]), item["uomCode"], 'N',)
        cursor.execute(query, data)
        q = """UPDATE location_stock SET location_product_quantity=%s WHERE 
        location_product_id=%s"""
        cursor.execute(q, (int(float(product["location_product_quantity"])) - int(float(item["quantity"])),
                           product["location_product_id"],))
        q = """insert into trans_file (
    trans_id,
    branch_id,
    cancelled,
    complete,
    confirmed,
    cost_price,
    created_on,
    location_id,
    location_product_id,
    running_balance,
    sprice,
    trans_comment,
    trans_date,
    trans_quantity,
    trans_reference,
    trans_type_id,
    uom_code,
    updated
    )
values (
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
;"""

        data = (uuid.uuid4(), branch_id, 'N', 'Y', 'Y', (int(item["unitPrice"]) * int(item["quantity"])),
                datetime.datetime.now(), location, product["location_product_quantity"],
                int(float(product["location_product_quantity"])) - int(float(item["quantity"])), item["unitPrice"],
                "POS Sale", datetime.datetime.now(), item["quantity"], code, '1', item["uomCode"], 'N',)
        cursor.execute(q, data)

    mysql.connection.commit()



