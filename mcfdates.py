#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script parses a Cewe Fotobuch project file (*.mcf) and
prints the Exif dates of the images for each page.

The output looks like this:

    >>> PAGE #72 (normalpage)
        LEFT (3 images)
                Tue, 20. Mar 2012 -> Tue, 20. Mar 2012
        RIGHT (4 images)
                Tue, 20. Mar 2012 -> Tue, 20. Mar 2012

The image dates are given as date range, as there might be multiple
images on one page with different dates.
"""

import dateutil.parser
import lxml.etree
import pyexiv2



def comma_float(s):
    return float(s.replace(',', '.'))


def get_image_date(imgfile):
    metadata = pyexiv2.ImageMetadata(imgfile)
    metadata.read()
    for key in ['Exif.Image.DateTime']:
        return(metadata[key].value.strftime('%a, %d. %b %Y'))


def parse_pages(mcffile):
    doc = lxml.etree.parse(mcffile)
    root = doc.getroot()
    pages = root.findall('page')
    for page in pages:
        bundlesizes = page.findall('bundlesize')
        assert len(bundlesizes) == 1
        bundlesize = bundlesizes[0].attrib
        half_width = float(bundlesize['width']) / 2
        image_areas = page.findall('.//area[@areatype="imagearea"]')
        left_side_images = []
        right_side_images = []
        for image_area in image_areas:
            rels = image_area.findall('.//relationship[@parent]')
            assert len(rels) == 1
            image_file = rels[0].attrib['parent']
            if comma_float(image_area.attrib['left']) > half_width:
                right_side_images.append(image_file)
            else:
                left_side_images.append(image_file)
        if left_side_images or right_side_images:
            print(">>> PAGE #{} ({})".format(page.attrib['pagenr'], page.attrib['type']))

            if left_side_images:
                print("\tLEFT ({} images)".format(len(left_side_images)))
                #for l in left_side_images:
                #    print("\t\t{} {}".format(l, get_image_date(l)))
                left_dates = sorted([get_image_date(l) for l in left_side_images])
                print("\t\t{} -> {}".format(left_dates[0], left_dates[-1]))

            if right_side_images:
                print("\tRIGHT ({} images)".format(len(right_side_images)))
                #for r in right_side_images:
                #    print("\t\t{} {}".format(r, get_image_date(r)))
                right_dates = sorted([get_image_date(r) for r in right_side_images])
                print("\t\t{} -> {}".format(right_dates[0], right_dates[-1]))

            #print("<<<")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mcffile')
    args = parser.parse_args()
    pages = parse_pages(args.mcffile)

