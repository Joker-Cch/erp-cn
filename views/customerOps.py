from flask import Blueprint, request, current_app
from models.customer_ops import CustomerOpsControl
from libs.defResponse import success, nonauthorization
from views.auth import auth

CustomerOpsView = Blueprint("CustomerOpsView", __name__)
role = ["admin", "users"]

@CustomerOpsView.route("/all", methods = ["GET"])
@auth.login_required(role= role)
def gets():
    data = request.args
    page = int(data.get("page", 1))
    page = page if page> 0 else 1
    pagesize = int(data.get("pageSize", 10))
    orderby = "+" if data.get("order", "desc") == "desc" else "-"
    sortkey = (orderby + data.get("sort")) if data.get("sort") else None
    return success(20000, data=CustomerOpsControl().gets(
        page = page, pagesize = pagesize, sortkey = sortkey, customer = data.get("customer", None)
    ))

@CustomerOpsView.route("/add", methods = ["POST"])
@auth.login_required(role = role)
def add():
    if not request.json:
        return success(40004,"缺少参数")
    customer = request.json.get("customer", None)
    technicalPerson = request.json.get("technicalPerson", [])
    reviewer = request.json.get("reviewer")
    monitorer = request.json.get("monitorer")
    status, msg = CustomerOpsControl().create_update(customer, technicalPerson, reviewer, monitorer, request.json.get("account"))
    return success(status, msg)

@CustomerOpsView.route("/update", methods = ["POST"])
@auth.login_required(role = role)
def update():
    if not request.json:
        return success(40004,"缺少参数")
    if not request.json.get('coid'):
        return success(40004, "缺少必要参数")
    customer = request.json.get("customer", None)

    technicalPerson = request.json.get("technicalPerson", [])
    reviewer = request.json.get("reviewer")
    monitorer = request.json.get("monitorer")
    status, msg = CustomerOpsControl().create_update(customer, technicalPerson, reviewer, monitorer, request.json.get("account"), request.json.get('coid'))
    return success(status, msg)

@CustomerOpsView.route("/delete", methods = ["POST"])
@auth.login_required(role = role)
def delete():
    if not request.json or not request.json.get("customerops"):
        return success(40004,"缺少参数")
    status, msg = CustomerOpsControl().delete(request.json.get("customerops"))
    return success(status, msg) if status == 20000 else success(status, msg = msg)
