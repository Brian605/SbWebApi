import uuid

from flask import jsonify


def addSupplier(
        branch_id,
        bank_acc,
        address,
        name,
        phone_no,
        balance,
        pin_number):
    sql = """insert into supplier (
    supplier_id,
    supplier_code,
    branch_id,
    supplier_address,
    supplier_bank_acc,
    supplier_name,
    supplier_phone_no,
    supplier_contact_person,
    Supplier_pin,
    supplier_running_bal)
values (
   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
;"""

    from main import mysql
    cursor = mysql.connection.cursor()
    suppId = uuid.uuid4()
    suppCode = suppId.int & 0xfffff
    data = (
        suppId, suppCode, branch_id, address, bank_acc, name, phone_no, phone_no, pin_number, balance,)
    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def getSupplierList(branchId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """select active,
    branch_id,
    supplier_address,
    supplier_bank_acc,
    supplier_id,
    supplier_name,
    supplier_phone_no,
    supplier_running_bal,
    supplier_code,
    Supplier_pin
    from
    supplier  WHERE branch_id=%s"""
    data = (branchId,)
    cursor.execute(sql, data)
    result = cursor.fetchall()
    response = []

    for x in result:
        response.append(x)
    cursor.close()
    return response


def changeSupplierStatus(status, customerId):
    sql = """UPDATE supplier SET active=%s WHERE supplier_id=%s"""
    from main import mysql
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (status, customerId,))
    mysql.connection.commit()
    cursor.close()


def updateSupplier(supplier_id,
                   bank_acc,
                   address,
                   name,
                   phone_no,
                   pin_number,
                   balance):
    sql = """update supplier set
     supplier_address=%s,
    supplier_bank_acc=%s,
    supplier_name=%s,
    supplier_phone_no=%s,
    Supplier_pin=%s,updated=%s,supplier_running_bal=%s WHERE supplier_id=%s"""

    from main import mysql
    cursor = mysql.connection.cursor()
    data = (address, bank_acc, name, phone_no, pin_number,
            'Y', balance, supplier_id,)
    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def getCurrentRunningBalance(supplierId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT supplier_running_bal FROM supplier WHERE supplier_id=%s"""
    cursor.execute(query, (supplierId,))
    result = cursor.fetchone()
    if result["supplier_running_bal"] is None:
        return 0
    return int(result["supplier_running_bal"])


def updateCurrentRunningBalance(supplierId, amount):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """UPDATE supplier SET supplier_running_bal=%s WHERE supplier_id=%s"""
    cursor.execute(query, (amount, supplierId,))
    mysql.connection.commit()
    cursor.close()


def addPayment(supplierId, branch_id,
               created_by,
               created_on,
               trans_type_id,
               transaction_amount,
               transaction_comment,
               transaction_ref):
    from main import mysql
    cursor = mysql.connection.cursor()
    currentBal = getCurrentRunningBalance(supplierId)
    currentBal = currentBal - int(transaction_amount)
    query = """insert into supplier_trans (
    supplier_trans_id,
    branch_id,
    created_by,
    created_on,
    running_bal,
    supplier_id,
    trans_by,
    trans_type_id,
    transaction_amount,
    transaction_approved,
    transaction_comment,
    transaction_date,
    transaction_payment_ref,
    transaction_ref)
values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    data = (uuid.uuid4(), branch_id, created_by, created_on, currentBal, supplierId, created_by, trans_type_id,
            transaction_amount, "Y", transaction_comment, created_on, transaction_ref, transaction_ref,)
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()
    updateCurrentRunningBalance(supplierId, currentBal)


def getTransactionList(supplierId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT  supplier_trans_id,
    branch_id,
    created_by,
    created_on,
    running_bal,
    supplier_id,
    trans_by,
    trans_type_id,
    transaction_amount,
    transaction_approved,
    transaction_comment,
    transaction_date,
    transaction_payment_ref,
    transaction_ref FROM supplier_trans WHERE supplier_id=%s"""

    cursor.execute(query, (supplierId,))
    results = cursor.fetchall()
    if results is None or len(results) < 1:
        return jsonify([])
    cursor.close()
    return jsonify(results)


def getTransactionListFiltered(supplierId, fromDate, toDate):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT  supplier_trans_id,
    branch_id,
    created_by,
    created_on,
    running_bal,
    supplier_id,
    trans_by,
    trans_type_id,
    transaction_amount,
    transaction_approved,
    transaction_comment,
    transaction_date,
    transaction_payment_ref,
    transaction_ref FROM supplier_trans WHERE supplier_id=%s AND created_on>=%s AND created_on<=%s"""

    cursor.execute(query, (supplierId, fromDate, toDate,))
    results = cursor.fetchall()
    if results is None or len(results) < 1:
        return jsonify([])
    cursor.close()
    return jsonify(results)


def getTransactionListFilteredTo(supplierId, toDate):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT  supplier_trans_id,
    branch_id,
    created_by,
    created_on,
    running_bal,
    supplier_id,
    trans_by,
    trans_type_id,
    transaction_amount,
    transaction_approved,
    transaction_comment,
    transaction_date,
    transaction_payment_ref,
    transaction_ref FROM supplier_trans WHERE supplier_id=%s AND created_on<=%s"""

    cursor.execute(query, (supplierId, toDate,))
    results = cursor.fetchall()
    if results is None or len(results) < 1:
        return jsonify([])
    cursor.close()
    return jsonify(results)


def getTransactionListFilteredFrom(supplierId, fromDate):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT  supplier_trans_id,
    branch_id,
    created_by,
    created_on,
    running_bal,
    supplier_id,
    trans_by,
    trans_type_id,
    transaction_amount,
    transaction_approved,
    transaction_comment,
    transaction_date,
    transaction_payment_ref,
    transaction_ref FROM supplier_trans WHERE supplier_id=%s AND created_on>=%s"""

    cursor.execute(query, (supplierId, fromDate,))
    results = cursor.fetchall()
    if results is None or len(results) < 1:
        return jsonify([])
    cursor.close()
    return jsonify(results)
