from ceq_user.database.models import User, AuditData
from ceq_user.resources.errors import unauthorized
from flask import Flask, request, Response, jsonify, abort, send_file
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from bson import ObjectId
from gridfs import GridFS
import io
from io import BytesIO
from bson import json_util
import base64





ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ObjectIdEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


# This api is used to return hello world
class Test(Resource):
    def get(self):
        return {"message": "hellow world "}


class CreateConsumerAudit(Resource):
    def post(self):
        try:
            # Access form data
            json_data = {
                'username': request.form.get('username'),
                'status': request.form.get('status'),
                'name': request.form.get('name'),
                'audit_id': int(request.form.get('audit_id')),
                'lastmodified': request.form.get('lastmodified'),
                'supervisor_id': int(request.form.get('supervisor_id')),
                'expiryDate': request.form.get('expiryDate'),  # Make sure to add this field
                'auditDate': request.form.get('auditDate'),  # Make sure to add this field
                'remarks': request.form.get('remarks'),
                'form1': json.loads(request.form.get('form1')),
                'department': request.form.get('department'),
                'createdDate': request.form.get('createdDate'),  # Make sure to add this field
                'auditor_id': int(request.form.get('auditor_id')),
                'form2': json.loads(request.form.get('form2')),
                'form3': json.loads(request.form.get('form3')),
                'description': request.form.get('description'),
            }   
            image_data = request.files.get('image')
            signature_data = request.files.get('signature')
            audit_data = AuditData(**json_data)
            
            existing_document = AuditData.objects(audit_id=json_data["audit_id"]).first()
            if existing_document is None:
                # Check if the file is an allowed image type
                if image_data and allowed_file(image_data.filename):
                    # Process and save image to GridFS
                    image_stream = io.BytesIO(image_data.read())
                    audit_data.image.put(image_stream, content_type='image/jpeg')
                    
                    # Save signature to GridFS
                    if signature_data and allowed_file(signature_data.filename):
                        signature_stream = io.BytesIO(signature_data.read())
                        audit_data.signature.put(signature_stream, content_type='image/jpeg')
                audit_data.save()
                return jsonify({'message': 'Data saved successfully'})
            else:
                return jsonify({"message": 'Error: audit_id must be unique. Duplicate audit_id found.'})
                
        except Exception as e:
            print("Exception: ", e)
            data = {"message": "error "+str(e)}
            return jsonify(data)
        
                
class GetConsumerAudit(Resource):
    def get(self):
        try: 
            data = request.args.get('audit_id')
            audit_data = AuditData.objects(audit_id=data).first()
            image = base64.b64encode(audit_data.image.read()).decode('utf-8')
            content_type1 = audit_data.image.content_type
            signature = base64.b64encode(audit_data.signature.read()).decode('utf-8')
            content_type2 = audit_data.signature.content_type
            if audit_data:
                result = json.loads(json.dumps(audit_data.to_mongo(), cls = ObjectIdEncoder))
                # return send_file(
                #     BytesIO(image),
                #     mimetype=content_type,
                #     as_attachment=True,
                #     download_name=f"downloaded_file_{data}.jpg"  # Set the desired download filename
                # )
                result['signature'] = str(signature)
                result['signature_content_type'] = content_type2               
                result['image'] = str(image)
                result['image_content_type'] = content_type1
                return jsonify(result)
                
            else:
                return jsonify({"message": "Audit data not found for audit_id: {}".format(data)})

        except Exception as e:
            print("Exception: ", e)
            return jsonify({"message": "Error: {}".format(str(e))})

   
class DeleteConsumerAudit(Resource):
    def get(self):
        try:
            audit_id = request.args.get('audit_id')            
            audit_document = AuditData.objects(audit_id=audit_id).first()
            if audit_document:
                audit_document.delete()
                return jsonify({"message": f"Audit with ID {audit_id} deleted successfully"})
            else:
                return jsonify({"message": f"Audit with ID {audit_id} not found"})
        except Exception as e:
            print("Exception: ", e)
            return jsonify({"message": "Error: {}".format(str(e))})
       

class UpdateConsumerAudit(Resource):
    def post(self):
        try: 
            # pdb.set_trace()
            json_data = {
                'username': request.form.get('username'),
                'status': request.form.get('status'),
                'name': request.form.get('name'),
                'lastmodified': request.form.get('lastmodified'),
                'supervisor_id': int(request.form.get('supervisor_id')),
                'expiryDate': request.form.get('expiryDate'),
                'auditDate': request.form.get('auditDate'),
                'remarks': request.form.get('remarks'),
                'form1': json.loads(request.form.get('form1')),
                'department': request.form.get('department'),
                'createdDate': request.form.get('createdDate'),
                'auditor_id': int(request.form.get('auditor_id')),
                'form2': json.loads(request.form.get('form2')),
                'form3': json.loads(request.form.get('form3')),
                'description': request.form.get('description'),
            }
            print(json_data)
            image_data = request.files.get('image')
            signature_data = request.files.get('signature')

            existing_document = AuditData.objects(audit_id=1).first()

            if existing_document:
                # Update existing fields
                for key, value in json_data.items():
                    setattr(existing_document, key, value)

                # Check and update image
                if image_data and allowed_file(image_data.filename):
                    image_stream = io.BytesIO(image_data.read())
                    existing_document.image.replace(image_stream, content_type='image/jpeg')

                # Check and update signature
                if signature_data and allowed_file(signature_data.filename):
                    signature_stream = io.BytesIO(signature_data.read())
                    existing_document.signature.replace(signature_stream, content_type='image/jpeg')

                existing_document.save()
                return jsonify({'message': 'Data updated successfully'})
            else:
                return jsonify({"message": 'Error: No audit found with the given audit_id.'})

        except Exception as e:
            print("Exception: ", e)
            data = {"message": "error "+str(e)}
            return jsonify(data)


          
class GetConsumerAuditList(Resource):
    def get(self):
        response = []
        try:
            audit_data_list = AuditData.objects()
            for audit_data in audit_data_list:
                image = base64.b64encode(audit_data.image.read()).decode('utf-8')
                content_type1 = audit_data.image.content_type
                signature = base64.b64encode(audit_data.signature.read()).decode('utf-8')
                content_type2 = audit_data.signature.content_type
                result = json.loads(json_util.dumps(audit_data.to_mongo(), cls=ObjectIdEncoder))
                result['signature'] = signature
                result['signature_content_type'] = content_type2
                result['image'] = image
                result['image_content_type'] = content_type1
                response.append(result)
            return jsonify(response)
        except Exception as e:
            print("Exception:", e)
            return jsonify({"message": "Error: {}".format(str(e))})