#!/usr/bin/env python
""" Convert SVG paths to UFO glyphs. """

from __future__ import print_function, absolute_import

__requires__ = ["FontTools", "ufoLib"]

from fontTools.misc.py23 import SimpleNamespace
from fontTools.svgLib import SVGPath
from ufoLib import UFOReader, UFOWriter, UFOLibError
from ufoLib.pointPen import SegmentToPointPen
from ufoLib.glifLib import writeGlyphToString
import argparse
import os


class InfoObject(object):
    pass


def parseSvg(path):
    import xml.etree.ElementTree as etree
    tree = etree.parse(path)
    return tree.getroot()


def getConfig(configFile):
    import yaml
    with open(configFile, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg


def split(arg):
    return arg.replace(",", " ").split()


def svg2glif(svg, name, width=0, height=0, unicodes=None, transform=None,
             version=2):
    """ Convert an SVG outline to a UFO glyph with given 'name', advance
    'width' and 'height' (int), and 'unicodes' (list of int).
    Return the resulting string in GLIF format (default: version 2).
    If 'transform' is provided, apply a transformation matrix before the
    conversion (must be tuple of 6 floats, or a FontTools Transform object).
    """
    glyph = SimpleNamespace(width=width, height=height, unicodes=unicodes)
    outline = SVGPath.fromstring(svg, transform=transform)

    # writeGlyphToString takes a callable (usually a glyph's drawPoints
    # method) that accepts a PointPen, however SVGPath currently only has
    # a draw method that accepts a segment pen. We need to wrap the call
    # with a converter pen.
    def drawPoints(pointPen):
        pen = SegmentToPointPen(pointPen)
        outline.draw(pen)

    return writeGlyphToString(name,
                              glyphObject=glyph,
                              drawPointsFunc=drawPoints,
                              formatVersion=version)


def transform_list(arg):
    try:
        return [float(n) for n in split(arg)]
    except ValueError:
        msg = "Invalid transformation matrix: %r" % arg
        raise argparse.ArgumentTypeError(msg)


def unicode_hex_list(arg):
    try:
        return [int(unihex, 16) for unihex in split(arg)]
    except ValueError:
        msg = "Invalid unicode hexadecimal value: %r" % arg
        raise argparse.ArgumentTypeError(msg)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Convert SVG outlines to UFO glyphs (.glif)")
    parser.add_argument(
        "infile", metavar="INPUT.svg", help="Input SVG file containing "
        '<path> elements with "d" attributes.')
    parser.add_argument(
        "outfile", metavar="OUTPUT.glif", help="Output GLIF file (default: "
        "print to stdout)", nargs='?')

    return parser.parse_args(args)


def main(args=None):
    from io import open
    config = getConfig("sources/svg-glif-mapping.yaml")
    options = parse_args(args)

    svg_file = options.infile

    # Parse SVG to read the width, height attributes defined in it
    svgObj = parseSvg(svg_file)
    width = float(svgObj.attrib['width'].replace("px", " "))

    name = os.path.splitext(os.path.basename(svg_file))[0]

    with open(svg_file, "r", encoding="utf-8") as f:
        svg = f.read()

    # Get the configuration for this svg
    try:
        svg_config = config['svgs'][name]
    except KeyError:
        print("Error: Configuration not found for svg : %r" % name)
        return

    # Get the font metadata from UFO
    ufo_font_path = config['font']['ufo']
    reader = UFOReader(ufo_font_path)
    infoObject = InfoObject()
    reader.readInfo(infoObject)
    glyphInfo = reader.readLib()

    if svg_config['glyph_name'] not in glyphInfo['public.glyphOrder']:
        print("Error: Glyph %s not found in the font" % svg_config['glyph_name'] )
        return

    # Calculate the transformation to do
    transform = transform_list(config['font']['transform'])
    transform[4] += int(svg_config['left'])  # X offset = left bearing
    transform[5] += int(getattr(infoObject, 'xHeight'))  # Y offset = x-height

    glyphWidth = width + int(svg_config['left']) + int(svg_config['right'])
    glif = svg2glif(svg,
                    name=svg_config['glyph_name'],
                    width=glyphWidth,
                    height=getattr(infoObject, 'unitsPerEm'),
                    unicodes=unicode_hex_list(svg_config['unicode']),
                    transform=transform,
                    version=config['font']['version'])
    if options.outfile is None:
        output_file = ufo_font_path + '/glyphs/' + \
            svg_config['glyph_name'] + '.glif'
    else:
        output_file = options.outfile
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(glif)
    print("[%s] %s -> %s ✔️" % (getattr(infoObject, 'familyName'), name, output_file))
    # TODO: Use UFOWriter to update UFO with this glif
    # writer = UFOWriter(ufo_font_path, formatVersion=config['font']['version'])


if __name__ == "__main__":
    import sys
    sys.exit(main())
