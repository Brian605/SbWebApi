from flask import jsonify


def getLocations():
    from main import mysql
    cursor = mysql.connection.cursor()
    sql = """SELECT location_id,location_description FROM location"""
    cursor.execute(sql)
    result = cursor.fetchall()
    response = []
    if result is None:
        return jsonify(response)
    for x in result:
        response.append(x)
    return jsonify(response)
