
def getImageFromScanner():

    try:
        import pyinsane2
    except:
        print "Scanning feature not supported on this OS. Disabling it..."


    pyinsane2.init()
    try:
        devices = pyinsane2.get_devices()
        assert(len(devices) > 0)
        device = devices[0]
        print("I'm going to use the following scanner: %s" % (str(device)))

        pyinsane2.set_scanner_opt(device, 'resolution', [75])

    # Beware: Some scanners have "Lineart" or "Gray" as default mode
    # better set the mode everytime

    # Beware: by default, some scanners only scan part of the area
    # they could scan.
        pyinsane2.maximize_scan_area(device)

        scan_session = device.scan(multiple=False)
        try:
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        finally:
            image = scan_session.images[-1]
            return image
    finally:
        pyinsane2.exit()
        return None

if __name__ == '__main__':
    img  = getImageFromScanner()
    img.save('outFromScan.jpg' , 'JPEG')
