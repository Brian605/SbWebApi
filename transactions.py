from flask import jsonify


def getTransactionTypes():
    from main import mysql
    cursor = mysql.connection.cursor()
    query = """SELECT * from trans_type"""
    cursor.execute(query)
    result = cursor.fetchall()
    if result is None:
        return []
    return jsonify(result)
