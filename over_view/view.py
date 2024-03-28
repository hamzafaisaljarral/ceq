# -*- coding: utf-8 -*-
from ceq_user.database.models import User, AuditData
from ceq_user.resources.errors import unauthorized
from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist
from bson import ObjectId
import json
from datetime import datetime, timedelta
import os
import uuid
import paramiko
import pdb






class ComplianceSummary(Resource):
    @jwt_required()    
    def get(self):
        try:
            user = User.objects.get(id=get_jwt_identity()['id'])
        except DoesNotExist:
            return unauthorized()    
        if user.role == "supervisor" and user.permission not in ["consumer", "all"]:
            return {"message": "Unauthorized access"}, 401
        try:
            current_date = datetime.now().date()
            last_date = current_date - timedelta(days=7)
            start_date = datetime(last_date.year, last_date.month, last_date.day)
            end_date = datetime(current_date.year, current_date.month, current_date.day)
            print(start_date)
            print(end_date)
            # Query the AuditData objects between the start and end dates
            all_audit_data = AuditData.objects(createdDate__gte=start_date, createdDate__lte=end_date)
            if all_audit_data:
                # Initialize an empty list to store serialized audit data
                report_list = []
                # Iterate through each audit and serialize it to JSON
                for audit_data in all_audit_data:
                    dict_data = {}           
                    if "ceqvs" in audit_data:                       
                        for ceqv in audit_data["ceqvs"]:
                            if "severity" in ceqv and ceqv["severity"] == "major":
                                # Initialize dict_data for each ceqv with major severity
                                if "remarks" in ceqv:
                                    dict_data["region"] = audit_data["region"]
                                    dict_data["remarks"] = ceqv["remarks"]
                                    dict_data["create_date"] = audit_data["createdDate"]
                                    dict_data["image"] = "https://ossdev.etisalat.ae:8400/public/uploads/ceq/4c8faa6b-6e32-4ad0-85a9-1ec90dd0d19a_image2.jpg"
                                else:
                                    dict_data["remarks"] = ""
                                if "image" in ceqv:
                                    dict_data["image"] = ceqv["image"]
                                report_list.append(dict_data)  # Append dict_data only for ceqvs with major severity
                return jsonify(report_list)              
            else:
                return {'message': 'No audits found'}, 404
        except Exception as e:
            print("Exception: ", e)
            return {'message': 'Error occurred while retrieving audits'}, 500  
