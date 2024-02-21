from mongoengine import Document, EmailField, StringField, IntField, \
    DateTimeField, ReferenceField, EmbeddedDocument, \
    EmbeddedDocumentField, DictField, ListField

"""
ALL our models are declared here

"""

class User(Document):
 
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    ROLE_CHOICES = (
        ('supervisor', 'SuperVisor'),
        ('auditor', 'Auditor'),
        ('admin', 'Admin'),
    )
    PERMISSION_CHOICE = (
        ('business', 'Business'),
        ('consumer', 'consumer'),
        ('all', 'All')
    )
    status = StringField(choices=STATUS_CHOICES)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    phone_number = StringField(required=False, min_length=9)
    role = StringField(choices=ROLE_CHOICES)
    name = StringField()
    permission = StringField(choices=PERMISSION_CHOICE, required=False)
    supervisor = ReferenceField('User')
    login_count = IntField(default=0)
    last_login = DateTimeField()
 
    def check_user_status(username):
        user = User.objects(username=username, status='active').first()
        if user is not None:
            return True
        else:
            return False

class Form2(EmbeddedDocument):
    YES = 'yes'
    NO = 'no'
    MAJOR = 'major'
    MINOR = 'minor'
    
    VIOLATION_CHOICES = [
        (YES, 'Yes'),
        (NO, 'No')
    ]
    
    SEVERITY_CHOICES = [
        (MAJOR, 'Major'),
        (MINOR, 'Minor')
    ]
    
    violation = StringField(choices=VIOLATION_CHOICES)
    remarks = StringField()
    image = StringField()
    severity = StringField(choices=SEVERITY_CHOICES)
    # Define a method to get severity choices based on the violation
    def get_severity_choices(self):
        if self.violation == self.YES:
            return self.SEVERITY_CHOICES
        else:
            return []


class Form1(EmbeddedDocument):
    supervisor_contact = StringField()
    tech_pt = StringField()
    vehicle_number = StringField()
    tech_skills = StringField()
    sr_manager = StringField()
    tech_fullname = StringField()
    region = StringField()
    vendor = StringField()
    director = StringField()
    auditor_id = IntField()
    sr_number = StringField()
    tech_ein = StringField()
    team = StringField()
    duty_manager = StringField()
    supervisor = StringField()
    shortdescription = StringField()
    tech_contact = StringField()
    controller = StringField()
    group_head = StringField()
    user_action = StringField()


class AuditData(Document):
    form1 = EmbeddedDocumentField(Form1)
    status = StringField()
    lastmodified = DateTimeField()
    supervisor_id = IntField()
    expiryDate = DateTimeField()
    auditDate = DateTimeField()
    remarks = StringField()
    department = StringField()
    createdDate = DateTimeField()
    ceqvs = DictField(EmbeddedDocumentField(Form2))
    audit_signature = StringField()
    signature_date = DateTimeField()
    audited_staff_signature = StringField()
    description = StringField()    


class BusinessAudit(Document):
    YES = 'yes'
    NO = 'no'    
    VIOLATION_CHOICES = [
        (YES, 'Yes'),
        (NO, 'No')
    ]
    sn = IntField(default=0)
    date_of_visit = DateTimeField(default=None)
    sr_dkt_no = IntField(default=0)
    region = StringField(default="")
    sub_region = StringField(default="")
    product_group = StringField(default="")
    sr_type = StringField(default="")
    product_type = StringField(default="")
    contact_number = StringField(default="")
    ont_type = StringField(default="")
    ont_sn = StringField(default="")
    olt_code = StringField(default="")
    exch_code = StringField(default="")
    eid = StringField(default="")
    fdh_no = StringField(default="")
    account_no = StringField(default="")
    customer_name = StringField(default="")
    account_category = StringField(default="")
    sr_group = StringField(default="")
    cbcm_close_date = DateTimeField(default=None)
    latitude = StringField(default="")
    longitude = StringField(default="")
    wfm_emp_id = IntField(default=0)
    tech_name = StringField(default="")
    party_id = IntField(default=0)
    wfm_task_id = IntField(default=0)
    wfm_wo_number = IntField(default=0)
    team_desc = StringField(default="")
    ceq_auditor_name = StringField(default="")
    observations_in_fhd_side = StringField(default="")
    violation_remarks = StringField(default="")
    violation = StringField(default="")
    photos = ListField(default=[])
    CEQV01 = StringField(choices=VIOLATION_CHOICES)
    CEQV02 = StringField(choices=VIOLATION_CHOICES)
    CEQV03 = StringField(choices=VIOLATION_CHOICES)
    CEQV04 = StringField(choices=VIOLATION_CHOICES)
    CEQV05 = StringField(choices=VIOLATION_CHOICES)
    CEQV06 = StringField(choices=VIOLATION_CHOICES)
    total = IntField(default=0)
    compliance = StringField(default="")