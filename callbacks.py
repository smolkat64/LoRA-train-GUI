import math
import os, webbrowser, subprocess, random, time, winreg
import dearpygui.dearpygui as gui
from ast import literal_eval

current_version = "0.26"
default_script = "ltg_default.ini"
app_width = 1000
app_height = 750
lora_tab_instances = 0
active_tab = ""
list_settings = ["pretrained_model_name_or_path", "v_parameterization", "v2", "use_vae",
                 "vae", "train_data_dir", "use_reg_data", "reg_data_dir",
                 "output_dir", "output_name", "training_duration_method", "max_train_epochs",
                 "train_time", "train_speed", "train_speed_type", "max_train_steps", "train_batch_size",
                 "save_every_n_epochs", "save_last_n_epochs", "use_separate_lr",
                 "learning_rate", "unet_lr", "text_encoder_lr",
                 "use_custom_scheduler", "scheduler_name", "scheduler_name_string", "lr_scheduler", "scheduler_args",
                 "lr_warmup_ratio", "resolution", "clip_skip",
                 "network_dim", "network_alpha", "shuffle_caption", "max_token_length",
                 "keep_tokens", "seed", "gradient_checkpointing", "gradient_accumulation_steps",
                 "max_data_loader_n_workers", "save_precision", "mixed_precision", "optimizer_type", "_optimizer_type", "optimizer_args",
                 "use_custom_optimizer", "optimizer_name", "optimizer_name_string",
                 "logging_dir", "use_custom_log_prefix", "log_prefix",
                 "LoCON", "locon_dim", "locon_dim_string", "locon_alpha", "locon_alpha_string",
                 "LoHA", "loha_dim", "loha_dim_string", "loha_alpha", "loha_alpha_string",
                 "DyLoRA", "dylora_unit", "dylora_unit_string", "dylora_dim", "dylora_dim_string", "dylora_alpha", "dylora_alpha_string",
                 "min_snr_gamma", "_offset_noise", "offset_noise", "scale_weight_normals",
                 "_noise_amount", "noise_amount", "_noise_discount", "noise_discount", "noise_iterations", "_noise_iterations"
                 "additional_parameters"]


def _help(message):
    last_item = gui.last_item()
    group = gui.add_group(horizontal = True)
    gui.move_item(last_item, parent = group)
    gui.capture_next_item(lambda s: gui.move_item(s, parent = group))
    t = gui.add_text("(?)", color = [0, 255, 0])
    with gui.tooltip(t):
        gui.add_text(message)


def _info_popup(message):
    if message is not None:
        with gui.window(no_move = True, no_collapse = True, no_resize = True, width = app_width / 2,
                        height = app_height / 2, pos = [200, 137.5], modal = True):
            gui.add_text(message)


def import_popup():
    gui.show_item("popup_import")


def export_settings():
    if get_active_tab() == 0:
        _info_popup("Невозможно экспортировать: нет активных\n"
                    "вкладок.")
        return
    suffix = append_caller_instance(get_active_tab())
    print(get_active_tab())
    settings_file = ["version=" + current_version + "\n", "\n", "##### SETTINGS #####\n", "\n"]
    for setting in list_settings:
        setting_value = gui.get_value(setting + suffix)
        if setting_value:
            settings_file.append(setting + ": " + str(setting_value) + "\n")
    filename = str(gui.get_value("output_name" + suffix)) + "_settings.ini"
    with open(filename, "w") as file:
        print("Записываем настройки в файл:", filename)
        file.writelines(settings_file)
        _info_popup("Настройки экспортированы в файл\n"
                    "" + filename)


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def import_settings(data, destination):
    if not get_active_tab():
        return
    suffix = append_caller_instance(append_instance_number("tab_lora"))
    try:
        settings_file = open(data, "r").readlines()
    except Exception as error:
        print("Ошибка при открытии файла:", error)
        return
    settings_file_version = settings_file[0].strip('\n').split("=")[-1]
    try:
        if float(settings_file_version) < float(current_version):
            print("Файл настроек для версии", settings_file_version)
    except ValueError:
        pass
    print("Импортируем настройки")
    is_any_setting_imported = False
    for line in settings_file:
        if line.count(':'):
            line_split = line.split(": ", 1)
        else:
            continue
        item = line_split[0].strip() + suffix
        value = line_split[-1].strip()
        # print(line_split[0], '=', value)
        if gui.does_item_exist(item):
            is_any_setting_imported = True
            item_type = type(gui.get_value(item))
            # print(item, item_type, value)
            if item_type == dict:
                gui.set_value(item, literal_eval(value))
            elif item_type == int:
                gui.set_value(item, int(value))
            elif item_type == float:
                gui.set_value(item, float(value))
            elif item_type == str:
                if value.lower == 'true' or value.lower == 'false':
                    gui.set_value(item, str2bool(value))
                else:
                    gui.set_value(item, value)
            elif item_type == bool:
                gui.set_value(item, str2bool(value))
            else:
                print("Несовместимая переменная:", item, "=", value, "типа", type(value))
    if not is_any_setting_imported:
        print("Не удалось импортировать")


def import_from_default_ini(destination):
    if os.path.isfile(default_script):
        if lora_tab_instances == 1:
            print("Найден файл", default_script)
        import_settings(default_script, destination)
    else:
        if lora_tab_instances == 1:
            print("Файл", default_script, "не найден")


def sd_scripts_path_to_registry():
    input_field = "sd_scripts_path"
    software_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\\")
    key = winreg.CreateKey(software_key, "LoRATrainGUI")
    winreg.SetValueEx(key, input_field, 0, winreg.REG_SZ, gui.get_value(input_field))
    if key:
        winreg.CloseKey(key)


def get_sd_scripts_path_from_registry():
    input_field = "sd_scripts_path"
    try:
        lora_train_gui_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\\LoRATrainGUI\\")
    except FileNotFoundError:
        return
    lora_train_gui_key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\\LoRATrainGUI\\")
    gui.set_value(input_field, winreg.QueryValueEx(lora_train_gui_key, input_field)[0])
    if lora_train_gui_key:
        winreg.CloseKey(lora_train_gui_key)


def path_button(tag, path_type, label):
    if path_type == "folder":
        callback = path_dialog_show
    if path_type == "file":
        callback = file_dialog_show
    return gui.add_button(tag = tag, label = label, callback = callback)


def calculate_total_images(caller):
    suffix = append_caller_instance(caller)
    main_image_folder = gui.get_value("train_data_dir" + suffix)
    try:
        image_dirs = os.listdir(main_image_folder)
        total_images = 0
        for dir in image_dirs:
            parts = dir.split('_', 1)
            repeats = int(parts[0])
            images_count = 0
            for training_file in os.listdir(main_image_folder + "\\" + dir):
                if training_file.split('.')[-1] == "jpg" or training_file.split('.')[-1] == \
                        "jpeg" or training_file.split('.')[-1] == "png" or training_file.split('.')[-1] == "webp" or \
                        training_file.split('.')[-1] == "bmp":
                    images_count += 1
            total_images += repeats * images_count
        return total_images
    except FileNotFoundError:
        # print("Укажите папку с изображениями!")
        return 0
    except ValueError:
        return -1


def append_instance_number(tag_string):
    return tag_string + "_" + str(lora_tab_instances)


def get_caller_instance(caller_string):
    # наворотил хуйни
    # return re.split(r'^[a-zA-Z_]+', caller_string)[-1]
    return str(caller_string).split("_")[-1]


def append_caller_instance(caller_instance):
    return "_" + get_caller_instance(caller_instance)


def lora_tab_update_name(caller):
    suffix = append_caller_instance(caller)
    gui.set_item_label("tab_lora" + suffix, gui.get_value("output_name" + suffix))
    if gui.get_value("output_name" + suffix) == "":
        gui.set_item_label("tab_lora" + suffix, "anon (" + get_caller_instance(caller) + ")")


def calculate_lora_tab_count():
    i = 0
    lora_tab_name_list = []
    for lora_tab in gui.get_item_children("tab_bar_main_panel", 1):
        if not gui.is_item_shown(lora_tab) and gui.get_item_info(lora_tab)["container"]:
            gui.delete_item(lora_tab)
        elif not gui.get_item_info(lora_tab)["container"]:
            pass
        else:
            i += 1

    gui.configure_item("combo_lora_list", items = lora_tab_name_list)
    return i


def remove_trailing_slashes(path):
    return path.rstrip('\\/')


def separate_lr(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("use_separate_lr" + suffix):
        gui.show_item("group_custom_lr" + suffix)
        gui.hide_item("group_main_lr" + suffix)
    if not gui.get_value("use_separate_lr" + suffix):
        gui.show_item("group_main_lr" + suffix)
        gui.hide_item("group_custom_lr" + suffix)

def custom_scheduler_name(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("use_custom_scheduler" + suffix):
        gui.show_item("scheduler_name" + suffix)
        gui.hide_item("scheduler" + suffix)
    if not gui.get_value("use_custom_scheduler" + suffix):
        gui.show_item("scheduler" + suffix)
        gui.hide_item("scheduler_name" + suffix)
        gui.set_value("scheduler_name_string" + suffix, "")


def custom_optimizer_name(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("use_custom_optimizer" + suffix):
        gui.show_item("optimizer_name" + suffix)
        gui.hide_item("_optimizer_type" + suffix)
        gui.set_value("optimizer_type" + suffix, "")
    if not gui.get_value("use_custom_optimizer" + suffix):
        gui.show_item("_optimizer_type" + suffix)
        gui.hide_item("optimizer_name" + suffix)
        gui.set_value("optimizer_name_string" + suffix, "")


def locon(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("LoCON" + suffix):
        gui.show_item("locon_dim" + suffix)
        gui.show_item("locon_alpha" + suffix)
        gui.set_value("DyLoRA" + suffix, False)
        dylora(suffix)
        gui.set_value("LoHA" + suffix, False)
        loha(suffix)
    if not gui.get_value("LoCON" + suffix):
        gui.hide_item("locon_dim" + suffix)
        gui.hide_item("locon_alpha" + suffix)
        gui.set_value("locon_dim_string" + suffix, "")
        gui.set_value("locon_alpha_string" + suffix, "")

def loha(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("LoHA" + suffix):
        gui.show_item("loha_dim" + suffix)
        gui.show_item("loha_alpha" + suffix)
        gui.set_value("DyLoRA" + suffix, False)
        dylora(suffix)
        gui.set_value("LoCON" + suffix, False)
        locon(suffix)
    if not gui.get_value("LoHA" + suffix):
        gui.hide_item("loha_dim" + suffix)
        gui.hide_item("loha_alpha" + suffix)
        gui.set_value("loha_dim_string" + suffix, "")
        gui.set_value("loha_alpha_string" + suffix, "")


def dylora(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("DyLoRA" + suffix):
        gui.show_item("dylora_dim" + suffix)
        gui.show_item("dylora_alpha" + suffix)
        gui.show_item("dylora_unit" + suffix)
        gui.set_value("LoCON" + suffix, False)
        locon(suffix)
        gui.set_value("LoHA" + suffix, False)
        loha(suffix)
    if not gui.get_value("DyLoRA" + suffix):
        gui.hide_item("dylora_dim" + suffix)
        gui.hide_item("dylora_alpha" + suffix)
        gui.hide_item("dylora_unit" + suffix)
        gui.set_value("dylora_dim_string" + suffix, "")
        gui.set_value("dylora_alpha_string" + suffix, "")
        gui.set_value("dylora_unit_string" + suffix, "")

def offset_noise(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("offset_noise" + suffix) == "None":
        gui.hide_item("_noise_amount" + suffix)
        gui.hide_item("_noise_discount" + suffix)
        gui.hide_item("_noise_iterations" + suffix)
        gui.set_value("noise_amount" + suffix, "")
        gui.set_value("noise_discount" + suffix, "")
        gui.set_value("noise_iterations" + suffix, "")
    elif gui.get_value("offset_noise" + suffix) == "Normal":
        gui.show_item("_noise_amount" + suffix)
        gui.set_value("noise_amount" + suffix, "0.05")
        gui.hide_item("_noise_discount" + suffix)
        gui.set_value("noise_discount" + suffix, "")
        gui.hide_item("_noise_iterations" + suffix)
        gui.set_value("noise_iterations" + suffix, "")
    elif gui.get_value("offset_noise" + suffix) == "Pyramid":
        gui.hide_item("_noise_amount" + suffix)
        gui.show_item("_noise_discount" + suffix)
        gui.show_item("_noise_iterations" + suffix)
        gui.set_value("noise_amount" + suffix, "")
        gui.set_value("noise_discount" + suffix, "0.15")
        gui.set_value("noise_iterations" + suffix, "6")


def network_module(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value('locon_dim_string' + suffix) or gui.get_value('loha_dim_string' + suffix):
        return f" \"--network_module=lycoris.kohya\" "
    elif gui.get_value('dylora_dim_string' + suffix):
        return f" \"--network_module=networks.dylora\" "


def additional_network_args(caller):
    suffix = append_caller_instance(caller)
    all_args = ""
    if gui.get_value('locon_dim_string' + suffix):
        locon_dim = gui.get_value('locon_dim_string' + suffix)
        locon_alpha = gui.get_value('locon_alpha_string' + suffix)
        all_args += f"\"conv_dim={locon_dim}\" "
        all_args += f"\"conv_alpha={locon_alpha}\" "
        all_args += f"\"algo=locon\" "
    elif gui.get_value('dylora_dim_string' + suffix):
        dylora_dim = gui.get_value('dylora_dim_string' + suffix)
        dylora_alpha = gui.get_value('dylora_alpha_string' + suffix)
        dylora_unit = gui.get_value('dylora_unit_string' + suffix)
        all_args += f"\"conv_dim={dylora_dim}\" "
        all_args += f"\"conv_alpha={dylora_alpha}\" "
        all_args += f"\"unit={dylora_unit}\" "
    elif gui.get_value('loha_dim_string' + suffix):
        loha_dim = gui.get_value('loha_dim_string' + suffix)
        loha_alpha = gui.get_value('loha_alpha_string' + suffix)
        all_args += f"\"conv_dim={loha_dim}\" "
        all_args += f"\"conv_alpha={loha_alpha}\" "
        all_args += f"\"algo=loha\" "
    return all_args


def combo_loras():
    active_tab = get_active_tab()
    lora_tab_name_list = []
    lora_tab_instance_list = []
    for lora_tab in gui.get_item_children("tab_bar_main_panel", 1):
        tab_instance = gui.get_item_alias(lora_tab).split('_')[-1]
        if gui.is_item_shown(lora_tab) and gui.get_item_info(lora_tab)["container"]:
            if not ("tab_lora_" + tab_instance) == active_tab:
                lora_tab_name_list.append(gui.get_item_label(lora_tab))
                lora_tab_instance_list.append("_" + tab_instance)
    gui.set_item_user_data("combo_lora_list", lora_tab_instance_list)
    # print(gui.get_item_user_data("combo_lora_list"))
    gui.configure_item("combo_lora_list", items = lora_tab_name_list)
    # print(gui.get_item_configuration("combo_lora_list")["items"])


def show_fonts():
    gui.show_font_manager()


def show_info():
    pass


def open_link_guide():
    webbrowser.open_new_tab("https://rentry.org/2chAI_LoRA_Dreambooth_guide")


def path_dialog_show(sender):
    item = "path_dialog"
    send_to = sender.replace("button_", "input_", 1)
    gui.show_item(item)
    gui.set_item_user_data(item, send_to)


def file_dialog_show(sender):
    item = "file_dialog"
    send_to = sender.replace("button_", "input_", 1)
    gui.show_item(item)
    gui.set_item_user_data(item, send_to)


def file_dialog_ok(sender, app_data, user_data):
    print("Sending ", app_data["file_path_name"], " to ", user_data)
    gui.set_value(user_data, app_data["file_path_name"])


def file_dialog_cancel():
    pass


def sd_2x(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("v2" + suffix):
        gui.show_item("v_parameterization" + suffix)
    else:
        gui.set_value("v_parameterization" + suffix, False)
        gui.hide_item("v_parameterization" + suffix)


def reg_images(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("use_reg_data" + suffix):
        gui.show_item("group_reg_images" + suffix)
    else:
        gui.hide_item("group_reg_images" + suffix)
        gui.set_value("reg_data_dir" + suffix, "")


def use_vae(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("use_vae" + suffix):
        gui.show_item("group_vae_path" + suffix)
    else:
        gui.hide_item("group_vae_path" + suffix)
        gui.set_value("vae" + suffix, "")


def custom_log_prefix(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("use_custom_log_prefix" + suffix):
        gui.show_item("group_custom_log_prefix" + suffix)
    else:
        gui.hide_item("group_custom_log_prefix" + suffix)
        gui.set_value("log_prefix" + suffix, "")


def scheduler(caller):
    suffix = append_caller_instance(caller)
    if not gui.get_value("lr_scheduler" + suffix) == "constant":
        gui.show_item("group_warmup_ratio" + suffix)
    else:
        gui.hide_item("group_warmup_ratio" + suffix)


def copy_settings_to_another_tab(user_data):
    i = 0
    active_tab = get_active_tab()
    send_to_suffix = ""
    for lora in gui.get_item_configuration("combo_lora_list")["items"]:
        if gui.get_value("combo_lora_list") == lora:
            send_to_suffix = gui.get_item_user_data("combo_lora_list")[i]
        i += 1
    print("Копируем настройки из:", get_active_tab())
    print("В:", "tab_lora" + send_to_suffix)
    for setting in list_settings:
        # print(setting + send_to_suffix, " -> ", gui.get_value(setting + "_" + active_tab.split('_')[-1]))
        try:
            gui.set_value(setting + send_to_suffix, gui.get_value(setting + "_" + active_tab.split('_')[-1]))
        except SystemError:
            print("##### Error in: ", setting + send_to_suffix, " -> ",
                  gui.get_value(setting + "_" + active_tab.split('_')[-1]))
    gui.set_value("output_name" + send_to_suffix, gui.get_value("output_name" + send_to_suffix) + "_copy")
    gui.set_value("combo_lora_list", "")


def get_active_tab():
    if tab_number == 1 and gui.get_value("tab_bar_main_panel") == 0:
        return "lora_tab_1"
    return gui.get_value("tab_bar_main_panel")


def close_modal_run():
    gui.hide_item("modal_run")


def training_duration_method(caller):
    suffix = append_caller_instance(caller)
    methods = { "Использовать эпохи": "group_epochs_number" + suffix,
                "Обучать в течении времени": "group_training_time" + suffix,
                "Своё количество шагов": "group_custom_steps" + suffix }
    gui.show_item(methods.get(gui.get_value("training_duration_method" + suffix)))
    del methods[gui.get_value("training_duration_method" + suffix)]
    for method in methods:
        gui.hide_item(methods.get(method))
    gui.set_value("text_max_train_steps" + suffix, train_steps(caller, "value"))


def train_steps(caller, request):
    suffix = append_caller_instance(caller)
    max_train_steps = 0
    if gui.get_value("training_duration_method" + suffix) == "Использовать эпохи":
        max_train_epochs = int(gui.get_value('max_train_epochs' + suffix))
        if gui.get_value("use_reg_data" + suffix):
            max_train_steps *= 2
        total_images = calculate_total_images(suffix)
        if not total_images:
            return "нет изображений"
        elif total_images < 0:
            return "неверная папка"
        else:
            max_train_steps = calculate_total_images(suffix) / \
                              int(gui.get_value("train_batch_size" + suffix)) * max_train_epochs
            if request == "value":
                return int(max_train_steps)
            if request == "arg":
                return f" --max_train_epochs={gui.get_value('max_train_epochs' + suffix)}"
    elif gui.get_value("training_duration_method" + suffix) == "Обучать в течении времени":
        training_speed = float(gui.get_value("train_speed" + suffix))
        if gui.get_value("train_speed_type" + suffix) == "s/it":
            training_speed = 1 / training_speed
        train_time_dict = gui.get_value("train_time" + suffix)
        training_time_minutes = train_time_dict['min'] + train_time_dict['sec'] / 60 + train_time_dict['hour'] * 60
        max_train_steps = training_speed * 60 * int(training_time_minutes)
        # if gui.get_value("use_reg_data" + suffix) == True:
        # max_train_steps *= 2
        if request == "value":
            return int(max_train_steps)
        if request == "arg":
            return f" --max_train_steps={int(max_train_steps)}"
    else:
        max_train_steps = gui.get_value('max_train_steps' + suffix)
        if request == "value":
            return max_train_steps
        if request == "arg":
            return f" --max_train_steps={int(max_train_steps)}"


def lora_resize():
    gui.show_item("modal_training")
    resize_args = {'new_rank': gui.get_value('new_rank_value'), 'dynamic_method': gui.get_value('dynamic_method_value'),
                   'dynamic_param': gui.get_value('dynamic_param_value'), 'lora_path': gui.get_value('lora_path_value'),
                   'output_path': gui.get_value('output_path_value'), 'save_precision': gui.get_value('save_precision_value'),
                   'device': gui.get_value('device_value')}
    commands = "[console]::OutputEncoding = [text.encoding]::UTF8\n"
    commands += "$env:PYTHONIOENCODING = 'utf-8'\n"
    commands += f"Set-Location \"{gui.get_value('sd_scripts_path')}\"\n"
    commands += ".\\venv\Scripts\\activate\n"
    if resize_args['lora_path'].endswith('.safetensors'):
        lora_name = resize_args['lora_path'].rsplit('\\', 1)
        lora_without_suffix = lora_name[1].removesuffix('.safetensors')
        commands += f"python networks\\resize_lora.py --save_precision {resize_args['save_precision']} --new_rank {resize_args['new_rank']}" \
                    f" --save_to \"{resize_args['output_path']}\{lora_without_suffix}-{resize_args['new_rank']}rank.safetensors\" " \
                    f" --model \"{resize_args['lora_path']}\" --device {resize_args['device']}" \
                    f" --dynamic_method {resize_args['dynamic_method']} --dynamic_param {resize_args['dynamic_param']}"
        proc = subprocess.Popen("powershell", stdin=subprocess.PIPE).communicate(input=commands.encode())
    else:
        loras = os.listdir(resize_args['lora_path'])
        for i in loras:
            if i.endswith('.safetensors'):
                commands = "[console]::OutputEncoding = [text.encoding]::UTF8\n"
                commands += "$env:PYTHONIOENCODING = 'utf-8'\n"
                commands += f"Set-Location \"{gui.get_value('sd_scripts_path')}\"\n"
                commands += ".\\venv\Scripts\\activate\n"
                commands += f"python networks\\resize_lora.py --save_precision {resize_args['save_precision']} --new_rank {resize_args['new_rank']}" \
                            f" --save_to \"{resize_args['output_path']}\{i.removesuffix('.safetensors')}-{resize_args['new_rank']}rank.safetensors\" " \
                            f" --model \"{resize_args['lora_path']}\{i}\" --device {resize_args['device']}" \
                            f" --dynamic_method {resize_args['dynamic_method']} --dynamic_param {resize_args['dynamic_param']}"
                proc = subprocess.Popen("powershell", stdin=subprocess.PIPE).communicate(input=commands.encode())
            else:
                continue
    return gui.hide_item("modal_training")


def start_tensorboard():
    log_dir = gui.get_value('log_path_value')
    commands = "[console]::OutputEncoding = [text.encoding]::UTF8\n"
    commands += "$env:PYTHONIOENCODING = 'utf-8'\n"
    commands += f"Set-Location \"{gui.get_value('sd_scripts_path')}\"\n"
    commands += ".\\venv\Scripts\\activate\n"
    commands += f"Start-Process -NoNewWindow tensorboard -ArgumentList \"--logdir {log_dir}\""
    proc = subprocess.Popen("powershell", stdin=subprocess.PIPE).communicate(input=commands.encode())
    time.sleep(10)
    webbrowser.open_new_tab(url="http://localhost:6006")
    return


def tensor_check():
    lora_path = gui.get_value('lora_path_for_tensorcheck_value')
    output_dir = gui.get_value('path_for_tensorchecker_output')
    lora_name = lora_path.rsplit('\\', 1)
    lora_without_suffix = lora_name[1].removesuffix('.safetensors')
    commands = "[console]::OutputEncoding = [text.encoding]::UTF8\n"
    commands += "$env:PYTHONIOENCODING = 'utf-8'\n"
    commands += f"Set-Location \"{gui.get_value('sd_scripts_path')}\"\n"
    commands += ".\\venv\Scripts\\activate\n"
    commands += f"python networks\\check_lora_weights.py \"{lora_path}\" > \"{output_dir}\\{lora_without_suffix}.txt\""
    proc = subprocess.Popen("powershell", stdin=subprocess.PIPE).communicate(input=commands.encode())
    return


def RUN():
    sd_scripts_path_to_registry()
    tab_count = calculate_lora_tab_count()
    gui.hide_item("modal_run")
    time.sleep(0.5)
    if tab_count < 1:
        _info_popup("Нечего обучать!")
        return
    for i in range(1, tab_count + 1):
        commands = ""
        suffix = "_" + str(i)

        gui.set_value("text_training_number", "Обучение сети: " + str(i) + "/" + str(tab_count))
        gui.set_value("text_training_path", "...\\" + gui.get_value('output_name' + suffix) + ".safetensors")
        gui.show_item("modal_training")

        commands = "[console]::OutputEncoding = [text.encoding]::UTF8\n"
        # блять jfs ебать ты чед
        commands += "$env:PYTHONIOENCODING = 'utf-8'\n"
        commands += f"Set-Location \"{gui.get_value('sd_scripts_path')}\"\n"
        commands += ".\\venv\Scripts\\activate\n"

        # \"{ gui.get_value('' + suffix) }\"
        commands += f"accelerate launch --num_cpu_threads_per_process {gui.get_value('max_data_loader_n_workers' + suffix)}" \
                    f" train_network.py --pretrained_model_name_or_path=\"{remove_trailing_slashes(gui.get_value('pretrained_model_name_or_path' + suffix))}\"" \
                    f" --train_data_dir=\"{remove_trailing_slashes(gui.get_value('train_data_dir' + suffix))}\"" \
                    f" --output_dir=\"{remove_trailing_slashes(gui.get_value('output_dir' + suffix))}\"" \
                    f" --output_name=\"{gui.get_value('output_name' + suffix)}\"" \
                    f" --save_every_n_epochs={gui.get_value('save_every_n_epochs' + suffix)}" \
                    f" --save_last_n_epochs={gui.get_value('save_last_n_epochs' + suffix)}" \
                    f" --train_batch_size={gui.get_value('train_batch_size' + suffix)}" \
                    f" --resolution=\"{gui.get_value('resolution' + suffix)}\"" \
                    f" --network_dim={gui.get_value('network_dim' + suffix)}" \
                    f" --keep_tokens={gui.get_value('keep_tokens' + suffix)}" \
                    f" --gradient_accumulation_steps={gui.get_value('gradient_accumulation_steps' + suffix)}" \
                    f" --max_data_loader_n_workers={gui.get_value('max_data_loader_n_workers' + suffix)}" \
                    f" --save_precision={gui.get_value('save_precision' + suffix)}" \
                    f" --mixed_precision={gui.get_value('mixed_precision' + suffix)}"
                    # f" --learning_rate={round(gui.get_value('learning_rate' + suffix), 8)}" \
                    # f" --unet_lr={round(gui.get_value('unet_lr' + suffix), 8)}" \
                    # f" --text_encoder_lr={round(gui.get_value('text_encoder_lr' + suffix), 8)}"

        if gui.get_value('scheduler_name_string' + suffix):
            commands += f" --lr_scheduler_type={gui.get_value('scheduler_name_string' + suffix)}"
        else:
            commands += f" --lr_scheduler={gui.get_value('lr_scheduler' + suffix)}"

        if gui.get_value('scheduler_args' + suffix):
            scheduler_args = gui.get_value('scheduler_args' + suffix)
            if "--lr_scheduler_num_cycles" in scheduler_args:
                commands += f" {gui.get_value('scheduler_args' + suffix)}"
            elif "--lr_scheduler_power" in scheduler_args:
                commands += f" {gui.get_value('scheduler_args' + suffix)}"
            else:
                commands += f" --lr_scheduler_args {gui.get_value('scheduler_args' + suffix)}"


        if gui.get_value('optimizer_name_string' + suffix):
            optimizer_type = (gui.get_value('optimizer_name_string' + suffix))               # https://github.com/kozistr/pytorch_optimizer
            commands += f" --optimizer_type={optimizer_type}"
        else:
            optimizer_type = (gui.get_value('optimizer_type' + suffix))
            if optimizer_type == "Old_version":  # old version compatibility
                commands += f" --use_8bit_adam"
            elif optimizer_type != "Old_version":
                commands += f" --optimizer_type={optimizer_type}"  # https://github.com/kohya-ss/sd-scripts/releases/tag/v0.4.4
                                                                                             # pip install lion-pytorch dadaptation в венве с сд-скриптс, чтобы юзать новые оптимайзеры

        if gui.get_value('optimizer_args' + suffix):
            commands += f" --optimizer_args {gui.get_value('optimizer_args' + suffix)}"

        if gui.get_value("use_separate_lr" + suffix):
            if optimizer_type == "DAdaptation":
                commands += f" --learning_rate={gui.get_value('unet_lr' + suffix)}"
                # commands += f" --unet_lr={gui.get_value('unet_lr' + suffix)}"
                commands += f" --text_encoder_lr={gui.get_value('text_encoder_lr' + suffix)}"
            else:
                commands += f" --unet_lr={gui.get_value('unet_lr' + suffix)}"
                commands += f" --text_encoder_lr={gui.get_value('text_encoder_lr' + suffix)}"
        else:
            commands += f" --learning_rate={gui.get_value('learning_rate' + suffix)}"


        if gui.get_value("v2" + suffix):
            commands += " --v2"
            if gui.get_value("v_parameterization" + suffix):
                commands += " --v_parameterization"

        if gui.get_value("use_reg_data" + suffix):
            commands += f" --reg_data_dir=\"{remove_trailing_slashes(gui.get_value('reg_data_dir' + suffix))}\""

        if gui.get_value("use_vae" + suffix):
            commands += f" --vae=\"{remove_trailing_slashes(gui.get_value('vae' + suffix))}\""

        max_train_steps = train_steps(suffix, "value")
        commands += train_steps(suffix, "arg")

        if not gui.get_value('lr_scheduler' + suffix) == 'constant':
            try:
                commands += " --lr_warmup_steps=" \
                            f"{int(gui.get_value('lr_warmup_ratio' + suffix) / 100 * int(max_train_steps))}"
            except ValueError:
                print('Не удалось расчитать количество шагов lr_warmup_steps: ошибка в папке с изображениями')
                continue

        if not gui.get_value('clip_skip' + suffix) == "1":
            commands += f" --clip_skip={gui.get_value('clip_skip' + suffix)}"

        network_alpha = gui.get_value('network_alpha' + suffix)

        if network_alpha:
            commands += f" --network_alpha={network_alpha}"

        if gui.get_value('shuffle_caption' + suffix):
            commands += " --shuffle_caption"

        if not gui.get_value('max_token_length' + suffix) == "75":
            commands += f" --max_token_length={gui.get_value('max_token_length' + suffix)}"

        seed = gui.get_value('seed' + suffix)
        if gui.get_value('seed' + suffix) == "-1":
            seed = random.randint(1, 2147483647)
        commands += f" --seed={seed}"

        if gui.get_value('gradient_checkpointing' + suffix):
            commands += " --gradient_checkpointing"

        if not gui.get_value('logging_dir' + suffix) == "":
            commands += f" --logging_dir=\"{remove_trailing_slashes(gui.get_value('logging_dir' + suffix))}\""
            log_prefix = gui.get_value('output_name' + suffix) + "_"
            if gui.get_value('use_custom_log_prefix' + suffix):
                log_prefix = gui.get_value('log_prefix' + suffix)
            commands += f" --log_prefix=\"{log_prefix}\""

        if gui.get_value('min_snr_gamma' + suffix):
            min_snr_gamma = gui.get_value('min_snr_gamma' + suffix)
            commands += f" --min_snr_gamma={min_snr_gamma}"

        if gui.get_value("offset_noise" + suffix) == "None":
            pass
        elif gui.get_value("offset_noise" + suffix) == "Normal":
            noise_offset = gui.get_value('noise_amount' + suffix)
            commands += f" --noise_offset={noise_offset}"
        elif gui.get_value("offset_noise" + suffix) == "Pyramid":
            # commands += f" --adaptive_noise_scale"
            # noise_offset = gui.get_value('noise_amount' + suffix)
            # commands += f" --noise_offset={noise_offset}"
            noise_discount = gui.get_value('noise_discount' + suffix)
            commands += f" --multires_noise_discount={noise_discount}"
            noise_iterations = gui.get_value('noise_iterations' + suffix)
            commands += f" --multires_noise_iterations={noise_iterations}"

        if gui.get_value("scale_weight_normals" + suffix):
            scale_weight_normals = gui.get_value('scale_weight_normals' + suffix)
            commands += f" --scale_weight_norms={scale_weight_normals}"

        if gui.get_value('LoCON' + suffix) or gui.get_value('LoHA' + suffix) or gui.get_value('DyLoRA' + suffix):
            commands += network_module(suffix)
            additional_network_arguments = additional_network_args(suffix)
            if additional_network_arguments:
                commands += f" --network_args {additional_network_arguments}"
        else:
            commands += f" --network_module=networks.lora"


        commands += f" {gui.get_value('additional_parameters' + suffix)}\n"
        proc = subprocess.Popen("powershell", stdin = subprocess.PIPE).communicate(input = commands.encode())
        # proc

    gui.hide_item("modal_training")


def calculate_scheduler_plot_data():
    sindatax = []; sindatay = []
    scheduler = gui.get_value("lr_scheduler")
    if scheduler == "linear":
        sindatax.append([0, gui.get_value("lr_warmup_ratio") / 100, 1])
        sindatay.append([0, 1, 0])
    gui.get_item_configuration("plot_line_series")


tab_number = 0


def add_lora_tab():
    global lora_tab_instances
    lora_tab_instances += 1

    global tab_number
    tab_number += 1

    with gui.item_handler_registry(tag = append_instance_number("handler_checkbox")):
        gui.add_item_visible_handler(callback = sd_2x, tag = append_instance_number("visibility_handler_sd_2x"))
        gui.add_item_visible_handler(callback = use_vae, tag = append_instance_number("visibility_handler_use_vae"))
        gui.add_item_visible_handler(callback = reg_images,
                                     tag = append_instance_number("visibility_handler_reg_images"))
        gui.add_item_visible_handler(callback = custom_log_prefix,
                                     tag = append_instance_number("visibility_handler_custom_log_prefix"))
        gui.add_item_visible_handler(callback = separate_lr,
                                     tag = append_instance_number("visibility_handler_separate_lr"))
        gui.add_item_visible_handler(callback=custom_scheduler_name,
                                     tag=append_instance_number("visibility_handler_custom_lr"))
        gui.add_item_visible_handler(callback=custom_optimizer_name,
                                     tag=append_instance_number("visibility_handler_custom_optimizer"))
        gui.add_item_visible_handler(callback=locon,
                                     tag=append_instance_number("visibility_handler_locon"))
        gui.add_item_visible_handler(callback=loha,
                                     tag=append_instance_number("visibility_handler_loha"))
        gui.add_item_visible_handler(callback=dylora,
                                     tag=append_instance_number("visibility_handler_dylora"))
        gui.add_item_visible_handler(callback=offset_noise,
                                     tag=append_instance_number("visibility_handler_offset_noise"))

    with gui.item_handler_registry(tag = append_instance_number("handler_radio")):
        gui.add_item_visible_handler(callback = training_duration_method,
                                     tag = append_instance_number("visibility_handler_training_method"))

    with gui.item_handler_registry(tag = append_instance_number("handler_combo")):
        gui.add_item_visible_handler(callback = scheduler, tag = append_instance_number("visibility_handler_scheduler"))

    with gui.item_handler_registry(tag = append_instance_number("handler_tab")):
        gui.add_item_visible_handler(callback = lora_tab_update_name, tag = append_instance_number("visibility_handler_tab_name"))

    with gui.tab(tag = append_instance_number("tab_lora"), before = "tab_button_add_lora_tab",
                 label = "network_" + str(tab_number), closable = True):
        calculate_lora_tab_count()
        with gui.tab_bar(tag = append_instance_number("tab_bar_lora")):

            gui.bind_item_handler_registry(append_instance_number("tab_lora"), append_instance_number("handler_tab"))

            with gui.tab(label = "Пути"):
                # ckpt
                with gui.group(horizontal = True):
                    path_button(tag = append_instance_number("button_ckpt_path"), path_type = "file",
                                label = "SD чекпоинт")
                    gui.add_input_text(tag = append_instance_number("pretrained_model_name_or_path"),
                                       hint = "X:\models\checkpoint.safetensors", width = -1)
                # sd 2.x checkboxes
                with gui.group(horizontal = True):
                    gui.add_checkbox(tag = append_instance_number("v_parameterization"), label = "768-v",
                                     show = False)
                    gui.add_checkbox(tag = append_instance_number("v2"),
                                     label = "Stable Diffusion 2.x",
                                     before = append_instance_number("v_parameterization"))
                    gui.bind_item_handler_registry(append_instance_number("v2"),
                                                   append_instance_number("handler_checkbox"))

                # vae checkbox
                gui.add_checkbox(tag = append_instance_number("use_vae"), label = "Использовать VAE",
                                 callback = use_vae)

                # vae
                with gui.group(tag = append_instance_number("group_vae_path"), horizontal = True, show = False):
                    path_button(tag = append_instance_number("button_vae_path"), path_type = "file",
                                label = "VAE чекпоинт")
                    gui.add_input_text(tag = append_instance_number("vae"), hint = "X:\models\\vae.pt",
                                       width = -1)
                    gui.bind_item_handler_registry(append_instance_number("use_vae"),
                                                   append_instance_number("handler_checkbox"))

                # images dir
                with gui.group(horizontal = True):
                    path_button(tag = append_instance_number("button_img_path"), path_type = "folder",
                                label = "Папка с изображениями")
                    gui.add_input_text(tag = append_instance_number("train_data_dir"), hint = "X:\\training_data\img",
                                       width = -1)

                # use reg images
                gui.add_checkbox(tag = append_instance_number("use_reg_data"),
                                 label = "Использовать рег. изображения",
                                 callback = reg_images)
                gui.bind_item_handler_registry(append_instance_number("use_reg_data"),
                                               append_instance_number("handler_checkbox"))

                # reg images dir
                with gui.group(tag = append_instance_number("group_reg_images"), horizontal = True, show = False):
                    path_button(tag = append_instance_number("button_reg_img_path"),
                                path_type = "folder",
                                label = "Папка с рег. изображениями")
                    gui.add_input_text(tag = append_instance_number("reg_data_dir"),
                                       hint = "X:\\training_data\img", width = -1)

                # output dir
                with gui.group(horizontal = True):
                    path_button(tag = append_instance_number("button_output_path"),
                                path_type = "folder",
                                label = "Папка сохранения файла")
                    gui.add_input_text(tag = append_instance_number("output_dir"), hint = "X:\LoRA",
                                       width = -1)

                # output name
                with gui.group(horizontal = True):
                    gui.add_text("Имя файла")
                    gui.add_input_text(tag = append_instance_number("output_name"), hint = "my_LoRA_network",
                                       width = -1,
                                       default_value = gui.get_item_label(append_instance_number("tab_lora")))

            with gui.tab(label = "Длительность"):
                with gui.table(header_row = False):
                    gui.add_table_column()
                    gui.add_table_column()
                    with gui.table_row():
                        gui.add_text("Метод расчёта шагов обучения")
                        with gui.group(horizontal = True):
                            gui.add_text("Количество шагов: ")
                            gui.add_text("", tag = append_instance_number("text_max_train_steps"))

                gui.add_radio_button(tag = append_instance_number("training_duration_method"),
                                     items = ["Использовать эпохи", "Обучать в течении времени",
                                              "Своё количество шагов"], default_value = "Использовать эпохи",
                                     horizontal = True, callback = training_duration_method)
                gui.bind_item_handler_registry(append_instance_number("training_duration_method"),
                                               append_instance_number("handler_radio"))

                gui.add_separator()

                with gui.group():
                    with gui.group(tag = append_instance_number("group_epochs_number"), horizontal = True, show = True):
                        gui.add_text("Количество эпох")
                        gui.add_input_text(tag = append_instance_number("max_train_epochs"), default_value = '10',
                                           width = -1, decimal = True)
                    with gui.group(tag = append_instance_number("group_training_time"), show = False):
                        with gui.group(horizontal = True):
                            gui.add_text("Время обучения")
                            gui.add_time_picker(hour24 = True, default_value = { 'hour': 0, 'min': 60, 'sec': 0 },
                                                tag = append_instance_number("train_time"))

                        with gui.group(horizontal = True):
                            gui.add_text("Скорость обучения")
                            gui.add_input_text(tag = append_instance_number("train_speed"),
                                               default_value = '1.00', width = 120, decimal = True)
                            gui.add_combo(tag = append_instance_number("train_speed_type"),
                                          items = ["it/s", "s/it"], width = -1, default_value = "it/s")
                    with gui.group(tag = append_instance_number("group_custom_steps"), horizontal = True, show = False):
                        gui.add_text("Количество шагов")
                        gui.add_input_text(tag = append_instance_number("max_train_steps"), default_value = '1000',
                                           width = -1)

                gui.add_separator()

                with gui.group(horizontal = True):
                    gui.add_text("Размер обучающей партии")
                    _help("train_batch_size")
                    gui.add_input_text(tag = append_instance_number("train_batch_size"), default_value = '1',
                                       width = -1, decimal = True)

                with gui.group(horizontal = True):
                    gui.add_text("Сохранять чекпоинт каждые")
                    gui.add_input_text(tag = append_instance_number("save_every_n_epochs"), default_value = '1',
                                       width = 100, decimal = True)
                    gui.add_text("эпох")
                with gui.group(horizontal = True):
                    gui.add_text("Сохранять только последние")
                    gui.add_input_text(tag = append_instance_number("save_last_n_epochs"), default_value = '1000',
                                       width = 100, decimal = True)
                    gui.add_text("эпох")

            with gui.tab(label = "Настройки"):
                with gui.collapsing_header(label = "Обучение"):
                    with gui.group(horizontal = True):
                        gui.add_text("Использовать раздельные скорости обучения")
                        gui.add_checkbox(tag = append_instance_number("use_separate_lr"), default_value = False)

                    gui.bind_item_handler_registry(append_instance_number("use_separate_lr"),
                                                   append_instance_number("handler_checkbox"))

                    with gui.group(horizontal = True, tag = append_instance_number("group_main_lr")):
                        gui.add_text("Скорость обучения")
                        gui.add_input_text(tag = append_instance_number("learning_rate"),
                                           default_value = '1e-3', width = -1, scientific = True)

                    with gui.group(tag = append_instance_number("group_custom_lr"), show = False):
                        with gui.group(horizontal = True):
                            gui.add_text("Скорость обучения UNet")
                            gui.add_input_text(tag = append_instance_number("unet_lr"),
                                               default_value = '1e-3', width = -1, scientific = True)

                        with gui.group(horizontal = True):
                            gui.add_text("Скорость обучения TE")
                            _help("ТЕ - текстовый энкодер")
                            gui.add_input_text(tag = append_instance_number("text_encoder_lr"),
                                               default_value = '1e-3', width = -1, scientific = True)

                    gui.add_checkbox(tag=append_instance_number("use_custom_optimizer"), label="Custom optimizer",
                                     callback=custom_optimizer_name, default_value=False)

                    with gui.group(tag=append_instance_number("optimizer_name"), horizontal=True, show=False):
                        gui.add_input_text(tag=append_instance_number("optimizer_name_string"),
                                           hint="pytorch_optimizer.DAdaptAdan",                 # https://github.com/kozistr/pytorch_optimizer/blob/5ee6ed692c14f5ddbaec8ccb685fe312949c3a9a/docs/optimizer_api.rst
                                           width=-1)

                    with gui.group(horizontal=True, tag = append_instance_number("_optimizer_type")):
                        gui.add_text("Optimizer type")
                        gui.add_combo(["Old_version", "AdamW", "AdamW8bit", "Lion", "Lion8bit", "SGDNesterov", "SGDNesterov8bit",   #https://github.com/lucidrains/lion-pytorch     #https://github.com/kohya-ss/sd-scripts/releases/tag/v0.6.4 8-битная версия подъехала
                                       "DAdaptation", "AdaFactor", "Prodigy"], tag=append_instance_number("optimizer_type"),        #https://github.com/kohya-ss/sd-scripts/pull/585
                                      default_value="AdamW8bit", width=-1)

                    with gui.group(horizontal=True):
                        gui.add_text("optimizer_args")
                        gui.add_input_text(tag=append_instance_number("optimizer_args"),
                                           default_value="",
                                           width=-1, height=100)

                    gui.add_checkbox(tag = append_instance_number("use_custom_scheduler"), label="Custom scheduler",
                                     callback = custom_scheduler_name, default_value = False)

                    with gui.group(tag=append_instance_number("scheduler_name"), horizontal=True, show=False):
                        gui.add_input_text(tag=append_instance_number("scheduler_name_string"),
                                           hint="CosineAnnealingLR",
                                           width=-1)

                    with gui.group(horizontal = True, tag = append_instance_number("scheduler")):
                        gui.add_text("Планировщик")
                        gui.add_combo(["linear", "cosine", "cosine_with_restarts", "polynomial",
                                       "constant", "constant_with_warmup"],
                                      tag = append_instance_number("lr_scheduler"),
                                      default_value = "linear", width = -1, callback = scheduler)

                    with gui.group(horizontal=True):
                        gui.add_text("scheduler_args")
                        gui.add_input_text(tag=append_instance_number("scheduler_args"),
                                           default_value="", hint="--lr_scheduler_num_cycles; --lr_scheduler_power; T_max; etc",
                                           width=-1, height=100)

                    with gui.group(tag = append_instance_number("group_warmup_ratio"), horizontal = True, show = True):
                        gui.add_text("Разогрев планировщика")
                        _help("Количество шагов в начале обучения,\n"
                              "в течении которых скорость обучения\n"
                              "будет линейно возрастать до значения\n"
                              "указанного выше.")
                        gui.add_slider_float(tag = append_instance_number("lr_warmup_ratio"), width = -1,
                                             min_value = 0.0, max_value = 100.0, format = '%.0f%%', default_value = 0.0,
                                             clamped = True)

                    '''with gui.child_window(height = 800, border = False):
                        with gui.plot(label = "Планировщик", width = -1, height = 400, no_menus = True,
                                      no_highlight = True,
                                      no_mouse_pos = True, no_box_select = True, anti_aliased = True):
                            gui.add_plot_axis(gui.mvXAxis, label = "Шаги обучения (%)")
                            with gui.plot_axis(gui.mvYAxis, label = "Скорость обучения"):
                                gui.add_line_series([1], [1], tag = "plot_line_series")'''

                    # gui.add_separator()

                with gui.collapsing_header(label = "Основные настройки"):
                    with gui.group(horizontal = True):
                        gui.add_text("Разрешение обучения")
                        gui.add_input_text(tag = append_instance_number("resolution"),
                                           default_value = "512,512", width = -1, decimal = True)

                    with gui.group(horizontal = True):
                        gui.add_text("CLIP Skip")
                        _help("Использовать вывод текстового\n"
                              "энкодера N-ного слоя с конца.\n"
                              "1 означает тренировать все слои.\n"
                              "1 для SD-основаных чекпоинтов,\n"
                              "2 для NAI-основанных чекпоинтов.\n"
                              "С помощью Ctrl+ЛКМ можно ввести\n"
                              "своё значение.")
                        gui.add_slider_int(tag = append_instance_number("clip_skip"),
                                           default_value = 1, width = 50, min_value = 1, max_value = 2)

                    with gui.group(horizontal = True):
                        gui.add_text("Размер (ранк) сети")
                        gui.add_input_text(tag = append_instance_number("network_dim"),
                                           default_value = '128', width = -1, decimal = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Альфа сети")
                        _help("Добавлено в версии sd-scripts 0.4.0.\n"
                              "Если не указана, равна единице."
                              "Если у вас старая версия, оставьте поле\n"
                              "пустым.\n")
                        gui.add_input_text(tag = append_instance_number("network_alpha"),
                                           default_value = '', width = -1, decimal = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Перемешивание описаний")
                        _help("Теги, написанные через запятую в файлах описания\n"
                              "будут перемешиваться. Делает обучение текстового\n"
                              "энкодера более гибким.")
                        gui.add_checkbox(tag = append_instance_number("shuffle_caption"), default_value = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Макс. длина токена")
                        gui.add_combo(['75', '150', '225'], tag = append_instance_number("max_token_length"),
                                      default_value = '225', width = -1)

                    with gui.group(horizontal = True):
                        gui.add_text("Защитить от перемешивания первые")
                        gui.add_input_text(tag = append_instance_number("keep_tokens"),
                                           default_value = '1', width = 120, decimal = True)
                        gui.add_text("токенов")

                    with gui.group(horizontal = True):
                        gui.add_text("Сид")
                        _help("-1 = рандомный сид")
                        gui.add_input_text(tag = append_instance_number("seed"),
                                           default_value = '-1', width = -1, decimal = True)
                    # gui.add_separator()

            with gui.tab(label = "Дополнительно"):
                with gui.group(horizontal = True):
                    gui.add_text("custom_parameters")
                    gui.add_input_text(tag = append_instance_number("additional_parameters"),
                                       default_value = "--caption_extension=\".txt\" --prior_loss_weight=1 "
                                                       "--enable_bucket --min_bucket_reso=256 --max_bucket_reso=1536 "
                                                       "--xformers --save_model_as=safetensors --cache_latents --cache_latents_to_disk --persistent_data_loader_workers", # https://github.com/kohya-ss/sd-scripts/releases/tag/v0.4.2
                                       width = -1, height = 100)
                with gui.group(horizontal = True):
                    gui.add_text("gradient_checkpointing")
                    gui.add_checkbox(tag = append_instance_number("gradient_checkpointing"), default_value = False)

                with gui.group(horizontal = True):
                    gui.add_text("gradient_accumulation_steps")
                    gui.add_input_text(tag = append_instance_number("gradient_accumulation_steps"),
                                       default_value = '1', width = -1, decimal = True)

                with gui.group(horizontal = True):
                    gui.add_text("max_data_loader_n_workers")
                    _help("Выделяемое количество потоков\n"
                          "процессора для DataLoader. Маленькие\n"
                          "значения могут негативно сказаться\n"
                          "скорости обучения.")
                    gui.add_input_text(tag = append_instance_number("max_data_loader_n_workers"),
                                       default_value = '4', width = -1, decimal = True)

                with gui.group(horizontal = True):
                    gui.add_text("save_precision")
                    gui.add_combo(["float", "fp16", "bf16"], tag = append_instance_number("save_precision"),
                                  default_value = "fp16", width = -1)

                with gui.group(horizontal = True):
                    gui.add_text("mixed_precision")
                    gui.add_combo(["fp16", "bf16"], tag = append_instance_number("mixed_precision"),
                                  default_value = "fp16", width = -1)

                with gui.group(horizontal = True):
                    button_img_path = path_button(tag = append_instance_number("button_log_dir"), path_type = "folder",
                                                  label = "logging_dir")
                    gui.add_input_text(tag = append_instance_number("logging_dir"), hint = "X:\\LoRA\\logs\\",
                                       width = -1)

                with gui.group(horizontal = True):
                    gui.add_text("use_custom_log_prefix")
                    gui.add_checkbox(tag = append_instance_number("use_custom_log_prefix"), default_value = False,
                                     callback = custom_log_prefix)

                with gui.group(horizontal = True):
                    gui.add_text("min_snr_gamma")
                    gui.add_input_text(tag = append_instance_number("min_snr_gamma"),
                                       hint='5', width = -1)

                with gui.group(horizontal = True):
                    gui.add_text("scale_weight_normals")
                    gui.add_input_text(tag = append_instance_number("scale_weight_normals"),    #https://github.com/KohakuBlueleaf/LyCORIS/issues/57
                                       hint='0.9', width = -1)                                  #https://github.com/kohya-ss/sd-scripts/pull/545

                with gui.group(horizontal=True, tag=append_instance_number("_offset_noise")):
                    gui.add_text("Offset noise")
                    gui.add_combo(
                        ["None", "Normal", "Pyramid"],
                        tag=append_instance_number("offset_noise"), default_value="None", width=-1, callback=offset_noise)
                with gui.group(horizontal = False, tag=append_instance_number("_noise_amount")):
                    gui.add_text("Noise amount")
                    gui.add_input_text(tag=append_instance_number("noise_amount"), width=-1)
                with gui.group(horizontal=False, tag=append_instance_number("_noise_iterations")):
                    gui.add_text("Pyramid iterations")
                    gui.add_input_text(tag=append_instance_number("noise_iterations"), width=-1)
                with gui.group(horizontal=False, tag=append_instance_number("_noise_discount")):
                    gui.add_text("Pyramid discount")
                    gui.add_input_text(tag=append_instance_number("noise_discount"), width=-1)

                with gui.group(tag = append_instance_number("group_custom_log_prefix"), horizontal = True,
                               show = False):
                    gui.add_text("log_prefix")
                    gui.add_input_text(tag = append_instance_number("log_prefix"),
                                       default_value = "", width = -1)
                    gui.bind_item_handler_registry(append_instance_number("use_custom_log_prefix"),
                                                   append_instance_number("handler_checkbox"))
            with gui.tab(label="LyCORIS"):

                gui.add_checkbox(tag=append_instance_number("LoCON"), label="LoCON",
                                 callback=locon, default_value = False)

                with gui.group(tag=append_instance_number("locon_dim"), horizontal=True, show=False):
                    gui.add_text("LoCON dim")
                    gui.add_input_text(tag=append_instance_number("locon_dim_string"),
                                       hint="8",
                                       width=-1)

                with gui.group(tag=append_instance_number("locon_alpha"), horizontal=True, show=False):
                    gui.add_text("LoCON alpha")
                    gui.add_input_text(tag=append_instance_number("locon_alpha_string"),
                                       hint="1",
                                       width=-1)

                gui.add_checkbox(tag=append_instance_number("LoHA"), label="LoHA",
                                 callback=loha, default_value=False)

                with gui.group(tag=append_instance_number("loha_dim"), horizontal=True, show=False):
                    gui.add_text("LoHA dim")
                    gui.add_input_text(tag=append_instance_number("loha_dim_string"),
                                       hint="8",
                                       width=-1)

                with gui.group(tag=append_instance_number("loha_alpha"), horizontal=True, show=False):
                    gui.add_text("LoHA alpha")
                    gui.add_input_text(tag=append_instance_number("loha_alpha_string"),
                                       hint="1",
                                       width=-1)

                gui.add_checkbox(tag=append_instance_number("DyLoRA"), label="DyLoRA",
                                 callback=dylora, default_value=False)

                with gui.group(tag=append_instance_number("dylora_dim"), horizontal=True, show=False):
                    gui.add_text("DyLoRA dim")
                    gui.add_input_text(tag=append_instance_number("dylora_dim_string"),
                                       hint="8",
                                       width=-1)

                with gui.group(tag=append_instance_number("dylora_alpha"), horizontal=True, show=False):
                    gui.add_text("DyLoRA alpha")
                    gui.add_input_text(tag=append_instance_number("dylora_alpha_string"),
                                       hint="1",
                                       width=-1)

                with gui.group(tag=append_instance_number("dylora_unit"), horizontal=True, show=False):
                    gui.add_text("DyLoRA unit value")
                    gui.add_input_text(tag=append_instance_number("dylora_unit_string"),
                                       hint="4",
                                       width=-1)
            if calculate_lora_tab_count() > 1:
                pass
            else:
                get_sd_scripts_path_from_registry()
                with gui.tab(label="Utils"):
                    with gui.collapsing_header(label="Start tensorboard"):
                        with gui.group(horizontal=True):
                            gui.add_text("Log path", tag="log_path")
                            gui.add_input_text(tag="log_path_value",
                                               hint="B:\lora\logs",
                                               width=500)
                            tensorboard_button = gui.add_button(label="Start", width=200, tag="button_tensorboard",
                                                           callback=start_tensorboard)
                    with gui.collapsing_header(label="Check tensors"):
                        with gui.group(horizontal=True):
                            gui.add_text("Lora path", tag="lora_path_for_tensorcheck")
                            gui.add_input_text(tag="lora_path_for_tensorcheck_value",
                                               hint="B:\lora\lora.safetensors",
                                               width=300)
                        with gui.group(horizontal=True):
                            gui.add_text("Txt output path", tag="txt_output_path")
                            gui.add_input_text(tag="path_for_tensorchecker_output",
                                               hint="B:\lora",
                                               width=300)
                            tensorboard_button = gui.add_button(label="Check", width=200, tag="button_tensorcheck",
                                                           callback=tensor_check)
                    with gui.collapsing_header(label = "Resize lora"):
                        with gui.group(horizontal=True):
                            gui.add_text("New rank", tag="new_rank")
                            gui.add_input_text(tag="new_rank_value",
                                               hint="32",
                                               default_value="32",
                                               width=50)
                            gui.add_text("Dynamic method", tag="dynamic_method")
                            gui.add_input_text(tag="dynamic_method_value",
                                               hint="sv_fro",
                                               default_value="sv_fro",
                                               width=150)
                            gui.add_text("Dynamic param", tag="dynamic_param")
                            gui.add_input_text(tag="dynamic_param_value",
                                               hint="0.9",
                                               default_value="0.9",
                                               width=100)
                            gui.add_text("Save precision", tag="save_precision")
                            gui.add_input_text(tag="save_precision_value",
                                               hint="bf16",
                                               default_value="bf16",
                                               width=50)
                            gui.add_text("Device", tag="device")
                            gui.add_input_text(tag="device_value",
                                               hint="cuda",
                                               default_value="cuda",
                                               width=75)
                        with gui.group(horizontal=True):
                            gui.add_text("Lora path", tag="lora_path")
                            gui.add_input_text(tag="lora_path_value",
                                               hint="B:\lora\lora.safetensors or B:\lora",
                                               width=350)
                            gui.add_text("Output path", tag="output_path")
                            gui.add_input_text(tag="output_path_value",
                                               hint="B:\lora",
                                               width=350)

                        resize_button = gui.add_button(label="Resize", width=500, tag="button_resize", callback=lora_resize)

    import_from_default_ini(append_instance_number("tab_lora"))