# General object colors
RED = "fillColor=#f8cecc;strokeColor=#b85450;"
BLUE = "fillColor=#dae8fc;strokeColor=#6c8ebf;"
YELLOW = "fillColor=#fff2cc;strokeColor=#d6b656;"
ORANGE = "fillColor=#ffe6cc;strokeColor=#d79b00;"
VIOLET = "fillColor=#e1d5e7;strokeColor=#9673a6;"
GREEN = "fillColor=#d5e8d4;strokeColor=#82b366;"
NAVY = "fillColor=#b0e3e6;strokeColor=#0e8088;"
GRAY = "fillColor=#f5f5f5;strokeColor=#666666;"

# Default table style
TABLE = (
    "shape=table;"
    "startSize=30;"
    "container=1;"
    "collapsible=1;"
    "childLayout=tableLayout;"
    "fixedRows=1;"
    "rowLines=0;"
    "fontStyle=1;"
    "align=center;"
    "resizeLast=1;"
    "strokeWidth=2;"
)

# Default row style
ROW = (
    "shape=tableRow;"
    "horizontal=0;"
    "startSize=0;"
    "swimlaneHead=0;"
    "swimlaneBody=0;"
    "fillColor=none;"
    "collapsible=0;"
    "dropTarget=0;"
    "points=[[0,0.5],[1,0.5]];"
    "portConstraint=eastwest;"
    "top=0;"
    "left=0;"
    "right=0;"
    "bottom=%s;"
)

ROWS = [
    FIRST := ROW % 1,
    OTHER := ROW % 0,
]

# First row cells style
CELL_HEADER = (
    "shape=partialRectangle;"
    "connectable=0;"
    "fillColor=none;"
    "top=0;"
    "left=0;"
    "bottom=0;"
    "right=0;"
    "overflow=hidden;"
)

CELLS_HEADER = [
    CELL_HEADER + (
        "fontStyle=1;"
    ),
    CELL_HEADER + (
        "align=left;"
        "spacingLeft=6;"
        "fontStyle=5;"
    ),
]

# Other rows cells style
CELL_FIELD = (
    "shape=partialRectangle;"
    "connectable=0;"
    "fillColor=none;"
    "top=0;"
    "left=0;"
    "bottom=0;"
    "right=0;"
)

CELLS_FIELD = [
    CELL_FIELD + (
        "editable=1;"
        "overflow=hidden;"
    ),
    CELL_FIELD + (
        "align=left;"
        "spacingLeft=6;"
        "overflow=hidden;"
    ),
]


ROW_WIDTH = 240
ROW_HEIGHT = 30


def get_default_color_map():
    return {
        "hub": BLUE,
        "lnk": RED,
        "sat": YELLOW,
        "ref": VIOLET,
        "raw": GREEN,
        "stg": NAVY,
    }


def get_default_color():
    return GRAY
