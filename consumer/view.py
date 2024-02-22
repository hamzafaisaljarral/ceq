from ceq_user.database.models import User, AuditData, Voilation, Category, ErrorCode
from ceq_user.resources.errors import unauthorized
from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from mongoengine import DoesNotExist
from bson import ObjectId
import json
from datetime import datetime
import base64
import os
import io
import uuid

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'C:\\Users\\hemanthareddy.p\\Desktop\\ceq_main\\static\\consumer')


# This api is used to return hello world
class Test(Resource):
    def get(self):
        return jsonify({"message": "hellow world "})


class DeleteConsumerAudit(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role != "audit" and user.permission != "consumer":
            return jsonify({"message" : "'error': 'Unauthorized access'"})        
        try:
            id_audit = ObjectId(request.args.get('audit_id'))
            # Retrieve audit data by audit_id
            audit_document = AuditData.objects(id=id_audit).first()
            if audit_document is None:
                return jsonify({'message': 'Audit ID Not Found'})
            if audit_document:
                audit_json = json.loads(audit_document.to_json())
                for key in ['audit_signature', 'audited_staff_signature']:
                    if key in audit_json:
                        if os.path.exists(audit_json[key]):
                            os.remove(audit_json[key])      
                if "ceqvs" in audit_json:
                    for img in audit_json["ceqvs"]:
                        if "image" in audit_json["ceqvs"][img]:
                            if os.path.exists(audit_json["ceqvs"][img]["image"]):
                                print(audit_json["ceqvs"][img]["image"])
                                os.remove(audit_json["ceqvs"][img]["image"])
          
                audit_document.delete()
                return jsonify({"message": "Audit with ID deleted successfully"})
            else:
                return jsonify({"message": "Audit with ID not found"})
        except Exception as e:
            print("Exception: ", e)
            return jsonify({"message": "Error: {}".format(str(e))})


class GetConsumerAudit(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role != "audit" and user.permission != "consumer":
            return jsonify({"message" : "'error': 'Unauthorized access'"})
        try:            
            audit_id = ObjectId(request.args.get('audit_id'))
            audit_data = AuditData.objects(id=audit_id).first()
            if audit_data is None:
                return jsonify({"message" : "Audit Id Not Found"})
            if audit_data:
                audit_json = json.loads(audit_data.to_json())
                for key in ['audit_signature', 'audited_staff_signature']:
                    if key in audit_json:
                        if os.path.exists(audit_json[key]):
                            with open(audit_json[key], 'rb') as file:
                                audit_json[key] = base64.b64encode(file.read()).decode('utf-8')         
                if "ceqvs" in audit_json:
                    for img in audit_json["ceqvs"]:
                        print(audit_json["ceqvs"][img])
                        if "image" in audit_json["ceqvs"][img]:
                            if os.path.exists(audit_json["ceqvs"][img]["image"]):
                                with open(audit_json["ceqvs"][img]["image"], 'rb') as file:
                                    audit_json["ceqvs"][img]["image"] = base64.b64encode(file.read()).decode('utf-8')
            return jsonify(audit_json)   
        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'Error occurred while retrieving audit'})


class GetConsumerAuditList(Resource):
    @jwt_required()    
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()     
        
        if user.role != "audit" and user.permission != "consumer":
            return jsonify({"message" : "'error': 'Unauthorized access'"})        
        
        try:
            # Retrieve all audit data
            all_audit_data = AuditData.objects()
            if all_audit_data:
                # Initialize an empty list to store serialized audit data
                audit_list = []
                # Iterate through each audit and serialize it to JSON
                for audit_data in all_audit_data:
                    audit_json = json.loads(audit_data.to_json())
                    for key in ['audit_signature', 'audited_staff_signature']:
                        if key in audit_json:
                            if os.path.exists(audit_json[key]):
                                with open(audit_json[key], 'rb') as file:
                                    audit_json[key] = base64.b64encode(file.read()).decode('utf-8')         
                    if "ceqvs" in audit_json:
                        for img in audit_json["ceqvs"]:
                            print(audit_json["ceqvs"][img])
                            if "image" in audit_json["ceqvs"][img]:
                                if os.path.exists(audit_json["ceqvs"][img]["image"]):
                                    with open(audit_json["ceqvs"][img]["image"], 'rb') as file:
                                        audit_json["ceqvs"][img]["image"] = base64.b64encode(file.read()).decode('utf-8')
                    audit_list.append(audit_json)
                return jsonify(audit_list)
            else:
                return jsonify({'message': 'No audits found'})

        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'Error occurred while retrieving audits'})


class CreateConsumerAudit(Resource): #please change it as per the model
        @jwt_required()
        def post(self):
            try:
                user = User.objects.get(id=get_jwt_identity()['id'])
            except DoesNotExist:
                return unauthorized()
            if user.role != "audit" and user.permission != "consumer":
                return jsonify({"message": "Unauthorized access"})
            try:
                # Access form data
                data = request.form
                form1_data = data.get('form1')
                # Convert JSON strings to Python dictionaries
                form1_data = json.loads(form1_data)
                # Create Form2 objects
                form2_data_str = data.get('ceqvs')
                form2_data = json.loads(form2_data_str)
                form2_objects = {}
                # Create Form1 object
                form1 = Voilation(**form1_data)
                # Create AuditData object
                audit_data = AuditData(
                    Voilation=Voilation,
                    status=data.get('status'),
                    lastmodified=datetime.now(),
                    supervisor_id=int(data.get('supervisor_id')),
                    expiryDate=datetime.now(),
                    auditDate=datetime.strptime(data.get('auditDate'), '%Y-%m-%d'),
                    remarks=data.get('remarks'),
                    permission=data.get('permission'),
                    createdDate=datetime.strptime(data.get('createdDate'), '%Y-%m-%d'),
                    description=data.get('description')
                )

                ceqv_images = []
                ceq_obj = []
                for obj in form2_data:
                    ceq_obj.append(str(obj))
                    if "image" in form2_data[obj]:
                        ceqv_images.append(form2_data[obj]['image'])
                for image_key, file_data in request.files.items():
                    if image_key in ['audited_staff_signature', 'audit_signature']:
                        # Generate a unique filename
                        unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file_data.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        if image_key == 'audited_staff_signature':
                            audit_data.audited_staff_signature = file_path
                        if image_key == 'audit_signature':
                            audit_data.audit_signature = file_path
                        file_data.save(file_path)
                    if image_key in ceqv_images:
                        unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file_data.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        for i in ceq_obj:
                            if "image" in form2_data[i]:
                                if form2_data[i]['image'] == image_key:
                                    form2_data[i]['image'] = file_path
                                    file_data.save(file_path)

                for key, value in form2_data.items():
                    form2_objects[key] = Voilation(**value)
                audit_data.ceqvs = form2_objects
                audit_data.save()

                return jsonify({'message': 'Audit created successfully'})

            except Exception as e:
                print("Exception:", e)
                return jsonify({'message': "error:{}".format(e)})


class UpdateConsumerAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role != "audit" and user.permission != "consumer":
            return jsonify({"message": "Unauthorized access"})
        
        audit_id = ObjectId(request.args.get("audit_id"))
        audit_data = AuditData.objects(id=audit_id).first()
        image_file = request.files
        if audit_data is None:
            print({"message": "Audit not found"})
            return jsonify({"message": "Audit not found"})  
        try:
            if audit_data:
                file_remove = []
                audit_json = json.loads(audit_data.to_json())
                for key in ['audit_signature', 'audited_staff_signature']:
                    if key in audit_json:
                        file_remove.append(audit_json[key])                      
                if "ceqvs" in audit_json:
                    for obj in audit_json['ceqvs']:       
                        if "image" in audit_json['ceqvs'][obj]:
                            file_remove.append(audit_json['ceqvs'][obj]["image"])
                print("file_remove ", file_remove)
                for fr in file_remove:
                    if os.path.exists(fr):
                        os.remove(fr)
                # Access form data
                data = request.form
                form1_data = data.get('form1')
                # Convert JSON strings to Python dictionaries
                form1_data = json.loads(form1_data)
                # Create Form1 object
                form1 = Voilation(**form1_data)
                # Update Form1 data
                for key, value in form1_data.items():
                    setattr(audit_data.form1, key, value)
                # Update other audit data fields
                audit_data.status = data.get('status')
                audit_data.lastmodified = datetime.now()
                audit_data.supervisor_id = int(data.get('supervisor_id'))
                audit_data.expiryDate = datetime.now()  # Update as needed
                audit_data.auditDate = data.get('auditDate')
                audit_data.remarks = data.get('remarks')
                audit_data.department = data.get('department')
                audit_data.createdDate = data.get('createdDate')
                audit_data.description = data.get('description')
                # Update CEQVs
                form2_data_str = data.get('ceqvs')
                form2_data = json.loads(form2_data_str)
                form2_objects = {}
                for key, value in form2_data.items():
                    form2_objects[key] = Voilation(**value)
                ceqv_images = []
                ceq_obj = []
                for obj in form2_data:
                    ceq_obj.append(str(obj))
                    if "image" in form2_data[obj]:
                        ceqv_images.append(form2_data[obj]['image'])
                # Update images
                
                for image_key, file_data in image_file.items():
                    if image_key in ['audited_staff_signature', 'audit_signature']:
                        # Generate a unique filename
                        unique_filename = str(uuid.uuid4()) + '_' + file_data.filename
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        if image_key == 'audited_staff_signature':
                            if os.path.exists(audit_data.audited_staff_signature):
                                file_remove.append(audit_data.audited_staff_signature)                                   
                            audit_data.audited_staff_signature = file_path
                            
                        if image_key == 'audit_signature':
                            audit_data.audit_signature = file_path
                        file_data.save(file_path)
                    if image_key in ceqv_images:
                        unique_filename = str(uuid.uuid4()) + '_' + file_data.filename
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        for i in ceq_obj:
                            if "image" in form2_data[i]:
                                if form2_data[i]['image'] == image_key:                                    
                                    form2_data[i]['image'] = file_path
                                    file_data.save(file_path) 
                for key, value in form2_data.items():
                    form2_objects[key] = Voilation(**value)
                audit_data.ceqvs = form2_objects
                # Save the updated audit data
                audit_data.save()

                return jsonify({'message': 'Audit updated successfully'})
        except Exception as e:
            print("Exception:", e)
            return jsonify({'message':'Error occurred while retrieving audits'})


class AddErrorCategory(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Category name is required')
        parser.add_argument('error_codes', type=list, location='json', required=False)
        args = parser.parse_args()

        name = args.get('name')
        error_codes = args.get('error_codes', [])

        category = Category(name=name)
        for ec in error_codes:
            error_code = ErrorCode(code=ec['code'], description=ec['description'])
            category.error_codes.append(error_code)

        category.save()
        return {'message': 'Category added successfully', 'category_id': str(category.id)}, 201


class GetAllCategories(Resource):
    def get(self):
        categories = Category.objects().all()
        categories_data = []
        for category in categories:
            category_data = {
                'id': str(category.id),
                'name': category.name,
                'error_codes': [{
                    'code': ec.code,
                    'description': ec.description
                } for ec in category.error_codes]
            }
            categories_data.append(category_data)

        return {'categories': categories_data}, 200
