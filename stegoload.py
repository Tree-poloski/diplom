import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import secrets

def choose_image():
    file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif")])
    if file_path:
        load_and_display_image(file_path)

def load_and_display_image(file_path):
    img = Image.open(file_path)
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk

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
            k = abs(dct[4][5]) - abs(dct[5][4])  # Розрахунок різниці
            
            # Вставка біта повідомлення в коефіцієнт ДКП
            if get_bit(text, l):
                if k <= 25:
                    dct[4][5] = dct[5][4] + 150 if dct[4][5] >= 0 else -1 * (dct[5][4] + 150)
            else:
                if k >= -25:
                    dct[5][4] = dct[4][5] + 150 if dct[5][4] >= 0 else -1 * (dct[4][5] + 150)
                    
            xt = [row[:] for row in temp]  # Копіювання тимчасової матриці
            temp = idct_transform(dct, temp)  # Виконання зворотного ДКП
            
            # Збереження відредагованих пікселів у зображенні
            for x in range(8):
                for y in range(8):
                    image.putpixel((j + x, i + y), (temp[x][y]['red'], temp[x][y]['green'], temp[x][y]['blue']))
                    
            l += 1  # Лічильник бітів
            
    image.save('encrypt_test.jpg')  # Збереження зображення з внесеним текстом
    return image

def encrypt_text():
    input_text = text_entry.get("1.0", "end-1c")
    # Add your encryption logic here
    # For simplicity, let's just display the encrypted text in the console
    print(f"Encrypted Text: {input_text[::-1]}")

def dct_transform(dct, arr):
    for i in range(8):
        for j in range(8):
            temp = 0.0
            for x in range(8):
                for y in range(8):
                    temp += cos_t[i][x] * cos_t[j][y] * arr[x][y]['blue']
            dct[i][j] = e[i][j] * temp
            
    return dct

def idct_transform(dct, arr):
    for i in range(8):
        for j in range(8):
            temp = 0
            for x in range(8):
                for y in range(8):
                    temp += dct[x][y] * cos_t[x][i] * cos_t[y][j] * e[x][y]
            arr[i][j]['blue'] = min(255, max(0, round(temp)))
            
    return arr

def get_bit(text, pos):
    return True if ord(text[pos // 8]) & (1 << pos % 8) > 0 else False


# Generate key with digits only
key = ''.join(secrets.choice('0123456789') for i in range(10))

# Main Tkinter window
root = tk.Tk()
root.title("Image Text Encryption")

# Label to display the key
key_label = tk.Label(root, text="Key: " + key)
key_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")  # Position key label on the top right corner

# Button to choose image
choose_image_button = tk.Button(root, text="Choose Image", command=choose_image)
choose_image_button.grid(row=1, column=0, padx=10, pady=10)

# Image display label
image_label = tk.Label(root)
image_label.grid(row=1, column=1, padx=10, pady=10)

# Text entry for input
text_entry = tk.Text(root, height=4, width=30)
text_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Button to encrypt text
encrypt_button = tk.Button(root, text="Encrypt", command=insert_message)
encrypt_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
