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
PLAY_BUTTON_PIXEL_COORDS = (1257, 1450)
PLAY_BUTTON_PIXEL_HUE = (252, 253)
STORE_BUTTON_LOCATION = (130, 1687)
STORE_PLAY_COLOR = (216, 57, 70)
STORE_PLAY_COORDS = (1993, 64)
SS_UPPER_LEFT = (157, 1520)
SS_LOWER_RIGHT = (3575, 2038)
SETTINGS_COORDS = (3769, 52)
ETD_COORDS = (1918, 1353)
SIGN_OUT_COORDS = (2250, 1223)
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

    # ====================== WIN R ==========================
    cc.send_hotkey('{WIN DOWN}r{WIN UP}')
    if not detect_pixel_exact_timeout(WINR_COORDS, WINR_COLOR, 10):
        return perf_counter() - start, "error"
    cc.send_hotkey("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Riot Games\VALORANT.lnk{ENTER}")

    # ===================== RIOT CLIENT =====================
    if not detect_pixel_exact_timeout(RIOT_LOGO_PIXEL_COORDS, RIOT_LOGO_COLOR, 60):
        return perf_counter() - start, "error"
    print("\nriot client loaded")
    cc.mouse.click(RIOT_LOGO_PIXEL_COORDS[0], RIOT_LOGO_PIXEL_COORDS[1]) 
    cc.send_hotkey('{TAB}' + username + '{TAB}' + password + '{ENTER}')

    # ================= RIOT CLIENT OTP/PLAY =================
    otp_exists = False
    play_exists = False
    timeout_start = perf_counter()
    print("waiting for OTP/Play")
    while not otp_exists and not play_exists:
        if perf_counter() - timeout_start > 60:
            # last chance, game may be open to main menu
            print("Testing last chance")
            cc.mouse.click(STORE_BUTTON_LOCATION[0], STORE_BUTTON_LOCATION[1])
            sleep(0.1)
            if detect_pixel_exact(STORE_PLAY_COORDS, STORE_PLAY_COLOR):
                print("Last chance success!")
                ss()
                return perf_counter() - start, "done"
            else:
                print("Last chance failed")
                return perf_counter() - start, "error"
        play_exists = detect_pixel(PLAY_BUTTON_PIXEL_COORDS, PLAY_BUTTON_PIXEL_HUE)
        if not play_exists:
            otp_exists = cc.is_existing(locator.riotclientux.verif_text)
        print(".", end="")
        sleep(0.25)
    
    if otp_exists:
        print("OTP prompt detected")
        return perf_counter() - start, "otp"

    elif play_exists:
        print("Play button detected")
        sleep(3)
        cc.mouse.click(PLAY_BUTTON_PIXEL_COORDS[0], PLAY_BUTTON_PIXEL_COORDS[1])
        
    print("Clicked play, waiting for store")

    # =================== IN GAME =======================
    if in_game():
        return perf_counter() - start, "done"
    else:
        return perf_counter() - start, "error"
    # in_store = False
    # timeout_start = perf_counter()
    # while not in_store:
    #     if perf_counter() - timeout_start > 60:
    #         return perf_counter() - start, "error"
    #     cc.mouse.click(STORE_BUTTON_LOCATION[0], STORE_BUTTON_LOCATION[1])
    #     sleep(0.1)
    #     in_store = detect_pixel_exact(STORE_PLAY_COORDS, STORE_PLAY_COLOR)
    #     # if ImageGrab.grab(bbox=(
    #     #     STORE_PLAY_COORDS[0], 
    #     #     STORE_PLAY_COORDS[1], 
    #     #     STORE_PLAY_COORDS[0]+1, 
    #     #     STORE_PLAY_COORDS[1]+1)).getcolors()[0][1] == STORE_PLAY_COLOR:
    #     #     in_store = True
    
    # print("In store, capturing screenshot")
    # store_ss = ImageGrab.grab(bbox=(
    #     SS_UPPER_LEFT[0],
    #     SS_UPPER_LEFT[1],
    #     SS_LOWER_RIGHT[0],
    #     SS_LOWER_RIGHT[1]
    # ))
    # store_ss.save("ss.png")

    # print("signing out and closing valorant")
    # cc.send_hotkey("{ALT DOWN}{F4}{ALT UP}")
    # cc.mouse.click(SETTINGS_COORDS[0], SETTINGS_COORDS[1])
    # sleep(0.1)
    # cc.mouse.click(ETD_COORDS[0], ETD_COORDS[1])
    # sleep(0.1)
    # cc.mouse.click(SIGN_OUT_COORDS[0], SIGN_OUT_COORDS[1])

    print("done!")
    print(f"elapsed: {perf_counter() - start}s")
    return perf_counter() - start, "done"

@to_thread
def continue_otp(otp):
    start = perf_counter()
    print("Received OTP from user, entering")
    cc.send_hotkey(otp + '{TAB}{ENTER}')
    play_exists = False
    otp_fail = False
    timeout_start = perf_counter()
    print("waiting for OTP/Play")
    while not otp_fail and not play_exists:
        if perf_counter() - timeout_start > 60:
            # last chance, game may be open to main menu
            cc.mouse.click(STORE_BUTTON_LOCATION[0], STORE_BUTTON_LOCATION[1])
            sleep(0.1)
            if detect_pixel_exact(STORE_PLAY_COORDS, STORE_PLAY_COLOR):
                ss()
                return perf_counter() - start, "done"
            else:
                return perf_counter() - start, "error"
        play_exists = detect_pixel(PLAY_BUTTON_PIXEL_COORDS, PLAY_BUTTON_PIXEL_HUE)
        if not play_exists:
            otp_fail = cc.is_existing(locator.riotclientux.invalid_otp)
        print(".", end="")
        sleep(0.25)
    
    if otp_fail:
        return perf_counter() - start, "invalid"
    
    elif play_exists:
        print("Play button detected")
        sleep(3)
        cc.mouse.click(PLAY_BUTTON_PIXEL_COORDS[0], PLAY_BUTTON_PIXEL_COORDS[1])

    print("Clicked play, waiting for store")

    if in_game():
        return perf_counter() - start, "done"
    else:
        return perf_counter() - start, "error"

    # in_store = False
    # timeout_start = perf_counter()
    # while not in_store:
    #     if perf_counter() - timeout_start > 60:
    #         return perf_counter() - start, "error"
    #     cc.mouse.click(STORE_BUTTON_LOCATION[0], STORE_BUTTON_LOCATION[1])
    #     sleep(0.1)
    #     in_store = detect_pixel_exact(STORE_PLAY_COORDS, STORE_PLAY_COLOR)
    
    # print("In store, capturing screenshot")
    # store_ss = ImageGrab.grab(bbox=(
    #     SS_UPPER_LEFT[0],
    #     SS_UPPER_LEFT[1],
    #     SS_LOWER_RIGHT[0],
    #     SS_LOWER_RIGHT[1]
    # ))
    # store_ss.save("ss.png")

    # print("signing out and closing valorant")
    # cc.send_hotkey("{ALT DOWN}{F4}{ALT UP}")

    # print("done!")
    # print(f"elapsed: {perf_counter() - start}s")
    # return perf_counter() - start, "done"
    
def detect_pixel_exact_timeout(coords, color, timeout):
    start = perf_counter()
    while not detect_pixel_exact(coords, color):
        if perf_counter() - start > timeout:
            return False
        sleep(0.25)
    return True

def detect_pixel_exact(coords, color):
    if ImageGrab.grab(bbox=(
        coords[0], 
        coords[1], 
        coords[0]+1, 
        coords[1]+1)).getcolors()[0][1] != color:
        return False
    else:
        return True
    
def detect_pixel(coords, target_hue):
    pixel_color = ImageGrab.grab(bbox=(
        coords[0],
        coords[1],
        coords[0]+1,
        coords[1]+1)).getcolors()[0][1]
    pixel_hue = colorsys.rgb_to_hsv(
        pixel_color[0], 
        pixel_color[1], 
        pixel_color[2])[0] * 255
    if pixel_hue > target_hue[0] and pixel_hue < target_hue[1]:
        return True
    else:
        return False
    
def in_game():
    in_store = False
    timeout_start = perf_counter()
    while not in_store:
        if perf_counter() - timeout_start > 60:
            print("Valorant probably had connectivity error")
            cc.send_hotkey("{ALT DOWN}{F4}{ALT UP}")
            return False
        cc.mouse.click(STORE_BUTTON_LOCATION[0], STORE_BUTTON_LOCATION[1])
        sleep(0.1)
        in_store = detect_pixel_exact(STORE_PLAY_COORDS, STORE_PLAY_COLOR)
    
    return ss()

def ss():
    print("In store, capturing screenshot")
    store_ss = ImageGrab.grab(bbox=(
        SS_UPPER_LEFT[0],
        SS_UPPER_LEFT[1],
        SS_LOWER_RIGHT[0],
        SS_LOWER_RIGHT[1]
    ))
    store_ss.save("ss.png")

    print("signing out and closing valorant")
    cc.send_hotkey("{ALT DOWN}{F4}{ALT UP}")

    print("done!")
    return True
