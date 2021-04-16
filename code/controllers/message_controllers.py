from statuses import statuses


class MessageController():
    r = None
    
    def __init__(self, redis_connection):
        MessageController.r = redis_connection

    def push_messages(from_login, to_login, message):
        new_mesage_id = MessageController.r.get('last+message_id')
        if new_mesage_id == None:
            new_mesage_id = 0
        else:
            new_mesage_id = int(new_mesage_id)+1
        MessageController.r.set('last+message_id', new_mesage_id)
        MessageController.r.hmset('message_'+str(new_mesage_id), {
            'from':from_login,
            'to':to_login,
            'text':message
        })
        MessageController.r.sadd(statuses['created'], new_mesage_id)
        MessageController.r.sadd(from_login+'_messages', new_mesage_id)
        MessageController.r.zadd('messages_sent', {from_login:1}, incr = True)
        # push to queue
        MessageController.r.lpush('message_queue', new_mesage_id)
        MessageController.r.srem(statuses['created'], new_mesage_id)
        MessageController.r.sadd(statuses['in queue'], new_mesage_id)

    def get_messages(from_login, to_login):
        [max_login, min_login] = [from_login, to_login] if from_login>to_login else [to_login, from_login] 
        channel_name = max_login+'_'+min_login+'_channel'
        sub_channel = channel_name+'_subscription'
        channel_messages = MessageController.r.smembers(channel_name) 
        messages_list = [*channel_messages]
        for m_id in messages_list:
            MessageController.r.srem(statuses['sent'], m_id)
            MessageController.r.sadd(statuses['delivered'], m_id)
        messages = [MessageController.r.hmget('message_'+ m_id, ['from', 'text']) for m_id in messages_list]
        text_messages = [text if message_from==from_login else to_login+' : '+text for [message_from, text] in messages]
        
        return text_messages, sub_channel

    def get_messages_stats(login):
        d = {}
        for value in statuses.values():
            d[value] = MessageController.r.sinter([login+'_messages', value])
        return d

    def print_admin_stats():
        print('most active users')
        print('enter n:')
        n=int(input())
        m_s = MessageController.r.zrange('messages_sent', 0, n-1, desc=True, withscores=True)
        print(m_s)
        print('biggest spammers')
        m_s = MessageController.r.zrange('messages_spammed', 0, n-1, desc=True, withscores=True)
        print(m_s)