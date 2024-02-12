from ceq_user.database.models import User, AuditData, Form1, Form2 
from ceq_user.resources.errors import unauthorized
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist
import json
# from datetime import datetime
import base64
import io


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
            audit_id = request.args.get('audit_id')
            if audit_id is not None:
                return jsonify({'message': 'Audit ID already exists'})
        
            audit_document = AuditData.objects(audit_id=audit_id).first()
            if audit_document:
                audit_document.delete()
                return jsonify({"message": f"Audit with ID {audit_id} deleted successfully"})
            else:
                return jsonify({"message": f"Audit with ID {audit_id} not found"})
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
        audit_id = request.args.get('audit_id')      
        
        try:
            # Retrieve audit data by audit_id
            audit_data = AuditData.objects(audit_id=audit_id).first()
            if audit_data is not None:
                return jsonify({'message': 'Audit ID already exists'})

            if audit_data:
                # Serialize audit_data to JSON
                audit_json = json.loads(audit_data.to_json())
                ceqv_list = ['ceqv01', 'ceqv02', 'ceqv03', 'ceqv04', 'ceqv05', 'ceqv06']
                for image_key in ceqv_list:
                    if hasattr(audit_data, image_key):
                        image_stream = getattr(audit_data[image_key], 'image')
                        if image_stream:                                   
                            audit_json[image_key]['image'] = base64.b64encode(image_stream.read()).decode('utf-8')
                                    
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
            # Retrieve all audit data
            all_audit_data = AuditData.objects()

            if all_audit_data:
                # Initialize an empty list to store serialized audit data
                audit_list = []
                # Iterate through each audit and serialize it to JSON
                for audit_data in all_audit_data:
                    audit_json = json.loads(audit_data.to_json())
                    # Convert image fields to base64 encoded strings    
                    audit_json = json.loads(audit_data.to_json())
                    ceqv_list = ['ceqv01', 'ceqv02', 'ceqv03', 'ceqv04', 'ceqv05', 'ceqv06']
                    for image_key in ceqv_list:
                        if hasattr(audit_data, image_key):
                            image_stream = getattr(audit_data[image_key], 'image')
                            if image_stream:                                   
                                audit_json[image_key]['image'] = base64.b64encode(image_stream.read()).decode('utf-8')            
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
        audit_id = request.args.get('audit_id')      
        try:
            # Retrieve the audit data by audit_id
            audit_data = AuditData.objects(audit_id=audit_id).first()
            if audit_data.first() is not None:
                return jsonify({'message': 'Audit ID already exists'})
            
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

                # Update Form2 objects
                form2_data = json.loads(data.get('form2'))
                for key, value in form2_data.items():
                    form2_obj = getattr(audit_data, key)
                    if form2_obj:
                        form2_obj.violation = value.get('violation')
                        form2_obj.remarks = value.get('remarks')
                
                # Update other audit data fields
                audit_data.username = data.get('username')
                audit_data.status = data.get('status')
                audit_data.name = data.get('name')
                audit_data.lastmodified = data.get('lastmodified')
                audit_data.supervisor_id = int(data.get('supervisor_id'))
                audit_data.expiryDate = data.get('expiryDate')
                audit_data.auditDate = data.get('auditDate')
                audit_data.remarks = data.get('remarks')
                audit_data.department = data.get('department')
                audit_data.createdDate = data.get('createdDate')
                audit_data.auditor_id = int(data.get('auditor_id'))
                audit_data.description = data.get('description')
                # Update images
                for image_key, file_data in request.files.items():
                    if image_key.startswith('ceqv') and image_key.endswith('_image'):
                        image_stream = io.BytesIO(file_data.read())
                        print(image_key)
                        setattr(audit_data[image_key[0:6]], 'image', image_stream)  
                    elif image_key in ['audit_signature', 'audited_staff_signature']:
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
            return jsonify({"message": "Unauthorized access"}), 403

        try:
            # Access form data
            data = request.form
            form1_data = data.get('form1')
            form2_data = data.get('form2')

            # Convert JSON strings to Python dictionaries
            form1_data = json.loads(form1_data)
            form2_data = json.loads(form2_data)

            # Create Form1 object
            form1 = Form1(**form1_data)

            # Create Form2 objects
            form2_objects = []
            for key, value in form2_data.items():
                form2_obj = Form2(
                    violation=value.get('violation'),
                    remarks=value.get('remarks')
                )
                form2_objects.append(form2_obj)

            # Create AuditData object
            audit_data = AuditData(
                username=data.get('username'),
                status=data.get('status'),
                name=data.get('name'),
                audit_id=int(data.get('audit_id')),
                lastmodified=data.get('lastmodified'),
                supervisor_id=int(data.get('supervisor_id')),
                expiryDate=data.get('expiryDate'),
                auditDate=data.get('auditDate'),
                remarks=data.get('remarks'),
                form1=form1,
                department=data.get('department'),
                createdDate=data.get('createdDate'),
                auditor_id=int(data.get('auditor_id')),
                description=data.get('description')
            )

            # Save Form2 objects
            for i, form2_obj in enumerate(form2_objects, start=1):
                setattr(audit_data, f'ceqv{i:02}', form2_obj)

            # Save image files
            for image_key, file_data in request.files.items():
                if image_key.startswith('ceqv') and image_key.endswith('_image'):
                    image_stream = io.BytesIO(file_data.read())
                    setattr(audit_data[image_key[0:6]], 'image', image_stream)  
                elif image_key in ['audit_signature', 'audited_staff_signature']:
                    signature_stream = io.BytesIO(file_data.read())
                    setattr(audit_data, image_key, signature_stream)    
            # Save the audit data to the database
            audit_data.save()

            return jsonify({'message': 'Audit created successfully'})

        except Exception as e:
            print("Exception:", e)
            return jsonify({'message': 'Error occurred while creating audit'})
