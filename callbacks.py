import decimal
import os, webbrowser, subprocess, random, time
import dearpygui.dearpygui as gui
from ast import literal_eval

current_version = "0.2"
app_width = 800
app_height = 650
lora_tab_instances = 0
active_tab = ""
list_settings = ["input_ckpt_path", "checkbox_is_sd_768v_ckpt", "checkbox_is_sd_2x_ckpt",
                 "checkbox_is_use_vae", "input_vae_path", "input_img_path", "checkbox_is_use_reg_images",
                 "input_reg_img_path",
                 "input_output_path", "input_output_name", "radio_training_duration_method", "input_epochs_number",
                 "time_picker", "input_training_speed", "combo_training_speed_type", "input_custom_steps",
                 "input_save_every_n_epochs", "input_save_last_n_epochs",
                 "input_learning_rate", "input_unet_learning_rate", "input_TE_learning_rate", "input_learning_rate",
                 "combo_scheduler", "slider_float_lr_warmup_ratio", "input_resolution", "slider_int_clip_skip",
                 "input_network_dim", "input_network_alpha", "checkbox_shuffle_caption", "combo_max_token_length",
                 "input_keep_tokens", "input_seed", "checkbox_grad_ckpt", "input_grad_accum_steps",
                 "input_max_data_loader_workers", "combo_save_precision", "combo_mixed_precision", "input_log_dir",
                 "checkbox_custom_log_prefix", "input_custom_log_prefix", "input_custom_parameters",
                 "checkbox_separate_lr"]


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
    filename = str(gui.get_value("input_output_name" + suffix)) + "_settings.ini"
    with open(filename, "w") as file:
        print("Записываем настройки в файл:", filename)
        file.writelines(settings_file)
        _info_popup("Настройки экспортированы в файл\n"
                    "" + filename)


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def import_settings(data):
    if get_active_tab() == 0:
        return
    suffix = append_caller_instance(get_active_tab())
    settings_file = open(data, "r").readlines()
    # print(settings_file)
    for line in settings_file:
        line_split = line.split(": ", 1)
        item = line_split[0].strip() + suffix
        value = line_split[-1].strip()
        if gui.does_item_exist(item):
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


def path_button(tag, path_type, label):
    if path_type == "folder":
        callback = path_dialog_show
    if path_type == "file":
        callback = file_dialog_show
    return gui.add_button(tag = tag, label = label, callback = callback)


def calculate_total_images(caller):
    suffix = append_caller_instance(caller)
    main_image_folder = gui.get_value("input_img_path" + suffix)
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


'''def lora_tab_name(caller):
    suffix = append_caller_instance(caller)
    gui.set_item_label("tab_lora" + suffix, gui.get_value("input_output_name" + suffix))
    if gui.get_item_label("tab_lora" + suffix) == "":
        gui.set_item_label("tab_lora" + suffix, "Tab " + get_caller_instance(caller))'''


def lora_tab_update_name(caller):
    suffix = append_caller_instance(caller)
    gui.set_item_label("tab_lora" + suffix, gui.get_value("input_output_name" + suffix))
    if gui.get_value("input_output_name" + suffix) == "":
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
    if gui.get_value("checkbox_separate_lr" + suffix):
        gui.show_item("group_custom_lr" + suffix)
        gui.hide_item("group_main_lr" + suffix)
    if not gui.get_value("checkbox_separate_lr" + suffix):
        gui.show_item("group_main_lr" + suffix)
        gui.hide_item("group_custom_lr" + suffix)


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
    if gui.get_value("checkbox_is_sd_2x_ckpt" + suffix):
        gui.show_item("checkbox_is_sd_768v_ckpt" + suffix)
    else:
        gui.set_value("checkbox_is_sd_768v_ckpt" + suffix, False)
        gui.hide_item("checkbox_is_sd_768v_ckpt" + suffix)


def reg_images(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("checkbox_is_use_reg_images" + suffix):
        gui.show_item("group_reg_images" + suffix)
    else:
        gui.hide_item("group_reg_images" + suffix)
        gui.set_value("input_reg_img_path" + suffix, "")


def use_vae(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("checkbox_is_use_vae" + suffix):
        gui.show_item("group_vae_path" + suffix)
    else:
        gui.hide_item("group_vae_path" + suffix)
        gui.set_value("input_vae_path" + suffix, "")


def custom_log_prefix(caller):
    suffix = append_caller_instance(caller)
    if gui.get_value("checkbox_custom_log_prefix" + suffix):
        gui.show_item("group_custom_log_prefix" + suffix)
    else:
        gui.hide_item("group_custom_log_prefix" + suffix)
        gui.set_value("input_custom_log_prefix" + suffix, "")


def scheduler(caller):
    suffix = append_caller_instance(caller)
    if not gui.get_value("combo_scheduler" + suffix) == "constant":
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
    gui.set_value("input_output_name" + send_to_suffix, gui.get_value("input_output_name" + send_to_suffix) + "_copy")
    gui.set_value("combo_lora_list", "")


def get_active_tab():
    return gui.get_value("tab_bar_main_panel")


def close_modal_run():
    gui.hide_item("modal_run")


def training_duration_method(caller):
    suffix = append_caller_instance(caller)
    methods = { "Использовать эпохи": "group_epochs_number" + suffix,
                "Обучать в течении времени": "group_training_time" + suffix,
                "Своё количество шагов": "group_custom_steps" + suffix }
    gui.show_item(methods.get(gui.get_value("radio_training_duration_method" + suffix)))
    del methods[gui.get_value("radio_training_duration_method" + suffix)]
    for method in methods:
        gui.hide_item(methods.get(method))
    gui.set_value("text_max_train_steps" + suffix, train_steps(caller, "value"))


def train_steps(caller, request):
    suffix = append_caller_instance(caller)
    max_train_steps = 0
    if gui.get_value("radio_training_duration_method" + suffix) == "Использовать эпохи":
        max_train_epochs = int(gui.get_value('input_epochs_number' + suffix))
        if gui.get_value("checkbox_is_use_reg_images" + suffix):
            max_train_steps *= 2
        total_images = calculate_total_images(suffix)
        if not total_images:
            return "нет изображений"
        elif total_images < 0:
            return "неверная папка"
        else:
            max_train_steps = calculate_total_images(suffix) / \
                              int(gui.get_value("input_train_batch_size" + suffix)) * max_train_epochs
            if request == "value":
                return int(max_train_steps)
            if request == "arg":
                return f" --max_train_epochs={gui.get_value('input_epochs_number' + suffix)}"
    elif gui.get_value("radio_training_duration_method" + suffix) == "Обучать в течении времени":
        training_speed = float(gui.get_value("input_training_speed" + suffix))
        if gui.get_value("combo_training_speed_type" + suffix) == "s/it":
            training_speed = 1 / training_speed
        time_picker_dict = gui.get_value("time_picker" + suffix)
        training_time_minutes = time_picker_dict['min'] + time_picker_dict['sec'] / 60 + time_picker_dict['hour'] * 60
        max_train_steps = training_speed * 60 * int(training_time_minutes)
        # if gui.get_value("checkbox_is_use_reg_images" + suffix) == True:
        # max_train_steps *= 2
        if request == "value":
            return int(max_train_steps)
        if request == "arg":
            return f" --max_train_steps={int(max_train_steps)}"
    else:
        max_train_steps = gui.get_value('input_custom_steps' + suffix)
        if request == "value":
            return max_train_steps
        if request == "arg":
            return f" --max_train_steps={int(max_train_steps)}"


def RUN():
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
        gui.set_value("text_training_path", "...\\" + gui.get_value('input_output_name' + suffix) + ".safetensors")
        gui.show_item("modal_training")

        commands = "[console]::OutputEncoding = [text.encoding]::UTF8\n"
        # блять jfs ебать ты чед
        commands += "$env:PYTHONIOENCODING = 'utf-8'\n"
        commands += f"Set-Location \"{gui.get_value('input_sdscripts_path')}\"\n"
        commands += ".\\venv\Scripts\\activate\n"

        # \"{ gui.get_value('' + suffix) }\"
        commands += f"accelerate launch --num_cpu_threads_per_process {gui.get_value('input_max_data_loader_workers' + suffix)}" \
                    f" train_network.py --network_module=networks.lora" \
                    f" --pretrained_model_name_or_path=\"{remove_trailing_slashes(gui.get_value('input_ckpt_path' + suffix))}\"" \
                    f" --train_data_dir=\"{remove_trailing_slashes(gui.get_value('input_img_path' + suffix))}\"" \
                    f" --output_dir=\"{remove_trailing_slashes(gui.get_value('input_output_path' + suffix))}\"" \
                    f" --output_name=\"{gui.get_value('input_output_name' + suffix)}\"" \
                    f" --save_every_n_epochs={gui.get_value('input_save_every_n_epochs' + suffix)}" \
                    f" --save_last_n_epochs={gui.get_value('input_save_last_n_epochs' + suffix)}" \
                    f" --lr_scheduler={gui.get_value('combo_scheduler' + suffix)}" \
                    f" --resolution=\"{gui.get_value('input_resolution' + suffix)}\"" \
                    f" --network_dim={gui.get_value('input_network_dim' + suffix)}" \
                    f" --keep_tokens={gui.get_value('input_keep_tokens' + suffix)}" \
                    f" --gradient_accumulation_steps={gui.get_value('input_grad_accum_steps' + suffix)}" \
                    f" --max_data_loader_n_workers={gui.get_value('input_max_data_loader_workers' + suffix)}" \
                    f" --save_precision={gui.get_value('combo_save_precision' + suffix)}" \
                    f" --mixed_precision={gui.get_value('combo_mixed_precision' + suffix)}"
                    # f" --learning_rate={round(gui.get_value('input_learning_rate' + suffix), 8)}" \
                    # f" --unet_lr={round(gui.get_value('input_unet_learning_rate' + suffix), 8)}" \
                    # f" --text_encoder_lr={round(gui.get_value('input_TE_learning_rate' + suffix), 8)}"

        if gui.get_value("checkbox_separate_lr" + suffix):
            commands += f" --unet_lr={decimal.Decimal(gui.get_value('input_unet_learning_rate' + suffix))}"
            commands += f" --text_encoder_lr={decimal.Decimal(gui.get_value('input_TE_learning_rate' + suffix))}"
        else:
            commands += f" --learning_rate={decimal.Decimal(gui.get_value('input_learning_rate' + suffix))}"


        if gui.get_value("checkbox_is_sd_2x_ckpt" + suffix):
            commands += " --v2"
            if gui.get_value("checkbox_is_sd_768v_ckpt" + suffix):
                commands += " --v_parameterization"

        if gui.get_value("checkbox_is_use_reg_images" + suffix):
            commands += f" --reg_data_dir=\"{remove_trailing_slashes(gui.get_value('input_reg_img_path' + suffix))}\""

        if gui.get_value("checkbox_is_use_vae" + suffix):
            commands += f" --vae=\"{remove_trailing_slashes(gui.get_value('input_vae_path' + suffix))}\""

        max_train_steps = train_steps(suffix, "value")
        commands += train_steps(suffix, "arg")

        if not gui.get_value('combo_scheduler' + suffix) == "constant":
            try:
                commands += f" --lr_warmup_steps=" \
                            f"{int((gui.get_value('slider_float_lr_warmup_ratio' + suffix) / 100) * int(max_train_steps))}"
            except ValueError:
                pass

        if not gui.get_value('slider_int_clip_skip' + suffix) == "1":
            commands += f" --clip_skip={gui.get_value('slider_int_clip_skip' + suffix)}"

        network_alpha = gui.get_value('input_network_alpha' + suffix)

        if network_alpha:
            if not network_alpha == "0":
                commands += f" --network_alpha={network_alpha}"

        if gui.get_value('checkbox_shuffle_caption' + suffix):
            commands += " --shuffle_caption"

        if not gui.get_value('combo_max_token_length' + suffix) == "75":
            commands += f" --max_token_length={gui.get_value('combo_max_token_length' + suffix)}"

        seed = gui.get_value('input_seed' + suffix)
        if gui.get_value('input_seed' + suffix) == "-1":
            seed = random.randint(1, 2147483647)
        commands += f" --seed={seed}"

        if gui.get_value('checkbox_grad_ckpt' + suffix):
            commands += " --gradient_checkpointing"

        if not gui.get_value('input_log_dir' + suffix) == "":
            commands += f" --logging_dir=\"{gui.get_value('input_log_dir' + suffix)}\""
            log_prefix = gui.get_value('input_output_name' + suffix) + "_"
            if gui.get_value('checkbox_custom_log_prefix' + suffix):
                log_prefix = gui.get_value('input_custom_log_prefix' + suffix)
            commands += f" --log_prefix=\"{log_prefix}\""

        commands += f" {gui.get_value('input_custom_parameters' + suffix)}\n"
        proc = subprocess.Popen("powershell", stdin = subprocess.PIPE).communicate(input = commands.encode())
        # proc

    gui.hide_item("modal_training")


def calculate_scheduler_plot_data():
    sindatax = []; sindatay = []
    scheduler = gui.get_value("combo_scheduler")
    if scheduler == "linear":
        sindatax.append([0, gui.get_value("slider_float_lr_warmup_ratio") / 100, 1])
        sindatay.append([0, 1, 0])
    gui.get_item_configuration("plot_line_series")


tab_number = 0


def add_lora_tab():
    global lora_tab_instances
    lora_tab_instances += 1
    # tab_number = 0
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
                    gui.add_input_text(tag = append_instance_number("input_ckpt_path"),
                                       hint = "X:\models\checkpoint.safetensors", width = -1)
                # sd 2.x checkboxes
                with gui.group(horizontal = True):
                    gui.add_checkbox(tag = append_instance_number("checkbox_is_sd_768v_ckpt"), label = "768-v",
                                     show = False)
                    gui.add_checkbox(tag = append_instance_number("checkbox_is_sd_2x_ckpt"),
                                     label = "Stable Diffusion 2.x",
                                     before = append_instance_number("checkbox_is_sd_768v_ckpt"))
                    gui.bind_item_handler_registry(append_instance_number("checkbox_is_sd_2x_ckpt"),
                                                   append_instance_number("handler_checkbox"))

                # vae checkbox
                gui.add_checkbox(tag = append_instance_number("checkbox_is_use_vae"), label = "Использовать VAE",
                                 callback = use_vae)

                # vae
                with gui.group(tag = append_instance_number("group_vae_path"), horizontal = True, show = False):
                    path_button(tag = append_instance_number("button_vae_path"), path_type = "file",
                                label = "VAE чекпоинт")
                    gui.add_input_text(tag = append_instance_number("input_vae_path"), hint = "X:\models\\vae.pt",
                                       width = -1)
                    gui.bind_item_handler_registry(append_instance_number("checkbox_is_use_vae"),
                                                   append_instance_number("handler_checkbox"))

                # images dir
                with gui.group(horizontal = True):
                    path_button(tag = append_instance_number("button_img_path"), path_type = "folder",
                                label = "Папка с изображениями")
                    gui.add_input_text(tag = append_instance_number("input_img_path"), hint = "X:\\training_data\img",
                                       width = -1)

                # use reg images
                gui.add_checkbox(tag = append_instance_number("checkbox_is_use_reg_images"),
                                 label = "Использовать рег. изображения",
                                 callback = reg_images)
                gui.bind_item_handler_registry(append_instance_number("checkbox_is_use_reg_images"),
                                               append_instance_number("handler_checkbox"))

                # reg images dir
                with gui.group(tag = append_instance_number("group_reg_images"), horizontal = True, show = False):
                    path_button(tag = append_instance_number("button_reg_img_path"),
                                path_type = "folder",
                                label = "Папка с рег. изображениями")
                    gui.add_input_text(tag = append_instance_number("input_reg_img_path"),
                                       hint = "X:\\training_data\img", width = -1)

                # output dir
                with gui.group(horizontal = True):
                    path_button(tag = append_instance_number("button_output_path"),
                                path_type = "folder",
                                label = "Папка сохранения файла")
                    gui.add_input_text(tag = append_instance_number("input_output_path"), hint = "X:\LoRA",
                                       width = -1)

                # output name
                with gui.group(horizontal = True):
                    gui.add_text("Имя файла")
                    gui.add_input_text(tag = append_instance_number("input_output_name"), hint = "my_LoRA_network",
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

                gui.add_radio_button(tag = append_instance_number("radio_training_duration_method"),
                                     items = ["Использовать эпохи", "Обучать в течении времени",
                                              "Своё количество шагов"], default_value = "Использовать эпохи",
                                     horizontal = True, callback = training_duration_method)
                gui.bind_item_handler_registry(append_instance_number("radio_training_duration_method"),
                                               append_instance_number("handler_radio"))

                gui.add_separator()

                with gui.group():
                    with gui.group(tag = append_instance_number("group_epochs_number"), horizontal = True, show = True):
                        gui.add_text("Количество эпох")
                        gui.add_input_text(tag = append_instance_number("input_epochs_number"), default_value = '10',
                                           width = -1, decimal = True)
                    with gui.group(tag = append_instance_number("group_training_time"), show = False):
                        with gui.group(horizontal = True):
                            gui.add_text("Время обучения")
                            gui.add_time_picker(hour24 = True, default_value = { 'hour': 0, 'min': 60, 'sec': 0 },
                                                tag = append_instance_number("time_picker"))

                        with gui.group(horizontal = True):
                            gui.add_text("Скорость обучения")
                            gui.add_input_text(tag = append_instance_number("input_training_speed"),
                                               default_value = '1.00', width = 120, decimal = True)
                            gui.add_combo(tag = append_instance_number("combo_training_speed_type"),
                                          items = ["it/s", "s/it"], width = -1, default_value = "it/s")
                    with gui.group(tag = append_instance_number("group_custom_steps"), horizontal = True, show = False):
                        gui.add_text("Количество шагов")
                        gui.add_input_text(tag = append_instance_number("input_custom_steps"), default_value = '1000',
                                           width = -1)

                gui.add_separator()

                with gui.group(horizontal = True):
                    gui.add_text("Размер обучающей партии")
                    gui.add_input_text(tag = append_instance_number("input_train_batch_size"), default_value = '1',
                                       width = -1, decimal = True)

                with gui.group(horizontal = True):
                    gui.add_text("Сохранять чекпоинт каждые")
                    gui.add_input_text(tag = append_instance_number("input_save_every_n_epochs"), default_value = '1',
                                       width = 100, decimal = True)
                    gui.add_text("эпох")
                with gui.group(horizontal = True):
                    gui.add_text("Сохранять только последние")
                    gui.add_input_text(tag = append_instance_number("input_save_last_n_epochs"), default_value = '1',
                                       width = 100, decimal = True)
                    gui.add_text("эпох")

            with gui.tab(label = "Настройки"):
                with gui.collapsing_header(label = "Обучение"):
                    with gui.group(horizontal = True):
                        gui.add_text("Использовать раздельные скорости обучения")
                        gui.add_checkbox(tag = append_instance_number("checkbox_separate_lr"), default_value = False)

                    gui.bind_item_handler_registry(append_instance_number("checkbox_separate_lr"),
                                                   append_instance_number("handler_checkbox"))

                    with gui.group(horizontal = True, tag = append_instance_number("group_main_lr")):
                        gui.add_text("Скорость обучения")
                        gui.add_input_text(tag = append_instance_number("input_learning_rate"),
                                           default_value = '1e-3', width = -1, scientific = True)

                    with gui.group(tag = append_instance_number("group_custom_lr"), show = False):
                        with gui.group(horizontal = True):
                            gui.add_text("Скорость обучения UNet")
                            gui.add_input_text(tag = append_instance_number("input_unet_learning_rate"),
                                               default_value = '1e-3', width = -1, scientific = True)

                        with gui.group(horizontal = True):
                            gui.add_text("Скорость обучения TE")
                            _help("ТЕ - текстовый энкодер")
                            gui.add_input_text(tag = append_instance_number("input_TE_learning_rate"),
                                               default_value = '1e-3', width = -1, scientific = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Планировщик")
                        gui.add_combo(["linear", "cosine", "cosine_with_restarts", "polynomial",
                                       "constant", "constant_with_warmup"],
                                      tag = append_instance_number("combo_scheduler"),
                                      default_value = "linear", width = -1, callback = scheduler)

                    gui.bind_item_handler_registry(append_instance_number("combo_scheduler"),
                                                   append_instance_number("handler_combo"))

                    with gui.group(tag = append_instance_number("group_warmup_ratio"), horizontal = True, show = True):
                        gui.add_text("Разогрев планировщика")
                        _help("Количество шагов в начале обучения,\n"
                              "в течении которых скорость обучения\n"
                              "будет линейно возрастать до значения\n"
                              "указанного выше.")
                        gui.add_slider_float(tag = append_instance_number("slider_float_lr_warmup_ratio"), width = -1,
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
                        gui.add_input_text(tag = append_instance_number("input_resolution"),
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
                        gui.add_slider_int(tag = append_instance_number("slider_int_clip_skip"),
                                           default_value = 1, width = 50, min_value = 1, max_value = 2)

                    with gui.group(horizontal = True):
                        gui.add_text("Размер (ранк) сети")
                        gui.add_input_text(tag = append_instance_number("input_network_dim"),
                                           default_value = '128', width = -1, decimal = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Альфа сети")
                        _help("Добавлено в версии sd-scripts 0.4.0.\n"
                              "Если у вас старая версия, оставьте поле\n"
                              "пустым или поставьте 0.")
                        gui.add_input_text(tag = append_instance_number("input_network_alpha"),
                                           default_value = '1', width = -1, decimal = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Перемешивание описаний")
                        _help("Теги, написанные через запятую в файлах описания\n"
                              "будут перемешиваться. Делает обучение текстового\n"
                              "энкодера более гибким.")
                        gui.add_checkbox(tag = append_instance_number("checkbox_shuffle_caption"), default_value = True)

                    with gui.group(horizontal = True):
                        gui.add_text("Макс. длина токена")
                        gui.add_combo(['75', '150', '225'], tag = append_instance_number("combo_max_token_length"),
                                      default_value = '225', width = -1)

                    with gui.group(horizontal = True):
                        gui.add_text("Защитить от перемешивания первые")
                        gui.add_input_text(tag = append_instance_number("input_keep_tokens"),
                                           default_value = '1', width = 120, decimal = True)
                        gui.add_text("токенов")

                    with gui.group(horizontal = True):
                        gui.add_text("Сид")
                        _help("-1 = рандомный сид")
                        gui.add_input_text(tag = append_instance_number("input_seed"),
                                           default_value = '-1', width = -1, decimal = True)
                    # gui.add_separator()

            with gui.tab(label = "Дополнительно"):
                with gui.group(horizontal = True):
                    gui.add_text("custom_parameters")
                    gui.add_input_text(tag = append_instance_number("input_custom_parameters"),
                                       default_value = "--caption_extension=\".txt\" --prior_loss_weight=1 "
                                                       "--enable_bucket --min_bucket_reso=256 --max_bucket_reso=1024 --use_8bit_adam "
                                                       "--xformers --save_model_as=safetensors --cache_latents",
                                       width = -1, height = 100)
                with gui.group(horizontal = True):
                    gui.add_text("gradient_checkpointing")
                    gui.add_checkbox(tag = append_instance_number("checkbox_grad_ckpt"), default_value = False)

                with gui.group(horizontal = True):
                    gui.add_text("gradient_accumulation_steps")
                    gui.add_input_text(tag = append_instance_number("input_grad_accum_steps"),
                                       default_value = '1', width = -1, decimal = True)

                with gui.group(horizontal = True):
                    gui.add_text("max_data_loader_n_workers")
                    _help("Выделяемое количество потоков\n"
                          "процессора для DataLoader. Маленькие\n"
                          "значения могут негативно сказаться\n"
                          "скорости обучения.")
                    gui.add_input_text(tag = append_instance_number("input_max_data_loader_workers"),
                                       default_value = '8', width = -1, decimal = True)

                with gui.group(horizontal = True):
                    gui.add_text("save_precision")
                    gui.add_combo(["float", "fp16", "bf16"], tag = append_instance_number("combo_save_precision"),
                                  default_value = "fp16", width = -1)

                with gui.group(horizontal = True):
                    gui.add_text("mixed_precision")
                    gui.add_combo(["fp16", "bf16"], tag = append_instance_number("combo_mixed_precision"),
                                  default_value = "fp16", width = -1)

                with gui.group(horizontal = True):
                    button_img_path = path_button(tag = append_instance_number("button_log_dir"), path_type = "folder",
                                                  label = "logging_dir")
                    gui.add_input_text(tag = append_instance_number("input_log_dir"), hint = "X:\\LoRA\\logs\\",
                                       width = -1)

                with gui.group(horizontal = True):
                    gui.add_text("custom log_prefix")
                    gui.add_checkbox(tag = append_instance_number("checkbox_custom_log_prefix"), default_value = False,
                                     callback = custom_log_prefix)

                with gui.group(tag = append_instance_number("group_custom_log_prefix"), horizontal = True,
                               show = False):
                    gui.add_text("log_prefix")
                    gui.add_input_text(tag = append_instance_number("input_custom_log_prefix"),
                                       default_value = "", width = -1)
                    gui.bind_item_handler_registry(append_instance_number("checkbox_custom_log_prefix"),
                                                   append_instance_number("handler_checkbox"))
