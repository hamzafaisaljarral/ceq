from mongoengine import Document, EmailField, StringField, IntField, \
    DateTimeField, ReferenceField, EmbeddedDocument, \
    EmbeddedDocumentField, FileField

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
    violation = IntField()
    remarks = StringField()


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
    sr_number = StringField()
    tech_ein = StringField()
    team = StringField()
    duty_manager = StringField()
    supervisor = StringField()
    shortdescription = StringField()
    tech_contact = StringField()


class AuditData(Document):
    username = StringField()
    status = StringField()
    name = StringField()
    audit_id = IntField()
    lastmodified = DateTimeField()
    supervisor_id = IntField()
    expiryDate = DateTimeField()
    auditDate = DateTimeField()
    remarks = StringField()
    form1 = EmbeddedDocumentField(Form1)
    department = StringField()
    createdDate = DateTimeField()
    auditor_id = IntField()
    ceqv01 = EmbeddedDocumentField(Form2)
    ceqv02 = EmbeddedDocumentField(Form2)
    ceqv03 = EmbeddedDocumentField(Form2)
    ceqv04 = EmbeddedDocumentField(Form2)
    ceqv05 = EmbeddedDocumentField(Form2)
    ceqv06 = EmbeddedDocumentField(Form2)
    ceqv01_image = FileField()
    ceqv02_image = FileField()
    ceqv03_image = FileField()
    ceqv04_image = FileField()
    ceqv05_image = FileField()
    ceqv06_image = FileField()
    audit_signature = FileField()
    audited_staff_signature = FileField()
    description = StringField()
