from flask_restful import Api
from ceq_user.user.auth import CEQLoginApi
from ceq_user.user.view import CEQAddUserAPI, CEQAddNewUserAPI, CEQUpdateUserAPI, \
    CEQViewAllUserAPI, CEQDeleteUserAPI, CEQUpdateUserStatusAPI
from consumer.view import Test, CreateConsumerAudit, GetConsumerAudit, GetConsumerAuditList,\
    DeleteConsumerAudit, UpdateConsumerAudit, AddErrorCategory, GetAllCategories


def initialize_routes(app):
    api = Api(app)

    # user management path
    api.add_resource(CEQLoginApi, '/ceq/user/login')
    api.add_resource(CEQViewAllUserAPI, '/ceq/user/view/all')
    api.add_resource(CEQAddUserAPI, '/ceq/user/add')
    api.add_resource(CEQAddNewUserAPI, '/ceq/new/user/add')
    api.add_resource(CEQUpdateUserAPI, '/ceq/user/update')
    api.add_resource(CEQUpdateUserStatusAPI, '/ceq/user/update/status')
    api.add_resource(CEQDeleteUserAPI, '/ceq/user/delete') 

    # consumer module path
    api.add_resource(Test, '/ceq/consumer/test')
    api.add_resource(CreateConsumerAudit, '/ceq/consumer/create_audit')
    api.add_resource(GetConsumerAudit, '/ceq/consumer/get_audit/')
    api.add_resource(GetConsumerAuditList, '/ceq/consumer/get_audit_list/')
    api.add_resource(DeleteConsumerAudit, '/ceq/consumer/delete_audit/')
    api.add_resource(UpdateConsumerAudit, '/ceq/consumer/update_audit/')
    api.add_resource(AddErrorCategory, '/ceq/add/category/')
    api.add_resource(GetAllCategories, '/ceg/get/category')
