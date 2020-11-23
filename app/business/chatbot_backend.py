from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from app.business.dialogflow_backend import get_intent
from app.model.database_query import DatabaseQuery, alloc_status
import app.model.colname as cname
import app.model.utils as utils
import logging
# import app.model.reply_templates as replies
import os

class ChatBot():
    def __init__(self):
        self.TOKEN = os.environ['TELEGRAM_TOKEN']
        self.PORT = int(os.environ.get('PORT', '8443'))
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.default_replies = DatabaseQuery().replies

    def welcome_intent(self, update, context):
        query = DatabaseQuery(self.default_replies)
        chat_id = update.effective_chat.id
        user = update.message.from_user
        registered = query.checkIfRegistered(user.id)
        # print("json key exists:", str(os.path.isfile('./'+os.environ["GOOGLE_APPLICATION_CREDENTIALS"])))
        # print(repr(open('./' + os.environ["GOOGLE_APPLICATION_CREDENTIALS"], "r").read()))
        if registered:
            context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_welcome).format(firstname=user.first_name))
        else:
            success = query.registerUser(user.id, "@"+user.username, withUsername=True)
            if success:
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_reg_pass).format(firstname=user.first_name))
            else:
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_reg_user).format(firstname=user.first_name))

    def register_user(self, update, context):
        query = DatabaseQuery(self.default_replies)
        chat_id = update.effective_chat.id
        if len(context.args) > 0:
            email = context.args[0].lower()
            user = update.message.from_user
            success = query.registerUser(user.id, email, withUsername=False)
            if success:
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_reg_pass).format(firstname=user.first_name))
            else:
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_reg_fail).format(firstname=user.first_name))
        else:
            context.bot.send_message(chat_id=chat_id, text="Please enter your email after /register.")

    def create_dates_kb(self, purpose, query, tgUserId = ""):
        if purpose == '/change_alloc':
            vacantDates = query.getVacantDates()
            kb = []
            for date in vacantDates:
                kb.append([KeyboardButton(purpose + ' ' + date)])
        elif purpose == '/cancel_alloc':
            kb = [[KeyboardButton("Enter manually:\n" + purpose + " <allocated_date>\n in dd/mm/yy format")],[KeyboardButton("NO! Go back!")]]
        elif purpose == '/set_avail':
            vacantDates = query.getVacantDates()
            kb = []
            for date in vacantDates:
                kb.append([KeyboardButton('/change_avail set ' + date)])
        elif purpose == '/cancel_avail':
            dates = query.getAvailability(tgUserId)
            kb = []
            for date in dates:
                kb.append([KeyboardButton('/change_avail cancel ' + date)])
        elif purpose == '/eventtime':
            vacantDates = query.getVacantDates()
            kb = []
            for date in vacantDates:
                kb.append([KeyboardButton(purpose + ' ' + date)])

        return kb

    def create_changecancel_inline(self, purpose):
        keyboard = [[InlineKeyboardButton("Change Date", callback_data='change_' + purpose),
                     InlineKeyboardButton("Cancel Date", callback_data='cancel_' + purpose)]]

        # reply_markup = InlineKeyboardMarkup(keyboard)
        # update.message.reply_text('Please select your dates:', reply_markup=reply_markup)
        return keyboard

    def create_setcancel_inline(self, purpose):
        keyboard = [[InlineKeyboardButton("Set Date", callback_data='set_' + purpose),
                     InlineKeyboardButton("Cancel Date", callback_data='cancel_' + purpose)]]
        return keyboard

    def inlineKB_callbacks(self, update, context):
        query = update.callback_query
        chat_id = update.effective_chat.id
        user = query.from_user
        query.answer()
        dbquery = DatabaseQuery(self.default_replies)
        if query.data == "change_allocation":
            kb = self.create_dates_kb('/change_alloc', query=dbquery)
            if len(kb) > 0:
                context.bot.send_message(chat_id=chat_id, text="Please select a slot.", reply_markup=ReplyKeyboardMarkup(kb))
            else:
                context.bot.send_message(chat_id=chat_id, text="I'm sorry there are no vacant slots remaining.", reply_markup=ReplyKeyboardRemove())
        elif query.data == "cancel_allocation":
            kb = self.create_dates_kb('/cancel_alloc', query=dbquery)
            context.bot.send_message(chat_id=chat_id, text="Please confirm cancellation.", reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))
        elif query.data == "set_availability":
            kb = self.create_dates_kb('/set_avail', query=dbquery)
            if len(kb) > 0:
                context.bot.send_message(chat_id=chat_id, text="Please select date.", reply_markup=ReplyKeyboardMarkup(kb))
            else:
                context.bot.send_message(chat_id=chat_id, text="I'm sorry there are no vacant slots remaining.", reply_markup=ReplyKeyboardRemove())
        elif query.data == "cancel_availability":
            kb = self.create_dates_kb('/cancel_avail', query=dbquery, tgUserId=user.id)
            if len(kb) > 0:
                context.bot.send_message(chat_id=chat_id, text="Please select date.", reply_markup=ReplyKeyboardMarkup(kb))
            else:
                context.bot.send_message(chat_id=chat_id, text="I'm sorry you have no availabilities indicated.", reply_markup=ReplyKeyboardRemove())

        # # query.answer() # comment this line if you wish to use answerCallbackQuery
        # context.bot.answerCallbackQuery(callback_query_id=query.id, text=f"Selected date: {query.data}") # show a notification bar when user press on inline btn
        # # query.edit_message_text(text=f"Selected date: {query.data}") # reply with text when user press on inline btn
        # context.bot.send_message(chat_id=chat_id, text=f"Selected date: {query.data}")

    def change_allocation(self, update, context):
        query = DatabaseQuery(self.default_replies)
        chat_id = update.effective_chat.id
        user = update.message.from_user
        old_alloc_date = query.getAllocation(user.id)
        if len(context.args) > 0:
            if old_alloc_date == alloc_status.pending.name:
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_chg_fail))
            elif old_alloc_date == 'error':
                context.bot.send_message(chat_id=chat_id, text="DB error. Allocated date in DB not in dd/mm/yy format.")
            else:
                new_alloc_date = context.args[0]
                success = query.setAllocation(user.id, new_alloc_date)
                if success:
                    new_date = utils.convertdate_for_display(new_alloc_date)
                    old_date = utils.convertdate_for_display(old_alloc_date)
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_chg_pass).format(new_date=new_date, old_date=old_date))
                else:
                    context.bot.send_message(chat_id=chat_id, text="Failed to change allocation")
        else:
            context.bot.send_message(chat_id=chat_id, text="Please enter a date (in dd/mm/yy format) after /change_alloc.")

    def cancel_allocation(self, update, context):
        query = DatabaseQuery(self.default_replies)
        chat_id = update.effective_chat.id
        user = update.message.from_user
        if len(context.args) > 0:
            entered_date = context.args[0]
            old_alloc_date = query.getAllocation(user.id)
            if utils.convertdate_for_display(old_alloc_date) != "None" and entered_date == old_alloc_date:
                date = utils.convertdate_for_display(old_alloc_date)
                query.cancelAllocation(user.id)
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_cancel_pass).format(date=date))
            else:
                date = utils.convertdate_for_display(entered_date)
                if date != "None":
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_cancel_fail2).format(date=date))
                else:
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_cancel_fail1))
        else:
            context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_cancel_fail1))

    def change_avail(self, update, context):
        query = DatabaseQuery(self.default_replies)
        chat_id = update.effective_chat.id
        user = update.message.from_user
        if len(context.args) > 1:
            action = "set" if context.args[0] == "set" else "cancel"
            date = context.args[1]
            date_converted = utils.convertdate_for_display(date) # ensure date is in dd/mm/yy format
            if date_converted != "None":
                success = query.setAvailability(user.id, date, set=(action=="set"))
                if success:
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_avail_set_pass).format(action=action, date=date_converted))
                else:
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_avail_set_fail).format(action=action))
            else:
                context.bot.send_message(chat_id=chat_id, text="Please enter a date (in dd/mm/yy format) after /change_avail <action>.")
        else:
            context.bot.send_message(chat_id=chat_id, text="Please enter an action (set/cancel) and a date (in dd/mm/yy format) after /set_avail.")

    def get_event_time(self, update, context):
        query = DatabaseQuery(self.default_replies)
        chat_id = update.effective_chat.id
        if len(context.args) > 0:
            date = context.args[0]
            date_converted = utils.convertdate_for_display(date)
            if date_converted != "None":
                startend = query.getEventStartEnd(date)
                if len(startend) > 0:
                    start = startend[0]
                    end = startend[1]
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_duration_user_entered).format(date=date_converted,start=start,end=end))
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_contConverse))
                else:
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_duration_invalid_date).format(date=date_converted))
            else:
                context.bot.send_message(chat_id=chat_id, text="Please enter a date in dd/mm/yy format")
        else:
            context.bot.send_message(chat_id=chat_id, text="Please enter a date in dd/mm/yy format")

    def unknown(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def openended_reply(self, update, context):
        print("message: ", update.message.text)
        user = update.message.from_user
        chat_id = update.effective_chat.id
        query = DatabaseQuery(self.default_replies)
        response = get_intent(session_id=update.effective_chat.id, text=update.message.text)
        intent_name = response.query_result.intent.display_name
        print(f"intent: {intent_name}")

        if not query.checkIfRegistered(user.id):
            context.bot.send_message(chat_id=chat_id,text=query.getReply(cname.i_reg_user).format(firstname=user.first_name))
            return

        if intent_name == "getAllocation" or intent_name == 'changeAllocation':
            date = query.getAllocation(user.id)
            if date == alloc_status.pending.name:
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_get_fail_pend), reply_markup=ReplyKeyboardRemove())
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_contConverse))
            elif date == alloc_status.nodatesavailable.name or date == alloc_status.availabilitynotgiven.name:
                kb = self.create_dates_kb('/change_alloc', query=query)
                if len(kb) > 0:
                    reply = cname.i_alloc_get_fail1 if date == alloc_status.nodatesavailable.name else cname.i_alloc_get_fail3
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(reply), reply_markup=ReplyKeyboardMarkup(kb))
                else:
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_get_fail2), reply_markup=ReplyKeyboardRemove())
            elif utils.convertdate_for_display(date) != "None":
                date = utils.convertdate_for_display(date)
                if intent_name == 'getAllocation':
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_alloc_get).format(date=date), reply_markup=ReplyKeyboardRemove())
                    context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_contConverse))
                else:
                    reply_markup = InlineKeyboardMarkup(self.create_changecancel_inline(purpose='allocation'))
                    update.message.reply_text(f'You have a slot on {date}. Do you like to CHANGE or CANCEL it?', reply_markup=reply_markup)
            else:
                context.bot.send_message(chat_id=chat_id, text='DB error', reply_markup=ReplyKeyboardRemove())
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_contConverse))
        elif intent_name == "changeAvailability" or intent_name == "setAvailability":
            availabilities = query.getAvailability(user.id)
            availabilities = [utils.convertdate_for_display(date) for date in availabilities]
            avail_string = '\n'.join(availabilities) if len(availabilities) > 0 else "None"
            reply_markup = InlineKeyboardMarkup(self.create_setcancel_inline(purpose='availability'))
            update.message.reply_text(query.getReply(cname.i_avail_set) + '\n' + avail_string, reply_markup=reply_markup)
        elif intent_name == "getEventDuration" or intent_name == "getEventTime":
            date = query.getAllocation(user.id)
            if utils.convertdate_for_display(date) != "None":
                startend = query.getEventStartEnd(date)
                start = startend[0]
                end = startend[1]
                date = utils.convertdate_for_display(date)
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_duration_user_alloc).format(date=date,start=start,end=end),
                                         reply_markup=ReplyKeyboardRemove())
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_contConverse))
            else:
                kb = self.create_dates_kb("/eventtime", query)
                context.bot.send_message(chat_id=chat_id, text="Please choose a date.", reply_markup=ReplyKeyboardMarkup(kb))
        else:
            resp_text = query.getReply(intent_name) if intent_name in query.replies.keys() else response.query_result.fulfillment_text
            context.bot.send_message(chat_id=update.effective_chat.id, text=resp_text, reply_markup=ReplyKeyboardRemove())
            if intent_name != "endConverse" and intent_name != 'contConverse' and intent_name != 'defaultWelcomeIntent':
                context.bot.send_message(chat_id=chat_id, text=query.getReply(cname.i_contConverse))

    def start_chatbot(self):
        updater = Updater(token=self.TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.welcome_intent)
        register_handler = CommandHandler('register', self.register_user)
        chgAlloc_handler = CommandHandler('change_alloc', self.change_allocation)
        cancelAlloc_handler = CommandHandler('cancel_alloc', self.cancel_allocation)
        setavail_handler = CommandHandler('change_avail', self.change_avail)
        eventtime_handler = CommandHandler('eventtime', self.get_event_time)
        nlpreply_handler = MessageHandler(Filters.text & (~Filters.command), self.openended_reply)
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        inlineKB_callback_handler = CallbackQueryHandler(self.inlineKB_callbacks)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(register_handler)
        dispatcher.add_handler(chgAlloc_handler)
        dispatcher.add_handler(cancelAlloc_handler)
        dispatcher.add_handler(setavail_handler)
        dispatcher.add_handler(eventtime_handler)
        dispatcher.add_handler(nlpreply_handler)
        dispatcher.add_handler(unknown_handler)
        dispatcher.add_handler(inlineKB_callback_handler)

        # use start_polling() if running on Windows, Telegram Bot webhook is not supported on Windows
        # updater.start_polling()

        # use webhook()
        updater.start_webhook(listen="0.0.0.0", port=self.PORT, url_path=self.TOKEN)
        # updater.bot.set_webhook("https://4f131644df5f.ngrok.io/" + self.TOKEN) # start chat bot backend in local host using webnhook and ngrok (note: remember to start ngrok tunneling before running chat bot)
        updater.bot.set_webhook("https://isapm1-ay2021-childcareliaison.herokuapp.com/" + self.TOKEN) # start chatbot backend in in heroku using webhook

        updater.idle()
        updater.stop()
