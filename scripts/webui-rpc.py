import gradio as gr
from modules import script_callbacks
from modules import ui
from modules import shared
import threading
import time
import os

github_link = "https://github.com/davehornik/sd-discordRPC"

enable_dynamic_status = True


def start_rpc():
    print('Running Discord Rich Presence Extension by https://github.com/davehornik, version 1.0.0')
    print(f'Bug reporting -> {github_link}')

    # Check if the required packages are installed, and install them if necessary
    try:
        import pypresence
    except ImportError:
        print("Installing the missing 'pypresence' package and its dependencies")
        os.system("pip install pypresence")
        import pypresence

    if enable_dynamic_status:
        print("Remember that it uses multithreading, so there may occur cases when the whole program freezes")
        print("In such cases close the webui, go to the 'extensions' folder and remove the plugin")

    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)

    client_id = "1091507869200957450"

    rpc = pypresence.Presence(client_id)
    rpc.connect()

    rpc.update(
        state="Waiting for the start" if enable_dynamic_status else "Dynamic Status - *WIP*",
        details=model_name,
        large_image="unknown" if enable_dynamic_status else "auto",
        start=time.time()
    )

    def RPC_thread(rpc):
        print('RPC thread on bg starting')
        while True:
            rpc.update()

    def state_watcher_thread():
        while True:
            checkpoint_info = shared.sd_model.sd_checkpoint_info
            model_name = os.path.basename(checkpoint_info.filename)
            if shared.state.job_count == 0:
                rpc.update(large_image="a1111", details=model_name,
                           state="Idle", start=time.time())
            else:
                rpc.update(large_image="a1111_gen", details=model_name,
                           state=f'generating {shared.state.job_count} pix', start=time.time())
            time.sleep(2)  # update once per two seconds

    rpc_watcher = threading.Thread(target=RPC_thread, args=(rpc,), daemon=True)
    state_watcher = threading.Thread(target=state_watcher_thread, daemon=True)
    state_watcher.start()
    rpc_watcher.start()

    if enable_dynamic_status:
        print("If everyhing is okey, it should be working already. Make sure u got Game Activity enabled in Discord.")


def on_ui_tabs():
    start_rpc()
    return []


script_callbacks.on_ui_tabs(on_ui_tabs)
