import dearpygui.dearpygui as gui
import callbacks
import sys, os, tkinter

gui.create_context()
tkinter = tkinter.Tk()
screen_width = tkinter.winfo_screenwidth()
screen_height = tkinter.winfo_screenheight()
app_width = 800
app_height = 600

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

font_path = resource_path("Assets/FiraSans-Regular.ttf")

with gui.font_registry():
    with gui.font(font_path, 20) as default_font:
        gui.add_font_range_hint(gui.mvFontRangeHint_Default)
        gui.add_font_range_hint(gui.mvFontRangeHint_Cyrillic)
    with gui.font(font_path, 14) as default_font_14:
        gui.add_font_range_hint(gui.mvFontRangeHint_Default)
        gui.add_font_range_hint(gui.mvFontRangeHint_Cyrillic)


with gui.item_handler_registry(tag = "combo_update_lora_list"):
    gui.add_item_clicked_handler(callback = callbacks.combo_loras)


with gui.file_dialog(directory_selector = True, show = False, modal = True,
                     callback = callbacks.file_dialog_ok, cancel_callback = callbacks.file_dialog_cancel,
                     tag = "path_dialog"):
    gui.set_item_width("path_dialog", int(app_width * 0.8))
    gui.set_item_height("path_dialog", int(app_height * 0.8))

with gui.file_dialog(directory_selector = False, show = False, modal = True,
                     callback = callbacks.file_dialog_ok, cancel_callback = callbacks.file_dialog_cancel,
                     tag = "file_dialog"):
    gui.set_item_width("file_dialog", int(app_width * 0.8))
    gui.set_item_height("file_dialog", int(app_height * 0.8))
    gui.add_file_extension(".*")
    gui.add_file_extension(".ckpt")
    gui.add_file_extension(".safetensors")
    gui.add_file_extension(".pt")

with gui.window(tag = "main_window"):
    gui.bind_font(default_font)
    with gui.tab_bar():
        with gui.tab(label = "Основная панель"):
            with gui.child_window(tag = "child_head", height = int(app_height * 0.8), border = False):
                with gui.tab_bar(tag = "tab_bar_main_panel"):
                    gui.add_tab_button(label = "+", tag = "tab_button_add_lora_tab", callback = callbacks.add_lora_tab)
            with gui.child_window(tag = "child_footer", height = -1, border = False):
                with gui.group(horizontal = True):
                    gui.add_spacer(width = 300)
                    gui.add_combo([""], label = "", width = 200, tag = "combo_lora_list")
                    gui.add_button(label = "Копировать в", callback = callbacks.copy_settings_to_another_tab,
                                   before = "combo_lora_list")
                    gui.add_button(label = "Запустить все", callback = callbacks.RUN, width = -1)
        with gui.tab(label = "Консоль", tag = "tab_console"):
            with gui.child_window():
                gui.add_text("помогите мне её сделать :(", tag = "text_console")


gui.bind_item_handler_registry("combo_lora_list", "combo_update_lora_list")


# dpg stuff
gui.create_viewport(title = "LoRA train GUI",
                    width = app_width,
                    height = app_height,
                    x_pos = int((screen_width - app_width) / 2),
                    y_pos = int((screen_height - app_height) / 2),
                    resizable = False)
gui.setup_dearpygui()
gui.show_viewport()
gui.set_viewport_vsync(True)
gui.set_primary_window("main_window", True)
while gui.is_dearpygui_running():
    # if gui.is_item_visible("text_console"):
        # gui.set_value("text_console", callbacks.RUN())
    gui.render_dearpygui_frame()
# gui.start_dearpygui()
gui.destroy_context()
