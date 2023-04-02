import gradio as gr
from modules import script_callbacks
from modules import ui
from modules import shared
from modules.txt2img import get_batch_size
import threading
import time
import os


github_link = "https://github.com/davehornik/sd-discordRPC"

enable_dynamic_status = True


def start_rpc():
    print('[Discord-RPC]  Running Discord Rich Presence Extension by https://github.com/davehornik, version 1.0.0')
    print(f'[Discord-RPC]  Bug reporting -> {github_link}')

    # Check if the required packages are installed, and install them if necessary
    from launch import is_installed, run_pip
    if not is_installed("pypresence"):
        print("[Discord-RPC]  Installing missing 'pypresence' module and its dependencies,")
        print("[Discord-RPC]  In case of module error after the installation, restart webui.")
        run_pip("install pypresence", "pypresence")

    if enable_dynamic_status:
        print("[Discord-RPC]  Remember that it uses multithreading, so there may occur cases when the whole program freezes")
        print("[Discord-RPC]  In such cases close the webui, go to the 'extensions' folder and remove the plugin")

    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)

    import pypresence

    client_id = "1091507869200957450"

    rpc = pypresence.Presence(client_id)
    rpc.connect()


    time_c=time.time()
    rpc.update(
        state="Waiting for the start" if enable_dynamic_status else "Dynamic Status - *WIP*",
        details=model_name,
        large_image="unknown" if enable_dynamic_status else "auto",
        start=time_c
        )

#    def RPC_thread(rpc):
#        print('[Discord-RPC]  RPC thread on bg starting')
#        while True:
#            rpc.update()

    def state_watcher_thread():
        reset_time = False
        while True:

            checkpoint_info = shared.sd_model.sd_checkpoint_info
            model_name = os.path.basename(checkpoint_info.filename)
            if shared.state.job_count == 0:
                if reset_time == False:
                    time_c = time.time()
                    reset_time= True

                rpc.update(large_image="a1111", details=model_name,
                           state="Idle", start=time_c)
            else:
                if reset_time == True:
                    time_c = time.time()
                    reset_time= False

                rpc.update(large_image="a1111_gen", details=model_name,
                           state=f'Total batch of {shared.state.job_count*get_batch_size()} image/s', start=time_c)
            time.sleep(2)  # update once per two seconds
            #print(get_batch_size())

#    rpc_watcher = threading.Thread(target=RPC_thread, args=(rpc,), daemon=True)
    state_watcher = threading.Thread(target=state_watcher_thread, daemon=True)
    state_watcher.start()
#    rpc_watcher.start()

    if enable_dynamic_status:
        print("[Discord-RPC]  If everyhing is okey, it should be working already. Make sure u got Game Activity enabled in Discord.")


def on_ui_tabs():
    start_rpc()
    return []


script_callbacks.on_ui_tabs(on_ui_tabs)