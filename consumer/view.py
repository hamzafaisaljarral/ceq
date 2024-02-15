from ceq_user.database.models import User, AuditData, Form1, Form2
from ceq_user.resources.errors import unauthorized
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist
from bson import ObjectId
import json
from datetime import datetime
import base64
import io

# fs = GridFS(connect(db='ceq', host='localhost'))
# db = client[your_database]  # Replace 'your_database' with your actual database name


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
            if audit_data:
                # Serialize audit_data to JSON
                audit_json = json.loads(audit_data.to_json())
                # Convert audit_signature and audited_staff_signature to base64 encoded strings
                for signature_key in ['audit_signature', 'audited_staff_signature']:
                    if hasattr(audit_data, signature_key):
                        signature_stream = getattr(audit_data, signature_key)
                        if signature_stream:
                            audit_json[signature_key] = base64.b64encode(signature_stream.read()).decode('utf-8')
            
                return jsonify(audit_json)
            else:
                return jsonify({'message': 'Audit not found'})

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
            print("Dateeeeeeeeeeeeeeeeee",datetime.now())
            # Retrieve all audit data
            all_audit_data = AuditData.objects()

            if all_audit_data:
                # Initialize an empty list to store serialized audit data
                audit_list = []
                # Iterate through each audit and serialize it to JSON
                for audit_data in all_audit_data:
                    audit_json = json.loads(audit_data.to_json())
                    # Convert audit_signature and audited_staff_signature to base64 encoded strings
                    for signature_key in ['audit_signature', 'audited_staff_signature']:
                        if hasattr(audit_data, signature_key):
                            signature_stream = getattr(audit_data, signature_key)
                            if signature_stream:
                                audit_json[signature_key] = base64.b64encode(signature_stream.read()).decode('utf-8')
                    # Append the serialized audit data to the audit_list
                    audit_list.append(audit_json)
                return jsonify(audit_list)
            else:
                return jsonify({'message': 'No audits found'})

        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'Error occurred while retrieving audits'})

class UpdateConsumerAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()       
        if (user.role == "audit" or user.role == "superviser" )  and (user.permission != "consumer"):
            return jsonify({"message" : "'error': 'Unauthorized access'"})
           
        try:
            # Retrieve the audit data by audit_id
            id = ObjectId(request.args.get('audit_id'))            
            audit_data = AuditData.objects(id=id).first()
            if audit_data is None:
                return jsonify({'message': 'Audit ID Not Found'})
            
            if audit_data:
                # Access form data
                data = request.form
                # Update Form1 object
                form1_data = json.loads(data.get('form1'))
                form1 = Form1(
                    supervisor_contact=form1_data.get('supervisor_contact'),
                    tech_pt=form1_data.get('tech_pt'),
                    vehicle_number=form1_data.get('vehicle_number'),
                    tech_skills=form1_data.get('tech_skills'),
                    sr_manager=form1_data.get('sr_manager'),
                    tech_fullname=form1_data.get('tech_fullname'),
                    region=form1_data.get('region'),
                    vendor=form1_data.get('vendor'),
                    director=form1_data.get('director'),
                    sr_number=form1_data.get('sr_number'),
                    tech_ein=form1_data.get('tech_ein'),
                    team=form1_data.get('team'),
                    duty_manager=form1_data.get('duty_manager'),
                    supervisor=form1_data.get('supervisor'),
                    shortdescription=form1_data.get('shortdescription'),
                    tech_contact=form1_data.get('tech_contact')
                )
                audit_data.form1 = form1

                form2_data_str = data.get('ceqvs')
                form2_data = json.loads(form2_data_str)
                form2_objects = {}
                for key, value in form2_data.items():
                    form2_objects[key] = Form2(**value)
                 
                audit_data.ceqvs = form2_objects
                # Update other audit data fields
                audit_data.status = data.get('status')
                audit_data.name = data.get('name')
                audit_data.lastmodified = datetime.now()
                audit_data.supervisor_id = data.get('supervisor_id')
                audit_data.expiryDate = data.get('expiryDate')
                audit_data.auditDate = data.get('auditDate')
                audit_data.remarks = data.get('remarks')
                audit_data.department = data.get('department')
                audit_data.description = data.get('description')
                # Update images
                for image_key, file_data in request.files.items(): 
                    if image_key in ['audit_signature', 'audited_staff_signature']:
                        signature_stream = io.BytesIO(file_data.read())
                        setattr(audit_data, image_key, signature_stream) 

                # Save the updated audit data
                audit_data.save()

                return jsonify({'message': 'Audit updated successfully'})
            else:
                return jsonify({'message': 'Audit not found'})

        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'Error occurred while updating audit'})


class CreateConsumerAudit(Resource):
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
            for key, value in form2_data.items():
                form2_objects[key] = Form2(**value)
            # Create Form1 object
            form1 = Form1(**form1_data)
            # Create AuditData object
            audit_data = AuditData(
                form1=form1,
                status=data.get('status'),
                lastmodified=datetime.now(),
                supervisor_id=int(data.get('supervisor_id')),
                expiryDate=datetime.now(),
                auditDate=data.get('auditDate'),
                remarks=data.get('remarks'),
                ceqvs=form2_objects,
                department=data.get('department'),
                createdDate=data.get('createdDate'),
                description=data.get('description')
            )  
            
            for image_key, file_data in request.files.items():
                if image_key in ['audit_signature', 'audited_staff_signature']:
                    signature_stream = io.BytesIO(file_data.read())
                    setattr(audit_data, image_key, signature_stream) 
            # Save the audit data to the database
            audit_data.save()

            return jsonify({'message': 'Audit created successfully'})

        except Exception as e:
            print("Exception:", e)
            return jsonify({'message': 'Error occurred while creating audit'})
