import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()

with dpg.window(tag = "main"):
    dpg.add_text("Hello, world")
    dpg.add_button(label = "Save")
    dpg.add_input_text(label = "string", default_value = "Quick brown fox")
    dpg.add_slider_float(label = "float", default_value = 0.273, max_value=1)

dpg.create_viewport(title='LoRA train GUI', width = 600, height = 400, resizable = False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.start_dearpygui()
dpg.destroy_context()