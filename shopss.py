from clicknium import clicknium as cc, ui, locator
from PIL import ImageGrab, Image
from time import sleep, perf_counter
import colorsys
import asyncio
from functools import partial, wraps
import base64

# ============================MACROS===========================
START_MENU_HUE_RANGE = (135, 165)
START_MENU_PIXEL_COORDS = (1615, 1435)
WINR_COORDS = (190, 1932)
WINR_COLOR = (255, 255, 255)
RIOT_LOGO_COLOR = (235, 0, 41)
RIOT_LOGO_PIXEL_COORDS = (1301,728)
OTP_FIELD_COLOR = (238, 238, 238)
OTP_CHECK_PIXEL_COORDS = (1473, 1007)
STORE_BUTTON_LOCATION = (130, 1687)
STORE_PLAY_COLOR = (216, 57, 70)
STORE_PLAY_COORDS = (1993, 64)
SS_UPPER_LEFT = (157, 1520)
SS_LOWER_RIGHT = (3575, 2038)
SETTINGS_COORDS = (3769, 52)
ETD_COORDS = (1918, 1353)
SIGN_OUT_COORDS = (2250, 1223)
LOGIN_CREDS = ("wilson289296", "PlsGrindBPTY<3")
# =============================================================

def to_thread(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        callback = partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, callback)
    return wrapper

@to_thread
def login(username, password):
    start = perf_counter()

    # cc.send_hotkey('{WIN}')

    # # detect start menu open and ready for query

    # starthue = 0
    # while starthue < START_MENU_HUE_RANGE[0] or starthue > START_MENU_HUE_RANGE[1]:
    #     start_pixel = ImageGrab.grab(bbox=(
    #         START_MENU_PIXEL_COORDS[0], 
    #         START_MENU_PIXEL_COORDS[1], 
    #         START_MENU_PIXEL_COORDS[0]+1, 
    #         START_MENU_PIXEL_COORDS[1]+1)).getcolors()[0][1]
    #     starthue = colorsys.rgb_to_hsv(start_pixel[0], start_pixel[1], start_pixel[2])[0] * 255
    #     print(".", end="")
    #     sleep(0.5)
    
    # print("\nStart menu open, launching Valorant Client")

    # cc.send_hotkey('valorant{ENTER}')

    cc.send_hotkey('{WIN DOWN}r{WIN UP}')
    while ImageGrab.grab(bbox=(
        WINR_COORDS[0], 
        WINR_COORDS[1], 
        WINR_COORDS[0]+1, 
        WINR_COORDS[1]+1)).getcolors()[0][1] != WINR_COLOR:
        sleep(0.25)
        print(".", end="")

    cc.send_hotkey("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Riot Games\VALORANT.lnk{ENTER}")
    # ui(locator.explorer.winrfield).click()
    # ui(locator.explorer.winrfield).set_text("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Riot Games\VALORANT.lnk", overwrite=True)
    # sleep(0.1)
    # cc.send_hotkey('{ENTER}')

    while ImageGrab.grab(bbox=(
        RIOT_LOGO_PIXEL_COORDS[0], 
        RIOT_LOGO_PIXEL_COORDS[1], 
        RIOT_LOGO_PIXEL_COORDS[0]+1, 
        RIOT_LOGO_PIXEL_COORDS[1]+1)).getcolors()[0][1] != RIOT_LOGO_COLOR:
        sleep(0.25)
        print(".", end="")

    print("\nriot client loaded")
    # sleep(2)
    ui(locator.riotclientux.riotlogo).click()
    cc.send_hotkey('{TAB}')
    cc.send_hotkey(username)
    cc.send_hotkey('{TAB}')
    cc.send_hotkey(password)
    ui(locator.riotclientux.redbutton).click()

    # OTP IS REQUESTED HERE
    otp_exists = False
    play_exists = False
    print("waiting for OTP/Play")
    while not otp_exists and not play_exists:
        play_exists = cc.is_existing(locator.riotclientux.playbutton)
        if not play_exists:
            otp_exists = cc.is_existing(locator.riotclientux.verif_text)
        print(".", end="")
        sleep(0.25)
    
    if otp_exists:
        return perf_counter() - start, "otp"

    elif play_exists:
        ui(locator.riotclientux.playbutton).click()
        print("\nLogin successful, launching game")

    print("waiting for store")

    in_store = False
    while not in_store:
        # cc.mouse.move()
        cc.mouse.click(STORE_BUTTON_LOCATION[0], STORE_BUTTON_LOCATION[1])
        sleep(0.1)
        # in_store = cc.is_existing(locator.valorant_win64_shipping.storebackbutton)
        if ImageGrab.grab(bbox=(
            STORE_PLAY_COORDS[0], 
            STORE_PLAY_COORDS[1], 
            STORE_PLAY_COORDS[0]+1, 
            STORE_PLAY_COORDS[1]+1)).getcolors()[0][1] == STORE_PLAY_COLOR:
            in_store = True
    
    print("In store, capturing screenshot")
    store_ss = ImageGrab.grab(bbox=(
        SS_UPPER_LEFT[0],
        SS_UPPER_LEFT[1],
        SS_LOWER_RIGHT[0],
        SS_LOWER_RIGHT[1]
    ))
    store_ss.save("ss.png")

    print("signing out and closing valorant")
    # cc.send_hotkey("{ALT DOWN}{F4}{ALT UP}")
    cc.mouse.click(SETTINGS_COORDS[0], SETTINGS_COORDS[1])
    sleep(0.1)
    cc.mouse.click(ETD_COORDS[0], ETD_COORDS[1])
    sleep(0.1)
    cc.mouse.click(SIGN_OUT_COORDS[0], SIGN_OUT_COORDS[1])

    print("done!")
    print(f"elapsed: {perf_counter() - start}s")
    return perf_counter() - start, "done"



if __name__ == "__main__":
    login(LOGIN_CREDS[0], LOGIN_CREDS[1])
    

