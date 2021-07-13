from flask import jsonify, make_response
def success(code = 20000, data = "", msg= ""):
    return jsonify({
        "status": code,
        "msg": msg,
        "data": data
    })
    
def nonauthorization():
    return make_response(jsonify({
        "status": 40001,
        "msg": "无权限操作",
        "data": ""
    }), 401)