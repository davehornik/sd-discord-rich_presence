import gradio as gr
from modules import script_callbacks
from modules import ui
from modules import shared
import threading
import time, os

github_link = "https://github.com/kabachuha/discord-rpc-for-automatic1111-webui"

enable_dynamic_status = False

def start_rpc():
    print('Launching the Discord RPC extension. By https://github.com/kabachuha, version 0.1b')
    print(f'Use this link to report any problems or add suggestions {github_link}')
    from launch import is_installed, run_pip
    if not is_installed("discord-rpc"):
        print("Installing the missing 'discord-rpc' package and its dependencies,")
        print("In case it will give a package error after the installation, restart the webui.")
        run_pip("install discord-rpc", "discord-rpc")
    if enable_dynamic_status:
        print("Remember that it uses multithreading, so there may occur cases when the whole program freezes")
        print("In such cases close the webui, go to the 'extensions' folder and remove the plugin")
    
    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)
    
    import DiscordRPC
    import time
    
    rpc = DiscordRPC.RPC.Set_ID(app_id=1065987911486550076)
    rpc.set_activity(
              state="Waiting for the start" if enable_dynamic_status else "*dynamic status is wip*",
              details=model_name,
              large_image="unknown" if enable_dynamic_status else "auto",
              timestamp=rpc.timestamp()
            )
    
    def RPC_thread(rpc):
        print('Starting the RPC thread')
        rpc.run()
    rpc_watcher = threading.Thread(target=RPC_thread, args=(rpc,), daemon=True)
    rpc_watcher.start()
    if enable_dynamic_status:
        state_watcher = threading.Thread(target=check_progress_loop, args=(rpc,RPC_thread,), daemon=True)
        state_watcher.start()
    print("If everything is fine, the RPC should be running by now. Proceed to your Discord settings and add the app (it's name is huge) to the game list.")
    
def on_ui_tabs():
    start_rpc()
    return []

script_callbacks.on_ui_tabs(on_ui_tabs)

# Dynamic status check #FIXME deadlock happens
def check_progress_loop(rpc,RPC_thread):
    while True:
        checkpoint_info = shared.sd_model.sd_checkpoint_info
        model_name = os.path.basename(checkpoint_info.filename)
        if shared.state.job_count == 0:
            rpc.set_activity(large_image="auto", details=model_name, state="Idle", timestamp=rpc.timestamp())
        else:
            rpc.set_activity(large_image="generating", details=model_name, state=f'generating {shared.state.job_count} pics', timestamp=rpc.timestamp())
        time.sleep(1) # update once per second
