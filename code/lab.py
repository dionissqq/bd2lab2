import redis
from controllers.users_controller import UsersController
from controllers.message_controllers import MessageController
import os
import atexit
import sys
import time
clear = lambda: os.system('clear')
clear()

r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)
UsersController(r)
MessageController(r)

UsersController.create_user('denis')
UsersController.add_to_admins('denis')

login = None

try:
    print('hello user, type your name')
    login = input()
    UsersController.user_logs_in(login)
    UsersController.add_online(login)
    if UsersController.check_admin(login):
        print('HI ADMIN')
        print('1)show log')
        print('2)show statistics')
        choice = input()
        if choice == '1':
            clear()
            print('log:')
            p = r.pubsub()
            p.subscribe('log')
            for message in p.listen():
                if message['type']=='message':
                    print(message['data'])
        elif choice == '2':
            clear()
            print('stats:')
            print('online users:', UsersController.get_all_online())            
            MessageController.print_admin_stats()
            input()
    else:
        if UsersController.check_user(login):
            print('welcome back')
        else:
            UsersController.create_user(login)
            print('hello stranger')
            print('you were automatically registered')
        print('select chat or checkout your messages')
        print('1) show chat')
        print('2) new message')
        print('3) show my messages')
        choice = input()
        if choice == '1' or choice == '2':
            clear()
            print('enter your friend login')
            friend_login = input()
            while not UsersController.check_user(friend_login):
                print('such user does not exist')
                print('enter your friend login')
                friend_login = input()
            if choice == '1':
                print('chat')
                p = r.pubsub()
                printed = False
                messages, sub_srtring = MessageController.get_messages(login, friend_login)
                p.subscribe(sub_srtring)
                for m in messages:
                    print(m)
                printed = True
                for message in p.listen():
                    if message['type']=='message':
                        print(message['data'])
            else:
                print('enter your messages')
                while True:
                    new_message = input()
                    MessageController.push_messages(login, friend_login, new_message)
        elif choice == '3':
            clear()
            print('here are your stats')
            d = MessageController.get_messages_stats(login)
            for k in d.keys():
                print(k+':')
                print(d[k])
            input()

except KeyboardInterrupt:
    print('closing session')
    if login:
        UsersController.user_logs_out(login)
        UsersController.remove_online(login)
    sys.exit()

        
