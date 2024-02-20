from mongoengine import Document, EmailField, StringField, IntField, \
    DateTimeField, ReferenceField, EmbeddedDocument, \
    EmbeddedDocumentField, FileField, DictField

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
    signature_date = StringField()
    audited_staff_signature = StringField()
    description = StringField()    
