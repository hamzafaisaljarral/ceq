from ceq_user.database.models import User, AuditData, Voilation, Category, ErrorCode
from ceq_user.resources.errors import unauthorized
from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from mongoengine import DoesNotExist
from bson import ObjectId
import json
from datetime import datetime,timedelta
import base64
import os
import io
import uuid
import pdb

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
            return jsonify({"message":"'error': 'Unauthorized access'"})        
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
                        if "image" in img["image"]:
                            if os.path.exists(img["image"]):
                                print(img["image"])
                                os.remove(img["image"])
          
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
        if user.role != "audit" and (user.permission not in ["consumer", "all"]):
            return jsonify({"message": "Unauthorized access"}) 
        
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
                        if "image" in img:
                            if os.path.exists(img["image"]):
                                with open(img["image"], 'rb') as file:
                                    img["image"] = base64.b64encode(file.read()).decode('utf-8')
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
        
        if user.role != "audit" and (user.permission not in ["consumer", "all"]):
            return jsonify({"message": "Unauthorized access"}) 
        
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
                            if "image" in img:
                                if os.path.exists(img["image"]):
                                    with open(img["image"], 'rb') as file:
                                        img["image"] = base64.b64encode(file.read()).decode('utf-8')
                    audit_list.append(audit_json)
                return jsonify(audit_list)
            else:
                return jsonify({'message': 'No audits found'})

        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'Error occurred while retrieving audits'})
        
class CreateConsumerAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role != "audit" and (user.permission not in ["consumer", "all"]):
            return jsonify({"message": "Unauthorized access"})        
        try:
            if user.role == "supervisor":
                supervisor = user.username
            else:
                supervisor = ""
            data = request.form
            ceqs_data = data.get('ceqvs')
            form2_data = json.loads(ceqs_data)
            current_date = datetime.now()
            expiry_date = current_date + timedelta(days=3)
            audit_data = AuditData(
                supervisor_contact=data.get('supervisor_contact'),
                tech_pt=data.get('tech_pt'),
                vehicle_number=data.get('vehicle_number'),
                tech_skills=data.get('tech_skills'),
                sr_manager=data.get('sr_manager'),
                tech_fullname=data.get('tech_fullname'),
                region=data.get('region'),
                vendor=data.get('vendor'), 
                director=data.get('director'),
                auditor_id=data.get('auditor_id'),
                sr_number=data.get('sr_number'),
                tech_ein=data.get('tech_ein'),
                team=data.get('team'),
                duty_manager=data.get('duty_manager'),
                supervisor=supervisor,
                shortdescription=data.get('shortdescription'),
                tech_contact=data.get('tech_contact'),
                controller=data.get('controller'),
                group_head=data.get('group_head'),
                user_action=data.get('user_action'),
                status=data.get('status'),
                lastmodified=datetime.now(),
                expiryDate=expiry_date,
                ceqvs=[],
                auditDate=data.get('auditDate'),
                permission=data.get('permission'),
                createdDate=current_date,
                signature_date=current_date
            )  
            ceqv_images = []
            ceq_obj = []
            for obj in form2_data:
                ceq_obj.append(obj)
                if "image" in obj["image"]:
                    ceqv_images.append(obj['image'])
            for image_key, file_data in request.files.items():
                if image_key in ['audited_staff_signature', 'audit_signature']:
                    unique_filename = str(uuid.uuid4()) + '_'+secure_filename(file_data.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    if image_key == 'audited_staff_signature':
                        audit_data.audited_staff_signature = file_path
                    if image_key == 'audit_signature':
                        audit_data.audit_signature = file_path
                    file_data.save(file_path)
                if image_key in ceqv_images:
                    unique_filename = str(uuid.uuid4()) + '_'+secure_filename(file_data.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    for obj in form2_data:
                        if "image" in obj["image"]:
                            if obj['image'] == image_key:
                                obj['image'] = file_path
                                file_data.save(file_path)
            for obj in form2_data:                             
                if "name" in obj['category_code']:
                    name = obj['category_code']["name"]
                    error_codes = obj['category_code']["error_codes"]
                    try:
                        category_obj = Category.objects.get(name=name)
                    except Category.DoesNotExist:
                        category_obj = Category.objects.create(name=name,error_codes=error_codes)
                    vilation_data = Voilation(  
                        category_code=category_obj,
                        violation_type=obj["violation_type"],
                        remarks=obj["remarks"],
                        image=obj["image"],
                        severity=obj["severity"]
                    )
                    audit_data.ceqvs.append(vilation_data)              
            audit_data.save()
            audit_id = str(audit_data.id)
            audit = "audit created " + audit_id
            return jsonify({'message': audit})
        except Exception as e:
            print("Exception:", e)
            return jsonify({'message': "error:{}".format(e)})

class UpdateConsumerAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return jsonify({"message": "Unauthorized access"})
        if user.role != "audit" and (user.permission not in ["consumer", "all"]):
            return jsonify({"message": "Unauthorized access"})
        audit_id = ObjectId(request.args.get("audit_id"))
        audit_data = AuditData.objects(id=audit_id).first()
        try:
            if audit_data is None:
                return jsonify({"message": "Audit not found"})
            # List to store file paths to be removed
            file_remove = []
            # Collect file paths from existing audit data
            for key in ['audit_signature', 'audited_staff_signature']:
                if key in audit_data:
                    file_remove.append(audit_data[key])
            if "ceqvs" in audit_data:
                for obj in audit_data['ceqvs']:     
                    if "image" in obj:
                        file_remove.append(obj["image"])
            for fr in file_remove:
                if os.path.exists(str(fr)):
                    os.remove(fr)
            # Fetch form data
            data = request.form
            ceqs_data = data.get('ceqvs')
            form2_data = json.loads(ceqs_data)
            current_date = datetime.now()
            expiry_date = current_date + timedelta(days=3)
            # Update audit data
            audit_data.update(
                set__supervisor_contact=data.get('supervisor_contact'),
                set__tech_pt=data.get('tech_pt'),
                set__vehicle_number=data.get('vehicle_number'),
                set__tech_skills=data.get('tech_skills'),
                set__sr_manager=data.get('sr_manager'),
                set__tech_fullname=data.get('tech_fullname'),
                set__region=data.get('region'),
                set__vendor=data.get('vendor'),
                set__director=data.get('director'),
                set__auditor_id=data.get('auditor_id'),
                set__sr_number=data.get('sr_number'),
                set__tech_ein=data.get('tech_ein'),
                set__team=data.get('team'),
                set__duty_manager=data.get('duty_manager'),
                set__shortdescription=data.get('shortdescription'),
                set__tech_contact=data.get('tech_contact'),
                set__controller=data.get('controller'),
                set__group_head=data.get('group_head'),
                set__user_action=data.get('user_action'),
                set__status=data.get('status'),
                set__lastmodified=datetime.now(),
                set__expiryDate=expiry_date,
                set__ceqvs=[],
                set__auditDate=data.get('auditDate'),
                set__permission=data.get('permission'),
                set__createdDate=current_date,
                set__signature_date=current_date
            )
            ceqv_images = []
            for img in form2_data:
                if "image" in img:
                    ceqv_images.append(img["image"])
            # Update images
            for image_key, file_data in request.files.items():
                # Generate unique filename
                unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file_data.filename)
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

                # Save the file
                file_data.save(file_path)
                # pdb.set_trace()
                # Update audit data with the file path
                if image_key in ['audited_staff_signature', 'audit_signature']:
                    if image_key == 'audited_staff_signature':
                        audit_data.update(set__audited_staff_signature=file_path)
                    elif image_key == 'audit_signature':
                        audit_data.update(set__audit_signature=file_path)        
                elif image_key in ceqv_images:
                    for img in form2_data:
                        if image_key == img["image"]:
                            img["image"] = file_path
            # Update ceqv data
            for obj in form2_data:
                if "name" in obj['category_code']:
                    name = obj['category_code']["name"]
                    error_codes = obj['category_code']["error_codes"]
                    try:
                        category_obj = Category.objects.get(name=name)
                    except Category.DoesNotExist:
                        category_obj = Category.objects.create(name=name,error_codes=error_codes)
                    vilation_data = Voilation(  
                        category_code=category_obj,
                        violation_type=obj["violation_type"],
                        remarks=obj["remarks"],
                        image=obj["image"],
                        severity=obj["severity"]
                    )
                    audit_data.ceqvs.append(vilation_data) 
            # Save the updated audit data
            audit_data.save()
            return jsonify({'message': 'Audit updated successfully'})
        except Exception as e:
            print("Exception:", e)
            return jsonify({'message': "error:{}".format(e)})


class AddErrorCategory(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Category name is required')
        parser.add_argument('error_codes', type=list, location='json', required=False)
        args = parser.parse_args()

        name = args.get('name')
        error_codes = args.get('error_codes')

        category = Category(name=name)
        if error_codes is not None:
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
