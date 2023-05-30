    # Check if the required packages are installed, and install them if necessary
from launch import is_installed, run_pip
if not is_installed("pypresence"):
    print("[Discord Rich Presence]  Installing missing 'pypresence' module and its dependencies,")
    print("[Discord Rich Presence]  In case of module error after the installation -> restart WebUI.")
    run_pip("install pypresence", "pypresence")
else:
    print("[Discord Rich Presence]  Requirements already satisfied, skipping.")
    print('[Discord Rich Presence]  Only working on local instalation. And only w/ desktop Discord app.')