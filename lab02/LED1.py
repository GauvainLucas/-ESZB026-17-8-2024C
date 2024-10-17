    sleep(0.1)
    writeLED (filename="direction", value="out")
    writeLED (filename="export", value=LED_NUMBER_20, path=SYSFS_DIR)
    sleep(0.1)
    writeLED (filename="direction", value="out")
    writeLED (filename="export", value=LED_NUMBER_21, path=SYSFS_DIR)
    sleep(0.1)
    writeLED (filename="direction", value="out")
setup()
cpt =0
while (cpt < 5):
    writeLED (filename="value", value="1", path=LED_PATH_20)
    sleep(2000)
    writeLED (filename="value", value="0", path=LED_PATH_20)
    writeLED (filename="value", value="1", path=LED_PATH_21)
    sleep(1000)
    writeLED (filename="value", value="0", path=LED_PATH_21)
    writeLED (filename="value", value="1", path=LED_PATH_16)
    sleep(1000)
    writeLED (filename="value", value="0", path=LED_PATH_16)
    cpt += 1

