from mongoengine import Document, EmailField, StringField, IntField, \
    DateTimeField, ReferenceField

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
    DEPARTMENT_CHOICE = (
        ('business', 'Business'),
        ('consumer', 'consumer'),
    )
    status = StringField(choices=STATUS_CHOICES)

    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    phone_number = StringField(required=False, min_length=9)
    role = StringField(choices=ROLE_CHOICES)
    department = StringField(choices=DEPARTMENT_CHOICE)
    supervisor = ReferenceField('User')
    login_count = IntField(default=0)
    last_login = DateTimeField()

    def check_user_status(username):
        user = User.objects(username=username, status='active').first()
        if user is not None:
            return True
        else:
            return False

