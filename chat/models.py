import redis

#TODO: Change conection mode!!!


class ChatMessage(object):
    """Class container for the messages"""

    _redis_prefix = "chat:message:%s"
    _conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    def __init__(self, msg_id, room_name=None):

        self._room = room_name
        self._msg_id = msg_id

        self._time = None
        self._user = None
        self._msg = None

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value

    @property
    def room(self):
        return self._room

    @room.setter
    def room(self, value):
        self._room = value

    @property
    def msg_id(self):
        return self._msg_id

    @msg_id.setter
    def msg_id(self, value):
        self._msg_id = value

    def save(self):
        # Atomic!
        pipe = ChatMessage._conn.pipeline()

        #Add the message metadata
        data = {"room": self._room,
                "time": self._time,
                "user": self._user,
                "msg": self._msg}

        pipe.hmset(ChatMessage._redis_prefix % self._msg_id, data)

        #Add the message to the list (room)
        redis_room_id = ChatRoom._redis_messages_prefix % self._room
        pipe.rpush(redis_room_id, self._msg_id)
        pipe.execute()

    def delete(self):
        raise NotImplementedError("We don't delete any message *.*")

    @staticmethod
    def find(msg_id):
        redis_res = ChatMessage._conn.hgetall(
                                        ChatMessage._redis_prefix % msg_id)
        cm = ChatMessage(msg_id, redis_res["room"])
        cm.msg = redis_res["msg"]
        cm.time = redis_res["time"]
        cm.user = redis_res["user"]
        return cm


class ChatRoom(object):
    """Class that represents the chat room"""

    _redis_users_prefix = "chat:room:%s:users"
    _redis_messages_prefix = "chat:room:%s:messages"
    _conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    def __init__(self, name):
        self._room_id = name

    def messages(self, limit=0):
        key = ChatRoom._redis_messages_prefix % self._room_id
        total = self._conn.llen(key)

        #If there is no limit then the start point is the first one
        start_point = 0
        if limit != 0:
            start_point = total - limit

        messages = ChatRoom._conn.lrange(key, start_point, total)
        message_list = []

        for msg in messages:
            cm = ChatMessage.find(msg)
            message_list.append(cm)

        return message_list

    def users(self):
        key = ChatRoom._redis_users_prefix % self._room_id
        return ChatRoom._conn.smembers(key)

    @staticmethod
    def join(room_id, user):
        key = ChatRoom._redis_users_prefix % room_id
        ChatRoom._conn.sadd(key, user)

    @staticmethod
    def connected(room_id, user):
        key = ChatRoom._redis_users_prefix % room_id
        return ChatRoom._conn.sismember(key, user)

    @staticmethod
    def disconnect(room_id, user):
        key = ChatRoom._redis_users_prefix % room_id
        ChatRoom._conn.srem(key, user)
