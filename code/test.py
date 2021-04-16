import redis
from controllers.users_controller import UsersController
from controllers.message_controllers import MessageController
import random

random.seed(20)

r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

UsersController(r)
MessageController(r)

users = []

for i in range(20):
    username = 'test_user_'+str(i)
    UsersController.create_user(username)
    users.append(username)

for iters in range(1000):
    user1 = users[random.randint(0, 19)]
    user2 = users[random.randint(0, 19)]
    MessageController.push_messages(user1, user2, 'text')

