from flask_restful import Api
from ceq_user.user.auth import CEQLoginApi
from ceq_user.user.view import CEQAddUserAPI, CEQAddNewUserAPI, CEQUpdateUserAPI, CEQViewAllUserAPI, CEQDeleteUserAPI, CEQUpdateUserStatusAPI


def initialize_routes(app):
    api = Api(app)

    #user management path
    api.add_resource(CEQLoginApi, '/ceq/user/login')
    api.add_resource(CEQViewAllUserAPI, '/ceq/user/view/all')
    api.add_resource(CEQAddUserAPI, '/ceq/user/add')
    api.add_resource(CEQAddNewUserAPI, '/ceq/new/user/add')
    api.add_resource(CEQUpdateUserAPI, '/ceq/user/update')
    api.add_resource(CEQUpdateUserStatusAPI, '/ceq/user/update/status')
    api.add_resource(CEQDeleteUserAPI, '/ceq/user/delete')


