# -*- coding: utf-8 -*-
from ceq_user.database.models import User, AuditData, Category, ErrorCode, Violations
from ceq_user.resources.errors import unauthorized
from flask import request, jsonify, current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from mongoengine import DoesNotExist
from bson import ObjectId
import json
from datetime import datetime, timedelta
import os
import uuid
import paramiko


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
        if user.role not in ["audit", "supervisor", "admin"] and user.permission not in ["consumer", "all"]:
            return {"message":"'error': 'Unauthorized access'"}, 401        
        try:
            id_audit = ObjectId(request.args.get('audit_id'))
            # Retrieve audit data by audit_id
            audit_document = AuditData.objects(id=id_audit).first()
            if audit_document is None:
                return {'message': 'Audit ID Not Found'}, 404
            if audit_document:
                audit_data = json.loads(audit_document.to_json())
                for key in ['audit_signature', 'audited_staff_signature']:
                    if key in audit_data:
                        image_file=None
                        path = audit_data[key]
                        split_path = path.split('ceq/')
                        file_name = split_path[-1]
                        exact_path= "/app1/DSCE/PortalGateway/estore_backend/public/uploads/ceq/" + file_name
                        send_image_to_server(image_file,file_path= exact_path)      
                if "ceqvs" in audit_data:
                    for obj in audit_data["ceqvs"]:
                        if "violations" in obj:
                            for violation in obj["violations"]:
                                if "image" in violation:
                                    image_file=None
                                    path = violation["image"]
                                    split_path = path.split('ceq/')
                                    file_name = split_path[-1]
                                    exact_path= "/app1/DSCE/PortalGateway/estore_backend/public/uploads/ceq/" + file_name
                                    send_image_to_server(image_file,file_path= exact_path)             
                audit_document.delete()
                return {"message": "Audit with ID deleted successfully"}, 200
            else:
                return {"message": "Audit with ID not found"}, 404
        except Exception as e:
            print("Exception: ", e)
            return {"message": "Error: {}".format(str(e))}, 500
      
class GetConsumerAudit(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role not in ["audit", "supervisor", "admin"] and user.permission not in ["consumer", "all"]:
            return {"message": "Unauthorized access"}, 401
        try:  
            audit_id = ObjectId(request.args.get('audit_id'))
            audit_data = AuditData.objects(id=audit_id).first()
            if audit_data is None:
                return {"message" : "Audit Id Not Found"}, 404
            audit_data = json.loads(audit_data.to_json())
            if "createdDate" in audit_data:
                # Convert createdDate from Unix timestamp to datetime string
                created_date_unix = audit_data["createdDate"]["$date"]
                created_date_str = datetime.fromtimestamp(created_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                audit_data["createdDate"] = created_date_str
            if "expiryDate" in audit_data:
                # Convert expiryDate from Unix timestamp to datetime string
                expiry_date_unix = audit_data["expiryDate"]["$date"]
                expiry_date_str = datetime.fromtimestamp(expiry_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                audit_data["expiryDate"] = expiry_date_str
            if "signature_date" in audit_data:
                # Convert signature_date from Unix timestamp to datetime string
                signature_date_unix = audit_data["signature_date"]["$date"]
                signature_date_str = datetime.fromtimestamp(signature_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                audit_data["signature_date"] = signature_date_str
            if "lastmodified" in audit_data:
                # Convert lastmodified from Unix timestamp to datetime string
                lastmodified_date_unix = audit_data["lastmodified"]["$date"]
                lastmodified_str = datetime.fromtimestamp(lastmodified_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                audit_data["lastmodified"] = lastmodified_str    
                
            return jsonify(audit_data)
        except Exception as e:
            print("Exception: ", e)
            return {'message': 'Error occurred while retrieving audit'}, 500



class GetConsumerAuditList(Resource):
    @jwt_required()    
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()    
       
        if user.role not in ["audit", "supervisor", "admin"] and user.permission not in ["consumer", "all"]:
            return {"message": "Unauthorized access"}, 401
        try:
            # Retrieve all audit data
            all_audit_data = AuditData.objects()
            if all_audit_data:
                # Initialize an empty list to store serialized audit data
                audit_list = []
                # Iterate through each audit and serialize it to JSON
                for audit_data in all_audit_data:
                    audit_data = json.loads(audit_data.to_json())
                    if "auditor_name" in  audit_data:
                        if audit_data["auditor_name"] == user.name or user.role == "supervisor":
                            if "createdDate" in audit_data:
                                # Convert createdDate from Unix timestamp to datetime string
                                created_date_unix = audit_data["createdDate"]["$date"]
                                created_date_str = datetime.fromtimestamp(created_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                audit_data["createdDate"] = created_date_str
                            if "expiryDate" in audit_data:
                                # Convert expiryDate from Unix timestamp to datetime string
                                expiry_date_unix = audit_data["expiryDate"]["$date"]
                                expiry_date_str = datetime.fromtimestamp(expiry_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                audit_data["expiryDate"] = expiry_date_str
                            if "signature_date" in audit_data:
                                # Convert signature_date from Unix timestamp to datetime string
                                signature_date_unix = audit_data["signature_date"]["$date"]
                                signature_date_str = datetime.fromtimestamp(signature_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                audit_data["signature_date"] = signature_date_str
                            if "lastmodified" in audit_data:
                                # Convert lastmodified from Unix timestamp to datetime string
                                lastmodified_date_unix = audit_data["lastmodified"]["$date"]
                                lastmodified_str = datetime.fromtimestamp(lastmodified_date_unix / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                audit_data["lastmodified"] = lastmodified_str           
                                audit_list.append(audit_data)
                return jsonify(audit_list)
            else:
                return {'message': 'No audits found'}, 404
 
        except Exception as e:
            print("Exception: ", e)
            return {'message': 'Error occurred while retrieving audits'}, 500  


class CreateConsumerAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role not in ["audit", "supervisor", "admin"] and user.permission not in ["consumer", "all"]:
            return {"message": "Unauthorized access"}, 401      
        try:
            if user.role == "supervisor":
                supervisor_name = user.username
            elif user.role != "supervisor":                 
                if user.supervisor:
                    if not None:
                        sup_id = ObjectId(supervisor_name)
                        user_data = User.objects(id=sup_id).first()
                        if user_data:
                            supervisor_name = user_data.name
            # Access form data
            data = request.form
            ceqs_data = data.get('ceqvs')
            form2_data = json.loads(ceqs_data)
            current_date = datetime.now() - timedelta(days=1)
            expiry_date = current_date + timedelta(days=3)
            audit_data = AuditData(
                auditor_name=user.name,
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
                supervisor=supervisor_name,
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
                signature_date=current_date,
                auditedDateTime=data.get('auditedDateTime')
            )   
            image_file = request.files 
            ceqv_images = []
            for obj in form2_data:
                if "image" in obj:
                    ceqv_images.append(obj["image"])  
            for image_key, file_data in image_file.items():
                print(image_key, file_data)
                unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file_data.filename)                
                file_path = os.path.join("/app1/DSCE/PortalGateway/estore_backend/public/uploads/ceq/", str(unique_filename))
                if image_key == "audited_staff_signature":
                    audit_data.audited_staff_signature = "https://ossdev.etisalat.ae:8400/public/uploads/ceq/"+str(unique_filename)
                    send_image_to_server(file_data, file_path)
                if image_key == "audit_signature": 
                    audit_data.audit_signature = "https://ossdev.etisalat.ae:8400/public/uploads/ceq/"+str(unique_filename)
                    send_image_to_server(file_data, file_path)                
                if image_key in ceqv_images:
                    for obj in form2_data:
                        if "image" in obj:
                            if image_key == obj["image"]:
                                obj["image"] = "https://ossdev.etisalat.ae:8400/public/uploads/ceq/"+str(unique_filename)
                                send_image_to_server(file_data, file_path)  
            print(form2_data)                               
            violations = [Violations(**violation) for violation in form2_data]
            audit_data.ceqvs =  violations
            audit_data.save()
            audit_id = str(audit_data.id)
            audit = "audit created" 
            return jsonify({'message': audit,"audit_id":audit_id})

        except Exception as e:
            # file.close()
            print("Exception:", e)
            return {'message': "error:{}".format(e)} , 500


class UpdateConsumerAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role not in ["audit", "supervisor", "admin"] and user.permission not in ["consumer", "all"]:
            return {"message": "Unauthorized access"}, 401
        
        audit_id = ObjectId(request.args.get("audit_id"))
        audit_data = AuditData.objects(id=audit_id).first()
        image_file = request.files
        if audit_data is None:
            return {"message": "Audit not found"}, 404
        try:
            if audit_data:
                file_remove = []
                audit_json = json.loads(audit_data.to_json())
                for key in ['audit_signature', 'audited_staff_signature']:
                    if key in audit_json:
                        file_remove.append(audit_json[key])                      
                if "ceqvs" in audit_json:
                    for img in audit_json['ceqvs']:
                        if "image" in img:
                            file_remove.append(img["image"])
                file_data = None      
                data = request.form
                ceqs_data = data.get('ceqvs')
                form2_data = json.loads(ceqs_data)
                current_date = datetime.now()
                expiry_date = current_date + timedelta(days=3)
                # Update audit data
                audit_data.update(
                    set__auditor_name=audit_data.auditor_name,
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
                    set__signature_date=current_date,
                    set__auditedDateTime=data.get('auditedDateTime')
                )
                ceqv_images = []                    
                for obj in form2_data:
                    if "image" in obj:
                        ceqv_images.append(obj["image"])   
                        
                if "audited_staff_signature"  not in audit_json: 
                    if "audited_staff_signature"  in audit_data:
                        audit_data.audited_staff_signature = audit_json.audited_staff_signature  
                        
                if "audit_signature"  not in audit_json: 
                    if "audit_signature"  in audit_data:
                        audit_data.audit_signature = audit_json.audit_signature  
                for obj in form2_data:
                    if "category_code" in obj and "violation_code" in obj:                    
                        if "image" not in obj:
                            if "ceqvs" in audit_data:
                                for ext in audit_data["ceqvs"]:
                                    if (ext["category_code"]== obj["category_code"]) and (ext["violation_code"] == obj["violation_code"]):
                                        if "image" in ext:
                                            obj["image"] = ext["image"]                                      
                                    
                for image_key, file_data in request.files.items():
                    unique_filename = str(uuid.uuid4()) + '_' + file_data.filename
                    file_path = os.path.join("/app1/DSCE/APIGateway/ceq_files/", str(unique_filename))
                    if image_key in ['audited_staff_signature', 'audit_signature']:
                        if image_key == 'audited_staff_signature':
                            if file_data is None or file_data.filename == '':
                                if "audited_staff_signature" in audit_json:
                                    audit_data.update(set__audited_staff_signature=audit_json["audited_staff_signature"])                                    
                            else:  
                                audit_data.update(set__audited_staff_signature= "https://ossdev.etisalat.ae:8400/public/uploads/ceq/"+str(unique_filename))
                                send_image_to_server(file_data,file_path)
                        elif image_key == 'audit_signature':
                            if file_data is None or file_data.filename == '':
                                if "audit_signature" in audit_json:
                                    audit_data.update(set__audit_signature=audit_json["audit_signature"]) 
                            else:    
                                audit_data.update(set__audit_signature="https://ossdev.etisalat.ae:8400/public/uploads/ceq/"+str(unique_filename))
                                send_image_to_server(file_data,file_path)        
                    if image_key in ceqv_images:
                        for obj in form2_data:
                            if "image" in obj:
                                if image_key == obj["image"]:
                                    if file_data is None or file_data.filename == '':
                                        if "ceqvs" in audit_json:
                                            for ext in audit_json['ceqvs']:
                                                if obj["violation_code"] == ext["violation_code"]:
                                                   obj["image"] = ext["image"]                                                                                        
                                    else:            
                                        obj["image"] = "https://ossdev.etisalat.ae:8400/public/uploads/ceq/"+str(unique_filename) 
                                        send_image_to_server(file_data,file_path) 
                           
                        
                                           
                audit_data.ceqvs.clear()                    
                violations = [Violations(**violation) for violation in form2_data]
                audit_data.ceqvs =  violations
                # Save the updated audit data
                audit_data.save()
                return jsonify({'message': 'Audit updated successfully'})
        except Exception as e:
            print("Exception:", e)
            return {'message':'Error occurred while retrieving audits'}, 500

     
class DeleteConsumerImage(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role not in ["audit", "supervisor", "admin"] and user.permission not in ["consumer", "all"]:
            return {"message":"'error': 'Unauthorized access'"}, 401
        try:
            img = str(request.json.get('image_path'))
            image_path = "https://ossdev.etisalat.ae:8400/public/uploads/ceq/" + img
            audit_id = ObjectId(request.args.get("audit_id"))
            audit_data = AuditData.objects(id=audit_id).first()
            if audit_data is None:
                return {'message': 'Audit ID Not Found'}, 404
            image_file = None
            # Delete images and update paths for specific image paths
            exact_path = "/app1/DSCE/PortalGateway/estore_backend/public/uploads/ceq/"+img
            flag = True            
            if  "audited_staff_signature" in audit_data:
                if audit_data["audited_staff_signature"] == exact_path:
                    flag = False
                    send_image_to_server(image_file,file_path= exact_path) 
                    audit_data["audited_staff_signature"] = ""                
            if  "audit_signature" in audit_data:
                if audit_data["audit_signature"] == exact_path:
                    flag = False
                    send_image_to_server(image_file,file_path= exact_path) 
                    audit_data["audit_signature"] = ""            
            if "ceqvs" in audit_data:
                for obj in audit_data["ceqvs"]:
                    if "image" in obj and obj["image"] == image_path:
                        flag = False                           
                        image_file = None
                        exact_path= "/app1/DSCE/PortalGateway/estore_backend/public/uploads/ceq/" + img
                        send_image_to_server(image_file,file_path= exact_path)      
                        obj["image"] = ""
            if flag:
                exist = check_file_exit(exact_path) 
                if exist != True:
                    return {'message': 'file does not exist'}, 404                             
            # Save modified audit data
            print("2222222")
            print(audit_data)
            audit_data.save()
            return {"message": "Specific image deleted and path updated for Audit with ID {}".format(audit_id)}, 200
        except Exception as e:
            print("Exception: ", e)
            return {"message": "Error: {}".format(str(e))}, 500



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
    
   
  
# Function to send image data to the other server using Paramiko
def send_image_to_server(image_file,file_path,):
    try:
        # Connect to the remote server via SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect('10.106.22.167', username='admin', password='zxcvbnm,./')  # Replace with actual credentials
        # Transfer the image file to the remote server
        sftp_client = ssh_client.open_sftp()
        if image_file == None:
           sftp_client.remove(file_path)
        else:
            sftp_client.putfo(image_file, file_path)  # Replace with the destination path on the server
        sftp_client.close()
        # Close the SSH connection
        ssh_client.close()
        return {'message': 'Image uploaded successfully'}
    except Exception as e:
        return {'error': str(e)}    
    
def check_file_exit(file_path):
    try:
        # Connect to the remote server via SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect('10.106.22.167', username='admin', password='zxcvbnm,./')  # Replace with actual credentials
        # Check if the image exists on the server
        sftp_client = ssh_client.open_sftp()
        try:
            sftp_client.stat(file_path)
            exist = True
        except FileNotFoundError:
            exist =  False
        return exist
    except Exception as e:
        return {'error': str(e)}     
    
    