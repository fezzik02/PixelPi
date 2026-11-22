import argparse
import csv
import os
import time
import sys

from PIL import Image


# 3 bytes per pixel
PIXEL_SIZE = 3
PIXEL_SIZE_SM16716 = 4

# My chips are not working if you send all bits with zero (just the first led is turning off)
# Change the value if pure black is working for you. Or use filter_pixel(BLACK, 1)
SM16716BLACK = bytearray(b'\x01\x01\x01\x01')

BLACK = bytearray(b'\x00\x00\x00')
AQUA = bytearray(b'\x00\xff\xff')
AQUAMARINE = bytearray(b'\x7f\xff\xd4')
AZURE = bytearray(b'\xf0\xff\xff')
BEIGE = bytearray(b'\xf5\xf5\xdc')
BISQUE = bytearray(b'\xff\xe4\xc4')
BLANCHEDALMOND = bytearray(b'\xff\xeb\xcd')
BLUE = bytearray(b'\x00\x00\xff')
BLUEVIOLET = bytearray(b'\x8a\x2b\xe2')
BROWN = bytearray(b'\xa5\x2a\x2a')
BURLYWOOD = bytearray(b'\xde\xb8\x87')
CADETBLUE = bytearray(b'\x5f\x9e\xa0')
CHARTREUSE = bytearray(b'\x7f\xff\x00')
CHOCOLATE = bytearray(b'\xd2\x69\x1e')
CORAL = bytearray(b'\xff\x7f\x50')
CORNFLOWERBLUE = bytearray(b'\x64\x95\xed')
CORNSILK = bytearray(b'\xff\xf8\xdc')
CRIMSON = bytearray(b'\xdc\x14\x3c')
CYAN = bytearray(b'\x00\xff\xff')
DARKBLUE = bytearray(b'\x00\x00\x8b')
DARKCYAN = bytearray(b'\x00\x8b\x8b')
DARKGOLDENROD = bytearray(b'\xb8\x86\x0b')
DARKGRAY = bytearray(b'\xa9\xa9\xa9')
DARKGREY = bytearray(b'\xa9\xa9\xa9')
DARKGREEN = bytearray(b'\x00\x64\x00')
DARKKHAKI = bytearray(b'\xbd\xb7\x6b')
DARKMAGENTA = bytearray(b'\x8b\x00\x8b')
DARKOLIVEGREEN = bytearray(b'\x55\x6b\x2f')
DARKORANGE = bytearray(b'\xff\x8c\x00')
DARKORCHID = bytearray(b'\x99\x32\xcc')
DARKRED = bytearray(b'\x8b\x00\x00')
DARKSALMON = bytearray(b'\xe9\x96\x7a')
DARKSEAGREEN = bytearray(b'\x8f\xbc\x8f')
DARKSLATEBLUE = bytearray(b'\x48\x3d\x8b')
DARKSLATEGRAY = bytearray(b'\x2f\x4f\x4f')
DARKSLATEGREY = bytearray(b'\x2f\x4f\x4f')
DARKTURQUOISE = bytearray(b'\x00\xce\xd1')
DARKVIOLET = bytearray(b'\x94\x00\xd3')
DEEPPINK = bytearray(b'\xff\x14\x93')
DEEPSKYBLUE = bytearray(b'\x00\xbf\xff')
DIMGRAY = bytearray(b'\x69\x69\x69')
DIMGREY = bytearray(b'\x69\x69\x69')
DODGERBLUE = bytearray(b'\x1e\x90\xff')
FIREBRICK = bytearray(b'\xb2\x22\x22')
FLORALWHITE = bytearray(b'\xff\xfa\xf0')
FORESTGREEN = bytearray(b'\x22\x8b\x22')
FUCHSIA = bytearray(b'\xff\x00\xff')
GAINSBORO = bytearray(b'\xdc\xdc\xdc')
GHOSTWHITE = bytearray(b'\xf8\xf8\xff')
GOLD = bytearray(b'\xff\xd7\x00')
GOLDENROD = bytearray(b'\xda\xa5\x20')
GRAY = bytearray(b'\x80\x80\x80')
GREY = bytearray(b'\x80\x80\x80')
GREEN = bytearray(b'\x00\x80\x00')
GREENYELLOW = bytearray(b'\xad\xff\x2f')
HONEYDEW = bytearray(b'\xf0\xff\xf0')
HOTPINK = bytearray(b'\xff\x69\xb4')
INDIANRED = bytearray(b'\xcd\x5c\x5c')
INDIGO = bytearray(b'\x4b\x00\x82')
IVORY = bytearray(b'\xff\xff\xf0')
KHAKI = bytearray(b'\xf0\xe6\x8c')
LAVENDER = bytearray(b'\xe6\xe6\xfa')
LAVENDERBLUSH = bytearray(b'\xff\xf0\xf5')
LAWNGREEN = bytearray(b'\x7c\xfc\x00')
LEMONCHIFFON = bytearray(b'\xff\xfa\xcd')
LIGHTBLUE = bytearray(b'\xad\xd8\xe6')
LIGHTCORAL = bytearray(b'\xf0\x80\x80')
LIGHTCYAN = bytearray(b'\xe0\xff\xff')
LIGHTGOLDENRODYELLOW = bytearray(b'\xfa\xfa\xd2')
LIGHTGRAY = bytearray(b'\xd3\xd3\xd3')
LIGHTGREY = bytearray(b'\xd3\xd3\xd3')
LIGHTGREEN = bytearray(b'\x90\xee\x90')
LIGHTPINK = bytearray(b'\xff\xb6\xc1')
LIGHTSALMON = bytearray(b'\xff\xa0\x7a')
LIGHTSEAGREEN = bytearray(b'\x20\xb2\xaa')
LIGHTSKYBLUE = bytearray(b'\x87\xce\xfa')
LIGHTSLATEGRAY = bytearray(b'\x77\x88\x99')
LIGHTSLATEGREY = bytearray(b'\x77\x88\x99')
LIGHTSTEELBLUE = bytearray(b'\xb0\xc4\xde')
LIGHTYELLOW = bytearray(b'\xff\xff\xe0')
LIME = bytearray(b'\x00\xff\x00')
LIMEGREEN = bytearray(b'\x32\xcd\x32')
LINEN = bytearray(b'\xfa\xf0\xe6')
MAGENTA = bytearray(b'\xff\x00\xff')
MAROON = bytearray(b'\x80\x00\x00')
MEDIUMAQUAMARINE = bytearray(b'\x66\xcd\xaa')
MEDIUMBLUE = bytearray(b'\x00\x00\xcd')
MEDIUMORCHID = bytearray(b'\xba\x55\xd3')
MEDIUMPURPLE = bytearray(b'\x93\x70\xd8')
MEDIUMSEAGREEN = bytearray(b'\x3c\xb3\x71')
MEDIUMSLATEBLUE = bytearray(b'\x7b\x68\xee')
MEDIUMSPRINGGREEN = bytearray(b'\x00\xfa\x9a')
MEDIUMTURQUOISE = bytearray(b'\x48\xd1\xcc')
MEDIUMVIOLETRED = bytearray(b'\xc7\x15\x85')
MIDNIGHTBLUE = bytearray(b'\x19\x19\x70')
MINTCREAM = bytearray(b'\xf5\xff\xfa')
MISTYROSE = bytearray(b'\xff\xe4\xe1')
MOCCASIN = bytearray(b'\xff\xe4\xb5')
NAVAJOWHITE = bytearray(b'\xff\xde\xad')
NAVY = bytearray(b'\x00\x00\x80')
OLDLACE = bytearray(b'\xfd\xf5\xe6')
OLIVE = bytearray(b'\x80\x80\x00')
OLIVEDRAB = bytearray(b'\x6b\x8e\x23')
ORANGE = bytearray(b'\xff\xa5\x00')
ORANGERED = bytearray(b'\xff\x45\x00')
ORCHID = bytearray(b'\xda\x70\xd6')
PALEGOLDENROD = bytearray(b'\xee\xe8\xaa')
PALEGREEN = bytearray(b'\x98\xfb\x98')
PALETURQUOISE = bytearray(b'\xaf\xee\xee')
PALEVIOLETRED = bytearray(b'\xd8\x70\x93')
PAPAYAWHIP = bytearray(b'\xff\xef\xd5')
PEACHPUFF = bytearray(b'\xff\xda\xb9')
PERU = bytearray(b'\xcd\x85\x3f')
PINK = bytearray(b'\xff\xc0\xcb')
PLUM = bytearray(b'\xdd\xa0\xdd')
POWDERBLUE = bytearray(b'\xb0\xe0\xe6')
PURPLE = bytearray(b'\x80\x00\x80')
RED = bytearray(b'\xff\x00\x00')
ROSYBROWN = bytearray(b'\xbc\x8f\x8f')
ROYALBLUE = bytearray(b'\x41\x69\xe1')
SADDLEBROWN = bytearray(b'\x8b\x45\x13')
SALMON = bytearray(b'\xfa\x80\x72')
SANDYBROWN = bytearray(b'\xf4\xa4\x60')
SEAGREEN = bytearray(b'\x2e\x8b\x57')
SEASHELL = bytearray(b'\xff\xf5\xee')
SIENNA = bytearray(b'\xa0\x52\x2d')
SILVER = bytearray(b'\xc0\xc0\xc0')
SKYBLUE = bytearray(b'\x87\xce\xeb')
SLATEBLUE = bytearray(b'\x6a\x5a\xcd')
SLATEGRAY = bytearray(b'\x70\x80\x90')
SLATEGREY = bytearray(b'\x70\x80\x90')
SNOW = bytearray(b'\xff\xfa\xfa')
SPRINGGREEN = bytearray(b'\x00\xff\x7f')
STEELBLUE = bytearray(b'\x46\x82\xb4')
TAN = bytearray(b'\xd2\xb4\x8c')
TEAL = bytearray(b'\x00\x80\x80')
THISTLE = bytearray(b'\xd8\xbf\xd8')
TOMATO = bytearray(b'\xff\x63\x47')
TURQUOISE = bytearray(b'\x40\xe0\xd0')
VIOLET = bytearray(b'\xee\x82\xee')
WHEAT = bytearray(b'\xf5\xde\xb3')
WHITE = bytearray(b'\xff\xff\xff')
WHITESMOKE = bytearray(b'\xf5\xf5\xf5')
YELLOW = bytearray(b'\xff\xff\x00')
YELLOWGREEN = bytearray(b'\x9a\xcd\x32')
RAINBOW = [AQUA, AQUAMARINE, AZURE, BEIGE, BISQUE, BLANCHEDALMOND, BLUE, BLUEVIOLET, BROWN, BURLYWOOD, CADETBLUE, CHARTREUSE, CHOCOLATE, CORAL, CORNFLOWERBLUE, CORNSILK, CRIMSON, CYAN, DARKBLUE, DARKCYAN, DARKGOLDENROD, DARKGRAY, DARKGREY, DARKGREEN, DARKKHAKI, DARKMAGENTA, DARKOLIVEGREEN, DARKORANGE, DARKORCHID, DARKRED, DARKSALMON, DARKSEAGREEN, DARKSLATEBLUE, DARKSLATEGRAY, DARKSLATEGREY, DARKTURQUOISE, DARKVIOLET, DEEPPINK, DEEPSKYBLUE, DIMGRAY, DIMGREY, DODGERBLUE, FIREBRICK, FLORALWHITE, FORESTGREEN, FUCHSIA, GAINSBORO, GHOSTWHITE, GOLD, GOLDENROD, GRAY, GREY, GREEN, GREENYELLOW, HONEYDEW, HOTPINK, INDIANRED, INDIGO, IVORY, KHAKI, LAVENDER, LAVENDERBLUSH, LAWNGREEN, LEMONCHIFFON, LIGHTBLUE, LIGHTCORAL, LIGHTCYAN, LIGHTGOLDENRODYELLOW, LIGHTGRAY, LIGHTGREY, LIGHTGREEN, LIGHTPINK, LIGHTSALMON, LIGHTSEAGREEN, LIGHTSKYBLUE, LIGHTSLATEGRAY, LIGHTSLATEGREY, LIGHTSTEELBLUE, LIGHTYELLOW, LIME, LIMEGREEN, LINEN, MAGENTA, MAROON, MEDIUMAQUAMARINE, MEDIUMBLUE, MEDIUMORCHID, MEDIUMPURPLE, MEDIUMSEAGREEN, MEDIUMSLATEBLUE, MEDIUMSPRINGGREEN, MEDIUMTURQUOISE, MEDIUMVIOLETRED, MIDNIGHTBLUE, MINTCREAM, MISTYROSE, MOCCASIN, NAVAJOWHITE, NAVY, OLDLACE, OLIVE, OLIVEDRAB, ORANGE, ORANGERED, ORCHID, PALEGOLDENROD, PALEGREEN, PALETURQUOISE, PALEVIOLETRED, PAPAYAWHIP, PEACHPUFF, PERU, PINK, PLUM, POWDERBLUE, PURPLE, RED, ROSYBROWN, ROYALBLUE, SADDLEBROWN, SALMON, SANDYBROWN, SEAGREEN, SEASHELL, SIENNA, SILVER, SKYBLUE, SLATEBLUE, SLATEGRAY, SLATEGREY, SNOW, SPRINGGREEN, STEELBLUE, TAN, TEAL, THISTLE, TOMATO, TURQUOISE, VIOLET, WHEAT, WHITE, WHITESMOKE, YELLOW, YELLOWGREEN, YELLOWGREEN]
#RAINBOW = [RED, GREEN, BLUE, YELLOW, VIOLET, ORANGE, GRAY, OLIVE, BROWN]


def put(buffer, offset, pixel):
    # Bounded write. An open-ended slice (buffer[offset:]) would resize the whole buffer.
    buffer[offset:offset + len(pixel)] = pixel


def read_pixel_map(width, height):
    # Use the map named for this array size when it exists, else the generic one.
    pixel_map = None
    for name in ("pixel_map_%dx%d.csv" % (width, height), "pixel_map.csv"):
        if os.path.exists(name):
            with open(name, "r", newline="") as map_file:
                pixel_map = list(csv.reader(map_file))
            break
    if pixel_map is None:
        print("[ERROR] no pixel map found: expected pixel_map_%dx%d.csv or pixel_map.csv"
              % (width, height))
        sys.exit(1)
    if len(pixel_map) != width * height:
        print("[ERROR] %s has %d entries, expected %d for a %dx%d array"
              % (name, len(pixel_map), width * height, width, height))
        sys.exit(1)
    return pixel_map


def check_pixel_map(pixel_map, image_size):
    image_width, image_height = image_size
    for row in pixel_map:
        x, y = int(row[0]), int(row[1])
        if not (0 <= x < image_width and 0 <= y < image_height):
            print("[ERROR] pixel map point %d/%d is outside the %dx%d image"
                  % (x, y, image_width, image_height))
            sys.exit(1)


def open_image(filename):
    img = Image.open(filename).convert("RGB")
    return img, img.load()


def write_stream(pixels):
    if args.chip_type == "LPD6803":
        pixel_out_bytes = bytearray(2)
        spidev.write(bytearray(4))
        pixel_count = len(pixels) // PIXEL_SIZE
        for pixel_index in range(pixel_count):

            pixel_in = bytearray(pixels[(pixel_index * PIXEL_SIZE):((pixel_index * PIXEL_SIZE) + PIXEL_SIZE)])

            pixel_out = 0b1000000000000000  # bit 16 must be ON
            pixel_out |= (pixel_in[0] & 0x00F8) << 7  # RED is bits 11-15
            pixel_out |= (pixel_in[1] & 0x00F8) << 2  # GREEN is bits 6-10
            pixel_out |= (pixel_in[2] & 0x00F8) >> 3  # BLUE is bits 1-5

            pixel_out_bytes[0] = (pixel_out & 0xFF00) >> 8
            pixel_out_bytes[1] = (pixel_out & 0x00FF) >> 0
            spidev.write(pixel_out_bytes)
        spidev.write(bytearray(len(pixels) // 8 + 1))
    elif args.chip_type == "LPD8806":
        spidev.write(pixels)
        spidev.write(bytearray(b'\x00\x00\x00'))  # zero fill the last to prevent stray colors at the end
        spidev.write(bytearray(b'\x00'))
    elif args.chip_type == "SM16716":
        # Each frame for SM17616 starts with 50 bits set to '0'
        # Also every pixel needs to start with a bit set to '1'
        spidev.write(bytearray(50) + pixels)
    else:
        spidev.write(pixels)

    return


def strip():
    img, input_image = open_image(args.filename)
    image_width = img.size[0]
    print("%dx%d pixels" % img.size)
    if img.size[1] < args.array_height:
        print("[ERROR] image is %d pixels high, array_height is %d"
              % (img.size[1], args.array_height))
        sys.exit(1)
    # Create bytearray for the entire image
    # R, G, B byte per pixel, plus extra '0' byte at end for latch.
    print("Allocating...")
    column = [0 for x in range(image_width)]
    for x in range(image_width):
        if args.chip_type == "SM16716":
            column[x] = bytearray(args.array_height * PIXEL_SIZE_SM16716)
        else:
            column[x] = bytearray(args.array_height * PIXEL_SIZE + 1)

    print("Process Image...")
    for x in range(image_width):
        for y in range(args.array_height):
            value = input_image[x, y]
            if args.chip_type == "LPD8806":
                # Convert RGB into column-wise GRB bytearray list.
                y3 = y * 3
                column[x][y3] = gamma[value[1]]
                column[x][y3 + 1] = gamma[value[0]]
                column[x][y3 + 2] = gamma[value[2]]
            elif args.chip_type == "SM16716":
                y4 = y * PIXEL_SIZE_SM16716
                column[x][y4] = 1
                column[x][y4 + 1] = value[0]
                column[x][y4 + 2] = value[1]
                column[x][y4 + 3] = value[2]
            else:
                y3 = y * 3
                column[x][y3] = value[0]
                column[x][y3 + 1] = value[1]
                column[x][y3 + 2] = value[2]

    print("Displaying...")
    while True:
        for x in range(image_width):
            write_stream(column[x])
            spidev.flush()
            time.sleep(0.001)
        time.sleep((args.refresh_rate / 1000.0))


def array():
    images = []
    if ('filelist.txt' in args.filename):
        with open(args.filename, 'r') as list_file:
            for filename in list_file:
                filename = filename.rstrip()
                if not filename:
                    print("[ERROR] Not a file or not readable: ", filename)
                    continue
                images.append(Image.open(filename).convert("RGB"))
                print("[INFO] Added file ", filename)
    else:
        images.append(Image.open(args.filename).convert("RGB"))
        print("[INFO] Added file ", args.filename)

    pixel_map = read_pixel_map(args.array_width, args.array_height)

    for img in images:
        input_image = img.load()
        print("[INFO] Imaged loaded: %dx%d pixels" % img.size)
        check_pixel_map(pixel_map, img.size)

        # 171026-AHo: added verbose output
        if args.verbose:
            print("[debug] pixel_map:")
            for i in range(1, len(pixel_map)):
                print(pixel_map[i])

        print("[INFO] Creating buffer for color values (", PIXEL_SIZE, " bytes)")
        value = bytearray(PIXEL_SIZE)

        # Create empty byte array (will be filled with SPI data)
        print("[INFO] Creating buffer for SPI data")
        if args.chip_type == "SM16716":
            pixel_output = bytearray(args.array_width * args.array_height * PIXEL_SIZE_SM16716)
            print("[INFO] Buffersize = ", args.array_width * args.array_height * PIXEL_SIZE_SM16716, " Bytes")
        else:
            pixel_output = bytearray(args.array_width * args.array_height * PIXEL_SIZE + 1)
            print("[INFO] Buffersize = ", args.array_width * args.array_height * PIXEL_SIZE + 1, " Bytes")

        # 171026-AHo: added verbose output
        if args.verbose:
            print("[debug] pixel_output:")
            print(''.join('{:02x}'.format(x) for x in pixel_output))

        print("[INFO] Creating SPI data")
        for array_index in range(len(pixel_map)):
            x = int(pixel_map[array_index][0])
            y = int(pixel_map[array_index][1])
            value = bytearray(input_image[x, y])

            if args.verbose:
                print("[debug] Processing ", x, "/", y, " -> ", input_image[x, y], ''.join('{:02x}'.format(b) for b in value))

            # 171026-AHo: bugfix, this block has to be executed inside the "for"-loop
            if args.chip_type == "SM16716":
                put(pixel_output, array_index * PIXEL_SIZE_SM16716, filter_pixel(value[:], 1))
            else:
                put(pixel_output, array_index * PIXEL_SIZE, filter_pixel(value[:], 1))

        print("[INFO] Displaying SPI data")
        if args.verbose:
            print("[debug] pixel_output:")
            print(''.join('{:02x}'.format(x) for x in pixel_output))
        write_stream(pixel_output)
        spidev.flush()
        time.sleep(args.refresh_rate / 1000.0)
        print("[INFO] Goodbye")


def pan():
    img, input_image = open_image(args.filename)
    image_width = img.size[0]
    print("%dx%d pixels" % img.size)
    if image_width < args.array_width:
        print("[ERROR] image is %d pixels wide, array_width is %d"
              % (image_width, args.array_width))
        sys.exit(1)
    print("Reading in array map")
    pixel_map = read_pixel_map(args.array_width, args.array_height)
    check_pixel_map(pixel_map, img.size)
    print("Remapping")

    # Create a byte array ordered according to the pixel map file
    if args.chip_type == "SM16716":
        pixel_output = bytearray(args.array_width * args.array_height * PIXEL_SIZE_SM16716)
    else:
        pixel_output = bytearray(args.array_width * args.array_height * PIXEL_SIZE + 1)
    while True:
        for x_offset in range(image_width - args.array_width + 1):
            for array_index in range(len(pixel_map)):
                value = bytearray(input_image[int(pixel_map[array_index][0]) + x_offset, int(pixel_map[array_index][1])])
                if args.chip_type == "SM16716":
                    put(pixel_output, array_index * PIXEL_SIZE_SM16716, filter_pixel(value[:], 1))
                else:
                    put(pixel_output, array_index * PIXEL_SIZE, filter_pixel(value[:], 1))

        print("Displaying...")
        write_stream(pixel_output)
        spidev.flush()
        time.sleep((args.refresh_rate) / 1000.0)


def all_off():
    if args.chip_type == "SM16716":
        pixel_output = bytearray(args.num_leds * PIXEL_SIZE_SM16716)
    else:
        pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
    print("Turning all LEDs Off")
    for led in range(args.num_leds):
        if args.chip_type == "SM16716":
            put(pixel_output, led * PIXEL_SIZE_SM16716, SM16716BLACK)
        else:
            put(pixel_output, led * PIXEL_SIZE, filter_pixel(BLACK, 1))
    write_stream(pixel_output)
    spidev.flush()


def all_on():
    if args.chip_type == "SM16716":
        pixel_output = bytearray(args.num_leds * PIXEL_SIZE_SM16716)
    else:
        pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
    print("Turning all LEDs On")
    for led in range(args.num_leds):
        if args.chip_type == "SM16716":
            put(pixel_output, led * PIXEL_SIZE_SM16716, filter_pixel(WHITE, 1))
        else:
            put(pixel_output, led * PIXEL_SIZE, filter_pixel(WHITE, 1))
    write_stream(pixel_output)
    spidev.flush()


def fade():
    if args.chip_type == "SM16716":
        pixel_output = bytearray(args.num_leds * PIXEL_SIZE_SM16716)
        current_color = bytearray(PIXEL_SIZE_SM16716)
        pixel_size = PIXEL_SIZE_SM16716
    else:
        pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
        current_color = bytearray(PIXEL_SIZE)
        pixel_size = PIXEL_SIZE
    print("Displaying...")

    while True:
        for color in RAINBOW:
            for brightness in [x * 0.01 for x in range(0, 100)]:
                current_color[:] = filter_pixel(color[:], brightness)
                for pixel_offset in [(x * pixel_size) for x in range(args.num_leds)]:
                    put(pixel_output, pixel_offset, current_color)
                write_stream(pixel_output)
                spidev.flush()
                time.sleep((args.refresh_rate) / 1000.0)
            for brightness in [x * 0.01 for x in range(100, 0, -1)]:
                current_color[:] = filter_pixel(color[:], brightness)
                for pixel_offset in [(x * pixel_size) for x in range(args.num_leds)]:
                    put(pixel_output, pixel_offset, current_color)
                write_stream(pixel_output)
                spidev.flush()
                time.sleep((args.refresh_rate) / 1000.0)


def chase():
    if args.chip_type == "SM16716":
        pixel_size = PIXEL_SIZE_SM16716
        off_color = SM16716BLACK
    else:
        pixel_size = PIXEL_SIZE
        off_color = filter_pixel(BLACK, 1)
    print("Displaying...")
    while True:
        for current_color in RAINBOW:
            for pixel_index in range(args.num_leds):
                # Fresh frame every step so nothing accumulates between writes.
                pixel_output = bytearray(off_color * args.num_leds)
                if args.chip_type != "SM16716":
                    pixel_output += bytearray(3)
                for step, brightness in ((-2, 0.2), (-1, 0.4), (0, 1)):
                    led = pixel_index + step
                    if 0 <= led < args.num_leds:
                        put(pixel_output, led * pixel_size, filter_pixel(current_color[:], brightness))

                write_stream(pixel_output)
                spidev.flush()
                time.sleep((args.refresh_rate) / 1000.0)


gamma = bytearray(256)


# Apply Gamma Correction and RGB / GRB reordering
# Optionally perform brightness adjustment
def filter_pixel(input_pixel, brightness):
    if args.chip_type == "SM16716":
        output_pixel = bytearray(PIXEL_SIZE_SM16716)
    else:
        output_pixel = bytearray(PIXEL_SIZE)

    input_pixel[0] = int(brightness * input_pixel[0])
    input_pixel[1] = int(brightness * input_pixel[1])
    input_pixel[2] = int(brightness * input_pixel[2])

    if args.chip_type == "LPD8806":
        # Convert RGB into GRB bytearray list.

        # Some LPD8806 strips use this ordering:
        # output_pixel[0] = gamma[input_pixel[1]]
        # output_pixel[1] = gamma[input_pixel[0]]
        # output_pixel[2] = gamma[input_pixel[2]]

        # While some others use this one:
        output_pixel[0] = gamma[input_pixel[2]]
        output_pixel[1] = gamma[input_pixel[0]]
        output_pixel[2] = gamma[input_pixel[1]]
    elif args.chip_type == "SM16716":
        # ON bit at the pixel front
        # What is gamma correction for?
        output_pixel[0] = 1
        output_pixel[1] = input_pixel[0]
        output_pixel[2] = input_pixel[1]
        output_pixel[3] = input_pixel[2]
    else:
        output_pixel[0] = gamma[input_pixel[0]]
        output_pixel[1] = gamma[input_pixel[1]]
        output_pixel[2] = gamma[input_pixel[2]]
    return output_pixel


parser = argparse.ArgumentParser(add_help=True, prog='pixelpi.py')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
subparsers = parser.add_subparsers(help='sub command help?')
common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument('--chip', action='store', dest='chip_type', default='WS2801', choices=['WS2801', 'LPD8806', 'LPD6803', 'SM16716'], help='Specify chip type LPD6803, LPD8806, WS2801 or SM16716')
#171026-AHo: default for --verbose changed from 'true' to 'false'
#action="store_true", default=False
common_parser.add_argument('--verbose', action='store_true', default=False, dest='verbose', help='enable verbose mode')
common_parser.add_argument('--spi_dev', action='store', dest='spi_dev_name', required=False, default='/dev/spidev0.0', help='Set the SPI device descriptor')
common_parser.add_argument('--refresh_rate', action='store', dest='refresh_rate', required=False, default=500, type=int, help='Set the refresh rate in ms (default 500ms)')
parser_strip = subparsers.add_parser('strip', parents=[common_parser], help='Stip Mode - Display an image using POV and a LED strip')
parser_strip.set_defaults(func=strip)
parser_strip.add_argument('--filename', action='store', dest='filename', required=True, help='Specify the image file eg: hello.png')
parser_strip.add_argument('--array_height', action='store', dest='array_height', required=True, type=int, default='7', help='Set the Y dimension of your pixel array (height)')
parser_array = subparsers.add_parser('array', parents=[common_parser], help='Array Mode - Display an image on a pixel array')
parser_array.set_defaults(func=array)
parser_array.add_argument('--filename', action='store', dest='filename', required=True, help='Specify the image file eg: hello.png')
parser_array.add_argument('--array_width', action='store', dest='array_width', required=True, type=int, default='7', help='Set the X dimension of your pixel array (width)')
parser_array.add_argument('--array_height', action='store', dest='array_height', required=True, type=int, default='7', help='Set the Y dimension of your pixel array (height)')
parser_fade = subparsers.add_parser('fade', parents=[common_parser], help='Fade Mode - Fade colors on all LEDs')
parser_fade.set_defaults(func=fade)
parser_fade.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int, help='Set the  number of LEDs in the string')
parser_chase = subparsers.add_parser('chase', parents=[common_parser], help='Chase Mode - Chase display test mode')
parser_chase.set_defaults(func=chase)
parser_chase.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int, help='Set the  number of LEDs in the string')
parser_pan = subparsers.add_parser('pan', parents=[common_parser], help='Pan Mode - Pan an image across an array')
parser_pan.set_defaults(func=pan)
parser_pan.add_argument('--filename', action='store', dest='filename', required=True, help='Specify the image file eg: hello.png')
parser_pan.add_argument('--array_width', action='store', dest='array_width', required=True, type=int, default='7', help='Set the X dimension of your pixel array (width)')
parser_pan.add_argument('--array_height', action='store', dest='array_height', required=True, type=int, default='7', help='Set the Y dimension of your pixel array (height)')
parser_all_on = subparsers.add_parser('all_on', parents=[common_parser], help='All On Mode - Turn all LEDs On')
parser_all_on.set_defaults(func=all_on)
parser_all_on.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int, help='Set the  number of LEDs in the string')
parser_all_off = subparsers.add_parser('all_off', parents=[common_parser], help='All Off Mode - Turn all LEDs Off')
parser_all_off.set_defaults(func=all_off)
parser_all_off.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int, help='Set the  number of LEDs in the string')

args = parser.parse_args()
if not hasattr(args, 'func'):
    parser.print_help()
    sys.exit(2)
spidev = open(args.spi_dev_name, "wb", buffering=0)
# Calculate gamma correction table. This includes
# LPD8806-specific conversion (7-bit color w/high bit set).
if args.chip_type == "LPD8806":
    for i in range(256):
        gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)

if args.chip_type == "SM16716":
    for i in range(256):
        gamma[i] = int(pow(float(i) / 255.0, 2.5) * 255.0)

if args.chip_type == "WS2801":
    for i in range(256):
        gamma[i] = int(pow(float(i) / 255.0, 2.5) * 255.0)

#LPD6803 has 5 bit color, this seems to work but is not exact.
if args.chip_type == "LPD6803":
    for i in range(256):
        gamma[i] = int(pow(float(i) / 255.0, 2.0) * 255.0 + 0.5)
args.func()


#print "Chip Type             = %s" % args.chip_type
#print "File Name             = %s" % args.filename
#print "Display Mode          = %s" % args.mode
#print "SPI Device Descriptor = %s" % args.spi_dev_name
#print "Refresh Rate          = %s" % args.refresh_rate
#print "Array Dimensions      = %dx%d" % (args.array_width, args.array_height)
