import telebot
from telebot import types
from PIL import Image, ImageDraw, ImageFont
import io
import os
import random

token = "2126250120:AAFVdLo84khXaNDWEOrybpWHI8SuLJLISM0"

bot = telebot.TeleBot(token)

main_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
main_markup_button1 = types.KeyboardButton("Случайное фото")
main_markup_button2 = types.KeyboardButton("Поиск")
main_markup_button3 = types.KeyboardButton("Добавить")
main_markup_button4 = types.KeyboardButton("Создать")
main_markup.add(
    main_markup_button1,
    main_markup_button2,
    main_markup_button3,
    main_markup_button4)

create_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
create_markup_button1 = types.KeyboardButton("Фото из архива")
create_markup_button2 = types.KeyboardButton("Отмена")
create_markup.add(create_markup_button1, create_markup_button2)

cancel_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
cancel_markup_button = types.KeyboardButton("Отмена")
cancel_markup.add(cancel_markup_button)

back_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
back_markup_button = types.KeyboardButton("Назад")
back_markup.add(back_markup_button)

downloaded_files = {}
chosen_photo = {}

bot_description = "I'm a cat's bot, meow!"


@bot.message_handler(func=lambda message: message.text == "Случайное фото", content_types=['text'])
def send_random_photo(message):  # Пользователь нажал кнопку Случайное фото
    # Если нет папки photos, то создаем её
    if not os.path.exists("./photos"):
        os.mkdir("./photos")
    if len(os.listdir("./photos")) > 0:  # Если папка photos не пустая
        # Отправляем рандомное изображение
        bot.send_photo(
            message.chat.id,
            photo=open(os.path.join("./photos", random.choice(os.listdir("./photos"))), 'rb'))
    else:
        # Если нет изображений в хранилище
        bot.send_message(message.chat.id, "Нет фото в архиве.")


@bot.message_handler(func=lambda message: message.text == "Поиск", content_types=['text'])
def search_photo(message):  # Пользователь нажал кнопку Поиск
    bot.send_message(
        message.chat.id,
        "Для поиска используйте ключевые слова. "
        "Например: \"веселый\", \"негодующий\", \"осуждающий\", \"забавный\", \"ъуъ\"",
        reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, search_result)


def search_result(message):
    if message.text is None:  # В сообщении нет текста
        bot.send_message(
            message.chat.id,
            "Для поиска используйте ключевые слова. "
            "Например: \"веселый\", \"негодующий\", \"осуждающий\", \"забавный\", \"ъуъ\"")
        bot.register_next_step_handler(message, search_result)
        return
    key_words = message.text.split(" ")  # Создаем список ключевых слов из входной строки
    if not os.path.exists("./photos"):
        os.mkdir("./photos")
    images = os.listdir("./photos")  # Получаем список файлов в папке изображений
    for image_name in images:
        for key_word in key_words:
            if key_word.lower() in image_name:  # Ищем ключевые слова в названии изображения
                bot.send_photo(
                    message.chat.id,
                    photo=open(os.path.join("./photos", image_name), 'rb'),
                    reply_markup=main_markup)
                return
    # Изображения не найдены
    bot.send_message(
        message.chat.id,
        "Изображения по заданным ключевым словам не найдены.",
        reply_markup=main_markup)


@bot.message_handler(func=lambda message: message.text == "Добавить", content_types=['text'])
def add_photo(message):  # Пользователь нажал кнопку Добавить
    bot.send_message(
        message.chat.id,
        "Загрузите фотографию или нажмите кнопку отмена.",
        reply_markup=cancel_markup)
    bot.register_next_step_handler(message, photo_upload)


def photo_upload(message):
    if message.text is not None and message.text == "Отмена":
        # Пользователь нажал кпопку отмена, возвращаемся в главное меню
        bot.send_message(message.chat.id, "Операция отменена.", reply_markup=main_markup)
        return
    if message.photo is None:
        # Если нет изображения в сообщении, то просим пользователя загрузить изображение еще раз
        bot.send_message(message.chat.id, "Загрузите фотографию или нажмите кнопку отмена.")
        bot.register_next_step_handler(message, photo_upload)
        return
    # Если пользователь загрузил изображение
    file_info = bot.get_file(message.photo[-1].file_id)  # Получаем данные изображения
    downloaded_files[message.chat.id] = bot.download_file(file_info.file_path)  # Скачиваем изображение

    # Просим пользователя описать изображение
    bot.send_message(message.chat.id, "Опишите фотографию.", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, ask_description)


def ask_description(message):  # Когда пользователь описывает изображение
    if message.text is None:
        # Если пользователь отправил не текст, то просим его описать изображение текстом
        bot.send_message(message.chat.id, "Опишите фотографию текстом.")
        bot.register_next_step_handler(message, ask_description)
        return
    if message.text == "Отмена":
        # Пользователь нажал кнопку отмена, возвращаемся в главное меню
        downloaded_files.pop(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена.", reply_markup=main_markup)
        return

    # Если нет папки photos, то создаем её
    if not os.path.exists("./photos"):
        os.mkdir("./photos")
    # Имя файла
    filepath = f"./photos/{message.text.lower()}.jpg"

    # Записываем файл на диск
    with open(filepath, 'wb') as new_file:
        new_file.write(downloaded_files[message.chat.id])

    bot.send_message(message.chat.id, "Фотография сохранена", reply_markup=main_markup)


@bot.message_handler(func=lambda message: message.text == "Создать", content_types=['text'])
def create_photo(message):  # Пользователь нажал кнопку Создать
    bot.send_message(
        message.chat.id,
        "Загрузите фотографию, выберите фото из архива или нажмите кнопку отмена.",
        reply_markup=create_markup)
    bot.register_next_step_handler(message, ask_photo)


def ask_photo(message):  # Пользователь отправляет фотографию
    if message.photo is None:
        if message.text is not None:
            if message.text == "Отмена":
                # Пользователь нажал кнопку отмена, выходим в главное меню
                bot.send_message(message.chat.id, "Операция отменена.", reply_markup=main_markup)
                return
            if message.text == "Фото из архива":
                # Пользователь нажал кнопку Фото из архива, переходим к поиску фото
                bot.send_message(
                    message.chat.id,
                    "Для поиска используйте ключевые слова. "
                    "Например: \"веселый\", \"негодующий\", \"осуждающий\", \"забавный\", \"ъуъ\"",
                    reply_markup=back_markup)
                bot.register_next_step_handler(message, search_photo_for_choose)
                return
        # Пользователь не отправил изображение и не нажал никаких кнопок
        bot.send_message(message.chat.id, "Загрузите фотографию, выберите фото из архива или нажмите кнопку отмена.")
        bot.register_next_step_handler(message, ask_photo)
        return
    # Получаем информацию о файле и скачиваем его
    file_info = bot.get_file(message.photo[-1].file_id)
    chosen_photo[message.chat.id] = bot.download_file(file_info.file_path)
    # Спрашиваем пользователя о тексте
    bot.send_message(
        message.chat.id,
        "Файл выбран. Какой текст добавить на изображение?",
        reply_markup=types.ReplyKeyboardRemove(),
        reply_to_message_id=message.id)
    bot.register_next_step_handler(message, ask_text)


def search_photo_for_choose(message):  # Пользователь отправил ключевые слова для поиска
    if message.text is None:
        # Если пользователь не написал текст, то просим его еще раз написать.
        bot.send_message(
            message.chat.id,
            "Для поиска используйте ключевые слова. "
            "Например: \"веселый\", \"негодующий\", \"осуждающий\", \"забавный\", \"ъуъ\"")
        bot.register_next_step_handler(message, search_photo_for_choose)
        return
    if message.text == "Назад":
        # Пользователь нажал кнопку назад, возвращаемся к загрузке изображения
        bot.send_message(
            message.chat.id,
            "Загрузите фотографию, выберите фото из архива или нажмите кнопку отмена.",
            reply_markup=create_markup)
        bot.register_next_step_handler(message, ask_photo)
        return
    key_words = message.text.split(" ")  # Создаем список ключевых слов из входной строки
    # Если нет папки photos, то создаем её
    if not os.path.exists("./photos"):
        os.mkdir("./photos")
    images = os.listdir("./photos")  # Получаем список файлов в папке photos
    for image_name in images:
        for key_word in key_words:
            if key_word.lower() in image_name:  # Ищем ключевые слова в названии изображения
                # Создаем кнопку Выбрать для изображения
                photo_markup = types.InlineKeyboardMarkup()
                photo_markup_button = types.InlineKeyboardButton("Выбрать", callback_data=f"choose|{image_name}")
                photo_markup.add(photo_markup_button)
                # Отправляем найденное изображение
                bot.send_photo(
                    message.chat.id,
                    photo=open(os.path.join("./photos", image_name), 'rb'),
                    reply_markup=photo_markup)
                bot.register_next_step_handler(message, search_photo_for_choose)
                return
    # Изображения не найдены
    bot.send_message(
        message.chat.id,
        "Изображения по заданным ключевым словам не найдены.")
    bot.register_next_step_handler(message, search_photo_for_choose)


@bot.callback_query_handler(func=lambda call: call.data.split("|")[0] == "choose")
def image_choose_callback_query(call):  # Когда пользователь нажал кнопку Выбрать под изображением
    bot.answer_callback_query(call.id)
    filename = call.data.split("|")[1]  # Получаем имя изображения
    # Если нет папки photos, то создаем её
    if not os.path.exists("./photos"):
        os.mkdir("./photos")
    if filename in os.listdir("./photos"):  # Проверяем наличие файла в папке
        image = Image.open(os.path.join("./photos", filename))  # Считываем изображение
        buffer = io.BytesIO()  # Создаем временный буфер
        image.save(buffer, format='JPEG')  # Записываем изображение в буфер
        # Сохраняем в оперативной памяти для данного пользователя выбранное изображение
        chosen_photo[call.message.chat.id] = buffer.getvalue()
        # Отправляем сообщение, что изображение выбрано
        bot.send_message(
            call.from_user.id,
            "Файл выбран. Какой текст добавить на изображение?",
            reply_markup=types.ReplyKeyboardRemove(),
            reply_to_message_id=call.message.id)
        bot.clear_step_handler(call.message)
        bot.register_next_step_handler(call.message, ask_text)
    else:
        # Если пользователь выбрал файл который не существует
        bot.send_message(call.from_user.id, "Файл не существует.")


def ask_text(message):  # Пользователь отправил текст, который должен быть на изображении
    if message.text is None:
        # В сообщениии нет текста
        bot.send_message(
            message.chat.id,
            "Какой текст добавить на изображение?")
        bot.register_next_step_handler(message, search_photo_for_choose)
        return

    # Проверка на присутствие изображения в оперативной памяти
    if message.chat.id in chosen_photo.keys():
        buffer = io.BytesIO()  # Создаем временный буфер
        buffer.write(chosen_photo[message.chat.id])  # Записываем в буфер выбранное изображение
        image = Image.open(buffer)  # Считываем изображение из буфера
        drawer = ImageDraw.Draw(image)  # Создаем из изображения объект для рисования
        font = ImageFont.truetype("arial.ttf", int(20 * image.width / 300))  # Считываем данные шрифта
        text_size = drawer.multiline_textsize(message.text, font=font)  # Вычисляем размер текста
        # Рисуем текст на изображении
        drawer.multiline_text(
            (image.width / 2, image.height - 20 - int(text_size[1]/2)),
            message.text,
            font=font,
            fill='white',
            anchor='mm')
        buffer = io.BytesIO()  # Создаем временный буфер
        image.save(buffer, format='JPEG')  # Сохраняем изображение в буфер
        # Отправляем готовое изображение пользователю
        bot.send_photo(message.chat.id, photo=buffer.getvalue(), reply_markup=main_markup)
        # Удаляем изображение из оперативной памяти
        chosen_photo.pop(message.chat.id)
    else:
        # Если изображение было удалено из оперативной памяти
        bot.send_message(message.chat.id, "Изображение не выбрано.", reply_markup=main_markup)


@bot.message_handler()
def start_handler(message):
    # Бот отвечает своим описанием на любые сообщения кроме команд
    bot.send_message(message.chat.id, bot_description, reply_markup=main_markup)


def start_bot():  # Запуск бот
    bot.polling()


if __name__ == '__main__':
    start_bot()
