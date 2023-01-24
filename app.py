import dearpygui.dearpygui as dpg
import callbacks

dpg.create_context()
app_width = 800
app_height = 600

def path_button(tag, type, label):
    if type == "folder":
        callback = callbacks.path_dialog_show
    if type == "file":
        callback = callbacks.file_dialog_show
    return dpg.add_button(tag = tag, label = label, callback = callback)

with dpg.font_registry():
    with dpg.font("Assets/FiraSans-Regular.ttf", 20) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    with dpg.font("Assets/FiraSans-Regular.ttf", 14) as default_font_smol:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

with dpg.file_dialog(directory_selector = True, show = False, modal = True,
                    callback = callbacks.file_dialog_ok, cancel_callback = callbacks.file_dialog_cancel,
                    tag = "path_dialog"):
    dpg.set_item_width("path_dialog", app_width * 0.8)
    dpg.set_item_height("path_dialog", app_height * 0.8)

with dpg.file_dialog(directory_selector = False, show = False, modal = True,
                    callback = callbacks.file_dialog_ok, cancel_callback = callbacks.file_dialog_cancel,
                    tag = "file_dialog"):
    dpg.set_item_width("file_dialog", app_width * 0.8)
    dpg.set_item_height("file_dialog", app_height * 0.8)
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".ckpt")
    dpg.add_file_extension(".safetensors")
    dpg.add_file_extension(".pt")


with dpg.window(tag = "main_window"):
    dpg.bind_font(default_font)
    with dpg.tab_bar():
        with dpg.tab(label = "Пути"):
            # sd-scripts dir
            with dpg.group(horizontal = True):
                button_sdscripts_path = path_button(tag = "button_sdscripts_path", type = "folder",
                                              label = "Путь к папке sd-scripts")
                dpg.add_input_text(tag = "input_sdscripts_path", hint = "X:\git\sd-scripts", width = -1)


            # ckpt
            with dpg.group(horizontal = True):
                button_ckpt_path = path_button(tag = "button_ckpt_path", type = "file",
                                              label = "SD чекпоинт")
                dpg.add_input_text(tag = "input_ckpt_path", hint = "X:\models\checkpoint.safetensors", width = -1)
            with dpg.group(horizontal = True):
                dpg.add_checkbox(tag = "is_sd_768v_ckpt", label = "768-v", show = False)
                dpg.add_checkbox(tag = "is_sd_2.x_ckpt", label = "Stable Diffusion 2.x", before = "is_sd_768v_ckpt",
                                 callback = callbacks.sd_2x)

            dpg.add_checkbox(tag = "is_use_vae", label = "Использовать VAE", callback = callbacks.use_vae)

            # vae
            with dpg.group(tag = "group_vae_path", horizontal = True, show = False):
                button_vae_path = path_button(tag = "button_vae_path", type = "file",
                                               label = "VAE чекпоинт")
                dpg.add_input_text(tag = "input_vae_path", hint = "X:\models\\vae.pt", width = -1)

            # images dir
            with dpg.group(horizontal = True):
                button_img_path = path_button(tag = "button_img_path", type = "folder",
                                              label = "Папка с изображениями")
                dpg.add_input_text(tag = "input_img_path", hint = "X:\\training_data\img", width = -1)

            # use reg images
            dpg.add_checkbox(tag = "is_use_reg_images", label = "Использовать рег. изображения", callback = callbacks.reg_images)

            # reg images dir
            with dpg.group(tag = "group_reg_images", horizontal = True, show = False):
                button_reg_img_path = path_button(tag = "button_reg_img_path", type = "folder",
                                              label = "Папка с рег. изображениями")
                dpg.add_input_text(tag = "input_reg_img_path", hint = "X:\\training_data\img", width = -1)

            # output dir
            with dpg.group(horizontal = True):
                button_output_path = path_button(tag = "button_output_path", type = "folder",
                                              label = "Папка сохранения сети")
                dpg.add_input_text(tag = "input_output_path", hint = "X:\LoRA\\", width = -1)

            # output name
            with dpg.group(horizontal = True):
                dpg.add_text("Название файла")
                dpg.add_input_text(tag = "input_output_name", hint = "my_LoRA_network_v1", width = -1)

        with dpg.tab(label = "Длительность"):
            pass
        with dpg.tab(label = "Настройки"):
            pass
        with dpg.tab(label = "Дополнительно"):
            pass
        with dpg.tab(label = "Консоль"):
            pass
        dpg.add_tab_button(label = "Запуск", trailing = True)


# dpg stuff
dpg.create_viewport(title = "LoRA train GUI", width = app_width, height = app_height, resizable = False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
