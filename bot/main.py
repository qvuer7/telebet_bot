import logging
import os
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    filters,
    MessageHandler,
    InlineQueryHandler,)

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext, CallbackQueryHandler,
)

from BetsAPI.json_reader import get_soccer_inplay_data
from BetsAPI.json_reader import User_data
from BetsAPI.json_reader import check_voucher, redeem_vaucher



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '5287272096:AAHzmbdDwDeLnWPRzbVGfrH246vP4oVtPtQ'
STARTED = 1
TOP_UP = 11
TOP_UP_BY_VAUCHER1 = 111
TOP_UP_BY_VAUCHER2 = 1111
BALANCE_CHECKED = 12
LOOKING_FOR_THE_GAME = 13
BETS_CHECKED = 14
INPLAY_OR_UPCOMING = 131
LOOKING_FOR_THE_GAME_BY_CAT = 1310
CHOOSING_LEAGUE = 1311
CHOOSING_GAME_IN_LEAGUE = 13111
PROCEEDING_WITH_BETTING = 131111
AMOUNT_TO_CHOOSE = 1311111
AMOUNT_TO_BET = 13111111
BET_TO_CONFIRM = 131111111





async def start(update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
    logging.info("User inside start function.")
    user = update.message.from_user
    user_data = User_data(user['id'])

    reply_keyboard = [['Пополнить баланс', 'Проверить Баланс'], ['Найти Матч', 'Проверить открытые ставки']]
    await update.message.reply_text('нужно добавить текст 1',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard
                              ),
                              )

    return STARTED

async def inplay_or_upcoming_event(update: Update, context: CallbackContext):
    reply_keyboard = [['Матч в онлайне', 'Матч в линии'], ['Назад в главное меню', 'Выйти']]
    logging.info("User inside inplay_or_upcoming_event")
    await update.message.reply_text(text = 'Нужно добавить текст132/131', reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                    one_time_keyboard=True))

    return INPLAY_OR_UPCOMING


async def find_game(update: Update, context: CallbackContext):
    logging.info("User inside find_game")
    if update.message.text == 'Матч в онлайне':
        context.user_data["inplay"] = 1
    if update.message.text == 'Матч в линии':
        context.user_data['inplay'] = 0

    reply_keyboard = [['Найти матч текстом(В разработке)', 'Выбрать спорт'], ['Назад к типу матча', 'Выйти']]
    await update.message.reply_text(text = 'Нужно добавить текст13', reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                    one_time_keyboard=True))

    return LOOKING_FOR_THE_GAME




async def find_game_by_category(update:Update, context: CallbackContext):
    logging.info("User inside find_game_by_category")
    reply_keyboard = [['Футбол', 'Баскетбол'],
                      ['Теннис','Волейбол'],
                      ['Ганбол','Бейсбол'],
                      ['Конные скачки','Собачьи скачки'],
                      ['Хокей','Снукер'],
                      ['Американский футбол','Крикет'],
                      ['Футзал','Дартс'],
                      ['Настольный теннис','Бадминтон'],
                      ['Рэгби Union','Рэгби Legue'],
                      ['Австралийский футбол','Боулз'],
                      ['Бокс/UFC','Гэльский спорт'],
                      ['Флорбол','Пляжный волейбол'],
                      ['Водное поло','Сквош'],
                      ['E-sports'],
                      ['Назад к типу поиска','Выйти']]

    await update.message.reply_text(text='Нужно добавить текст132', reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                                   one_time_keyboard=True))
    return LOOKING_FOR_THE_GAME_BY_CAT

async def choosing_socer_league(update: Update, context: CallbackContext):
    logging.info("User inside choosing_socer_league")
    if context.user_data['inplay']:
        #At this point context['user data'] contains soccer_data class object with all inplay games in it
        data = get_soccer_inplay_data()
        reply_keyboard = data.get_leagues_keyboard()
        context.user_data['data'] = data

        await update.message.reply_text(text='Нужно добавить текст132', reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                                         one_time_keyboard=True))
    else:
        pass

    return CHOOSING_LEAGUE

async def choose_soccer_league(update: Update, context: CallbackContext):
    logging.info("user in choose_soccer_league")
    mes = update.message.text.replace('Лига ', '')
    if mes != 'Назад к играм': context.user_data['chosen_league'] = mes

    if mes in context.user_data['data'].leagues or mes == 'Назад к играм':
        # At this point context['user data'] contains soccer_data class object with all inplay games in it
        # and self.games_in_league cointains games in chosen league

        data = context.user_data['data']
        games = list(data.get_games_in_league(context.user_data['chosen_league']))
        games = [games[i].betsapi_event_id for i in range(len(games))]
        reply_keyboard = data.get_games_keyboard()
        await update.message.reply_text(text='chosen game' + str(games), reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                                         one_time_keyboard=True))

    else:
        await update.message.reply_text(text='Не правильно введен текст, просто нажимай на кнопку в следющи раз, сейчас начни заново')

    return CHOOSING_GAME_IN_LEAGUE




async def choose_game_from_games(update: Update, context: CallbackContext):
    mes = update.message.text
    if mes!='Назад к выбору ставки':
        mes = update.message.text.replace('Игра ', '')
        game = context.user_data['data'].get_game_by_name(mes)
        context.user_data['game'] = game


    mes = update.message.text.replace('Игра ', '')
    game =  context.user_data['data'].get_game_by_name(mes)
    logging.info("User entered choose_game_from_games_function.")
    logging.info('User texted message: %s', mes)

    if game or mes == 'Назад к выбору ставки':
        game = context.user_data['game']
        PA_ods = game.get_data_from_FI_id()
        keyboard = game.get_WDL_odds_keyboard()
        await update.message.reply_text(text='Выбери ставкуProblem', reply_markup=ReplyKeyboardMarkup(keyboard,one_time_keyboard = True))

    else:
        await update.message.reply_text(text = f'Не правильно введенный текст просто нажми на кнопку в следующий раз1111')

    return PROCEEDING_WITH_BETTING




async def choose_bet(update: Update, context: CallbackContext):

    logging.info("User entered choose_bet.")
    message = update.message.text.split(':')
    context.user_data['chosen_bet'] = 'kek'
    keyboard = [['Подтвердить и выбрать сумму'], ['Назад к выбору ставки', 'Выйти']]
    if 'П1' in message:
        context.user_data['chosen_bet'] = context.user_data['game'].PA_field[0]['ID']
        await update.message.reply_text(text=f'Выбрана победа {message[1]} за {message[2]} ',
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    elif 'Ничья' in message:
        context.user_data['chosen_bet'] = context.user_data['game'].PA_field[1]['ID']
        await update.message.reply_text(text=f'Выбрана ничья за {message[1]} ',
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    elif 'П2' in message:
        context.user_data['chosen_bet'] = context.user_data['game'].PA_field[2]['ID']
        await update.message.reply_text(text=f'Выбрана победа {message[1]} за {message[2]} ',
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))




    return AMOUNT_TO_CHOOSE




async def amount_for_bet(update: Update, context: CallbackContext):
    logging.info("User entered amount_for_bet.")
    logging.info("message from user: %s", update.message.text)
    keyboard = [['Назад к выбору ставки', 'Выйти']]
    await update.message.reply_text(text = 'Напиши текстом сумму для ставки пример формата: 250',
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return AMOUNT_TO_BET


async def second_bet_confiramtion(update: Update, context: CallbackContext):
    user = update.message.from_user
    logging.info("User entered amount_for_bet.")
    logging.info("message from user: %s", update.message.text)
    logging.info("message from username: %s , with id: %s", user['username'], user['id'])
    user_data = User_data(user['id'])
    keyboard = [['Подтвердить'], ['Назад', 'Выйти']]
    bet = context.user_data['game'].get_bet_by_ID(context.user_data['chosen_bet'])
    context.user_data['amount'] = update.message.text


    if bet:
        new_line = "\n"
        if bet['NA'] == 'Draw': res = 'Ничья'
        else: res = f"Победа {bet['NA']}"
        response_text = f"Выбрана ставка: {res} {new_line} по коэфициенту {bet['OD']} {new_line}" \
                        f"на сумму {context.user_data['amount']} {new_line}," \
                        f"возможный выигрыш {float(context.user_data['amount']) * float(bet['OD']) } Подтвердить?"
        await update.message.reply_text(text = response_text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return BET_TO_CONFIRM
    else:
        await update.message.reply_text(text = 'Произошла ошибка разговор автоматически закончен')
        return ConversationHandler.END


async def place_bet(update:Update, context: CallbackContext):
    user = update.message.from_user
    user_data = User_data(user['id'])
    if update.message.text == 'Назад':
        pass
    elif user_data.check_avaliable_balance(float(context.user_data['amount'])):

        user_data.add_open_bet(context.user_data['game'].get_bet_by_ID(context.user_data['chosen_bet']),context.user_data['amount'] )
        user_data.balance-= float(context.user_data['amount'])
        user_data.write_to_file()
        await update.message.reply_text(text='Ставка принята начните процесс заново командой /start')
        return ConversationHandler.END
    else:
        await update.message.reply_text(text='Не достаточно средств на баланасе')
        return AMOUNT_TO_BET

async def balance_top_up_method_choose(update: Update, context: CallbackContext):

    keyboard = [['Пополнить вучер кодом', 'Пополнить криптой (в разработке)'], ['Назад', 'Выйти']]
    await update.message.reply_text(text='Добавить текст 11', reply_markup=ReplyKeyboardMarkup(keyboard))

    return TOP_UP

async def balance_top_up_by_vaucher_to_enter(update: Update, context: CallbackContext):
    keyboard = [['Назад', 'Выйти']]
    await update.message.reply_text(text='Введи код ваучера:',
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return TOP_UP_BY_VAUCHER1





async def check_and_top_up_vaucher(update: Update, context):
    user_data = User_data(update.message.from_user['id'])
    text = update.message.text
    amount = check_voucher(text)
    keyboard = [['Выйти']]
    if amount:
        user_data.top_up(amount)
        redeem_vaucher(text)
        await update.message.reply_text(text = f"Баланс пополнен на {amount}, теперь ваш баланс {user_data.balance} вернитесь в главное меню: /start")
        return ConversationHandler.END
    else:
        await update.message.reply_text(text=f"Код не верный ваш баланс {user_data.balance}, введите код еще раз или выйдите в главное меню",
                                        reply_markup= ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return TOP_UP


async def check_balance(update: Update, context: CallbackContext):
    user_data = User_data(update.message.from_user['id'])
    keyboard = [['Назад', 'Выйти']]
    await update.message.reply_text(text=f"Ваш баланс {user_data.balance}", reply_markup=ReplyKeyboardMarkup(keyboard))
    return BALANCE_CHECKED

async def check_open_bets(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_data = User_data(user['id'])
    user_data.close_bets()
    reply_text = user_data.get_info_about_closed_and_open_bets()
    print(f"type of reply text: {type(reply_text)}, reply text itself:")
    print(reply_text)
    keyboard = [['Назад'], ['Выйти']]
    await update.message.reply_text(text = reply_text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return BETS_CHECKED

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""

    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(text = 'Разговор окончен', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:

    application = ApplicationBuilder().token(TOKEN).build()


    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STARTED: [MessageHandler(filters.Regex('^(Найти Матч)$'), callback=inplay_or_upcoming_event),
                      MessageHandler(filters.Regex('^(Пополнить баланс)$'), callback=balance_top_up_method_choose),
                      MessageHandler(filters.Regex('^(Проверить Баланс)$'), callback=check_balance),
                      MessageHandler(filters.Regex('^(Проверить открытые ставки)$'), callback=check_open_bets)],

            BETS_CHECKED: [MessageHandler(filters.Regex('^(Назад)$'), start)],
            BALANCE_CHECKED: [MessageHandler(filters.Regex('^(Назад)$'), start)],

            INPLAY_OR_UPCOMING: [MessageHandler(filters.Regex('^(Матч в онлайне|Матч в линии)$'),callback = find_game),
                                 MessageHandler(filters.Regex('^(Назад в главное меню)$'), start)],
            TOP_UP: [MessageHandler(filters.Regex('^(Пополнить вучер кодом)$'), balance_top_up_by_vaucher_to_enter),
                     MessageHandler(filters.Regex('^(Назад)$'), start)],

            TOP_UP_BY_VAUCHER1: [MessageHandler(filters.Regex('^((?!Назад|Выйти).)*$'), check_and_top_up_vaucher),
                                 MessageHandler(filters.Regex('^(Назад)$'), balance_top_up_method_choose)],


            LOOKING_FOR_THE_GAME: [MessageHandler(filters.Regex('^(Выбрать спорт)$'),callback = find_game_by_category),
                                   MessageHandler(filters.Regex('^(Назад к типу матча)$'), inplay_or_upcoming_event)],

            LOOKING_FOR_THE_GAME_BY_CAT: [MessageHandler(filters.Regex('^(Футбол)$'),callback = choosing_socer_league),
                                          MessageHandler(filters.Regex('^(Назад к типу поиска)$'), find_game)],

            CHOOSING_LEAGUE: [MessageHandler(filters.Regex('^.*Лига.*$'), choose_soccer_league),
                              MessageHandler(filters.Regex('^(Назад к категориям спорта)$'), find_game_by_category)],

            CHOOSING_GAME_IN_LEAGUE: [MessageHandler(filters.Regex('^.*Игра.*$'), choose_game_from_games),
                                      MessageHandler(filters.Regex('^(Назад к лигам)$'), choosing_socer_league)],

            PROCEEDING_WITH_BETTING: [MessageHandler(filters.Regex('^.*П2.*|.*П1.*|.*Ничья.*$'), choose_bet),
                                      MessageHandler(filters.Regex('^(Назад к играм)$'), choose_soccer_league)],

            AMOUNT_TO_CHOOSE: [MessageHandler(filters.Regex('^(Подтвердить и выбрать сумму)$'), amount_for_bet),
                             MessageHandler(filters.Regex('^(Назад к выбору ставки)$'), choose_game_from_games)],

            AMOUNT_TO_BET: [MessageHandler(filters.Regex('^([\s\d]+)$'),second_bet_confiramtion),
                            MessageHandler(filters.Regex('^(Назад к выбору ставки)$'), choose_game_from_games)],

            BET_TO_CONFIRM: [MessageHandler(filters.Regex('^(Подтвердить)$'), place_bet),
                             MessageHandler(filters.Regex('^(Назад)$'), amount_for_bet)]

        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.Regex('^(Выйти)$'), callback = cancel)],
       )
    application.add_handler(conv_handler1)
    application.run_polling()

if __name__ == '__main__':
    main()


