import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import MessageHandler, Filters, Dispatcher, updater
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from config import *
import numpy as np
from time import time
from colorama import Fore
import logging

logging.basicConfig(format='%(levelname)s - %(message)s',
                    level=logging.DEBUG)

def yellow_print(text=''):
    print(Fore.YELLOW, text, Fore.WHITE)

def get_user_id(raw_data: Update):
    try:
        res = raw_data['callback_query']['message']['chat']['id']
    except:
        res = raw_data['message']['chat']['id']
    return res

class TutovnikAudio:
    def __init__(self) -> None:
        with open('TOKEN') as f:
            TOKEN = f.read()
        self.bot = telegram.Bot(token=TOKEN)
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        self.command_dict = {
            'start' : self.command_start,
            'send_audio' : self.command_send_audio,
        }
        self.func_dict = {
            'answer': self.command_answer,
        }
        with open(user_stat_path) as f: 
            self.user_stat = json.load(f)
        with open(user_audiotable_path) as f:
            self.user_audiotable = json.load(f)
        with open(user_audiotable_path) as f:
            self.user_audiotable = json.load(f)
        
        with open(user_settings_path) as f:
            self.user_settings = json.load(f)
        self.audio_listdir = os.listdir(audio_path)
        self.last_messages = {}

    def start_bot(self):
        # print('\n\t start_bot\n')
        for name, func in self.command_dict.items():
            self.dispatcher.add_handler(CommandHandler(name, func))
        self.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), self.Command_tracker))
        self.dispatcher.add_handler(CallbackQueryHandler(self.Button_tracker))
        self.updater.start_polling()    
        self.updater.idle()

    def check_user(self, user_id):
        if user_id not in self.user_stat:
            self.user_stat[user_id] = {'id_sound': [], 'status': [], 'time': []}
        if user_id not in self.user_audiotable:
            audio_indexes = [i for i in range(len(self.audio_listdir))]
            np.random.shuffle(audio_indexes)
            self.user_audiotable[user_id] = audio_indexes
        if user_id not in self.last_messages:
            self.last_messages[user_id] = {'audio_id': None, 'answer_id': None, 'true_answer_id': None}

    def update_user_stat(self, user_id, id_sound, status):
        self.check_user(user_id)
        self.user_stat[user_id]['id_sound'].append(id_sound)  
        self.user_stat[user_id]['status'].append(status)  
        time_for_answer = time() - self.last_messages[user_id]['abs_time'] 
        self.user_stat[user_id]['time'].append(time_for_answer) 
        self.save_user_stat()

    def save_user_stat(self):
        with open(user_stat_path, 'w') as f:
            json.dump(self.user_stat, f)
    
    def save_user_audiotable(self):
        with open(user_audiotable_path, 'w') as f:
            json.dump(self.user_audiotable, f)
    
    def Command_tracker(self, update: Update, context:CallbackContext):
        user_id = get_user_id(update)
        answer_id = update.message.message_id

        self.check_user(user_id)
        if context.user_data[user_id]:
            self.func_dict[context.user_data[user_id]](update, context)
        if context.user_data[user_id] == 'answer':
            self.last_messages[user_id]['answer_id'] = answer_id
            audio_id = self.last_messages[user_id]['audio_id']
            self.bot.edit_message_reply_markup(user_id, audio_id)


    def Button_tracker(self, update: Updater, context: CallbackContext):
        user_id = get_user_id(update)
        audio_id = self.last_messages[user_id]['audio_id']
        true_answer_id = self.last_messages[user_id]['true_answer_id']

        query = update.callback_query
        query.answer()
        status = query.data
        id_sound = self.user_audiotable[user_id][0:1]
        
        if status == 'drop_audio':
            self.user_audiotable[user_id] = self.user_audiotable[user_id][1:]
            self.bot.delete_message(user_id, audio_id)
        elif status == 'drop':
            self.user_audiotable[user_id] = self.user_audiotable[user_id][1:]
            self.bot.delete_message(user_id, audio_id)
            self.bot.delete_message(user_id, self.last_messages[user_id]['answer_id'])
            self.bot.delete_message(user_id, true_answer_id)
        else:
            if status == 'correct':
                self.user_audiotable[user_id] = self.user_audiotable[user_id][1:]
            elif status == 'again':
                self.user_audiotable[user_id] = self.user_audiotable[user_id][1:] + id_sound
            self.bot.edit_message_reply_markup(user_id, true_answer_id)

        self.update_user_stat(user_id, id_sound[0], status)
        self.command_send_audio(update, context)
        self.save_user_audiotable()

    def command_start(self, update: Update, context:CallbackContext):
        user_id = get_user_id(update)
        self.check_user(user_id)
        # self.bot.send_message(user_id, '/send_audio')
        self.command_send_audio(update, context)

    def command_send_audio(self, update: Update, context:CallbackContext):
        user_id = get_user_id(update)
        audio_name = self.audio_listdir[self.user_audiotable[user_id][0]]        

        drop_button = telegram.InlineKeyboardButton('🗑️',  callback_data='drop_audio')
        drop_markup = telegram.InlineKeyboardMarkup([[drop_button]])
        with open(audio_path+audio_name, 'rb') as f:
            audio_message = self.bot.send_audio(user_id, f, performer=' ', title=' ', reply_markup=drop_markup)
        context.user_data[user_id] = 'answer'
        
        self.last_messages[user_id]['abs_time'] = time()
        self.last_messages[user_id]['audio_id'] = audio_message.message_id

    def command_answer(self, update: Update, context:CallbackContext):
        user_id = get_user_id(update)
        # text = update.message.text
        true_answer = self.audio_listdir[self.user_audiotable[user_id][0]]    
        true_answer = true_answer.split('#')[-1][:-4 ]

        drop_button = telegram.InlineKeyboardButton('🗑️',  callback_data='drop')
        correct_button = telegram.InlineKeyboardButton('✅',  callback_data='correct')
        again_button = telegram.InlineKeyboardButton('🔄',  callback_data='again')
        
        answer_markup = telegram.InlineKeyboardMarkup([[drop_button, correct_button, again_button]])

        answer_message = self.bot.send_message(user_id, true_answer, reply_markup=answer_markup)

        self.last_messages[user_id]['true_answer_id'] = answer_message.message_id

    def command_stat(self, update: Update, context:CallbackContext):
        user_id = get_user_id(update)
        user_stat = self.user_stat[user_id]
        
    def command_settings(self, update: Update, context:CallbackContext):
        user_id = get_user_id(update)
        # text = update.message.text

        # set_max_length_button = telegram.InlineKeyboardButton(f'max length: {}',  callback_data='drop')
        # set_min_length_button = telegram.InlineKeyboardButton(f'min length: {}',  callback_data='drop')
        correct_button = telegram.InlineKeyboardButton('✅',  callback_data='correct')
        again_button = telegram.InlineKeyboardButton('🔄',  callback_data='again')
        
        # answer_markup = telegram.InlineKeyboardMarkup([[drop_button, correct_button, again_button]])

        # answer_message = self.bot.send_message(user_id, 'SETTINGS', reply_markup=answer_markup)

if __name__ == '__main__':
    Tut = TutovnikAudio()
    Tut.start_bot()