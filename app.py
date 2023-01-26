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

with gui.theme() as test_theme:
    with gui.theme_component(gui.mvAll):
        gui.add_theme_style(gui.mvStyleVar_FrameRounding, 2, category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_TabActive, (150, 15, 30), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_TabHovered, (100, 10, 15), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_ButtonActive, (150, 15, 30), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_ButtonHovered, (100, 10, 15), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_CheckMark, (255, 255, 255), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_FrameBgHovered, (100, 30, 30), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_FrameBgActive, (150, 15, 30), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_HeaderHovered, (100, 10, 15), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_HeaderActive, (150, 15, 30), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_SliderGrab, (255, 255, 255), category = gui.mvThemeCat_Core)
        gui.add_theme_color(gui.mvThemeCol_SliderGrabActive, (192, 192, 192), category = gui.mvThemeCat_Core)


with gui.window(tag = "main_window"):
    gui.bind_font(default_font)
    with gui.group(horizontal = True):
        with gui.tab_bar():
            with gui.tab(label = "Настройки сетей"):
                with gui.child_window(tag = "child_head", height = int(app_height * 0.755), border = False):
                    with gui.tab_bar(tag = "tab_bar_main_panel"):
                        gui.add_tab_button(label = "+", tag = "tab_button_add_lora_tab", callback = callbacks.add_lora_tab)
                with gui.child_window(tag = "child_footer", height = -1, border = False):
                    with gui.group(horizontal = True):
                        button_sdscripts_path = callbacks.path_button(tag = "button_sdscripts_path",
                                                                      path_type = "folder",
                                                                      label = "Путь к папке sd-scripts")
                        gui.add_input_text(tag = "input_sdscripts_path", hint = "X:\git\sd-scripts",
                                           width = -1)
                    with gui.group(horizontal = True):
                        # gui.add_text(tag = "text_train_steps")
                        gui.add_combo([""], label = "", width = 300, tag = "combo_lora_list")
                        gui.add_button(label = "Копировать настройки вкладки в", callback = callbacks.copy_settings_to_another_tab,
                                       before = "combo_lora_list")
                        gui.add_button(label = "Запустить", callback = lambda: gui.show_item("modal_run"),
                                       width = -1, tag = "button_run")
            with gui.tab(label = "Консоль", tag = "tab_console"):
                with gui.child_window():
                    gui.add_text("помогите мне её сделать :(", tag = "text_console")
            gui.add_tab_button(label = "Гайд", callback = callbacks.open_link_guide, trailing = True)

    with gui.window(tag = "modal_run", modal = True, show = False, no_move = True, no_resize = True, no_title_bar = True,
                    width = app_width / 4, height = app_height / 4, pos = [app_width * 0.635, app_height * 0.55]):
        with gui.child_window(height = 100, border = False):
            gui.add_text("Вы уверены?")
        with gui.child_window(height = -1, border = False):
            with gui.group(horizontal = True):
                gui.add_spacer(width = 65)
                gui.add_button(label = "Да", callback = callbacks.RUN, width = 50)
                gui.add_button(label = "Нет", callback = callbacks.close_modal_run, width = 50)

    with gui.window(tag = "modal_training", modal = True, no_move = True, no_resize = True, no_title_bar = True,
                    width = app_width / 1.5, height = app_height / 1.5, pos = [app_width * 0.155, app_height * 0.13],
                    show = False):
        with gui.child_window(border = False, height = 97):
            gui.add_text("", tag = "text_training_number")
            gui.add_text("", tag = "text_training_path")
        with gui.child_window(border = False, height = -1):
            with gui.table(header_row = False):
                #gui.add
                gui.add_table_column()
                gui.add_table_column()
                gui.add_table_column()
                with gui.table_row():
                    gui.add_spacer()
                    gui.add_loading_indicator(radius = 8.5, color = (255, 255, 255), secondary_color = (128, 128, 128))

gui.bind_theme(test_theme)
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
