import os
import zlib
import base64
import random
from xml.dom import minidom
from urllib.parse import unquote, quote
from string import ascii_lowercase, digits
from datetime import datetime

import erdio.styles as styles


# Diagram content is compressed by default
deflate = zlib.decompressobj(-zlib.MAX_WBITS)
inflate = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-zlib.MAX_WBITS)


class Drawio:
    """Drawio composer"""
    tables = {}
    links = []

    def __init__(self, file_path, compressed=True):
        self.file_path = file_path
        if not os.path.exists(file_path):
            self.create_document(compressed)
        else:
            self.read_document()

    def random_crumbs(self, length=19):
        """Helper to generate random symbols for using in XML id."""
        return ''.join(random.choice(ascii_lowercase + digits) for _ in range(length))

    def create_element(self, name, params=None, data=None):
        """Helper to create XML element from dict."""
        element = self._dom.createElement(name)
        if params:
            for key, value in params.items():
                element.setAttribute(key, str(value))
        return element

    def create_document(self, compressed=True):
        """Create empty document."""
        self._dom = minidom.Document()

        self._dom.appendChild(
            mxfile := self.create_element(
                name="mxfile",
                params={
                    "host": "ERDio",
                    "modified": datetime.now().isoformat(),
                    "agent": "ERDio Generator",
                    "etag": self.random_crumbs(),
                    "compressed": "true" if compressed else "false",
                    "version": "0.0.1",
                    "type": "device",
                }
            )
        )

        mxfile.appendChild(
            diagram := self.create_element(
                name="diagram",
                params={
                    "id": self.random_crumbs(),
                    "name": "Page 1",
                }
            )
        )

        diagram.appendChild(
            self._dom.createTextNode("")
        )

        self._content = diagram
        self.create_diagram(compressed)

    def create_diagram(self, compressed=True):
        """Create empty diagram with two starting cells."""
        self._model = self.create_element(
            name="mxGraphModel",
            params={
                "dx": "0",
                "dy": "0",
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": "827",
                "pageHeight": "1169",
                "math": "0",
                "shadow": "0",
            }
        )

        self._model.appendChild(
            root := self.create_element(name="root")
        )

        root.appendChild(
            self.create_element(name="mxCell", params={"id": "0"})
        )

        root.appendChild(
            self.create_element(name="mxCell", params={"id": "1", "parent": "0"})
        )

        self.compressed = compressed
        self._root = root

    def find_element(self, id):
        nodes = self._root.childNodes
        for i in range(len(nodes)):
            if nodes[i].getAttribute("id") == id:
                return nodes[i]

    def read_document(self):
        """Read the document."""
        self._dom = minidom.parse(self.file_path)
        mxfile = self._dom.firstChild
        diagram = mxfile.firstChild
        self._content = diagram

        self.read_diagram()
        self.load_tables()

    def read_diagram(self):
        """Read and uncompress diagram content."""
        node = self._content.firstChild
        is_compressed = node.nodeType == node.TEXT_NODE

        if is_compressed:
            model_base64 = node.nodeValue
            model_compressed = base64.b64decode(model_base64)
            model_decompressed = deflate.decompress(model_compressed)
            model_decompressed += deflate.flush()
            model_xml = unquote(model_decompressed)
            model_dom = minidom.parseString(model_xml)
            self._model = model_dom.firstChild
            self.compressed = True

        else:
            self._model = self._content.firstChild
            self.compressed = False

        self._root = self._model.firstChild

    def save(self):
        """Write document with modified diagram."""
        if self.compressed:
            model_decompressed = quote(self._model.toxml()).encode()
            model_compressed = inflate.compress(model_decompressed)
            model_compressed += inflate.flush()
            model_base64 = base64.b64encode(model_compressed)
            self._content.firstChild.nodeValue = model_base64.decode()

        else:
            self._content.appendChild(self._model)

        # Remove XML declaration as in original diagram
        with open(self.file_path, "wb") as f:
            xml = self._dom.toxml()
            text = xml[(xml.find("?>")+2):]
            f.write(text.encode())

    def _geometry(self, x=None, y=None, width=None, height=None):
        """Helper to create nested mxGeometry XML element."""
        return self.create_element(
            name="mxGeometry",
            params={"x": x, "y": y, "width": width, "height": height, "as": "geometry"}
        )

    def _rectangle(self, x=None, y=None, width=None, height=None):
        """Helper to create nested mxRectangle XML element."""
        return self.create_element(
            name="mxRectangle",
            params={"width": width, "height": height, "as": "alternateBounds"}
        )

    def _cell(self, geometry, params, bounds=False):
        """Helper to create mxCell XML element."""
        params["vertex"] = "1"  # each mxCell table element contains vertex
        cell = self.create_element("mxCell", params)
        geometry_element = self._geometry(**geometry)
        if bounds:
            rectangle_element = self._rectangle(**geometry)
            geometry_element.appendChild(rectangle_element)
        cell.appendChild(geometry_element)
        self._root.appendChild(cell)

    def add_table(self, name="", x=0, y=0, width=200, height=200, style=None, data=[]):
        """Add table to diagram from list of columns."""
        crumbs = self.random_crumbs()

        # Table
        index = 1
        table_id = f"_{crumbs}-{index}"
        self._cell(
            geometry={"x": x, "y": y, "width": width, "height": 30 * (len(data) + 1)},
            params={
                "id": table_id,
                "value": name,
                "style": styles.TABLE + (style or styles.BLUE),
                "parent": "1",
            }
        )

        default_column_width = [30, 150]
        for n, row in enumerate(data, start=1):
            index += 1
            row_id = f"_{crumbs}-{index}"
            self._cell(
                geometry={"x": 0, "y": 30 * n, "width": width, "height": 30},
                params={
                    "id": row_id,
                    "value": "",
                    "style": styles.ROWS[n != 1],
                    "parent": table_id,
                }
            )

            column = 0
            for value in row:
                index += 1
                style_header = styles.CELLS_HEADER[column]
                style_field = styles.CELLS_FIELD[column]
                style = style_header if n == 1 else style_field
                self._cell(
                    geometry={"width": default_column_width[column], "height": 30},
                    params={
                        "id": f"_{crumbs}-{index}",
                        "value": value,
                        "style": style,
                        "parent": row_id,
                    },
                    bounds=True,
                )
                column += 1

        self.tables[name] = table_id

    def load_tables(self):
        """Collecting all tables names and cells id."""
        self.index = {}
        self.tables = {}
        for cell in self._root.childNodes:
            object_id = cell.getAttribute("id")
            parent_id = cell.getAttribute("parent")
            style = cell.getAttribute("style")

            # Table
            if "shape=table;" in style:
                table_id = object_id
                name = cell.getAttribute("value")
                self.index[table_id] = self.tables[name] = {
                    "id": table_id,
                    "name": name,
                    "rows": {},
                    "type": "table",
                }

            # Row
            elif "shape=tableRow" in style:
                row_id = object_id
                table = self.index[parent_id]
                self.index[row_id] = table["rows"][row_id] = {
                    "id": row_id,
                    "table_id": table["id"],
                    "cells": {},
                    "type": "row",
                }

            # Cell
            elif "shape=partialRectangle" in style:
                cell_id = object_id
                row = self.index[parent_id]
                table = self.index[row["table_id"]]
                name = cell.getAttribute("value")
                self.index[cell_id] = row["cells"][cell_id] = {
                    "id": cell_id,
                    "row_id": row["id"],
                    "table_id": table["id"],
                    "name": name,
                    "type": "cell",
                }

            # Link
            elif "edgeStyle" in style:
                source_id = cell.getAttribute("source")
                target_id = cell.getAttribute("target")
                if source_id and target_id:
                    self.links.append((source_id, target_id))
                    self.links.append((target_id, source_id))

    def find_recursive(self, cell_id):
        """Return list nested DOM Elements."""
        # WARNING: Recursive scanning is too slow
        cells = []
        for cell in self._root.childNodes:
            object_id = cell.getAttribute("id")
            parent_id = cell.getAttribute("parent")
            if object_id == cell_id:
                cells.append(cell)
            if parent_id == cell_id:
                cells += self.find_recursive(object_id)
        return cells

    def remove_cells(self, cells):
        """Remove DOM Elements."""
        for cell in cells:
            self._root.removeChild(cell)

    def remove_table(self, name=""):
        """Remove table from diagram by name."""
        table = self.tables.get(name)
        table_id = table["id"]
        items = [x for x in self.index if self.index[x].get("table_id") == table_id]
        self.remove_cells(items + [table_id])

    def replace_table(self, name="", x=0, y=0, width=200, height=200, style=None, data=[]):
        """Replace table by name with new data."""
        self.remove_table(name)
        self.add_table(name, x, y, width, height, style, data)

    def update_table(self, name="", data=[]):
        """Update table by name with new data."""
        table = self.tables.get(name)
        for r, row_id in enumerate(table["rows"]):
            row = table["rows"][row_id]
            for c, cell_id in enumerate(row["cells"]):
                cell = row["cells"][cell_id]
                element = self.find_element(cell_id)
                if data[r][c] != cell["name"]:
                    element.setAttribute("value", str(data[r][c]))

    def add_link(self, source="", target="", style=None):
        """Add simple link as a line without arrows."""
        crumbs = self.random_crumbs()

        source = self.tables.get(source)
        target = self.tables.get(target)

        if not source or not target:
            return

        source_id = source["id"]
        target_id = target["id"]

        for i, x in enumerate(self.links):
            if source_id == x[0] and target_id == x[1]:
                # is already linked
                return

        index = 1
        link_id = f"_{crumbs}-{index}"
        cell = self.create_element(
            "mxCell",
            {
                "id": link_id,
                "style": styles.LINK,
                "source": source["id"],
                "target": target["id"],
                "edge": "1",
                "parent": "1",
            },
        )

        geometry_relative = self.create_element(
            name="mxGeometry",
            params={"relative": "1", "as": "geometry"}
        )

        cell.appendChild(geometry_relative)
        self._root.appendChild(cell)

        self.links.append((source_id, target_id))
        self.links.append((target_id, source_id))
