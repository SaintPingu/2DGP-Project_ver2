if __name__ == "__main__":
    quit()

from tools import *

_crnt_bgm : Music = None
_sounds : dict[str, Wav] = {}

def play_bgm(name, volume=128):
    global _crnt_bgm

    if _crnt_bgm != None:
        stop_bgm()
    
    file_name = 'bgm_' + name
    _crnt_bgm = load_music_path(file_name)
    _crnt_bgm.set_volume(volume)
    _crnt_bgm.repeat_play()

def play_battle_bgm(index):
    file_name = 'battle_' + str(index)
    play_bgm(file_name, 64)

def stop_bgm():
    global _crnt_bgm

    _crnt_bgm.stop()
    _crnt_bgm.set_volume(0)
    del _crnt_bgm
    _crnt_bgm = None

def add_sound(name):
    global _sounds
    
    if name in _sounds.keys():
        return

    file_name = 'sound_' + name
    wav = load_wav_path(file_name)

    _sounds[name] = wav

def play_sound(name, volume=128, channel=-1, is_repeat=False):
    assert(name in _sounds)

    wav = _sounds[name]
    wav.set_volume(volume)

    if is_repeat == False:
        Mix_PlayChannel(channel, wav.wav, 0)
    else:
        Mix_PlayChannel(channel, wav.wav, -1)

def stop_sound(name):
    if name not in _sounds:
        return

    sound = _sounds.pop(name)
    sound.set_volume(0)

def stop_channel(channel):
    Mix_HaltChannel(channel)

def enter(state : str):
    if state == 'battle':
        add_sound('tank_fire_general')
        add_sound('tank_fire_homing')
        add_sound('explosion')
        add_sound('tank_explosion')
        add_sound('tank_movement')
        add_sound('lock_on')
        add_sound('air_ship')
        add_sound('crash')
        add_sound('pickup_item')
        add_sound('parachute')
    else:
        assert(0)

def exit():
    for sound in _sounds.values():
        del sound
    _sounds.clear()