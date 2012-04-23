#!/usr/bin/python

import Image
import ImageOps
import numpy
from scipy import ndimage
from autometa import AutoMeta
import sys
import time
import argparse


# buttons:
# 1 - add image locations
#     prompt for a pair of image extents, add this pair to the list
# 2 - solve
#     run through all the possible image locations; if a pair of locations is similar but different, click the differences


def get_images(am):
    i1tl = am.prompt_pos("Hover near image #1 top left...")
    i1br = am.prompt_pos("Hover near image #1 bottom right...")
    i1 = i1tl[0], i1tl[1], i1br[0] - i1tl[0], i1br[1] - i1tl[1]

    i2tl = am.prompt_pos("Hover near image #2 top left...")
    i2 = i2tl[0], i2tl[1], i1[2], i1[3]

    i1o = am.grab_screen(*i1)
    i2o = am.grab_screen(*i2)

    return i1tl, i1o, i2o


def get_difference_image(im1, im2):
    try:
        import cv2
        result = cv2.matchTemplate(numpy.array(im1), numpy.array(im2)[32:-32, 32:-32], cv2.TM_CCOEFF_NORMED)
        #Image.fromarray(result * 255).show()
        off = numpy.unravel_index(result.argmax(), result.shape)
        minoff = off[0]-32, off[1]-32
    except ImportError:
        # pick a sample
        pix1 = numpy.array(ImageOps.grayscale(im1))[32:64, 32:64]
        pix2 = numpy.array(ImageOps.grayscale(im2))[32:64, 32:64]

        mindiff = sys.maxint
        minoff = (0, 0)

        # find best alignment for the sample
        for xoff in range(-20, 20):
            for yoff in range(-20, 20):
                #print xoff, yoff
                pix2off = pix2
                pix2off = numpy.roll(pix2off, xoff, 0)
                pix2off = numpy.roll(pix2off, yoff, 1)
                diff = sum((numpy.maximum(pix1, pix2off) - numpy.minimum(pix1, pix2off)).flatten())
                if diff < mindiff:
                    mindiff = diff
                    minoff = xoff, yoff
                    print mindiff, minoff

    # align the full images
    xoff, yoff = minoff

    pix1 = numpy.array(im1)
    pix2 = numpy.array(im2)

    pix2off = pix2
    pix2off = numpy.roll(pix2off, minoff[0], 0)
    pix2off = numpy.roll(pix2off, minoff[1], 1)

    diff = numpy.maximum(pix1, pix2off) - numpy.minimum(pix1, pix2off)

    # only show the overlap
    xoff = abs(xoff)
    yoff = abs(yoff)
    diff = diff[xoff:diff.shape[0]-2*xoff, yoff:diff.shape[1]-2*yoff]

    #Image.fromarray(diff).show()

    return diff


def get_difference_spots(pix):
    bpix = pix > 20
    bpix = ndimage.binary_opening(bpix)
    bpix = ndimage.binary_closing(bpix)
    labels, n = ndimage.measurements.label(bpix)
    clicks = ndimage.measurements.center_of_mass(pix, labels, range(1, n+1))
    return clicks


def main(argv):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mirror-x', action='store_true')
    parser.add_argument('--mirror-y', action='store_true')
    parser.add_argument('--no-display', action='store_false', dest='display')
    parser.add_argument('--no-click', action='store_false', dest='clicks')
    args = parser.parse_args(argv[1:])

    am = AutoMeta()

    print "Getting images..."
    pos, im1, im2 = get_images(am)
    if args.mirror_x:
        im2 = ImageOps.mirror(im2)
    if args.mirror_y:
        im2 = ImageOps.flip(im2)
    print "got"

    print "Aligning..."
    pix = get_difference_image(im1, im2)
    print "done"

    print "Finding differences...",
    diffs = get_difference_spots(pix)
    print "done"

    if args.clicks:
        # TODO: if two diffs are very close, only click one
        for diff in diffs:
            am.move_mouse(pos[0] + diff[1], pos[1] + diff[0])
            time.sleep(.1)
            am.left_click()

    if args.display:
        Image.fromarray(pix).show()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
