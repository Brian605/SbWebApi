import uuid

from flask import jsonify


def addUom(branchId, code, desc):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """INSERT INTO uom (uom_code,uom_description,branch_id,uom_id,updated) VALUES(%s,%s,%s,%s,%s)"""
    data = (code, desc, branchId, uuid.uuid4(), 'N',)

    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def editUom(uomId, code, desc):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """UPDATE uom SET uom_code=%s,uom_description=%s WHERE uom_id=%s"""
    data = (code, desc, uomId,)
    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def getUoms(branchId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """SELECT * FROM uom WHERE branch_id=%s"""
    data = (branchId,)
    cursor.execute(sql, data)
    result = cursor.fetchall()
    response = []
    for x in result:
        response.append(x)
    cursor.close()
    return response


def deleteUom(uomId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """DELETE FROM uom WHERE uom_id=%s"""
    data = (uomId,)
    cursor.execute(sql, data)
    mysql.connection.commit()


def addCategory(branchId, wm, rm, name):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """INSERT INTO category (category_id,show_in_pos,branch_id,category_desc,rmargin,wmargin,updated) VALUES(%s,%s,%s,
    %s,%s,%s,%s)"""
    data = (uuid.uuid4(), 'Y', branchId, name, rm, wm, 'N',)
    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def getCategories(branchId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """SELECT * FROM category WHERE branch_id=%s"""
    data = (branchId,)
    cursor.execute(sql, data)
    result = cursor.fetchall()
    response = []
    for x in result:
        response.append(x)
    cursor.close()
    return response


def deleteCategory(categoryId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """DELETE FROM category WHERE category_id=%s"""
    data = (categoryId,)
    cursor.execute(sql, data)
    mysql.connection.commit()


def editCategory(categoryId, name, wmargin, rmargin):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """UPDATE category SET category_desc=%s,rmargin=%s,wmargin=%s WHERE category_id=%s"""
    data = (name, rmargin, wmargin, categoryId)
    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def getNextScanCode(branchId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """SELECT location_product_scancode FROM location_stock WHERE branch_id=%s ORDER BY 
    location_product_scancode DESC LIMIT 1"""
    cursor.execute(sql, (branchId,))
    results = cursor.fetchone()
    if results is None:
        return {"location_product_scancode": 0}
    return results


def addInventory(active, blockneg, branchId, categoryId, name, qtty, scanncode, rp, wp, uom, bp):
    from main import mysql
    sql = """insert into location_stock(
        location_product_id,
        active,
        blockneg,
        branch_id,
        category_id,
        location_product_description,
        location_product_quantity,
        location_product_scancode,
        location_product_sp,
        location_product_sp1,
        product_bp,
        product_id,
        product_name,
        uom_code,
        updated)
    values(
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
    )"""
    productid = uuid.uuid4()
    cursor = mysql.connection.cursor()
    data = (
        productid, active, blockneg, branchId, categoryId, name, qtty, scanncode, rp, wp, bp, productid,
        name, uom, 'N',)
    cursor.execute(sql, data)
    mysql.connection.commit()
    cursor.close()


def getInventoryList(branchId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """SELECT location_product_id,
        active,
        blockneg,
        branch_id,
        category_id,
        location_product_description,
        location_product_quantity,
        location_product_scancode,
        location_product_sp,
        location_product_sp1,
        packaging_uom,
        product_bp,
        product_id,
        product_name,
        uom_code,
        updated FROM location_stock WHERE branch_id=%s"""
    data = (branchId,)
    cursor.execute(sql, data)
    result = cursor.fetchall()
    response = []
    for x in result:
        response.append(x)
    cursor.close()
    return response


def deactivateProduct(productId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """UPDATE location_stock SET active=%s WHERE location_product_id=%s"""
    cursor.execute(sql, ('N', productId,))
    mysql.connection.commit()


def activateProduct(productId):
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """UPDATE location_stock SET active=%s WHERE location_product_id=%s"""
    cursor.execute(sql, ('Y', productId,))
    mysql.connection.commit()


def receiveStock(qtty, sp, bp, pid, newBal, supplierId):
    sql = """UPDATE location_stock SET location_product_quantity=location_product_quantity+%s,location_product_sp1=%s,
    product_bp=%s WHERE location_product_id=%s"""
    from main import mysql
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (qtty, sp, bp, pid,))

    sql = """UPDATE supplier SET supplier_running_bal=supplier_running_bal+%s WHERE supplier_id=%s"""
    cursor.execute(sql, (newBal, supplierId,))
    mysql.connection.commit()
    return jsonify({"success": True})
