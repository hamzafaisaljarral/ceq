import json

from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist

from ceq_user.database.models import User

from ceq_user.resources.errors import unauthorized, not_found


class CEQAddUserAPI(Resource):
    # @jwt_required()
    def post(self):
        # authorized: bool = User.objects.get(id=get_jwt_identity()).role.superadmin

        # if authorized:
        data = request.get_json()
        new_user = User(status=data['status'], username=data['username'], email=data['email'], role=data['role'],
                        supervisor=data['supervisor'], department=data['department'])
        try:
            new_user.save()
        except Exception as e:
            print(e)
            return 'User already exist', 400
        return 'User added successfully', 201


class CEQAddNewUserAPI(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return not_found()

        if user.role == "admin":
            data = request.get_json()
            new_user = User(status=data['status'], username=data['username'], email=data['email'], role=data['role'],
                            supervisor=data['supervisor'], department=data['department'])
            new_user.save()
            return 'User added successfully', 201
        else:
            return unauthorized()


class CEQUpdateUserAPI(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return not_found()

        if user.role == "admin":
            try:
                user = User.objects.get(id=request.json.get('id'))
                username = request.json.get('username')
                email = request.json.get('email')
                status = request.json.get('status')
                role = request.json.get('role')
                supervisor = request.json.get('supervisor')
                department = request.json.get('department')
                user.update(username=username, email=email, status=status, role=role, supervisor=supervisor, department=department)
            except DoesNotExist:
                return not_found()
            return 'User updated successfully', 201
        else:
            return unauthorized()


class CEQViewAllUserAPI(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return not_found()

        # if user.role == "superadmin":
        users = User.objects().order_by("-id")
        users_json = json.loads(users.to_json())
        return jsonify(users_json)
        # else:
        # return unauthorized()


class CEQDeleteUserAPI(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return not_found()

        if user.role == "admin":
            try:
                User.objects(username=data['username']).delete()
            except DoesNotExist:
                return not_found()
            return 'User deleted successfully', 201
        else:
            return unauthorized()


class CEQUpdateUserStatusAPI(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return not_found()

        if user.role == "admin":
            try:
                user = User.objects.get(username=request.json.get('username'))
                user.update(status=request.json.get('status'))
            except DoesNotExist:
                return not_found()
            return 'User status updated successfully', 201
        else:
            return unauthorized()
