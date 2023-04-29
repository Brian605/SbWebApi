import datetime
import hashlib
import json
import time
import uuid
from uuid import UUID

import bcrypt
from dateutil.relativedelta import relativedelta
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_mysqldb import MySQL

from banks import addBank, updateBank, deleteBank, getBankList, addTransaction, getBankTransactions
from checkout import createPosReceipt
from company import createCompany, setPaid, getBranchDetails, getCurrentCompany, createBranch, getAllMyBranches, \
    subscriptionStatus
from customers import addCustomer, getCustomerList, changeCustomerStatus, updateCustomer
from helpers import getLocations
from inventory import addUom, getUoms, deleteUom, editUom, addCategory, getCategories, deleteCategory, editCategory, \
    getNextScanCode, addInventory, getInventoryList, deactivateProduct, activateProduct, receiveStock
from shifts import addShift, getRunningShift, addExpense, getExpenses
from suppliers import addSupplier, getSupplierList, changeSupplierStatus, updateSupplier, getCurrentRunningBalance, \
    addPayment, getTransactionList, getTransactionListFilteredFrom, getTransactionListFilteredTo, \
    getTransactionListFiltered
from transactions import getTransactionTypes

app = Flask(__name__)
CORS(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'returnzero'
app.config['MYSQL_PASSWORD'] = 'Brian605$ret0'
app.config['MYSQL_DB'] = 'Nawiriapp$pos'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def home():
    return "You are here"


@app.route("/createUser", methods=["POST"])
@cross_origin()
def createUser():
    companyEmail = request.form.to_dict().get("company[email]")
    username = request.form.to_dict().get("user[name]")
    userphone = request.form.to_dict().get("user[phone]")
    userref = request.form.to_dict().get("user[ref]")
    userpassword = request.form.to_dict().get("user[password]")
    companyname = request.form.to_dict().get("company[name]")
    companylocation = request.form.to_dict().get("company[location]")
    companytill = request.form.to_dict().get("company[till]")
    companyreceipt = request.form.to_dict().get("company[receipt]")

    userpassword = hashlib.sha256(userpassword.encode("utf-8")).hexdigest()

    sql2 = """SELECT user_id FROM sys_user WHERE user_pin=%s"""
    data = (companyEmail,)

    cursor = mysql.connection.cursor()
    cursor.execute(sql2, data)
    rows = cursor.fetchone()
    mysql.connection.commit()
    if rows is not None:
        cursor.close()
        return jsonify({"success": False, "message": "Email is already registered"})

    # print("Staff Code:", staff_code)

    ##Create User
    sql = """INSERT INTO sys_user(user_id,staff_id,User_name,user_pass,user_pin,updated,branch_id,referal_code,paid)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    branchId = int(time.time_ns() & 0xffff)
    data = (uuid.uuid4(), 0, username, userpassword, companyEmail, "N", branchId, userref, "N",)
    cursor.execute(sql, data)
    mysql.connection.commit()

    sql = """insert into parameter_file (
    parameter_id,
    branch_id,
    categoryno,
    customerno,
    expence_no,
    foliono,
    fscan,
    grn_no,
    invoice_no,
    jobno,
    lpo_no,
    quote_no,
    rmargin,
    staffno,
    supplierno,
    updated,
    wmargin)
values (
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
;"""
    data = (uuid.uuid4(), branchId, '0', '0', '0', '0', 'N', '0', '0', '0', '0', '0', '0', '0', '0', 'N', '0',)
    cursor.execute(sql, data)
    mysql.connection.commit()

    ##Create Company
    companyId = createCompany(companyname, userphone, companylocation, companyEmail, companytill, branchId)
    cursor.close()

    return jsonify({"success": True, "message": "Created User", "branchId": branchId, "companyId": companyId})


@app.route("/loginUser", methods=["POST"])
def loginUser():
    username = request.form.to_dict().get("email")
    password = request.form.to_dict().get("password")
    userpassword = hashlib.sha256(password.encode("utf-8")).hexdigest()

    cursor = mysql.connection.cursor()
    sql = """SELECT user_id,staff_id,user_name,updated,branch_id,referal_code,paid FROM sys_user WHERE user_pin=%s 
    AND user_pass=%s"""
    cursor.execute(sql, (username, userpassword,))
    users = cursor.fetchone()
    if users == None:
        return jsonify({"success": False, "message": "Invalid email or password"})
    response = {"success": True, "message": "User Logged In", "user": users}

    sql = """SELECT company_name,company_tel,company_town,company_address,payment_details FROM company WHERE 
    company_address=%s"""
    cursor.execute(sql, (username,))
    company = cursor.fetchone()
    response["company"] = company
    cursor.close()
    return jsonify(response)


@app.route("/setPaid", methods=["POST"])
def markPaid():
    amount = request.form.to_dict().get("amount")
    plan = request.form.to_dict().get("plan")
    email = request.form.to_dict().get("email")
    branchId = request.form.to_dict().get("branchId")
    setPaid(plan, email, branchId, amount)

    return jsonify({"success": True, "message": "Activated"})


@app.route("/addUom", methods=["POST"])
def addUnitOfMeasurement():
    branchId = request.form.to_dict().get("branchId")
    code = request.form.to_dict().get("code")
    desc = request.form.to_dict().get("desc")
    addUom(branchId, code, desc)
    return jsonify({"success": True, "message": "UOM added"})


@app.route("/getBranchUoms", methods=["POST"])
def getUomsList():
    branchId = request.form.to_dict().get("branch")
    resp = getUoms(branchId)
    return jsonify(resp)


@app.route("/deleteUom", methods=["POST"])
def deleteSingleUom():
    uomId = request.form.to_dict().get("id")
    deleteUom(uomId)
    return jsonify({"success": True, "message": "UOM deleted"})


@app.route("/editUom", methods=["POST"])
def editSingleUom():
    uomId = request.form.to_dict().get("id")
    code = request.form.to_dict().get("code")
    desc = request.form.to_dict().get("desc")
    editUom(uomId, code, desc)
    return jsonify({"success": True, "message": "UOM edited"})


@app.route("/addCategory", methods=["POST"])
def addProductCategory():
    branchId = request.form.to_dict().get("branchId")
    name = request.form.to_dict().get("name")
    wm = request.form.to_dict().get("wm")
    rm = request.form.to_dict().get("rm")
    addCategory(branchId, wm, rm, name)
    return jsonify({"success": True, "message": "UOM edited"})


@app.route("/getBranchCategories", methods=["POST"])
def getBranchCategories():
    branchId = request.form.to_dict().get("branch")
    return jsonify(getCategories(branchId))


@app.route("/deleteCategory", methods=["POST"])
def deleteSingleCategory():
    categoryId = request.form.to_dict().get("id")
    deleteCategory(categoryId)
    return jsonify({"success": True, "message": "UOM deleted"})


@app.route("/editCategory", methods=["POST"])
def editSingleCategory():
    categoryId = request.form.to_dict().get("id")
    name = request.form.to_dict().get("name")
    wm = request.form.to_dict().get("wm")
    rm = request.form.to_dict().get("rm")
    editCategory(categoryId, name, wm, rm)
    return jsonify({"success": True, "message": "UOM edited"})


@app.route("/nextScanCode", methods=["POST"])
def getNextProductScanCode():
    branchId = request.form.to_dict().get("branch")
    return jsonify(getNextScanCode(branchId))


@app.route("/addInventory", methods=["POST"])
def newInventory():
    uomCode = request.form.to_dict().get("uomcode")
    name = request.form.to_dict().get("name")
    categoryId = request.form.to_dict().get("category")
    scancode = request.form.to_dict().get("code")
    bp = request.form.to_dict().get("bp")
    wp = request.form.to_dict().get("wp")
    rp = request.form.to_dict().get("rp")
    bn = request.form.to_dict().get("bn")
    active = request.form.to_dict().get("active")
    branchId = request.form.to_dict().get("branch")
    qtty = request.form.to_dict().get("quantity")

    addInventory(active, bn, branchId, categoryId, name, qtty, scancode, rp, wp, uomCode, bp)
    return jsonify({"success": True, "message": "Inventory Added"})


@app.route("/getInventory", methods=["POST"])
def getInventory():
    branchId = request.form.to_dict().get("branch")
    return jsonify(getInventoryList(branchId))


@app.route("/deactivateProduct", methods=["POST"])
def deactivateItem():
    itemId = request.form.to_dict().get("id")
    deactivateProduct(itemId)
    return jsonify({"success": True, "message": "Inventory Deactivated"})


@app.route("/activateProduct", methods=["POST"])
def activateItem():
    itemId = request.form.to_dict().get("id")
    activateProduct(itemId)
    return jsonify({"success": True, "message": "Inventory Activated"})


@app.route("/productLocations", methods=["POST"])
def getProductLocations():
    return getLocations()


@app.route("/newCustomer", methods=["POST"])
def newCustomer():
    account = request.form.to_dict().get("account")
    name = request.form.to_dict().get("name")
    status = request.form.to_dict().get("status")
    phone = request.form.to_dict().get("phone")
    balance = request.form.to_dict().get("balance")
    credit = request.form.to_dict().get("credit")
    limit = request.form.to_dict().get("limit")
    pin = request.form.to_dict().get("pin")
    branchId = request.form.to_dict().get("branch")
    addCustomer(status, branchId, account, limit, name, phone, balance, credit, pin)
    return jsonify({"success": True, "message": "Customer Added"})


@app.route("/getCustomerList", methods=["POST"])
def getMyCustomers():
    branchId = request.form.to_dict().get("branch")
    return jsonify(getCustomerList(branchId))


@app.route("/changeCustomerStatus", methods=["POST"])
def changeMyCustomerStatus():
    status = request.form.to_dict().get("status")
    customerId = request.form.to_dict().get("id")
    changeCustomerStatus(status, customerId)
    return jsonify({"success": True, "message": "Customer Updated"})


@app.route("/updateCustomer", methods=["POST"])
def updateMyCustomer():
    account = request.form.to_dict().get("account")
    name = request.form.to_dict().get("name")
    status = request.form.to_dict().get("status")
    phone = request.form.to_dict().get("phone")
    credit = request.form.to_dict().get("credit")
    limit = request.form.to_dict().get("limit")
    pin = request.form.to_dict().get("pin")
    customerId = request.form.to_dict().get("customerId")
    updateCustomer(status, account, limit, name, phone, credit, pin, customerId)
    return jsonify({"success": True, "message": "Customer Updated"})


@app.route("/newSupplier", methods=["POST"])
def newSupplier():
    account = request.form.to_dict().get("account")
    name = request.form.to_dict().get("name")
    phone = request.form.to_dict().get("phone")
    address = request.form.to_dict().get("address")
    pin = request.form.to_dict().get("pin")
    branchId = request.form.to_dict().get("branch")
    balance = request.form.to_dict().get("balance")

    addSupplier(branchId, account, address, name, phone, balance, pin)
    return jsonify({"success": True, "message": "Customer Added"})


@app.route("/getSupplierList", methods=["POST"])
def getMySuppliers():
    branchId = request.form.to_dict().get("branch")
    return jsonify(getSupplierList(branchId))


@app.route("/changeSupplierStatus", methods=["POST"])
def changeMySupplierStatus():
    status = request.form.to_dict().get("status")
    customerId = request.form.to_dict().get("id")
    changeSupplierStatus(status, customerId)
    return jsonify({"success": True, "message": "Supplier Updated"})


@app.route("/updateSupplier", methods=["POST"])
def updateMySupplier():
    account = request.form.to_dict().get("account")
    name = request.form.to_dict().get("name")
    phone = request.form.to_dict().get("phone")
    address = request.form.to_dict().get("address")
    pin = request.form.to_dict().get("pin")
    balance = request.form.to_dict().get("balance")
    supplierId = request.form.to_dict().get("supplierId")
    print("Supplier ID:", supplierId, "balance:", balance)
    updateSupplier(supplierId, account, address, name, phone, pin, balance)
    return jsonify({"success": True, "message": "Supplier Updated"})


@app.route("/getTransactionTypes", methods=["POST"])
def getTransTypes():
    return getTransactionTypes()


@app.route("/addSupplierPayment", methods=["POST"])
def addPayments():
    branchId = request.form.to_dict().get("branch")
    createdBy = request.form.to_dict().get("createdBy")
    createdOn = request.form.to_dict().get("createdOn")
    transTypeId = request.form.to_dict().get("type")
    amount = request.form.to_dict().get("amount")
    comment = request.form.to_dict().get("comments")
    ref = request.form.to_dict().get("reference")
    supplierId = request.form.to_dict().get("supplierId")
    addPayment(supplierId, branchId, createdBy, createdOn, transTypeId, amount, comment, ref)
    return jsonify({"success": True, "message": "Payment Added"})


@app.route("/getSupplierTrans", methods=["POST"])
def getSupTrans():
    supplierId = request.form.to_dict().get("supplierId")
    return getTransactionList(supplierId)


@app.route("/getSupplierTransFiltered", methods=["POST"])
def getSupplierTransFiltered():
    supplierId = request.form.to_dict().get("supplierId")
    fromDate = request.form.to_dict().get("from")
    to = request.form.to_dict().get("to")
    if fromDate == "":
        return getTransactionListFilteredTo(supplierId, to)
    elif to == "":
        return getTransactionListFilteredFrom(supplierId, fromDate)
    else:
        return getTransactionListFiltered(supplierId, fromDate, to)


@app.route("/newBank", methods=["POST"])
def newBank():
    account_details = request.form.to_dict().get("branchName")
    bank_acc_no = request.form.to_dict().get("account")
    bank_name = request.form.to_dict().get("name")
    branch_id = request.form.to_dict().get("branch")
    phone = request.form.to_dict().get("phone")
    addBank(account_details, bank_acc_no, bank_name, branch_id, phone)
    return jsonify({"success": True, "message": "Bank Added"})


@app.route("/updateBank", methods=["POST"])
def updateABank():
    account_details = request.form.to_dict().get("branchName")
    bank_acc_no = request.form.to_dict().get("account")
    bank_name = request.form.to_dict().get("name")
    phone = request.form.to_dict().get("phone")
    bankId = request.form.to_dict().get("id")
    updateBank(account_details, bank_acc_no, bank_name, phone, bankId)
    return jsonify({"success": True, "message": "Bank Updated"})


@app.route("/deleteBank", methods=["POST"])
def removeBank():
    bankId = request.form.to_dict().get("id")
    deleteBank(bankId)
    return jsonify({"success": True, "message": "Bank Deleted"})


@app.route("/listBanks", methods=["POST"])
def listBanks():
    branch_id = request.form.to_dict().get("branch")
    return getBankList(branch_id)


@app.route("/bankTransaction", methods=["POST"])
def addBankTransaction():
    bank_id = request.form.to_dict().get("bankId")
    bank_trans_type_id = request.form.to_dict().get("type")
    branch_id = request.form.to_dict().get("branch")
    created_by = request.form.to_dict().get("createdBy")
    created_on = request.form.to_dict().get("createdOn")
    trans_amount = request.form.to_dict().get("amount")
    trans_comment = request.form.to_dict().get("comments")
    trans_date = created_on
    trans_ref = request.form.to_dict().get("ref"),
    trans_complete = request.form.to_dict().get("complete")
    sign = request.form.to_dict().get("sign")
    addTransaction(bank_id, bank_trans_type_id, branch_id, created_by, created_on, trans_amount, trans_comment,
                   trans_date, trans_ref, trans_complete, sign)
    return jsonify({"success": True, "message": "Transaction Added"})


@app.route("/bankTransactionsList", methods=["POST"])
def bankTransactionsList():
    branch_id = request.form.to_dict().get("branch")
    return getBankTransactions(branch_id)


@app.route("/newShift", methods=["POST"])
def newShift():
    branchId = request.form.to_dict().get("branch")
    sdate = request.form.to_dict().get("date"),
    shift_description = request.form.to_dict().get("desc"),
    till_id = request.form.to_dict().get("till")
    addShift(branchId, sdate, shift_description, till_id)
    return jsonify({"success": True, "message": "Shift Started"})


@app.route("/runningShift", methods=["POST"])
def runningShift():
    branchId = request.form.to_dict().get("branch")
    return getRunningShift(branchId)


@app.route("/newExpense", methods=["POST"])
def newExpense():
    branch_id = request.form.to_dict().get("branch")
    cash_amount = request.form.to_dict().get("amount")
    pay_date = request.form.to_dict().get("date")
    pay_description = request.form.to_dict().get("desc")
    pay_ref = request.form.to_dict().get("ref")
    pay_to = request.form.to_dict().get("to")
    shift_id = request.form.to_dict().get("shift")
    till_id = request.form.to_dict().get("till")
    addExpense(branch_id, cash_amount, pay_date, pay_description, pay_ref, pay_to, shift_id, till_id)
    return jsonify({"success": True, "message": "Expense Added"})


@app.route("/getExpenses", methods=["POST"])
def getMyExpenses():
    branch_id = request.form.to_dict().get("branch")
    print(branch_id)
    return getExpenses(branch_id)


@app.route("/posCheckout", methods=["POST"])
def getCartCheckout():
    branch_id = request.form.to_dict().get("branch")
    total = request.form.to_dict().get("total")
    cash = request.form.to_dict().get("cash")
    mpesa = request.form.to_dict().get("mpesa")
    bank = request.form.to_dict().get("bank")
    cart = request.form.to_dict().get("cart")
    shift_id = request.form.to_dict().get("shift")
    till_id = request.form.to_dict().get("till")
    customerId = request.form.to_dict().get("customerId")
    staffId = request.form.to_dict().get("staffId")
    location = request.form.to_dict().get("location")
    cart = json.loads(cart)
    createPosReceipt(branch_id, customerId, location, cash, bank, mpesa, total, shift_id, staffId, till_id, cart)
    return jsonify({"success": True, "message": "Expense Added"})


@app.route("/receiveStock", methods=["POST"])
def receiveSuppStock():
    qtty = request.form.to_dict().get("quantity")
    sp = request.form.to_dict().get("sellingPrice")
    bp = request.form.to_dict().get("buyingPrice")
    pid = request.form.to_dict().get("product")
    newBal = request.form.to_dict().get("amount")
    supplierId = request.form.to_dict().get("supplierId")
    return receiveStock(qtty, sp, bp, pid, newBal, supplierId)


@app.route("/branchDetails", methods=["POST"])
def branchDetails():
    branch_id = request.form.to_dict().get("branch")
    return getBranchDetails(branch_id)


@app.route("/companyDetails", methods=["POST"])
def companyDetails():
    email = request.form.to_dict().get("email")
    return getCurrentCompany(email)


@app.route("/addBranch", methods=["POST"])
def newCompanyBranch():
    branchId = int(time.time_ns() & 0xffff)
    company = request.form.to_dict().get("company")
    amount = request.form.to_dict().get("amount")
    name = request.form.to_dict().get("name")
    phone = request.form.to_dict().get("phone")
    createBranch(company, branchId, name, phone)
    today = datetime.datetime.now()
    endDate = today + relativedelta(months=+1)
    cursor = mysql.connection.cursor()
    sql = """INSERT INTO subscription (branch_id,plan,amount,payment_method,start_date,end_date,status)VALUES(%s,%s,%s,%s,
        %s,%s,%s)"""
    data = (branchId, "monthly", amount, "Mpesa", today, endDate, "Active",)
    cursor.execute(sql, data)
    mysql.connection.commit()
    return jsonify({"success": True})


@app.route("/companyBranches", methods=["POST"])
def getCompanyBranches():
    company = request.form.to_dict().get("company")
    return getAllMyBranches(company)


@app.route("/branchSubscription", methods=["POST"])
def getBranchSubscription():
    branch = request.form.to_dict().get("branch")
    return subscriptionStatus(branch)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=5000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
