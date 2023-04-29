import datetime

from dateutil.relativedelta import relativedelta
from flask import jsonify


def createCompany(cName, cTel, cTown, cAddress, cPayment, branchId):
    sql = """INSERT INTO company(company_name,company_tel,company_town,company_address,payment_details)
       VALUES(%s,%s,%s,%s,%s)"""
    from main import mysql
    cursor = mysql.connection.cursor()
    data = (cName, cTel, cTown, cAddress, cPayment,)
    cursor.execute(sql, data)
    mysql.connection.commit()
    companyId = cursor.lastrowid
    createBranch(companyId, branchId, "Main", cTel)
    return companyId


def createBranch(companyId, branchId, companyName, contact):
    from main import mysql
    sql = """insert into branch (
    branch_id,
    branch_name,
    branchcontact,
    company_id)
values (
   %s,%s,%s,%s)
;"""
    cursor = mysql.connection.cursor()
    data = (branchId, companyName, contact, companyId,)
    cursor.execute(sql, data)
    mysql.connection.commit()


def getBranchDetails(branchId):
    from main import mysql
    sql = """SELECT * FROM branch WHERE branch_id=%s LIMIT 1"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (branchId,))
    result = cursor.fetchone()
    cursor.close()
    return jsonify(result)


def getParameterInfo(branchId):
    from main import mysql
    sql = """SELECT * FROM parameter_file WHERE branch_id=%s"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (branchId,))
    result = cursor.fetchone()
    if result is None:
        cursor.close()
        return {"value": 0}
    cursor.close()
    return result


def updateInvoiceNo(branchId, newNo):
    from main import mysql
    sql = """UPDATE parameter_file SET invoice_no=%s WHERE branch_id=%s"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (newNo, branchId,))
    mysql.connection.commit()


def setPaid(plan, email, branchId, amount):
    sql = """UPDATE sys_user SET paid=%s WHERE user_pin=%s"""
    from main import mysql
    cursor = mysql.connection.cursor()
    cursor.execute(sql, ('Y', email,))
    mysql.connection.commit()

    today = datetime.datetime.now()
    if plan == "monthly":
        endDate = today + relativedelta(months=+1)
    else:
        endDate = today + relativedelta(years=+1)

    sql = """INSERT INTO subscription (branch_id,plan,amount,payment_method,start_date,end_date,status)VALUES(%s,%s,%s,%s,
    %s,%s,%s)"""
    data = (branchId, plan, amount, "Mpesa", today, endDate, "Active",)
    cursor.execute(sql, data)
    mysql.connection.commit()


def getCurrentCompany(email):
    from main import mysql
    sql = """SELECT * FROM company WHERE company_address=%s LIMIT 1"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (email,))
    return jsonify(cursor.fetchone())


def getAllMyBranches(companyId):
    from main import mysql
    sql = """SELECT * FROM branch WHERE company_id=%s"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (companyId,))
    result = cursor.fetchall()
    cursor.close()
    return jsonify(result)


def subscriptionStatus(branchId):
    from main import mysql
    sql = """SELECT * FROM subscription WHERE branch_id=%s ORDER BY start_date DESC LIMIT 1"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (branchId,))
    result = cursor.fetchone()
    if result is None:
        return jsonify({"status": "Expired", "expiry": datetime.datetime.now()})
    if result["status"].lower() != "active":
        return jsonify({"status": "Expired", "expiry": result["end_date"]})
    start_date = result["start_date"]
    end_date = result["end_date"]
    remaining = (end_date - start_date).days
    if remaining < 1:
        sql = """UPDATE subscription SET status=%s WHERE branch_id=%s"""
        cursor.execute(sql, ("Expired", branchId,))
        mysql.connection.commit()
        return jsonify({"status": "Expired", "expiry": result["end_date"]})
    return jsonify({"status": "Active", "expiry": result["end_date"]})
