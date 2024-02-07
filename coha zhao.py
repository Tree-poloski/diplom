import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math

# Коефіцієнти косинусного перетворення та ентропії
cos_t = [
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [0.9807853, 0.8314696, 0.5555702, 0.1950903, -0.1950903, -0.5555702, -0.8314696, -0.9807853],
    [0.9238795, 0.3826834, -0.3826834, -0.9238795, -0.9238795, -0.3826834, 0.3826834, 0.9238795],
    [0.8314696, -0.1950903, -0.9807853, -0.5555702, 0.5555702, 0.9807853, 0.1950903, -0.8314696],
    [0.7071068, -0.7071068, -0.7071068, 0.7071068, 0.7071068, -0.7071068, -0.7071068, 0.7071068],
    [0.5555702, -0.9807853, 0.1950903, 0.8314696, -0.8314696, -0.1950903, 0.9807853, -0.5555702],
    [0.3826834, -0.9238795, 0.9238795, -0.3826834, -0.3826834, 0.9238795, -0.9238795, 0.3826834],
    [0.1950903, -0.5555702, 0.8314696, -0.9807853, 0.9807853, -0.8314696, 0.5555702, -0.1950903]
]

e = [
    [0.125, 0.176777777, 0.176777777, 0.176777777, 0.176777777, 0.176777777, 0.176777777, 0.176777777],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
]

# Функція для вставки текстового повідомлення в зображення
def insert_message(image, text):
    dct = [[0] * 8 for _ in range(8)]  # Ініціалізація коефіцієнтів ДКП
    k = 0
    l = 0
    temp = [[{'red': 0, 'green': 0, 'blue': 0}] * 8 for _ in range(8)]  # Ініціалізація тимчасової матриці для пікселів
    
    # Прохід по зображенню блоками 8x8
    for i in range(0, image.width, 8):
        for j in range(0, image.height, 8):
            if l >= len(text) * 8:
                break
            for x in range(8):
                for y in range(8):
                    pixel = image.getpixel((j + x, i + y))
                    temp[x][y] = {'red': pixel[0], 'green': pixel[1], 'blue': pixel[2]}  # Зчитування пікселів
                    
            dct = dct_transform(dct, temp)  # Виконання ДКП
            k = abs(dct[3][4]) - abs(dct[4][3])  # Розрахунок різниці
            
            # Вставка біта повідомлення в коефіцієнт ДКП
            if get_bit(text, l):
                if k <= 25:
                    dct[3][4] = dct[4][3] + 150 if dct[3][4] >= 0 else -1 * (dct[4][3] + 150)
            else:
                if k >= -25:
                    dct[4][3] = dct[3][4] + 150 if dct[4][3] >= 0 else -1 * (dct[3][4] + 150)
                    
            xt = [row[:] for row in temp]  # Копіювання тимчасової матриці
            temp = idct_transform(dct, temp)  # Виконання зворотного ДКП
            
            # Збереження відредагованих пікселів у зображенні
            for x in range(8):
                for y in range(8):
                    image.putpixel((j + x, i + y), (temp[x][y]['red'], temp[x][y]['green'], temp[x][y]['blue']))
                    
            l += 1  # Лічильник бітів
            
    image.save('test_encrypted.jpg')  # Збереження зображення з внесеним текстом
    return image

# Функція для читання текстового повідомлення з зображення
def read_message(image):
    k = 0
    out = []
    l = 0
    a = ''
    p = 0
    b = 0
    dct = [[0] * 8 for _ in range(8)]  # Ініціалізація коефіцієнтів ДКП
    temp = [[{'red': 0, 'green': 0, 'blue': 0}] * 8 for _ in range(8)]  # Ініціалізація тимчасової матриці для пікселів
    
    # Прохід по зображенню блоками 8x8
    for i in range(0, image.width, 8):
        for j in range(0, image.height, 8):
            for x in range(8):
                for y in range(8):
                    pixel = image.getpixel((j + x, i + y))
                    temp[x][y] = {'red': pixel[0], 'green': pixel[1], 'blue': pixel[2]}  # Зчитування пікселів
                    
            l += 1  # Лічильник бітів
            dct = dct_transform(dct, temp)  # Виконання ДКП
            k = abs(dct[3][4]) - abs(dct[4][3])  # Розрахунок різниці
            
            # Визначення біту повідомлення на основі різниці коефіцієнтів
            if k >= 25:
                a = 1
            elif k <= -25:
                a = 0
            else:
                a = -1
                break
            
            b |= a << p  # Зчитування біта в байт
            
            if p == 7:
                out.append(chr(b))  # Додавання символу в результуючий текст
                b = 0  # Скидання байту
                
            p = (p + 1) if p < 7 else 0  # Зміна позиції біта
            
        if a == -1:
            break
            
    return ''.join(out)  # Повернення текстового повідомлення

# Функція для виконання косинусного перетворення ДКП
def dct_transform(dct, arr):
    for i in range(8):
        for j in range(8):
            temp = 0.0
            for x in range(8):
                for y in range(8):
                    temp += cos_t[i][x] * cos_t[j][y] * arr[x][y]['blue']  # Сумування коефіцієнтів
            dct[i][j] = e[i][j] * temp  # Застосування ентропії
            
    return dct

# Функція для виконання зворотного косинусного перетворення ДКП
def idct_transform(dct, arr):
    for i in range(8):
        for j in range(8):
            temp = 0
            for x in range(8):
                for y in range(8):
                    temp += dct[x][y] * cos_t[x][i] * cos_t[y][j] * e[x][y]  # Сумування коефіцієнтів
            arr[i][j]['blue'] = min(255, max(0, round(temp)))  # Обмеження значень до діапазону [0, 255]
            
    return arr

# Функція для отримання біту з тексту
def get_bit(text, pos):
    return True if ord(text[pos // 8]) & (1 << pos % 8) > 0 else False

# Функція для вибору зображення з комп'ютера
def choose_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global image
        image = Image.open(file_path)
        # image.thumbnail((300, 300))  # Зменшуємо розмір зображення для відображення на вікні
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo

# Функція для шифрування повідомлення
def encrypt_message(image):
    text = entry.get()
    if text:
        insert_message(image, text)
        messagebox.showinfo("Інформація", "Повідомлення зашифровано і збережено!")

# Створення та розміщення елементів у вікні
root = tk.Tk()
root.title("Шифрування повідомлення в зображенні")

choose_button = tk.Button(root, text="Обрати зображення", command=choose_image)
choose_button.pack(pady=10)

image_label = tk.Label(root)
image_label.pack()

entry = tk.Entry(root, width=50)
entry.pack(pady=10)

encrypt_button = tk.Button(root, text="Зашифрувати", command=lambda: encrypt_message(image))
encrypt_button.pack(pady=10)

root.mainloop()
