from ceq_user.database.models import User, BusinessAudit 
from ceq_user.resources.errors import unauthorized
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist
from bson import ObjectId
import json
import pandas as pd


class CreateBusinessAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role != "supervisor" and (user.permission not in ["business", "all"]):
            return {"message": "'error': 'Unauthorized access'"}, 401        
        try:
            excel_data = request.files['upload_excel']
            if not excel_data:
                return {'message': 'No file provided'}, 400
            try:
                df = pd.read_excel(excel_data)
            except Exception as e:
                return {'message': f'Error reading excel: {str(e)}'}, 400
            records = df.to_dict(orient='records')
            for record in records:
                # Filter out NaN values from record
                record = {k: v for k, v in record.items() if not pd.isna(v)}
                business_audit = BusinessAudit(
                    sn=record.get("SN"),
                    date_of_visit=record.get("Date of Visit "),
                    sr_dkt_no=record.get("SR DKT NO"),
                    region=record.get("REGION"),
                    sub_region=record.get('SUB REGION'),
                    product_group=record.get("PRODUCT GROUP"),
                    sr_type=record.get("SR TYPE"),
                    product_type=record.get("PRODUCT TYPE"),
                    contact_number=str(record.get("CONTACT NUMBER")),
                    ont_type=str(record.get("ONT TYPE")),
                    ont_sn=str(record.get("ONT SN")),
                    olt_code=str(record.get("OLT CODE")),
                    exch_code=record.get("EXCH-CODE"),
                    eid=record.get("EID"),
                    fdh_no=str(record.get("FDH NO")),
                    account_no=str(record.get("ACCOUNT NO")),
                    customer_name=record.get("CUSTOMER NAME"),
                    account_category=record.get("A/C_CATEGORY"),
                    sr_group=record.get("SRGroup"),
                    cbcm_close_date=record.get("CBCM_CLOSE_DATE"),
                    latitude=record.get("LATITUDE"),
                    longitude=record.get("LONGITUDE"),
                    wfm_emp_id=record.get("WFM_EMP_ID"),
                    tech_name=record.get("Tech_Name"),
                    party_id=record.get("PARTY_ID"),
                    wfm_task_id=record.get("WFM_TASK_ID"),
                    wfm_wo_number=record.get("WFM_WO_NUMBER"),
                    team_desc=record.get("TEAM_DESC"),
                    ceq_auditor_name=record.get("CEQ (Auditor Name)"),
                    observations_in_fhd_side=str(record.get("Obervations in FDH Side")),
                    violation_remarks=record.get("Violation Remarks"),
                    violation=record.get("Violation (Yes / No / NA)"),
                    image=[],
                    ceqv01_sub_cable_inst=record.get("CEQV01 Substandard Cable handling and installation"),
                    ceqvo2_sub_inst_ont=record.get("CEQV02 Substandard Installation of ONT"),
                    ceqv03_sub_inst_wastes_left_uncleaned=record.get("CEQV03 Installation Wastes Left Uncleaned"),
                    ceqv04_existing_sub_inst_not_rectified=record.get("CEQV04 Existing Substandard Installation Not Rectified "),
                    ceqv05_sub_inst_cpe=record.get("CEQV05 Substandard Installation of CPE "),
                    ceqv06_sub_labelling=record.get("CEQV06 Substandard Labelling"),
                    sub_cable_inst=record.get("Substandard Cable handling and installation"),
                    sub_inst_ont=record.get("CEQV02 Substandard Installation of ONT.1"),
                    sub_inst_wastes_left_uncleaned=record.get(" Installation Wastes Left Uncleaned"),
                    existing_sub_inst_not_rectified=record.get("Existing Substandard Installation Yest Rectified Yesr Escalated to Supervisor"),
                    sub_inst_cpe=record.get("Substandard Installation of CPE "),
                    sub_labelling=record.get("Substandard Labelling"),
                    compliance=record.get("COMPLIANCE")
                )                             
                business_audit.save() 
            print(record)                  
            return {'message': 'excel data successfully processed'}, 201
        except Exception as e:  
            print(record)         
            return jsonify({"message": "Error: {}".format(str(e))})
        
class GetBusinessAudit(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if (user.role not in ["supervisor", "audit", "admin"]) and (user.permission not in ["business", "all"]):
            return {"message": "'error': 'Unauthorized access'"}, 401 
        try:            
            audit_id = ObjectId(request.args.get('audit_id'))
            audit_data = BusinessAudit.objects(id=audit_id).first()
            if audit_data is None:
                return {"message": "Audit Id Not Found"}, 404
            if audit_data:
                audit_json = json.loads(audit_data.to_json())
            return jsonify(audit_json)   
        except Exception as e:
            print("Exception: ", e)
            return {'message': 'Error occurred while retrieving audit'}, 500       


class GetBusinessAuditList(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role not in ["audit", "supervisor", "admin"] and (user.permission not in ["business", "all"]):
            return {"message": "'error': 'Unauthorized access'"}, 401 
        try:            
            audit_data = BusinessAudit.objects()
            if audit_data is None:
                return {"message": "Audit's Not Found"}, 404
            respose = []
            if audit_data:
                audit_json = json.loads(audit_data.to_json())
                for records in audit_json:
                    respose.append(records)
            return jsonify(respose)   
        except Exception as e:
            print("Exception: ", e)
            return {'message': 'Error occurred while retrieving audit'}, 500      
       
class UpdateBusinessAudit(Resource):
    @jwt_required()
    def post(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role not in ["audit", "supervisor", "admin"] and (user.permission not in ["business", "all"]):
            return {"message": "'error': 'Unauthorized access'"}, 401 
        try:
            # Retrieve audit ID from request args
            audit_id = request.args.get('audit_id')
            if audit_id is None:
                return {'message': 'Audit ID not provided'}, 400

            # Retrieve audit data by audit_id
            audit_document = BusinessAudit.objects(id=audit_id).first()
            if audit_document is None:
                return {'message': 'Audit ID Not Found'}, 404

            # Convert the incoming JSON data to a dictionary
            data = request.json
            
            # Update the fields of the existing audit_document with the new data
            for key, value in data.items():
                setattr(audit_document, key, value)

            # Save the updated audit document
            audit_document.save()
            
            return {'message': 'Audit record updated successfully'}, 200
        except Exception as e:
            return {"message": "Error: {}".format(str(e))}, 500

        
class DeleteBusinessAudit(Resource):
    @jwt_required()
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()
        if user.role != "audit" and (user.permission not in ["business", "all"]):
            return {"message": "'error': 'Unauthorized access'"}, 401       
        try:
            id_audit = ObjectId(request.args.get('audit_id'))
            # Retrieve audit data by audit_id
            audit_document = BusinessAudit.objects(id=id_audit).first()
            if audit_document is None:
                return {'message': 'Audit ID Not Found'}, 404
            if audit_document:       
                audit_document.delete()
                return {"message": "Audit with ID deleted successfully"}, 200
            else:
                return {"message": "Audit with ID not found"}, 404
        except Exception as e:
            print("Exception: ", e)
            return {"message": "Error: {}".format(str(e))}, 500
