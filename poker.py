import os
import re
import cv2
import numpy as np
import pyautogui as pag
import pytesseract as ts
from PIL import Image

ORIGINAL_IM_PATH = 'test.png'
GRAY_IM_PATH = 'gray.png'
STACK_OPPONENT_OFFSET = -100, 0, 0, 60
STACK_USER_OFFSET = 0, 0, 200, 60
BET_OPPONENT_OFFSET = 50, 70, 130, 100
BET_USER_OFFSET = 50, -100, 200, -60
DATA_FILENAME = 'extracted_data.txt'
OPPONENT_REFERENCE_PATH = 'opponent_reference.png'
USER_REFERENCE_PATH = 'user_reference.png'

def create_new_file(filename):
    """
    Эмуляция создания нового текстового файла с помощью pyautogui.
    :param filename: имя создаваемого файла.
    """
    if os.path.isfile(filename):
        os.remove(filename)
    pag.hotkey('ctrl', 'n')
    pag.hotkey('ctrl', 's')
    pag.write(filename, interval=0.1)
    pag.press('enter')

def create_gray_image():
    """
    Создание черно-белой версии оригинального изображения.
    Это нужно для корректной работы pytesseract.
    """

    image = cv2.imread(ORIGINAL_IM_PATH)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(GRAY_IM_PATH, gray)

def show_image(im_path: str):
    """
    Открыть изображение im_path.
    :param im_path: Путь к изображению. 
    :returns: ~PIL.Image.Image.
    """

    im = Image.open(im_path)
    im.show()
    return im

def get_stack(reference_im_path: str, opponent = True) -> str:
    """
    Получить значение стека.
    Поиск производится путем применения pytesseract.image_to_string 
    ко всему изображению.
    :param reference_im_path: путь к изображению-ориентиру (аватарка игрока). 
        Считаем, что положение значения ставки на изображении
        относительно ориентира не меняется.
    :param opponent: оппонент. Необходимо для определения вектора сдвига 
        относительно ориентира при поиске значения стека. 
    :returns: значение стека.
    """

    reference_coords = pag.locateOnScreen(reference_im_path)
    stack_coords = np.repeat([reference_coords[:2]], 2, 0).reshape(-1)
    stack_coords += STACK_OPPONENT_OFFSET if opponent else STACK_USER_OFFSET
    stack_im = pag.screenshot().crop(stack_coords)
    stack = ts.image_to_string(stack_im)
    stack = ''.join(re.findall('[^\w]\d{1,}', stack))
    stack = stack.replace(' ', '').replace('\n', '')
    return stack

def get_bet(reference_im_path: str, opponent = True) -> str:
    """
    Получение значения ставки.
    Поиск производится путем применения pytesseract.image_to_string 
    ко всему изображению.
    :param reference_im_path: путь к изображению-ориентиру (аватарка игрока). 
        Считаем, что положение значения ставки на изображении
        относительно ориентира не меняется.
    :param opponent: оппонент. Необходимо для определения вектора сдвига 
        относительно ориентира при поиске значения банка. 
    :returns: значение банка.
    """

    reference_coords = pag.locateOnScreen(reference_im_path)
    stack_coords = np.repeat([reference_coords[:2]], 2, 0).reshape(-1)
    stack_coords += BET_OPPONENT_OFFSET if opponent else BET_USER_OFFSET
    image = pag.screenshot().crop(stack_coords)
    bet = ts.image_to_string(image, lang='rus')
    bet = bet.replace('\n', '')
    return bet

def get_bank(gray_image) -> str:
    """
    Получение значения банка.
    Поиск производится путем применения pytesseract.image_to_string 
    ко всему изображению.
    :param gray_image: ~PIL.Image.Image. 
    :returns: значение банка.
    """
    
    text = ts.image_to_string(gray_image, lang='rus')
    bank = re.search('Банк:[" "]*\d*', text)[0]
    bank = re.search('\d{1,}', bank)[0]
    return bank

def make_note(string):
    """
    Эмуляция записи в текстовый файл строки string с помощью pyautogui.
    При выполнении окно с текстовым файлом должно быть открыто вторым по счету. 
    То есть при переключении alt+tab внимание должно переключиться на это окно. 
    :param string: строка для записи.
    """
    pag.hotkey('alt', 'tab')
    pag.write(string + '\n', interval=0.1)
    pag.hotkey('alt', 'tab')

if __name__ == '__main__':
    ts.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    create_new_file(DATA_FILENAME)
    create_gray_image()
    gray_image = show_image(GRAY_IM_PATH)

    opponent_bet = get_bet(OPPONENT_REFERENCE_PATH, opponent=True)
    make_note("Opponent's bet: " + opponent_bet)

    user_bet = get_bet(USER_REFERENCE_PATH, opponent=False)
    make_note('My bet: ' + user_bet)

    opponent_stack = get_stack(OPPONENT_REFERENCE_PATH, opponent=True)
    make_note("Opponent's stack: " + opponent_stack)

    user_stack = get_stack(USER_REFERENCE_PATH, opponent=False)
    make_note('My stack: ' + user_stack)

    bank = get_bank(gray_image)
    make_note('Bank: ' + bank)

    pag.hotkey('alt', 'tab')
    pag.hotkey('ctrl', 's')
