from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 因为登录用的是jwt所以socpe里无法获取到user数据，只有用session认证的用户才可以默认被scope获取，所以得自己写获取用户的逻辑
        if self.scope['user'].is_anonymous:
            # 未登录用户拒绝连接
            await self.close()
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # 把房间用户写入缓存
        room_data = cache.get(self.room_group_name)
        if room_data :
            avatar =  '/media/' + str(self.scope['user'].avatar)
            room_data[self.scope['user'].username] = {'username': self.scope['user'].username, 'avatar': avatar}
            cache.set(self.room_group_name, room_data, None)
        else:
            room_data = {}
            avatar =  '/media/' + str(self.scope['user'].avatar)
            room_data[self.scope['user'].username] = {'username': self.scope['user'].username, 'avatar': avatar}
            cache.set(self.room_group_name, room_data, None)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 断开连接的同时，要把这个用户踢出缓存，并且通知出去
        username = self.scope['user'].username
        data = cache.get(self.room_group_name)
        data.pop(username)
        cache.set(self.room_group_name, data, None)

        message = {'code': '200', 'message': data}
        await self.channel_layer.group_send(
            self.room_group_name,  # 发送的通道，用房间号就会传到房间里，用channel_name这个个人通道号只会传给个人
            {
                'type': 'chat_message',
                'message': message  # message 传入到chat_message的event['message']
            }
        )
        # 这发的信息不是给断开连接的人看的，而是给其他人房间里面的
        await self.send(text_data=json.dumps({
            'message': message
        }))


        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        # message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,  # 发送的通道，用房间号就会传到房间里，用channel_name这个个人通道号只会传给个人
            {
                'type': 'chat_message',
                'message': message  # message 传入到chat_message的event['message']
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # 这里可以对收到的信息进行各种操作修改返回
        code = str(event['message']['code'])
        # 我规定code返回是200就从缓存取房间用户信息内容返回，不是就直接返回用户发的内容到前端
        if code == '200':
            username = self.scope['user'].username
            print('200')
            print(username)
            data = cache.get(self.room_group_name)
            message = { 'code': '200', 'message': data}
            await self.send(text_data=json.dumps({
                'message': message
            }))
        elif code == '666':
            username = self.scope['user'].username
            print('666')
            print(username)
            print(event['message']['message'])
            message = {'code': '666', 'message': event['message']['message']}
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message
            }))
        else:
            message = {'code': '500', 'message': '提交了错误的信息'}
            await self.send(text_data=json.dumps({
                'message': message
            }))