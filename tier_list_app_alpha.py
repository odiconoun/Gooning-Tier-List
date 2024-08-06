import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import webbrowser
import re
import shutil
import os

# Diccionarios para URLs, tooltips y propiedades de imágenes
image_urls, image_tooltips, image_properties = {}, {}, {}
image_counter = 1
canvas_image_to_index = {}

def extract_username(url):
    """ Extrae el nombre de usuario de la URL usando expresiones regulares. """
    match = re.search(r'(?:https?://(?:www\.)?)(?:instagram\.com/|tiktok\.com/@|onlyfans\.com/)([^/?#&]+)', url)
    return match.group(1) if match else "usuario_desconocido"

def draw_all_lines_and_labels(canvas):
    canvas.delete("all")
    line_thickness, num_categories = 2, 7
    canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()
    y_positions = [i * (canvas_height / num_categories) for i in range(num_categories + 1)]
    
    for y in y_positions:
        canvas.create_line(0, y, canvas_width, y, fill="black", width=line_thickness)
    
    vertical_x = canvas_width // 6
    canvas.create_line(vertical_x, 0, vertical_x, canvas_height, fill="black", width=line_thickness)
    canvas.create_line(0, 0, canvas_width, 0, fill="black", width=line_thickness)
    canvas.create_line(0, canvas_height, canvas_width, canvas_height, fill="black", width=line_thickness)
    
    left_line_x = vertical_x - 10
    for y in y_positions:
        canvas.create_line(left_line_x, y, vertical_x, y, fill="black", width=line_thickness)
    
    categories = ['S', 'A', 'B', 'C', 'D', 'E', 'F']
    for i, category in enumerate(categories):
        y = i * (canvas_height / num_categories) + (canvas_height / num_categories) / 2
        canvas.create_text(vertical_x - 30, y, anchor="w", text=category, font=('Arial', 12), fill="black")
    
    for img_id, properties in image_properties.items():
        canvas.create_image(*properties['coords'], anchor="center", image=properties['image'])
    
    configure_image_events()
    update_window_title()

def configure_image_events():
    for img_id in image_properties.keys():
        canvas.tag_bind(img_id, "<Button-1>", lambda event, id=img_id: on_image_click(event, id))
        canvas.tag_bind(img_id, "<B1-Motion>", lambda event, id=img_id: on_image_drag(event, id))
        canvas.tag_bind(img_id, "<Double-1>", lambda event, id=img_id: on_image_double_click(event, id))
        canvas.tag_bind(img_id, "<Button-3>", lambda event, id=img_id: on_image_right_click(event, id))
        canvas.tag_bind(img_id, "<Enter>", lambda event, id=img_id: show_tooltip(event, id))
        canvas.tag_bind(img_id, "<Leave>", lambda event: hide_tooltip())

def on_image_click(event, img_id):
    canvas.drag_data = {'x': event.x, 'y': event.y, 'id': img_id}

def on_image_drag(event, img_id):
    canvas.move(img_id, event.x - canvas.drag_data['x'], event.y - canvas.drag_data['y'])
    canvas.drag_data.update({'x': event.x, 'y': event.y})

def on_image_double_click(event, img_id):
    index = canvas_image_to_index.get(img_id)
    url = image_urls.get(index)
    if url:
        webbrowser.open(url)

def on_image_right_click(event, img_id):
    if messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que quieres eliminar esta imagen?"):
        index = canvas_image_to_index.get(img_id)
        canvas.delete(img_id)
        if index:
            del image_urls[index]
            del image_tooltips[index]
            del canvas_image_to_index[img_id]
        del image_properties[img_id]
        update_window_title()

def show_tooltip(event, img_id):
    index = canvas_image_to_index.get(img_id)
    tooltip_text = image_tooltips.get(index)
    if tooltip_text:
        x, y, _, _ = canvas.bbox(img_id)
        tooltip_label.config(text=tooltip_text, bg="lightyellow")
        tooltip_label.place(x=x + 10, y=y + 10)

def hide_tooltip():
    tooltip_label.place_forget()

def add_image():
    global image_counter
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        resources_folder = "resources"
        os.makedirs(resources_folder, exist_ok=True)
        destination_path = os.path.join(resources_folder, os.path.basename(file_path))
        shutil.copy(file_path, destination_path)
        
        url = simpledialog.askstring("Ingrese URL", "Ingrese el enlace de red social para la imagen:")
        if url:
            try:
                img = Image.open(destination_path).resize((100, 100), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                center_x, center_y = canvas.winfo_width() // 2, canvas.winfo_height() // 2
                img_id = canvas.create_image(center_x, center_y, anchor="center", image=img_tk)
                image_properties[img_id] = {'image': img_tk, 'coords': (center_x, center_y)}
                image_urls[image_counter] = url
                image_tooltips[image_counter] = extract_username(url)
                canvas_image_to_index[img_id] = image_counter
                print(f"Imagen añadida con ID: {img_id}, URL: {url}, Usuario: {image_tooltips[image_counter]}")
                image_counter += 1
                configure_image_events()
            except IOError as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            update_window_title()

def update_window_title():
    """ Actualiza el título de la ventana con el número de imágenes. """
    num_images = len(image_properties)
    root.title(f"Gooning Tier List - {num_images} Targets")

root = tk.Tk()
root.title("Gooning Tier List - 0 Targets")

canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

root.attributes("-fullscreen", True)

canvas.bind("<Configure>", lambda event: draw_all_lines_and_labels(canvas))

tooltip_label = tk.Label(root, text="", font=('Arial', 12), relief=tk.SOLID, borderwidth=1, wraplength=200)

add_button = tk.Button(root, text="Añadir Imagen", command=add_image)
add_button.pack(pady=10)

root.mainloop()
