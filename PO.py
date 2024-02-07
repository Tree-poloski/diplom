import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

def validate_key(char, key):
    if char.isdigit() and len(key.get()) <= 10:
        return True
    else:
        return False

def split_key(key):
    key_digits = [int(digit) for digit in key if digit.isdigit()]
    key_parts = [key_digits[i:i+2] for i in range(0, len(key_digits), 2)]

    while len(key_parts) < 5:
        key_parts.append([0, 0])

    return key_parts[:5]

def select_blocks(image_blocks, row, col):
    selected_blocks = []
    for i in range(row * 10, (row + 1) * 10):
        for j in range(col * 10, (col + 1) * 10):
            selected_blocks.append(image_blocks[i * 10 + j])
    return selected_blocks

def apply_dct(blocks):
    dct_blocks = []
    for block in blocks:
        pixels = np.array(block).astype(float)
        dct_matrix = np.fft.fftn(pixels)
        dct_blocks.append(dct_matrix)
    return dct_blocks

def invert_dct(blocks):
    inverted_blocks = []
    for dct_matrix in blocks:
        pixels = np.fft.ifftn(dct_matrix).real.clip(0, 255)
        inverted_blocks.append(Image.fromarray(pixels.astype(np.uint8)))
    return inverted_blocks

def encrypt_text(text, key):
    result = ""

    for char in text:
        if char.isalpha():
            ascii_offset = ord('a') if char.islower() else ord('A')
            shift = key.pop(0)[0]
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def encrypt_image(text, image_path, key):
    image = Image.open(image_path)
    blocks = get_image_blocks(image)

    encrypted_text = encrypt_text(text, key)

    text_index = 0
    for i, block in enumerate(blocks):
        pixels = list(block.getdata())
        for j in range(len(pixels)):
            pixel = list(pixels[j])
            pixel[1] = (pixel[1] + ord(encrypted_text[text_index])) % 256
            text_index = (text_index + 1) % len(encrypted_text)
            pixels[j] = tuple(pixel)
        block.putdata(pixels)

    key_digits = [int(digit) for digit in key if digit.isdigit()]
    key_parts = [key_digits[i:i+2] for i in range(0, len(key_digits), 2)]

    while len(key_parts) < 5:
        key_parts.append([0, 0])

    for row in range(5):
        for col in range(5):
            selected_blocks = select_blocks(blocks, row, col)
            dct_blocks = apply_dct(selected_blocks)

            for i in range(10):
                for j in range(10):
                    dct_blocks[i][j] += key_parts[row][0]
                    dct_blocks[i][j] += key_parts[col][1]

            inverted_blocks = invert_dct(dct_blocks)

            index = 0
            for i in range(row * 10, (row + 1) * 10):
                for j in range(col * 10, (col + 1) * 10):
                    blocks[i * 10 + j] = inverted_blocks[index]
                    index += 1

    encrypted_image = Image.new(image.mode, image.size)
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            encrypted_image.paste(blocks[y * image.width // 8 + x], (x, y))

    return encrypted_image

def get_image_blocks(image):
    width, height = image.size
    blocks = []
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            block = image.crop((x, y, x + 8, y + 8))
            blocks.append(block)
    return blocks

def choose_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image = Image.open(file_path)
        img_label.image = ImageTk.PhotoImage(image)
        img_label.config(image=img_label.image)
        img_label.file_path = file_path

def encrypt():
    text_to_encrypt = text_entry.get("1.0", "end-1c")
    key_value = key_entry.get()
    
    if len(key_value) == 10 and key_value.isdigit():
        try:
            key_parts = split_key(key_value)
            encrypted_text = encrypt_text(text_to_encrypt, key_parts)
            encrypted_image = encrypt_image(encrypted_text, img_label.file_path, key_parts)
            img_label.image = ImageTk.PhotoImage(encrypted_image)
            img_label.config(image=img_label.image)
        except ValueError as e:
            result_label.config(text=str(e))
    else:
        result_label.config(text="Please enter a 10-digit key.")

# Створення головного вікна
root = tk.Tk()
root.title("Text Encryption App")

# Створення віджетів
choose_button = tk.Button(root, text="Choose Image", command=choose_image)
img_label = tk.Label(root)
text_entry = tk.Text(root, height=5, width=30)
key_label = tk.Label(root, text="Key (10 digits):")
key_var = tk.StringVar()
key_var.trace_add('write', lambda *args: key_var.set(''.join(filter(str.isdigit, key_var.get()))))
key_entry = tk.Entry(root, textvariable=key_var)
encrypt_button = tk.Button(root, text="Encrypt", command=encrypt)
result_label = tk.Label(root, text="Encrypted Text will appear here")

# Розміщення віджетів у вікні
choose_button.pack(pady=10)
img_label.pack(pady=10)
text_entry.pack(pady=10)
key_label.pack()
key_entry.pack()
encrypt_button.pack(pady=10)
result_label.pack(pady=10)

# Запуск головного циклу
root.mainloop()
