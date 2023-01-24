import webbrowser

import dearpygui.dearpygui as dpg


def show_fonts():
    dpg.show_font_manager()


def show_info():
    pass


def open_link_guide():
    webbrowser.open_new_tab("https://rentry.org/2chAI_LoRA_Dreambooth_guide")


def open_link_technothread():
    webbrowser.open_new_tab("https://rentry.org/2chAI_LoRA_Dreambooth_guide")


def path_dialog_show(sender):
    item = "path_dialog"
    send_to = sender.replace("button_", "input_", 1)
    dpg.show_item(item)
    dpg.set_item_user_data(item, send_to)


def file_dialog_show(sender):
    item = "file_dialog"
    send_to = sender.replace("button_", "input_", 1)
    dpg.show_item(item)
    dpg.set_item_user_data(item, send_to)


def file_dialog_ok(sender, app_data, user_data):
    print("Sending ", app_data["file_path_name"], " to ", user_data)
    dpg.set_value(user_data, app_data["file_path_name"])



def file_dialog_cancel():
    pass

def sd_2x():
    if not dpg.is_item_shown("is_sd_768v_ckpt"):
        dpg.show_item("is_sd_768v_ckpt")
    else:
        dpg.hide_item("is_sd_768v_ckpt")


def reg_images():
    if not dpg.is_item_shown("group_reg_images"):
        dpg.show_item("group_reg_images")
    else:
        dpg.hide_item("group_reg_images")
        dpg.set_value("input_reg_img_path", "")

def use_vae():
    if not dpg.is_item_shown("group_vae_path"):
        dpg.show_item("group_vae_path")
    else:
        dpg.hide_item("group_vae_path")
        dpg.set_value("input_vae_path", "")
