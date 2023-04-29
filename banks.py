import uuid

from flask import jsonify


def addBank(
        account_details,
        bank_acc_no,
        bank_name,
        branch_id, phone):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """insert into banks (
    bank_id,
    account_details,
    active,
    bank_acc_no,
    bank_name,
    bank_running_bal,
    branch_id,
    account_manager
   )
values (%s,%s,%s,%s,%s,%s,%s,%s)
;"""
    tillId = uuid.uuid4()
    data = (tillId, account_details, "Y", bank_acc_no, bank_name, "0", branch_id, phone,)
    cursor.execute(query, data)

    sql = """insert into till (
        till_id,
        branch_id,
        till_no,
        till_receipt_msg1,
        updated)
    values (
        %s,%s,%s,%s,%s)
    ;"""
    data = (tillId, branch_id, bank_acc_no, bank_name, 'N',)
    cursor.execute(sql,data)
    mysql.connection.commit()
    cursor.close()


def getBankList(branchId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT * FROM banks WHERE branch_id=%s"""
    cursor.execute(query, (branchId,))
    results = cursor.fetchall()
    if results is None or len(results) < 1:
        return jsonify([])
    return jsonify(results)


def updateBank(
        account_details,
        bank_acc_no,
        bank_name,
        phone, bankId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """UPDATE banks SET
    account_details=%s,
    bank_acc_no=%s,
    bank_name=%s,
    account_manager=%s
   WHERE bank_id=%s
;"""
    data = (account_details, bank_acc_no, bank_name, phone, bankId,)
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()


def deleteBank(bankId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """DELETE FROM banks WHERE bank_id=%s"""
    cursor.execute(query, (bankId,))
    mysql.connection.commit()
    cursor.close()


def updateRunningBalance(newVal, bankId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """UPDATE banks SET bank_running_bal=%s WHERE bank_id=%s"""
    cursor.execute(query, (newVal, bankId,))
    mysql.connection.commit()
    cursor.close()


def getCurrentRunningBal(bankId):
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT bank_running_bal FROM banks WHERE bank_id=%s"""
    cursor.execute(query, (bankId,))
    result = cursor.fetchone()
    if result is None:
        return 0
    return int(result["bank_running_bal"])


def addTransaction(
        bank_id,
        bank_trans_type_id,
        branch_id,
        created_by,
        created_on,
        trans_amount,
        trans_comment,
        trans_date,
        trans_ref,
        trans_complete, sign):
    from main import mysql
    cursor = mysql.connection.cursor()

    currentbal = getCurrentRunningBal(bank_id)
    if sign == "-":
        currentbal = currentbal - int(trans_amount)
    else:
        currentbal = currentbal + int(trans_amount)

    query = """insert into bank_trans (
    bank_trans_id,
    bank_id,
    bank_trans_type_id,
    branch_id,
    created_by,
    created_on,
    trans_amount,
    trans_comment,
    trans_date,
    trans_ref,
    trans_running_bal,
    trans_complete
   )
values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
;"""
    data = (uuid.uuid4(), bank_id, bank_trans_type_id, branch_id, created_by, created_on, trans_amount, trans_comment,
            trans_date, trans_ref, currentbal, trans_complete,)
    cursor.execute(query, data)
    mysql.connection.commit()
    cursor.close()
    updateRunningBalance(currentbal, bank_id)


def getBankTransactions(branchId):
    query = """SELECT * FROM bank_trans WHERE branch_id=%s"""
    from main import mysql
    cursor = mysql.connection.cursor()
    cursor.execute(query, (branchId,))
    results = cursor.fetchall()
    if results is None or len(results) < 1:
        return jsonify([])
    return jsonify(results)
