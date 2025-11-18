#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram бот для опитування пацієнтів мануального терапевта
"""

import logging
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Стани розмови
(PIB, VIK, DE_BOLIT, DE_BOLIT_DETALІ, ОНІМІННЯ, ОНІМІННЯ_DE,
 KOLY_ZYAVYVSYA, TRAVMA, TRAVMA_DETALІ, KHARAKTER_BOLY,
 SHKALA_BOLY, POHIRSHUE, POLEHSHUE, RANISHI_EPIZODY, RANISHI_YAK_LIKUVALY,
 CHERVONI_PRAPORY, SUPUTNI, AKTYVNIST, SPORT_YAKYI, LIKUVANNYA,
 FIZIOTERAPIYA, ZRIST, VAGA, CONFIRM, EDIT_CHOICE) = range(25)

# Отримання змінних оточення
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = [int(id) for id in os.environ.get('ADMIN_IDS', '').split(',') if id.strip()]

def format_survey_result(user_data, for_admin=False):
    """Форматує результати анкети для відправки"""
    result = "📋 АНКЕТА ПАЦІЄНТА З БОЛЕМ У СПИНІ\n"
    result += "=" * 40 + "\n\n"
    
    result += f"👤 ПІБ: {user_data.get('pib', 'Не вказано')}\n"
    result += f"📅 Вік: {user_data.get('vik', 'Не вказано')}\n"
    result += f"🗓 Дата заповнення: {user_data.get('date', 'Не вказано')}\n\n"
    
    result += "1️⃣ ДЕ САМЕ БОЛИТЬ?\n"
    result += f"   {user_data.get('de_bolit', 'Не вказано')}\n"
    if user_data.get('onіmіnnya') == 'Так':
        result += f"   Оніміння/поколювання: {user_data.get('onіmіnnya_de', 'Не вказано')}\n"
    else:
        result += f"   Оніміння/поколювання: {user_data.get('onіmіnnya', 'Не вказано')}\n"
    result += "\n"
    
    result += "2️⃣ КОЛИ ПОЯВИВСЯ БІЛЬ?\n"
    result += f"   {user_data.get('koly_zyavyvsya', 'Не вказано')}\n"
    if user_data.get('travma') == 'Так':
        result += f"   Після травми: {user_data.get('travma_detalі', 'Не вказано')}\n"
    else:
        result += f"   Травма: {user_data.get('travma', 'Не вказано')}\n"
    result += "\n"
    
    result += "3️⃣ ХАРАКТЕР БОЛЮ:\n"
    result += f"   {user_data.get('kharakter_boly', 'Не вказано')}\n"
    result += f"   Інтенсивність (0-10): {user_data.get('shkala_boly', 'Не вказано')}\n\n"
    
    result += "4️⃣ ЩО ПОГІРШУЄ/ПОЛЕГШУЄ:\n"
    result += f"   Погіршує: {user_data.get('pohirshue', 'Не вказано')}\n"
    result += f"   Полегшує: {user_data.get('polehshue', 'Не вказано')}\n\n"
    
    result += "5️⃣ РАНІШЕ ПОДІБНІ ЕПІЗОДИ:\n"
    result += f"   {user_data.get('ranishi_epizody', 'Не вказано')}\n"
    if user_data.get('ranishi_epizody') == 'Так':
        result += f"   Як лікували: {user_data.get('ranishi_yak_likuvaly', 'Не вказано')}\n"
    result += "\n"
    
    result += "6️⃣ ЧЕРВОНІ ПРАПОРИ:\n"
    result += f"   {user_data.get('chervoni_prapory', 'Немає')}\n\n"
    
    result += "7️⃣ СУПУТНІ ЗАХВОРЮВАННЯ:\n"
    result += f"   {user_data.get('suputni', 'Немає')}\n\n"
    
    result += "8️⃣ РІВЕНЬ АКТИВНОСТІ:\n"
    result += f"   {user_data.get('aktyvnist', 'Не вказано')}\n"
    if user_data.get('sport_yakyi') and user_data.get('sport_yakyi') != 'Не займаюся спортом':
        result += f"   Спорт: {user_data.get('sport_yakyi')}\n"
    result += "\n"
    
    result += "9️⃣ ПОТОЧНЕ ЛІКУВАННЯ:\n"
    result += f"   Ліки: {user_data.get('likuvannya', 'Не вказано')}\n"
    result += f"   Фізіотерапія/масаж: {user_data.get('fizioterapiya', 'Не вказано')}\n"
    
    result += "\n"
    result += "🔟 АНТРОПОМЕТРИЧНІ ДАНІ:\n"
    result += f"   Зріст: {user_data.get('zrist', 'Не вказано')} см\n"
    result += f"   Вага: {user_data.get('vaga', 'Не вказано')} кг\n"
    
    result += "\n" + "=" * 40
    
    # Додаємо контактну інформацію тільки для адміністраторів
    if for_admin:
        result += f"\n📱 Telegram: @{user_data.get('username', 'невідомий')}"
        result += f"\n🆔 User ID: {user_data.get('user_id', 'невідомий')}"
    
    return result

async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує анкету для підтвердження"""
    result = format_survey_result(context.user_data, for_admin=False)
    
    keyboard = [
        ['✅ Підтвердити'],
        ['✏️ Змінити дані'],
        ['❌ Скасувати']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "📋 ПЕРЕВІРТЕ ВАШІ ДАНІ:\n\n" + result + "\n\nВсе правильно?",
        reply_markup=reply_markup
    )
    return CONFIRM

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок розмови"""
    user = update.effective_user
    context.user_data.clear()  # Очищаємо попередні дані
    context.user_data['username'] = user.username or user.first_name
    context.user_data['user_id'] = user.id
    context.user_data['date'] = datetime.now().strftime('%d.%m.%Y')
    context.user_data['editing'] = False  # Прапорець режиму редагування
    
    logger.info(f"Користувач {user.first_name} (@{user.username}) розпочав анкетування. User ID: {user.id}")
    
    await update.message.reply_text(
        f"Вітаю, {user.first_name}! 👋\n\n"
        "Я допоможу вам заповнити анкету перед прийомом до мануального терапевта.\n\n"
        "Це займе приблизно 5 хвилин. Ваші відповіді допоможуть лікарю краще підготуватися до прийому.\n\n"
        "Натисніть /cancel щоб скасувати в будь-який момент.\n\n"
        "Почнемо! 📋\n\n"
        "Введіть, будь ласка, ваше ПІБ:"
    )
    return PIB

async def pib(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отримання ПІБ"""
    context.user_data['pib'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    await update.message.reply_text("Скільки вам років? (введіть число)")
    return VIK

async def vik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отримання віку"""
    context.user_data['vik'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Шия', 'Грудний відділ'],
        ['Поперек', 'Крижі'],
        ['Біль віддає у руку', 'Біль віддає у ногу']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "1️⃣ ДЕ САМЕ БОЛИТЬ?\n\n"
        "Оберіть одну або декілька зон (можете написати кілька через кому):",
        reply_markup=reply_markup
    )
    return DE_BOLIT

async def de_bolit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отримання локалізації болю"""
    context.user_data['de_bolit'] = update.message.text
    
    # Якщо в режимі редагування і немає віддачі, повертаємося до підтвердження
    if context.user_data.get('editing') and 'віддає' not in update.message.text.lower():
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    if 'віддає' in update.message.text.lower():
        await update.message.reply_text(
            "Опишіть детальніше, куди саме віддає біль:\n"
            "(наприклад: у праву руку до ліктя, у ліву ногу до коліна)"
        )
        return DE_BOLIT_DETALІ
    else:
        keyboard = [['Так', 'Ні']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Чи є оніміння, поколювання або слабкість?",
            reply_markup=reply_markup
        )
        return ОНІМІННЯ

async def de_bolit_detalі(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Деталі про віддачу болю"""
    context.user_data['de_bolit'] += f"\nДеталі: {update.message.text}"
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [['Так', 'Ні']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Чи є оніміння, поколювання або слабкість?",
        reply_markup=reply_markup
    )
    return ОНІМІННЯ

async def onіmіnnya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оніміння"""
    context.user_data['onіmіnnya'] = update.message.text
    
    # Якщо в режимі редагування і відповідь "Ні", повертаємося до підтвердження
    if context.user_data.get('editing') and update.message.text != 'Так':
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    if update.message.text == 'Так':
        await update.message.reply_text("Де саме? (опишіть локалізацію)")
        return ОНІМІННЯ_DE
    else:
        keyboard = [
            ['До 6 тижнів (гострий)'],
            ['6-12 тижнів (підгострий)'],
            ['Більше 3 місяців (хронічний)']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "2️⃣ КОЛИ ПОЯВИВСЯ БІЛЬ?",
            reply_markup=reply_markup
        )
        return KOLY_ZYAVYVSYA

async def onіmіnnya_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Локалізація оніміння"""
    context.user_data['onіmіnnya_de'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['До 6 тижнів (гострий)'],
        ['6-12 тижнів (підгострий)'],
        ['Більше 3 місяців (хронічний)']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "2️⃣ КОЛИ ПОЯВИВСЯ БІЛЬ?",
        reply_markup=reply_markup
    )
    return KOLY_ZYAVYVSYA

async def koly_zyavyvsya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тривалість болю"""
    context.user_data['koly_zyavyvsya'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [['Так', 'Ні']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Біль з'явився після травми, падіння або підйому ваги?",
        reply_markup=reply_markup
    )
    return TRAVMA

async def travma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Травма"""
    context.user_data['travma'] = update.message.text
    
    # Якщо в режимі редагування і відповідь "Ні", повертаємося до підтвердження
    if context.user_data.get('editing') and update.message.text != 'Так':
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    if update.message.text == 'Так':
        keyboard = [['Пропустити']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Що саме сталося? (опишіть ситуацію або натисніть 'Пропустити')",
            reply_markup=reply_markup
        )
        return TRAVMA_DETALІ
    else:
        keyboard = [
            ['Гострий', 'Ниючий', 'Прострілюючий'],
            ['Пекучий', 'Тиснучий'],
            ['Постійний', 'Періодичний']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "3️⃣ ОХАРАКТЕРИЗУЙТЕ БІЛЬ\n\n"
            "Оберіть один або декілька варіантів (можете написати через кому):",
            reply_markup=reply_markup
        )
        return KHARAKTER_BOLY

async def travma_detalі(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Деталі травми"""
    if update.message.text != 'Пропустити':
        context.user_data['travma_detalі'] = update.message.text
    else:
        context.user_data['travma_detalі'] = 'Не вказано'
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Гострий', 'Ниючий', 'Прострілюючий'],
        ['Пекучий', 'Тиснучий'],
        ['Постійний', 'Періодичний']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "3️⃣ ОХАРАКТЕРИЗУЙТЕ БІЛЬ\n\n"
        "Оберіть один або декілька варіантів (можете написати через кому):",
        reply_markup=reply_markup
    )
    return KHARAKTER_BOLY

async def kharakter_boly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Характер болю"""
    context.user_data['kharakter_boly'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9', '10']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Оцініть інтенсивність болю за шкалою від 0 до 10\n"
        "(0 - немає болю, 10 - максимальний біль):",
        reply_markup=reply_markup
    )
    return SHKALA_BOLY

async def shkala_boly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Шкала болю"""
    context.user_data['shkala_boly'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Сидіння', 'Стояння', 'Ходьба'],
        ['Нахили', 'Повороти'],
        ['Кашель/чхання', 'Нічний час'],
        ['Немає особливих факторів']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "4️⃣ ЩО ПОГІРШУЄ БІЛЬ?\n\n"
        "Оберіть один або декілька варіантів:",
        reply_markup=reply_markup
    )
    return POHIRSHUE

async def pohirshue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Що погіршує"""
    context.user_data['pohirshue'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Лежання', 'Рух'],
        ['Тепло', 'Холод', 'Ліки'],
        ['Немає полегшення']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "ЩО ПОЛЕГШУЄ БІЛЬ?\n\n"
        "Оберіть один або декілька варіантів:",
        reply_markup=reply_markup
    )
    return POLEHSHUE

async def polehshue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Що полегшує"""
    context.user_data['polehshue'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [['Так', 'Ні']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "5️⃣ ЧИ БУЛИ РАНІШЕ ПОДІБНІ ЕПІЗОДИ БОЛЮ В СПИНІ?",
        reply_markup=reply_markup
    )
    return RANISHI_EPIZODY

async def ranishi_epizody(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Попередні епізоди"""
    context.user_data['ranishi_epizody'] = update.message.text
    
    # Якщо в режимі редагування і відповідь "Ні", повертаємося до підтвердження
    if context.user_data.get('editing') and update.message.text != 'Так':
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    if update.message.text == 'Так':
        keyboard = [['Не лікував(ла)']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Як тоді лікували? (опишіть методи лікування або оберіть 'Не лікував(ла)')",
            reply_markup=reply_markup
        )
        return RANISHI_YAK_LIKUVALY
    else:
        keyboard = [
            ['Незрозуміла втрата ваги', 'Температура'],
            ['Онкологія в анамнезі'],
            ['Проблеми з сечовипусканням'],
            ['Проблеми з дефекацією'],
            ['Оніміння в промежині'],
            ['Різка слабкість кінцівки'],
            ['Немає таких симптомів']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "6️⃣ ЧЕРВОНІ ПРАПОРИ ⚠️\n\n"
            "Чи є у вас наступні симптоми?\n"
            "(оберіть всі, що є, або 'Немає таких симптомів'):",
            reply_markup=reply_markup
        )
        return CHERVONI_PRAPORY

async def ranishi_yak_likuvaly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Попереднє лікування"""
    context.user_data['ranishi_yak_likuvaly'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Незрозуміла втрата ваги', 'Температура'],
        ['Онкологія в анамнезі'],
        ['Проблеми з сечовипусканням'],
        ['Проблеми з дефекацією'],
        ['Оніміння в промежині'],
        ['Різка слабкість кінцівки'],
        ['Немає таких симптомів']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "6️⃣ ЧЕРВОНІ ПРАПОРИ ⚠️\n\n"
        "Чи є у вас наступні симптоми?\n"
        "(оберіть всі, що є, або 'Немає таких симптомів'):",
        reply_markup=reply_markup
    )
    return CHERVONI_PRAPORY

async def chervoni_prapory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Червоні прапори"""
    context.user_data['chervoni_prapory'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Остеопороз', 'Цукровий діабет'],
        ['Ревматичні захворювання'],
        ['Прийом стероїдів'],
        ['Немає супутніх захворювань']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "7️⃣ СУПУТНІ ЗАХВОРЮВАННЯ\n\n"
        "Оберіть всі, що є:",
        reply_markup=reply_markup
    )
    return SUPUTNI

async def suputni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Супутні захворювання"""
    context.user_data['suputni'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [
        ['Сидяча робота'],
        ['Фізична робота'],
        ['Займаюся спортом'],
        ['Мало рухаюсь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "8️⃣ РІВЕНЬ АКТИВНОСТІ / РОБОТА\n\n"
        "Оберіть найбільш підходящий варіант:",
        reply_markup=reply_markup
    )
    return AKTYVNIST

async def aktyvnist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рівень активності"""
    context.user_data['aktyvnist'] = update.message.text
    
    # Якщо в режимі редагування і немає спорту, повертаємося до підтвердження
    if context.user_data.get('editing') and 'спорт' not in update.message.text.lower():
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    if 'спорт' in update.message.text.lower():
        keyboard = [['Не займаюся спортом']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Яким спортом займаєтесь?",
            reply_markup=reply_markup
        )
        return SPORT_YAKYI
    else:
        keyboard = [['Не приймаю ліків']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "9️⃣ ПОТОЧНЕ ЛІКУВАННЯ\n\n"
            "Які ліки ви зараз приймаєте?\n"
            "(напишіть назви або оберіть 'Не приймаю ліків')",
            reply_markup=reply_markup
        )
        return LIKUVANNYA

async def sport_yakyi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Який спорт"""
    context.user_data['sport_yakyi'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [['Не приймаю ліків']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "9️⃣ ПОТОЧНЕ ЛІКУВАННЯ\n\n"
        "Які ліки ви зараз приймаєте?\n"
        "(напишіть назви або оберіть 'Не приймаю ліків')",
        reply_markup=reply_markup
    )
    return LIKUVANNYA

async def likuvannya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поточне лікування"""
    context.user_data['likuvannya'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    keyboard = [['Так', 'Ні']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Чи проходите зараз фізіотерапію, масаж або мануальну терапію?",
        reply_markup=reply_markup
    )
    return FIZIOTERAPIYA

async def fizioterapiya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Фізіотерапія"""
    context.user_data['fizioterapiya'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    # Запитуємо зріст
    await update.message.reply_text(
        "🔟 АНТРОПОМЕТРИЧНІ ДАНІ\n\n"
        "Введіть ваш зріст у сантиметрах:"
    )
    return ZRIST

async def zrist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Зріст"""
    context.user_data['zrist'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    await update.message.reply_text("Введіть вашу вагу в кілограмах:")
    return VAGA

async def vaga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вага"""
    context.user_data['vaga'] = update.message.text
    
    # Якщо в режимі редагування, повертаємося до підтвердження
    if context.user_data.get('editing'):
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    # Показуємо повний список відповідей (без персональної інформації для пацієнта)
    return await show_confirmation(update, context)

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Підтвердження або редагування"""
    if update.message.text == '✅ Підтвердити':
        # Відправляємо пацієнту (без персональної інформації)
        await update.message.reply_text(
            "✅ Дякую! Анкету заповнено успішно.\n\n"
            "Ваші дані відправлено лікарю. Очікуйте на підтвердження запису.\n\n"
            "Бажаєте заповнити анкету заново? Натисніть /start",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Відправляємо лікарям (з персональною інформацією)
        result = format_survey_result(context.user_data, for_admin=True)
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=result)
                    logger.info(f"Анкету відправлено адміністратору {admin_id}")
                except Exception as e:
                    logger.error(f"Помилка відправки адміністратору {admin_id}: {e}")
        else:
            logger.warning("ADMIN_IDS порожній! Анкету не відправлено жодному адміністратору.")
        
        # Зберігаємо в файл
        save_to_file(context.user_data)
        
        return ConversationHandler.END
        
    elif update.message.text == '✏️ Змінити дані':
        # Встановлюємо прапорець режиму редагування
        context.user_data['editing'] = True
        
        # Показуємо меню редагування
        keyboard = [
            ['👤 ПІБ', '📅 Вік'],
            ['📍 Локалізація болю', '🔔 Оніміння'],
            ['⏰ Коли появився біль', '💥 Травма'],
            ['💊 Характер болю', '📊 Інтенсивність'],
            ['⬆️ Що погіршує', '⬇️ Що полегшує'],
            ['🔄 Попередні епізоди', '⚠️ Червоні прапори'],
            ['🏥 Супутні захворювання', '🏃 Активність'],
            ['💊 Поточні ліки', '💆 Фізіотерапія'],
            ['📏 Зріст', '⚖️ Вага'],
            ['◀️ Назад до перевірки']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "✏️ Оберіть, що ви хочете змінити:",
            reply_markup=reply_markup
        )
        return EDIT_CHOICE
    else:
        await update.message.reply_text(
            "❌ Анкетування скасовано.\n\n"
            "Натисніть /start щоб почати заново.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def edit_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вибір поля для редагування"""
    choice = update.message.text
    
    if choice == '◀️ Назад до перевірки':
        # Вимикаємо режим редагування і повертаємось до підтвердження
        context.user_data['editing'] = False
        return await show_confirmation(update, context)
    
    elif choice == '👤 ПІБ':
        await update.message.reply_text(
            f"Поточне ПІБ: {context.user_data.get('pib')}\n\n"
            "Введіть нове ПІБ:"
        )
        return PIB
        
    elif choice == '📅 Вік':
        await update.message.reply_text(
            f"Поточний вік: {context.user_data.get('vik')}\n\n"
            "Введіть новий вік:"
        )
        return VIK
        
    elif choice == '📍 Локалізація болю':
        keyboard = [
            ['Шия', 'Грудний відділ'],
            ['Поперек', 'Крижі'],
            ['Біль віддає у руку', 'Біль віддає у ногу']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна локалізація: {context.user_data.get('de_bolit')}\n\n"
            "Оберіть нову локалізацію:",
            reply_markup=reply_markup
        )
        return DE_BOLIT
        
    elif choice == '🔔 Оніміння':
        keyboard = [['Так', 'Ні']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('onіmіnnya')}\n\n"
            "Чи є оніміння, поколювання або слабкість?",
            reply_markup=reply_markup
        )
        return ОНІМІННЯ
        
    elif choice == '⏰ Коли появився біль':
        keyboard = [
            ['До 6 тижнів (гострий)'],
            ['6-12 тижнів (підгострий)'],
            ['Більше 3 місяців (хронічний)']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('koly_zyavyvsya')}\n\n"
            "Коли появився біль?",
            reply_markup=reply_markup
        )
        return KOLY_ZYAVYVSYA
        
    elif choice == '💥 Травма':
        keyboard = [['Так', 'Ні']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('travma')}\n\n"
            "Біль з'явився після травми, падіння або підйому ваги?",
            reply_markup=reply_markup
        )
        return TRAVMA
        
    elif choice == '💊 Характер болю':
        keyboard = [
            ['Гострий', 'Ниючий', 'Прострілюючий'],
            ['Пекучий', 'Тиснучий'],
            ['Постійний', 'Періодичний']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('kharakter_boly')}\n\n"
            "Охарактеризуйте біль:",
            reply_markup=reply_markup
        )
        return KHARAKTER_BOLY
        
    elif choice == '📊 Інтенсивність':
        keyboard = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9', '10']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна оцінка: {context.user_data.get('shkala_boly')}\n\n"
            "Оцініть інтенсивність болю (0-10):",
            reply_markup=reply_markup
        )
        return SHKALA_BOLY
        
    elif choice == '⬆️ Що погіршує':
        keyboard = [
            ['Сидіння', 'Стояння', 'Ходьба'],
            ['Нахили', 'Повороти'],
            ['Кашель/чхання', 'Нічний час'],
            ['Немає особливих факторів']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('pohirshue')}\n\n"
            "Що погіршує біль?",
            reply_markup=reply_markup
        )
        return POHIRSHUE
        
    elif choice == '⬇️ Що полегшує':
        keyboard = [
            ['Лежання', 'Рух'],
            ['Тепло', 'Холод', 'Ліки'],
            ['Немає полегшення']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('polehshue')}\n\n"
            "Що полегшує біль?",
            reply_markup=reply_markup
        )
        return POLEHSHUE
        
    elif choice == '🔄 Попередні епізоди':
        keyboard = [['Так', 'Ні']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('ranishi_epizody')}\n\n"
            "Чи були раніше подібні епізоди болю в спині?",
            reply_markup=reply_markup
        )
        return RANISHI_EPIZODY
        
    elif choice == '⚠️ Червоні прапори':
        keyboard = [
            ['Незрозуміла втрата ваги', 'Температура'],
            ['Онкологія в анамнезі'],
            ['Проблеми з сечовипусканням'],
            ['Проблеми з дефекацією'],
            ['Оніміння в промежині'],
            ['Різка слабкість кінцівки'],
            ['Немає таких симптомів']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('chervoni_prapory')}\n\n"
            "Чи є тривожні симптоми?",
            reply_markup=reply_markup
        )
        return CHERVONI_PRAPORY
        
    elif choice == '🏥 Супутні захворювання':
        keyboard = [
            ['Остеопороз', 'Цукровий діабет'],
            ['Ревматичні захворювання'],
            ['Прийом стероїдів'],
            ['Немає супутніх захворювань']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('suputni')}\n\n"
            "Супутні захворювання:",
            reply_markup=reply_markup
        )
        return SUPUTNI
        
    elif choice == '🏃 Активність':
        keyboard = [
            ['Сидяча робота'],
            ['Фізична робота'],
            ['Займаюся спортом'],
            ['Мало рухаюсь']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('aktyvnist')}\n\n"
            "Рівень активності / робота:",
            reply_markup=reply_markup
        )
        return AKTYVNIST
        
    elif choice == '💊 Поточні ліки':
        keyboard = [['Не приймаю ліків']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('likuvannya')}\n\n"
            "Які ліки приймаєте?",
            reply_markup=reply_markup
        )
        return LIKUVANNYA
        
    elif choice == '💆 Фізіотерапія':
        keyboard = [['Так', 'Ні']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            f"Поточна відповідь: {context.user_data.get('fizioterapiya')}\n\n"
            "Чи проходите зараз фізіотерапію, масаж або мануальну терапію?",
            reply_markup=reply_markup
        )
        return FIZIOTERAPIYA
        
    elif choice == '📏 Зріст':
        await update.message.reply_text(
            f"Поточний зріст: {context.user_data.get('zrist', 'Не вказано')} см\n\n"
            "Введіть новий зріст у сантиметрах:"
        )
        return ZRIST
        
    elif choice == '⚖️ Вага':
        await update.message.reply_text(
            f"Поточна вага: {context.user_data.get('vaga', 'Не вказано')} кг\n\n"
            "Введіть нову вагу в кілограмах:"
        )
        return VAGA

def save_to_file(user_data):
    """Зберігає результати в файл"""
    try:
        filename = f"surveys/survey_{user_data.get('user_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        import os
        os.makedirs('surveys', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(format_survey_result(user_data, for_admin=True))
        
        logger.info(f"Анкету збережено: {filename}")
    except Exception as e:
        logger.error(f"Помилка збереження файлу: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скасування розмови"""
    await update.message.reply_text(
        "❌ Анкетування скасовано.\n\n"
        "Натисніть /start щоб почати заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    """Запуск бота"""
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не встановлено в змінних оточення!")
        print("❌ Помилка: TELEGRAM_BOT_TOKEN не знайдено!")
        print("Встановіть змінну оточення TELEGRAM_BOT_TOKEN перед запуском бота.")
        return
    
    if not ADMIN_IDS:
        logger.warning("⚠️ УВАГА: ADMIN_IDS порожній!")
        print("⚠️ УВАГА: ADMIN_IDS порожній!")
        print("Анкети не будуть відправлятися адміністраторам.\n")
    
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PIB: [MessageHandler(filters.TEXT & ~filters.COMMAND, pib)],
            VIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, vik)],
            DE_BOLIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, de_bolit)],
            DE_BOLIT_DETALІ: [MessageHandler(filters.TEXT & ~filters.COMMAND, de_bolit_detalі)],
            ОНІМІННЯ: [MessageHandler(filters.TEXT & ~filters.COMMAND, onіmіnnya)],
            ОНІМІННЯ_DE: [MessageHandler(filters.TEXT & ~filters.COMMAND, onіmіnnya_de)],
            KOLY_ZYAVYVSYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, koly_zyavyvsya)],
            TRAVMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, travma)],
            TRAVMA_DETALІ: [MessageHandler(filters.TEXT & ~filters.COMMAND, travma_detalі)],
            KHARAKTER_BOLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, kharakter_boly)],
            SHKALA_BOLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, shkala_boly)],
            POHIRSHUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pohirshue)],
            POLEHSHUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, polehshue)],
            RANISHI_EPIZODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ranishi_epizody)],
            RANISHI_YAK_LIKUVALY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ranishi_yak_likuvaly)],
            CHERVONI_PRAPORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, chervoni_prapory)],
            SUPUTNI: [MessageHandler(filters.TEXT & ~filters.COMMAND, suputni)],
            AKTYVNIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, aktyvnist)],
            SPORT_YAKYI: [MessageHandler(filters.TEXT & ~filters.COMMAND, sport_yakyi)],
            LIKUVANNYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, likuvannya)],
            FIZIOTERAPIYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, fizioterapiya)],
            ZRIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, zrist)],
            VAGA: [MessageHandler(filters.TEXT & ~filters.COMMAND, vaga)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
            EDIT_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_choice)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    logger.info("🤖 Бот запущено!")
    print("🤖 Бот запущено! Натисніть Ctrl+C для зупинки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()