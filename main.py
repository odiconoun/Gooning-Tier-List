import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import webbrowser
import re
import shutil
import os
import pickle

# Diccionarios para URLs, tooltips y propiedades de imágenes
image_urls, image_tooltips, image_properties = {}, {}, {}
canvas_image_to_index = {}
image_counter = 1

def extract_username(url):
    """ Extrae el nombre de usuario de la URL usando expresiones regulares. """
    match = re.search(r'(?:https?://(?:www\.)?)(?:instagram\.com/|tiktok\.com/@|onlyfans\.com/)([^/?#&]+)', url)
    return match.group(1) if match else "usuario_desconocido"

def draw_all_lines_and_labels(canvas):
    """ Dibuja todas las líneas y etiquetas en el canvas. """
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
        canvas.create_text(vertical_x - 30, y, anchor="w", text=category, font=('Arial', 14), fill="black")
    
    # Redibujar las imágenes después de las líneas y etiquetas
    for img_id, properties in image_properties.items():
        try:
            img = Image.open(properties['filename'])
            img_tk = ImageTk.PhotoImage(img.resize((100, 100), Image.Resampling.LANCZOS))
            properties['image'] = img_tk
            # Coloca la imagen en las coordenadas guardadas
            canvas.create_image(*properties['coords'], anchor="center", image=img_tk, tags=img_id)
        except Exception as e:
            print(f"Error al cargar la imagen {properties['filename']}: {e}")
    
    configure_image_events()

def configure_image_events():
    """ Configura los eventos de las imágenes en el canvas. """
    for img_id in image_properties.keys():
        canvas.tag_bind(img_id, "<Button-1>", lambda event, id=img_id: on_image_click(event, id))
        canvas.tag_bind(img_id, "<B1-Motion>", lambda event, id=img_id: on_image_drag(event, id))
        canvas.tag_bind(img_id, "<Double-1>", lambda event, id=img_id: on_image_double_click(event, id))
        canvas.tag_bind(img_id, "<Button-3>", lambda event, id=img_id: on_image_right_click(event, id))
        canvas.tag_bind(img_id, "<Enter>", lambda event, id=img_id: show_tooltip(event, id))
        canvas.tag_bind(img_id, "<Leave>", lambda event: hide_tooltip())

def on_image_click(event, img_id):
    """ Maneja el clic en la imagen para arrastrarla. """
    canvas.drag_data = {'x': event.x, 'y': event.y, 'id': img_id}

def on_image_drag(event, img_id):
    """ Arrastra la imagen con el cursor. """
    if img_id in canvas.drag_data:
        canvas.move(img_id, event.x - canvas.drag_data['x'], event.y - canvas.drag_data['y'])
        canvas.drag_data.update({'x': event.x, 'y': event.y})
        # Actualizar las coordenadas en el diccionario de propiedades
        x, y = canvas.coords(img_id)
        image_properties[img_id]['coords'] = (x, y)

def on_image_double_click(event, img_id):
    """ Abre la URL asociada a la imagen. """
    url = image_urls.get(canvas_image_to_index.get(img_id))
    if url:
        webbrowser.open(url)

def on_image_right_click(event, img_id):
    """ Elimina la imagen y su información asociada. """
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
    """ Muestra el tooltip con el nombre de usuario. """
    index = canvas_image_to_index.get(img_id)
    tooltip_text = image_tooltips.get(index)
    if tooltip_text:
        x, y, _, _ = canvas.bbox(img_id)
        tooltip_label.config(text=tooltip_text, bg="lightyellow")
        tooltip_label.place(x=x + 10, y=y + 10)

def hide_tooltip():
    """ Oculta el tooltip. """
    tooltip_label.place_forget()

def add_image():
    """ Añade una nueva imagen al canvas. """
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
                img_id = canvas.create_image(center_x, center_y, anchor="center", image=img_tk, tags=image_counter)
                image_properties[img_id] = {'image': img_tk, 'coords': (center_x, center_y), 'filename': destination_path}
                image_urls[image_counter] = url
                image_tooltips[image_counter] = extract_username(url)
                canvas_image_to_index[img_id] = image_counter
                image_counter += 1
                update_window_title()
                configure_image_events()
            except IOError as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

def update_window_title():
    """ Actualiza el título de la ventana con el número de imágenes. """
    root.title(f"Gooning Tier List - {len(image_properties)} Targets")

def save_tier_list():
    """ Guarda la tier list en un archivo seleccionado por el usuario. """
    filename = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl")])
    if filename:
        try:
            data = {
                'image_properties': {},
                'image_urls': image_urls,
                'image_tooltips': image_tooltips,
                'image_counter': image_counter
            }
            
            for img_canvas_id, properties in image_properties.items():
                coords = properties['coords']
                filename = properties['filename']
                data['image_properties'][img_canvas_id] = {
                    'coords': coords,
                    'filename': filename
                }
                
            with open(filename, 'wb') as file:
                pickle.dump(data, file)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la tier list: {e}")

def load_tier_list():
    """ Carga una tier list desde un archivo seleccionado por el usuario. """
    global image_counter
    filename = filedialog.askopenfilename(filetypes=[("Pickle Files", "*.pkl")])
    if filename:
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                
                clear_canvas()  # Limpia el canvas antes de cargar nuevos datos
                
                image_urls.update(data.get('image_urls', {}))
                image_tooltips.update(data.get('image_tooltips', {}))
                image_counter = data.get('image_counter', 1)
                
                for img_canvas_id, props in data.get('image_properties', {}).items():
                    filename = props['filename']
                    coords = props['coords']
                    try:
                        img = Image.open(filename)
                        img_tk = ImageTk.PhotoImage(img.resize((100, 100), Image.Resampling.LANCZOS))
                        image_properties[img_canvas_id] = {'image': img_tk, 'coords': coords, 'filename': filename}
                        canvas_image_to_index[img_canvas_id] = image_counter
                        image_counter += 1
                    except Exception as e:
                        print(f"Error al cargar la imagen {filename}: {e}")
                
                draw_all_lines_and_labels(canvas)
                update_window_title()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tier list: {e}")

def clear_canvas():
    """ Limpia el canvas y los diccionarios de propiedades de imágenes. """
    canvas.delete("all")
    image_properties.clear()
    canvas_image_to_index.clear()

root = tk.Tk()
root.title("Gooning Tier List")

canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

canvas.bind("<Configure>", lambda event: draw_all_lines_and_labels(canvas))

tooltip_label = tk.Label(root, text="", font=('Arial', 12), relief=tk.SOLID, borderwidth=1, wraplength=200)

add_button = tk.Button(root, text="Añadir Imagen", command=add_image)
add_button.pack(pady=10)

save_button = tk.Button(root, text="Guardar Lista", command=save_tier_list)
save_button.pack(pady=10)

load_button = tk.Button(root, text="Cargar Lista", command=load_tier_list)
load_button.pack(pady=10)

root.mainloop()
