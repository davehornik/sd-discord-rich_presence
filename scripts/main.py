from modules import script_callbacks
from modules import shared
import threading
import time
import os
import pypresence

github_link = "https://github.com/davehornik/sd-discord-rich_presence"

enable_dynamic_status = True
        
def start_rpc():
    print('[Discord Rich Presence]  Running Discord Rich Presence Extension, version 1.3.0')
    print(f'[Discord Rich Presence]  Bug reporting -> {github_link}')

    checkpoint_info = shared.sd_model.sd_checkpoint_info
    model_name = os.path.basename(checkpoint_info.filename)

    client_id = "1091507869200957450"

    rpc = pypresence.Presence(client_id)
    rpc.connect()

    time_c = time.time()
    rpc.update(
        state="Waiting for the start" if enable_dynamic_status else "Dynamic Status - OFF",
        details=model_name,
        large_image="unknown" if enable_dynamic_status else "auto",
        start=int(time_c)
    )

    state_watcher = threading.Thread(target=state_watcher_thread, args=(rpc, time_c), daemon=True)
    state_watcher.start()

    if enable_dynamic_status:
        print("[Discord Rich Presence]  Make sure that Game Activity is enabled in Discord.")
        print("[Discord Rich Presence]  Should be running already if there's no error.")


def state_watcher_thread(rpc, time_c):
    global reloadedUI
    reloadedUI = False
    reset_time = False
    batch_size_r = False
    batch_size = 0
    status = True
    total_progress = 0
    image_to_show = "small_gen_00"
    percent_show = 0

    dict_images = {
        0: "small_gen_00",
        5: "small_gen_05",
        10: "small_gen_10",
        15: "small_gen_15",
        20: "small_gen_20",
        25: "small_gen_25",
        30: "small_gen_30",
        35: "small_gen_35",
        40: "small_gen_40",
        45: "small_gen_45",
        50: "small_gen_50",
        55: "small_gen_55",
        60: "small_gen_60",
        65: "small_gen_65",
        70: "small_gen_70",
        75: "small_gen_75",
        80: "small_gen_80",
        85: "small_gen_85",
        90: "small_gen_90",
        95: "small_gen_95",
        100: "small_gen_100"
    }

    while reloadedUI is not True:

        checkpoint_info = shared.sd_model.sd_checkpoint_info
        model_name = os.path.basename(checkpoint_info.filename)
        model_name = model_name.split('.')
        model_name = model_name[0]

        if shared.state.job_count == 0:

            if reset_time == False:
                time_c = int(time.time())
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
                time_c = int(time.time())
                reset_time = False

            if batch_size_r == False:
                batch_size = get_batch_size()
                if batch_size != 0:
                    batch_size_r = True
            if shared.total_tqdm._tqdm is not None:

                if status:
                    total_progress = shared.state.sampling_steps * shared.state.job_count
                    status = False

                # This is really nasty line of code please don't look or i will cry :'( Edesak
                progress = shared.total_tqdm._tqdm.n

                percent_progress = progress / total_progress * 100


            else:
                percent_progress = 0

            for image in dict_images:
                if image >= int(percent_progress):
                    image_to_show = dict_images[image]
                    percent_show = image
                    break

            rpc.update(large_image="a1111_gen",
                       small_image=image_to_show,
                       large_text="Generating",
                       small_text=f"{percent_show}%",
                       details=model_name,
                       state=f'Generating {shared.state.job_count * batch_size} image/s',
                       start=time_c)
        # print(reloadedUI)
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

# in dev
# def reloadprint():
#     global reloadedUI
#     reloadedUI = True
#     print (reloadedUI)
# script_callbacks.on_before_reload(reloadprint)