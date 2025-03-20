import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Настройка логирования для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start: приветствует пользователя и запускает процесс
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["started"] = True
    # Сбрасываем данные викторины, если они есть
    context.user_data.pop("target_number", None)
    text = (
        "Привет! Я интерактивный бот для обучения разработанный студентами КГПК!.\n\n"
        "Нажми на кнопку ниже, чтобы начать тест бота."
    )
    keyboard = [
        [InlineKeyboardButton("Начать", callback_data='start_interaction')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# Обработчик нажатия кнопок (callback_query)
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Отвечаем на callback, чтобы убрать "часики"
    if query.data == 'start_interaction':
        await query.edit_message_text(
            text="Отлично, давай начнем!\n"
                 "Напиши /quiz чтобы начать викторину (угадай число от 1 до 10) или /help для справки."
        )

# Команда /help: выводит список доступных команд и подробное описание работы скрипта с аналитическим разбором.
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Доступные команды:\n"
        "/start - инициализирует работу бота и активирует пользовательскую сессию.\n"
        "/quiz - запускает викторину, в которой бот генерирует случайное число от 1 до 10 и ожидает, что пользователь угадает его.\n"
        "/help - выводит эту справку с подробным описанием логики работы.\n\n"
        "Аналитическое описание логики работы:\n"
        "1. Активация сессии (/start):\n"
        "   - При вызове команды /start бот сохраняет информацию в `context.user_data`, что позволяет отслеживать, что сессия начата.\n"
        "   - Это необходимо для того, чтобы не позволять выполнять команды, требующие инициализации, если пользователь еще не активировал бота.\n\n"
        "2. Запуск викторины (/quiz):\n"
        "   - После проверки, что сессия активна, бот генерирует случайное число от 1 до 10 с помощью функции, подобной `random.randint(1, 10)`.\n"
        "   - Загаданное число сохраняется в `context.user_data` (например, по ключу \"target_number\"), что позволяет в последующих сообщениях сравнивать ответ пользователя с загаданным числом.\n\n"
        "3. Обработка ответов пользователя:\n"
        "   - Каждое входящее текстовое сообщение обрабатывается обработчиком, который сначала проверяет, активна ли сессия (/start), а затем – запущена ли викторина.\n"
        "   - Если викторина активна, бот пытается преобразовать текст в число и сравнивает его с загаданным значением.\n"
        "   - В зависимости от результата бот сообщает, что загаданное число больше или меньше, или поздравляет при совпадении.\n\n"
        "Эта структура демонстрирует использование асинхронных функций, управления состоянием пользователя через `context.user_data` и обработки команд и сообщений с помощью библиотеки python-telegram-bot."
    )
    await update.message.reply_text(text)

# Команда /quiz: запускает викторину с угадыванием числа
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("started"):
        await update.message.reply_text("Пожалуйста, сначала введите команду /start")
        return
    # Запускаем викторину: бот загадывает число от 1 до 10
    target = random.randint(1, 10)
    context.user_data["target_number"] = target
    await update.message.reply_text(
        "Я загадал число от 1 до 10. Попробуйте угадать его, отправив свой ответ."
    )

# Обработчик текстовых сообщений: проверяет, правильно ли угадано число, или информирует о порядке работы бота
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("started"):
        await update.message.reply_text("Пожалуйста, начните с команды /start")
        return

    # Если викторина активна, проверяем ответ
    if "target_number" in context.user_data:
        try:
            guess = int(update.message.text)
        except ValueError:
            await update.message.reply_text("Введите, пожалуйста, число от 1 до 10.")
            return

        target = context.user_data["target_number"]
        if guess == target:
            await update.message.reply_text("Поздравляю, вы угадали число!")
            # Завершаем викторину, удаляя загаданное число
            context.user_data.pop("target_number", None)
        elif guess < target:
            await update.message.reply_text("Мое число больше. Попробуйте еще раз.")
        else:
            await update.message.reply_text("Мое число меньше. Попробуйте еще раз.")
    else:
        # Если викторина не запущена, информируем пользователя
        await update.message.reply_text(
            "В данный момент викторина не запущена.\n"
            "Введите /quiz чтобы начать или /help для получения информации."
        )

def main():
    # Замените 'YOUR_TOKEN_HERE' на токен вашего бота
    application = Application.builder().token("7603833756:AAFJ5f0C7PfDXo_f1LBJ8nodnmVFeWjhygQ").build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    # Запускаем бота в режиме polling
    application.run_polling()

if __name__ == '__main__':
    main()
