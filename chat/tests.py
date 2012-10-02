import uuid
import time

from django.test import SimpleTestCase
import redis

from chat.models import ChatMessage, ChatRoom


class ModelTest(SimpleTestCase):

    conn = None

    def setUp(self):
        ModelTest.conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    def tearDown(self):
        ModelTest.conn.flushdb()
        ModelTest.conn.connection_pool.disconnect()

    def test_chat_message_basic(self):
        """Tests creation, getters and setter of ChatMessage model"""
        cm = ChatMessage(uuid.uuid4(), "default")
        cm.msg = "Python rulz!"
        cm.user = "slok"
        cm.time = time.time()

        self.assertEqual(cm.msg, "Python rulz!")
        self.assertEqual(cm.user, "slok")

    def test_chat_message_save(self):
        """Tests the save of the instance in redis"""
        for i in range(100):
            cm = ChatMessage(uuid.uuid4(), "default")
            cm.msg = "Python rulz!%d" % i
            cm.user = "slok%d" % i
            cm.time = time.time()
            cm.save()

    def test_chat_message_delete(self):
        """Tests the delete of the instance in redis"""

        with self.assertRaises(NotImplementedError):
            cm = ChatMessage(uuid.uuid4(), "default")
            cm.delete()

    def test_chat_message_find(self):
        """Tests the find of the instance in redis"""

        uuid_id = uuid.uuid4()
        cm = ChatMessage(uuid_id, "default")
        cm.msg = "Python rulz!"
        cm.user = "slok"
        cm.time = time.time()
        cm.save()

        cm_find = ChatMessage.find(uuid_id)

        self.assertEqual(cm_find.msg, cm.msg)
        self.assertEqual(cm_find.user, cm.user)
        self.assertEqual(cm_find.room, cm.room)

    def test_chat_messages(self):
        """Tests the find of the instance in redis"""

        for i in range(30):
            uuid_id = uuid.uuid4()
            cm = ChatMessage(uuid_id, "room1")
            cm.msg = "Python rulz!%d" % i
            cm.user = "slok%d" % i
            cm.time = time.time()
            cm.save()

        cr = ChatRoom("room1")
        messages = cr.messages(10)
        self.assertEqual(len(messages), 10)

        name_number = 20
        for i in messages:
            self.assertEqual(i.user, "slok%d" % name_number)
            name_number += 1

    def test_chat_join(self):
        ChatRoom.join("room1", "slok")
        self.assertTrue(ChatRoom.connected("room1", "slok"))

    def test_chat_disconnect(self):
        ChatRoom.join("room1", "slok")
        self.assertTrue(ChatRoom.connected("room1", "slok"))
        ChatRoom.disconnect("room1", "slok")
        self.assertFalse(ChatRoom.connected("room1", "slok"))
