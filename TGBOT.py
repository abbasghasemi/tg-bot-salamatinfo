class TelegramBot:

    json = {}

    bot_token = ""

    # SalamatInfo.com
    targetChat = -1001418071951
    senderChatVerified = False

    channelPost = False
    #                @Masiresabzzzz  @tebiraann    @My8Behesht
    targetChannels = {-1001293868346,-1001222117814,-1001006831974}
    # { "id": ID, "title":"TITLE", "username":"USERNAME", "type":"channel" }
    forwardFromChat = None
    forwardFromMessageId = None
    forwardDate = None
    forwardFromChatVerified = False

    file_id = None
    caption = False
    text = None
    entities = None

    def __init__(self, json):
        if type(json) is dict:
            self.json = json
            self.startInit()
        else:
            raise ValueError("Json is invalid.")
    
    def startInit(self):
        self.channelPost = self.json.__contains__('channel_post')
        if self.channelPost:
            channel_post = self.json['channel_post']
            self.senderChatVerified = channel_post['chat']['id'] == self.targetChat
            if channel_post.__contains__('forward_from_chat'):
                self.forwardFromMessageId = channel_post['forward_from_message_id']
                self.forwardDate = channel_post['forward_date']
                self.forwardFromChat = channel_post['forward_from_chat']
                self.forwardFromChatVerified = self.targetChannels.__contains__(self.forwardFromChat['id'])
            self.caption = channel_post.__contains__('caption')
            self.entities = None
            if self.caption:
                if channel_post.__contains__('photo'):
                    photo = channel_post['photo']
                    photo = photo[len(photo)-1]
                    self.file_id = photo['file_id']
                self.text = channel_post['caption']
                if channel_post.__contains__('caption_entities'):
                    self.entities = channel_post['caption_entities']
            else:
                self.text = channel_post['text']
                if channel_post.__contains__('entities'):
                    self.entities = channel_post['entities']

    def isChannelPost(self):
        return self.channelPost

    def isCaption(self):
        return self.caption

    def isMessageVerified(self):
        return self.senderChatVerified and self.forwardFromChatVerified

    # 0 return title
    # 1 return channel
    # 2 return post address
    # 3 return title & post address
    def getReference(self, type = 3):
        if self.isMessageVerified():
            if type == 0:
                return self.forwardFromChat['title']
            elif type == 1:
                return "https://t.me/" + self.forwardFromChat['username']
            elif type == 2:
                return "https://t.me/" + self.forwardFromChat['username'] + "/" + str(self.forwardFromMessageId)
            return self.forwardFromChat['title'] + " - https://t.me/" + self.forwardFromChat['username'] + "/" + str(self.forwardFromMessageId)
        return ''
    
    def getChannelID(self):
        if self.isMessageVerified():
            return self.forwardFromChat['id']
        return -1

    def getDate(self):
        return self.forwardDate

    def getMessage(self):
        if self.text == None:
            return ''
        return self.text
    
    def getContentFile(self):
        if self.file_id == None:
            return False
        from SIAPI import API
        file = API()
        file.addHeader('Authorization', '')
        file.setUrl("https://api.telegram.org/bot"+self.bot_token+"/getFile?file_id="+ self.file_id)
        file.request()
        if type(file.content) is dict and file.content['ok'] == True:
            result = {'size':file.content['result']['file_size']}
            file.setUrl("https://api.telegram.org/file/bot"+self.bot_token+"/"+file.content['result']['file_path'])
            file.request()
            result['content'] = file.content
            return result
        return False
            
    def getEntities(self):
        if self.entities == None:
            return []
        return self.entities