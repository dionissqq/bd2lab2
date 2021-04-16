class UsersController():
    r = None
    
    def __init__(self, redis_connection):
        UsersController.r = redis_connection
    
    def create_user(login):
        return UsersController.r.sadd('app_users', login)
    
    def check_user(login):
        return UsersController.r.sismember('app_users', login)
    
    def add_to_admins(login):
        return UsersController.r.sadd('admins', login)

    def check_admin(login):
        return UsersController.r.sismember('admins', login)
    
    def add_online(login):
        return UsersController.r.sadd('online', login)

    def remove_online(login):
        return UsersController.r.srem('online', login)

    def get_all_online():
        return UsersController.r.smembers('online')
    
    def user_logs_in(login):
        UsersController.r.publish('log', login+' logged in ')
    
    def user_logs_out(login):
        UsersController.r.publish('log', login+' logged out ')