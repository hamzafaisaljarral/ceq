import json

from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist

from ceq_user.database.models import User
from bson import ObjectId
from ceq_user.resources.errors import unauthorized, not_found


class CEQAddUserAPI(Resource):
    # @jwt_required()
    def post(self):
        # authorized: bool = User.objects.get(id=get_jwt_identity()).role.superadmin

        # if authorized:
        data = request.get_json()
        new_user = User(status=data['status'], username=data['username'], email=data['email'], role=data['role'],  
                        permission = data['permission'], supervisor = data["supervisor"])
        try:
            new_user.save()
        except Exception as e:
            print(e)
            return str(e)
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
                            permission = data['permission'], superviser = data["superviser"])

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
                id = request.json.get('id')
                obj_id = ObjectId(id)
                user_to_update = User.objects.get(id=obj_id)    
                if user_to_update is None:
                    return "user id not found", 404            
                # Retrieve supervisor if provided
                supervisor_name = request.json.get('supervisor')
                try:
                    if supervisor_name:
                        supervisor_obj = User.objects.get(username = supervisor_name)
                        if supervisor_obj["role"] != "supervisor":
                           supervisor_obj = None 
                    else: 
                        supervisor_obj = None
                except DoesNotExist:
                    return "supervisor user name not found", 404
                user_to_update.supervisor = supervisor_obj            
                user_to_update.username = request.json.get('username')
                user_to_update.email = request.json.get('email')
                user_to_update.status = request.json.get('status')
                user_to_update.role = request.json.get('role')
                user_to_update.name = request.json.get('name')
                user_to_update.permission = request.json.get('permission')
                
                user_to_update.save()
            except DoesNotExist:
                return not_found()
            return 'User updated successfully', 201
        else:
            print("error")
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
