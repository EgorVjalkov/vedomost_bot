from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_keyboard(keyboard, keys_list, rows=None):
    for key in keys_list:
        keyboard.add(KeyboardButton(text=key))
    keyboard.add(KeyboardButton(text='завершаю'))
    if rows:
        keyboard.adjust(rows)
    else:
        keyboard.adjust(4)
    return keyboard.as_markup(resize_keyboard=True)


def get_filling_inline(inline, cat_name, cat_keys, end_key):
    if cat_keys:
        keys = [InlineKeyboardButton(text=str(i),
                                     callback_data=f'fill_{cat_name}_{i}')
                for i in cat_keys]
        inline.row(*keys)

    inline.row(InlineKeyboardButton(text='не мог', callback_data=f'fill_{cat_name}_не мог'),
               InlineKeyboardButton(text='забыл', callback_data=f'fill_{cat_name}_забыл'),
               InlineKeyboardButton(text=end_key, callback_data=f'fill_{cat_name}_{end_key}'))
    # надо красивое тут сдлать!
    return inline
