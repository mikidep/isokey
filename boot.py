import usb_midi

from kmk.bootcfg import bootcfg

bootcfg(
    midi=True,
    mouse=False,
    storage=False,
    cdc_console=False,
    keyboard=False,
    consumer_control=False,
    usb_id=("Ultima", "EWI"),
)

usb_midi.enable()
