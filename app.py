import time

import callbacks
import dearpygui.dearpygui as gui
import DearPyGui_DragAndDrop as dnd
import sys, os, tkinter

gui.create_context()
dnd.initialize()

tkinter = tkinter.Tk()
screen_width = tkinter.winfo_screenwidth()
screen_height = tkinter.winfo_screenheight()



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def drop(data, keys):
    gui.bind_item_theme(import_window, None)
    dnd.set_drop_effect()
    gui.hide_item(import_window)
    callbacks.import_settings(data[0], gui.get_value("tab_bar_main_panel"))


def drag_over(keys):
    if gui.is_item_hovered(import_window):
        gui.bind_item_theme(import_window, hover_drag_theme)
        dnd.set_drop_effect(dnd.DROPEFFECT.MOVE)
    else:
        gui.bind_item_theme(import_window, None)
        dnd.set_drop_effect()


with gui.font_registry():
    with gui.font(resource_path("Assets/FiraSans-Regular.ttf"), 20) as default_font:
        gui.add_font_range_hint(gui.mvFontRangeHint_Default)
        gui.add_font_range_hint(gui.mvFontRangeHint_Cyrillic)

with gui.item_handler_registry(tag = "combo_update_lora_list"):
    gui.add_item_clicked_handler(callback = callbacks.combo_loras)

with gui.file_dialog(directory_selector = True, show = False, modal = True,
                     callback = callbacks.file_dialog_ok, cancel_callback = callbacks.file_dialog_cancel,
                     tag = "path_dialog"):
    gui.set_item_width("path_dialog", int(callbacks.app_width * 0.8))
    gui.set_item_height("path_dialog", int(callbacks.app_height * 0.8))

with gui.file_dialog(directory_selector = False, show = False, modal = True,
                     callback = callbacks.file_dialog_ok, cancel_callback = callbacks.file_dialog_cancel,
                     tag = "file_dialog"):
    gui.set_item_width("file_dialog", int(callbacks.app_width * 0.8))
    gui.set_item_height("file_dialog", int(callbacks.app_height * 0.8))
    gui.add_file_extension(".*")
    gui.add_file_extension(".ckpt")
    gui.add_file_extension(".safetensors")
    gui.add_file_extension(".pt")

with gui.theme() as test_theme:
    with gui.theme_component(gui.mvAll):
        gui.add_theme_style(gui.mvStyleVar_FrameRounding, 0, category = gui.mvThemeCat_Core)

with gui.theme() as hover_drag_theme:
    with gui.theme_component(gui.mvAll):
        gui.add_theme_color(gui.mvThemeCol_Border, (0, 180, 255), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_PopupBg, (25, 50, 75), category = gui.mvThemeCat_Core)


with gui.window(tag = "main_window"):
    gui.bind_font(default_font)
    with gui.group(horizontal = True):
        with gui.tab_bar():
            with gui.tab(label = "Настройки сетей"):
                with gui.child_window(tag = "child_head", height = int(callbacks.app_height - 150), border = False):
                    with gui.tab_bar(tag = "tab_bar_main_panel"):
                        gui.add_tab_button(label = "+", tag = "tab_button_add_lora_tab", callback = callbacks.add_lora_tab)
                with gui.child_window(tag = "child_footer", height = -1, border = False):
                    gui.add_separator()
                    with gui.group(horizontal = True):
                        button_sdscripts_path = callbacks.path_button(tag = "button_sdscripts_path",
                                                                      path_type = "folder",
                                                                      label = "Путь к папке sd-scripts")
                        gui.add_input_text(tag = "sd_scripts_path", hint = "X:\git\sd-scripts",
                                           width = -1)
                    with gui.group(horizontal = True):
                        # gui.add_text(tag = "text_train_steps")
                        gui.add_combo([""], label = "", width = 300, tag = "combo_lora_list")
                        gui.add_button(label = "Копировать настройки вкладки в", callback = callbacks.copy_settings_to_another_tab,
                                       before = "combo_lora_list")
                        gui.add_button(label = "Запустить", callback = lambda: gui.show_item("modal_run"),
                                       width = -1, tag = "button_run")
            '''with gui.tab(label = "Консоль", tag = "tab_console"):
                with gui.child_window():
                    gui.add_text("", tag = "text_console") # помогите мне её сделать :('''
            gui.add_tab_button(label = "Импорт", callback = callbacks.import_popup)
            gui.add_tab_button(label = "Экспорт", callback = callbacks.export_settings)
            gui.add_tab_button(label = "Гайд", callback = callbacks.open_link_guide, trailing = True)

    with gui.window(tag = "modal_run", modal = True, show = False, no_move = True, no_resize = True, no_title_bar = True,
                    width = callbacks.app_width / 4, height = callbacks.app_height / 4, pos = [callbacks.app_width * 0.635, callbacks.app_height * 0.6]):
        with gui.child_window(height = 115, border = False):
            gui.add_text("Вы уверены?")
        with gui.child_window(height = -1, border = False):
            with gui.group(horizontal = True):
                gui.add_spacer(width = 65)
                gui.add_button(label = "Да", callback = callbacks.RUN, width = 50)
                gui.add_button(label = "Нет", callback = callbacks.close_modal_run, width = 50)

    with gui.window(no_move = True, no_collapse = True, no_resize = True, width = callbacks.app_width / 2,
                    height = callbacks.app_height / 2, pos = [200, 137.5], modal = True,
                    show = False, tag = "popup_import") as import_window:
        gui.add_text("Для того чтобы импортировать настройки в\n"
                     "текущую вкладку, перетяните файл в это окно\n")

    with gui.window(tag = "modal_training", modal = True, no_move = True, no_resize = True, no_title_bar = True,
                    width = callbacks.app_width / 1.5, height = callbacks.app_height / 1.5, pos = [callbacks.app_width * 0.155, callbacks.app_height * 0.13],
                    show = False):
        with gui.child_window(border = False, height = 115):
            gui.add_text("", tag = "text_training_number")
            gui.add_text("", tag = "text_training_path")
        with gui.child_window(border = False, height = -1):
            with gui.table(header_row = False):
                gui.add_table_column()
                gui.add_table_column()
                gui.add_table_column()
                with gui.table_row():
                    gui.add_spacer()
                    gui.add_loading_indicator(radius = 8.5, color = (255, 255, 255), secondary_color = (128, 128, 128))
    callbacks.add_lora_tab()


gui.bind_theme(test_theme)
gui.bind_item_handler_registry("combo_lora_list", "combo_update_lora_list")

dnd.set_drop(drop)
dnd.set_drag_over(drag_over)

callbacks.get_sd_scripts_path_from_registry()

# dpg stuff
gui.create_viewport(title = "LoRA train GUI v" + callbacks.current_version,
                    large_icon = resource_path("Assets/large_icon.ico"),
                    small_icon = resource_path("Assets/small_icon.ico"),
                    width = callbacks.app_width,
                    height = callbacks.app_height,
                    x_pos = int((screen_width - callbacks.app_width) / 2),
                    y_pos = int((screen_height - callbacks.app_height) / 2),
                    resizable = False)

gui.setup_dearpygui()
gui.show_viewport()
gui.set_viewport_vsync(True)
gui.set_primary_window("main_window", True)
while gui.is_dearpygui_running():
    gui.render_dearpygui_frame()
# gui.start_dearpygui()
gui.destroy_context()
