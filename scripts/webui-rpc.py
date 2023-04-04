import gradio as gr
from modules import script_callbacks
from modules import ui
from modules import shared
import threading
import time
import os

github_link = "https://github.com/davehornik/sd-discord-rich_presence"

enable_dynamic_status = True

def start_rpc():
    print('[Discord Rich Presence]  Running Discord Rich Presence Extension, version 1.1.0')
    print(f'[Discord Rich Presence]  Bug reporting -> {github_link}')

    # Check if the required packages are installed, and install them if necessary
    from launch import is_installed, run_pip
    if not is_installed("pypresence"):
            print("[Discord Rich Presence]  Installing missing 'pypresence' module and its dependencies,")
            print("[Discord Rich Presence]  In case of module error after the installation -> restart WebUI.")
            run_pip("install pypresence", "pypresence")
    else:
        print("[Discord Rich Presence]  'pypresence' module is installed - skipping.")

    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)

    import pypresence

    client_id = "1091507869200957450"

    rpc = pypresence.Presence(client_id)
    rpc.connect()

    time_c = time.time()
    rpc.update(
        state="Waiting for the start" if enable_dynamic_status else "Dynamic Status - OFF",
        details=model_name,
        large_image="unknown" if enable_dynamic_status else "auto",
        start=time_c
    )

    state_watcher = threading.Thread(target=state_watcher_thread, args=(rpc,), daemon=True)
    state_watcher.start()

    if enable_dynamic_status:
        print("[Discord Rich Presence]  Make sure that Game Activity is enabled in Discord.")
        print("[Discord Rich Presence]  Should be running already if there's no error.")
def state_watcher_thread(rpc):
    reset_time = False
    batch_size_r = False
    batch_size = 0

    while True:

        checkpoint_info = shared.sd_model.sd_checkpoint_info
        model_name = os.path.basename(checkpoint_info.filename)
        model_name = model_name.split('.')
        model_name = model_name[0]

        if shared.state.job_count == 0:

            if reset_time == False:
                time_c = time.time()
                reset_time = True

            if batch_size_r == True:
                batch_size_r = False
                batch_size = 0

            rpc.update(large_image="a1111",
                       details=model_name,
                       state="Idle",
                       start=time_c)
        else:
            if reset_time == True:
                time_c = time.time()
                reset_time = False

            if batch_size_r == False:
                batch_size = get_batch_size()
                if batch_size != 0:
                    batch_size_r = True

            rpc.update(large_image="a1111_gen",
                       details=model_name,
                       state=f'Total batch of {shared.state.job_count * batch_size} image/s',
                       start=time_c)

        time.sleep(2)  # update once per two seconds

def on_ui_tabs():
    start_rpc()
    return []

def get_batch_size():

    if shared.state.current_latent != None:
        x = shared.state.current_latent.size()
        x = x[0]
        return x
    else:
        return 0

script_callbacks.on_ui_tabs(on_ui_tabs)