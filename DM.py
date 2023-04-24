from TGBOT import TelegramBot
from datetime import datetime
from collections import Counter
from FLOG import LOG_INFO
import re, string

class DataMining:

    tg:TelegramBot = None

    extraLetters = [
        'با', 'اگرچه', 'اگر', 'بلکه', 'که', 'یا', 'پس', 'ولی', 'تا', 'نه', 'چون', 'چه', 'را', 'اما', 'باری', 'کنه', 'خوردن',
        'خواه', 'زیرا', 'لیکن', 'نیز', 'هم', 'بالعکس', 'ولو', 'جز', 'به', 'سپس', 'این', 'همچنین', 'چندان', 'گذشته', 'همان',
        'چنانچه', 'آن', 'آنگاه', 'جا', 'رو', 'اینرو', 'بس', 'بهر', 'اکنون', 'مگر', 'حال', 'وجود', 'شرط', 'همین', 'لحظه',
        'در', 'لیک', 'ولکن', 'ولیکن', 'لکن', 'ساز', 'پیرو', 'نتیجه', 'هرگاه', 'علت', 'جهت', 'زائد', 'از', 'خود', 'هستند',
        'می', 'کنه', 'بعد', 'بعد', 'بشه', 'تونه', 'شما', 'اون', 'کنید', 'کمتر', 'بگیرید', 'نام', 'میخونن', 'نسبت', 'خودتان',
        'افراد', 'نسبت', 'ایجاد', 'نباید', 'میده', 'بهت', 'اگه', 'کنی', 'بیا', 'های', 'کمی', 'است', 'برای', 'میکنی',  'آنها',
        'کنم', 'ها', 'من', 'یاد', 'کردن', 'کنن', 'باشی', 'میکند', 'باشد', 'شود', 'میشود', 'باید', 'همه', 'باشه', 'توی', 'دیگه',
        'هستن', 'داشته', 'باشید', 'داشتن', 'دهند', 'باشیم', 'نبین', 'ندارد', 'نشنو', 'شود', 'رفت', 'بریزید', 'میباشد'
    ]

    originText = ''
    text = ''
    title = ''
    links = []
    hashtag_count = 4
    hashtags = []

    def __init__(self, telegramBot):
        if isinstance(telegramBot, TelegramBot):
            self.tg = telegramBot
            self.checkTelegramBot()
        else:
            raise ValueError("Object is invalid.")

    def checkTelegramBot(self):
        if self.tg.isMessageVerified() == False:
            raise ValueError("The received text is invalid.")
        else:
            self.originText = self.tg.getMessage()
            self_text_lines = self.arabicToPersian(self.removeAllEntities(self.removeEmoji(self.originText)))
            self_text_lines = self_text_lines.split("\n")
            self_text_lines = [x.strip() for x in self_text_lines if len(x.strip()) > 2 or len(x.strip()) == 0]
            self.text = "\n".join(self_text_lines)
            self.links.clear()
            self.hashtags.clear()
            self.title()
            self.hashtagsAndLinks()

    def arabicToPersian(self, text:str):
        diff = {
            "ة": "ه",
            "ك": "ک",
            "دِ": "د",
            "بِ": "ب",
            "زِ": "ز",
            "ذِ": "ذ",
            "شِ": "ش",
            "سِ": "س",
            "ى": "ی",
            "ي": "ی",
            "٠": "۰",
            "١": "۱",
            "٢": "۲",
            "٣": "۳",
            "٤": "۴",
            "٥": "۵",
            "٦": "۶",
            "٧": "۷",
            "٨": "۸",
            "٩": "۹"
        }
        for char in diff:
            if char in text:
                text = text.replace(char, diff[char])
        return text
    
    def removeEmoji(self, text):
        patterns = ''
        with open('emoji-v15.txt', 'r') as f:
            patterns = f.readlines()
            patterns =  "".join(patterns)
        _rx = re.compile(pattern = "["+patterns+"]+", flags = re.UNICODE)
        # remove
        return _rx.sub(r'',text).replace('°', '').replace("﷽", '').replace('‌', '').strip()
    
    def removeAllEntities(self, text):
        hashtags = []
        for entity in self.tg.getEntities():
            if entity['type'] == 'hashtag':
                while self.originText[entity['offset']] != "#":
                    if entity['offset'] < 1:
                        LOG_INFO('Hashtag not found:' + self.originText + self.entities)
                        import sys
                        sys.exit()
                    entity['offset'] -= 1
                s = entity['offset']
                e = s + entity['length']
                hashtag = self.originText[s:e]
                self.hashtags.append(hashtag[1:].replace("_", " "))
                hashtags.append(hashtag)
        entity_prefixes = ['@','#']
        words = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                if line in hashtags:
                    continue
                added = False
                for word in line.split():
                    word = word.strip()
                    if word in hashtags:
                        word = word.replace(word, word[1:].replace("_", " "))
                    if word and word[0] not in entity_prefixes:
                        words.append(word + " ")
                        added = True
                if added:
                    words[-1] = words[-1].strip() + "\n"
            else:
                words.append("\n")
        return "".join(words).strip()

    def removeWordEntities(self, word):
        chars = string.punctuation + "،؟"
        chars += "ًٌٍَُِّْٰٔ" # ده کاراکتر تنوینی یا آوائی
        for c in chars:
            if c in word:
                word = word.replace(c, '')
        return word.strip()

    def isNumeric(self, word):
        return re.match("^[\d.۰۱۲۳۴۵۶۷۸۹+-]+$", word)

    def wornInHashtags(self, words):
        for hashtag in self.hashtags:
            if words in hashtag:
                return True
        return False

    def countRepeatWords(self):
        words = re.findall(r'\w+', self.removeWordEntities(self.text))
        repeat_words2 = [' '.join(ws) for ws in zip(words, words[1:])]
        repeat_words2 = [w for w, f in Counter(repeat_words2).most_common() if f > 1]
        if len(repeat_words2) == 0:
            return []
        repeat_words3 = [' '.join(ws) for ws in zip(words, words[1:], words[2:])]
        repeat_words3 = [w for w, f in Counter(repeat_words3).most_common() if f > 1]
        wordscount_filter = repeat_words3
        i = 0
        while i < len(wordscount_filter):
            words = wordscount_filter[i].split()
            if words[0] in self.extraLetters and words[1] in self.extraLetters:
                del wordscount_filter[i]
            else:
                i += 1
        i = 1
        while i < len(wordscount_filter):
            for j in range(0, i):
                c = 0
                words1 = wordscount_filter[j]
                for word in wordscount_filter[i].split():
                    if word in words1:
                        c += 1
                if c > 1:
                    del wordscount_filter[i]
                    i -= 1
                    break
            i += 1
        i = 0
        while i < len(repeat_words2):
            tow_word = repeat_words2[i]
            for three_word in wordscount_filter:
                if tow_word in three_word:
                    del repeat_words2[i]
                    i -= 1
                    break
            i += 1
        wordscount_filter += repeat_words2
        i = 0
        while i < len(wordscount_filter):
            words = wordscount_filter[i]
            n = 0
            c = 0
            for word in words.split():
                n += 1
                if len(word) < 3 or word in self.extraLetters or self.isNumeric(word):
                    c += 1
            if n - c <= 0:
                del wordscount_filter[i]
            else:
                i += 1
        return wordscount_filter
    
    def hashtagsAndLinks(self):
        for entity in self.tg.getEntities():
            if entity['type'] == 'text_link' and entity['url'] not in self.links:
                self.links.append(entity['url'])
        if len(self.hashtags) < self.hashtag_count:
            count_word = self.countRepeatWords()
            if len(count_word) > 0:
                max = min(self.hashtag_count-len(self.hashtags), len(count_word))
                for words in count_word:
                    if max < 1:
                        return
                    max -= 1
                    self.hashtags.append(words)
        if len(self.hashtags) < self.hashtag_count:
            words = self.removeWordEntities(self.text).split()
            word_index = {}
            for word in words:
                word = word.strip()
                if len(word) < 3 or word in self.extraLetters or self.wornInHashtags(word) or self.isNumeric(word):
                    continue
                if word not in word_index:
                    word_index[word] = 1
                else:
                    word_index[word] += 1
            word_index = sorted(word_index.items(), key=lambda x: x[1], reverse=True)
            word_index = [x for x in word_index if x[1] > 1]
            if len(word_index) > 0:
                max = min(self.hashtag_count-len(self.hashtags), len(word_index))
                for word in word_index:
                    if max < 1:
                        return
                    max -= 1
                    self.hashtags.append(word[0])

    def title(self):
        self_text = self.text.replace('_', ' ')
        self_text_lines = self_text.split("\n")
        next_line_for_step2 = False
        # Step 1: Ignore the first line
        hashtags = ['تکنیک سلامت', 'آیا می دانید', 'آیا میدانید']
        for hashtag in hashtags:
            if hashtag in self_text_lines[0] and len(hashtag) + 11 > len(self_text_lines[0]):
                del self_text_lines[0]
                next_line_for_step2 = True
                if self.wornInHashtags(hashtag) == False:
                    self.hashtags.append(hashtag)
                break
        self_text_lines = [x.strip() for x in self_text_lines if len(x.strip()) > 3]
        self_text = "\n".join(self_text_lines).lstrip()
        # Step 2: hashtag
        text = self.removeEmoji(self.originText).split("\n")
        text = [x.strip() for x in text if x.strip()]
        if next_line_for_step2:
            if len(text) > 1:
                text = text[1].strip()
            else:
                text = False
        else:
            text = text[0].rstrip()
        if text and "#" in text:
            text2 = text.replace('_', ' ')
            for hashtag in hashtags:
                if hashtag in text2 and len(hashtag) + 11 > len(text2):
                    text = False
                    break
            if text:
                text = text.replace("#", '_').split('_')
                text = [x.strip() for x in text if x.strip()]
                if len(text) > 1:
                    text =  " ".join(text)
                    self.title = self.removeWordEntities(text)
                    return
        # Step 3: final
        p = "؟"
        p += "?:.,;؛،!_"
        title_pattern = "\s*([^" + p + "]+)[" + p + "]"
        text = self_text_lines[0].rstrip()
        if len(text.split()) == 1: # single word
            if len(self_text_lines) > 1: # has next line
                findall = re.findall(title_pattern, text)
                if len(findall) > 0:
                    text = findall[0]
                if len(text) > 3 and text not in self.extraLetters and self.wornInHashtags(text) == False and self.isNumeric(text) == False:
                    self.hashtags.append(text.replace("_", " "))
                text = self_text_lines[1].strip()
        findall = re.findall(title_pattern, text)
        if len(findall) > 0:
            findall[0] = findall[0].strip()
            if findall[0] and len(findall[0].split()) != 1:
                text = findall[0]
            elif len(findall) > 1:
                text = findall[0] + " " + findall[1]
        if len(text) > 99:
            for l in [' و ', ' تا ', '،']:
                if len(text.split(l)) > 1:
                    text = text.split(l)[0]
        else:
            self_text = self.text.split("\n")
            if text.strip() in self_text[0]:
                del self_text[0]
                self.text = "\n".join(self_text).strip()
        self.title = self.removeWordEntities(text)

    def getTitle(self):
        return self.title

    def getText(self):
        return self.text

    def getReference(self, type = 3):
        return self.tg.getReference(type)

    def getTime(self):
        return self.tg.getDate()

    def getDate(self):
        return datetime.utcfromtimestamp(self.tg.getDate()).strftime('%Y-%m-%dT%H:%M:%S')

    def getLinks(self):
        return self.links

    def getHashTags(self):
        return self.hashtags
    
    def getCategoryID(self):
        return {
            -1001293868346: 1010, #سلامت روان
            -1001222117814: 1012, #پزشکی و سلامت
            -1001006831974: 2018  #روانشناسی
        }.get(self.tg.getChannelID(), 2043) #کلینیک

    def getCrawledID(self):
        return {
            -1001293868346: 2104, # @Masiresabzzzz
            -1001222117814: 2105, # @tebiraann
            -1001006831974: 2106  # @My8Behesht
        }.get(self.tg.getChannelID(), 0)

    def data(self):
        return {
            'title': self.getTitle(), 'text': self.getText(),
            'text_origin': self.originText, 'hashtags': self.getHashTags(),
            'links': self.getLinks(), 'time': self.getTime(),'date': self.getDate(),
            'reference': self.getReference()
        }                         