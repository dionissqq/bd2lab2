import redis
import sched, time
import random
from statuses import statuses

random.seed(2)

r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

s = sched.scheduler(time.time, time.sleep)
def do_something(sc): 
    print("checking spam")
    m_id = r.rpop('message_queue')
    if m_id:
        rand = random.randint(0,1)
        r.srem(statuses['in queue'], m_id)
        r.sadd(statuses['checking for spam'], m_id)
        if rand:
            [from_login, to_login, text] = r.hmget('message_'+ str(m_id), ['from', 'to', 'text']) 
            [max_login, min_login] = [from_login, to_login] if from_login>to_login else  [to_login, from_login] 
            channel_name = max_login+'_'+min_login+'_channel'
            sub_channel = channel_name+'_subscription'
            r.sadd(channel_name, m_id)
            r.publish(sub_channel, text)
            r.srem(statuses['checking for spam'], m_id)
            r.sadd(statuses['sent'], m_id)
            # send and add status
        else:
            r.srem(statuses['checking for spam'], m_id)
            from_login = r.hget('message_'+ str(m_id), 'from') 
            r.publish('log', 'spam from '+from_login)
            r.zadd('messages_spammed', {from_login:1}, incr = True)
            r.sadd(statuses['spam'], m_id)
    # do your stuff
    s.enter(2, 1, do_something, (sc,))

s.enter(0, 1, do_something, (s,))
s.run()
