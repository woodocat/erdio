import os
import click
from pydbml import PyDBML
from erdio.drawio import Drawio
import erdio.styles as styles


@click.group()
def cli():
    """
    Command line utility to converting DBML to Draw.io editable diagram.
    """


@cli.command()
@click.option(
    "--target",
    "-t",
    help="Target directory with diagram-as-code manifests",
    default=os.getenv("TARGET_DIR", "./target/"),
    type=click.Path(),
)
@click.option(
    "--grid-columns",
    "-c",
    default=0,
    help="Placing tables in a grid with number of columns",
    type=int,
)
@click.option(
    "--remove-common-prefix",
    "-r",
    default=True,
    help="Reduce table name length with removing common prefix",
)
def run(target, grid_columns, remove_common_prefix):
    """Convert all files in target directory."""
    for filename in os.listdir(target):
        if not filename.endswith('.dbml'):
            continue
        dbml_file = os.path.join(target, filename)
        convert_file(
            dbml_file=dbml_file,
            drawio_file=None,
            remove_common_prefix=remove_common_prefix,
            grid_columns=grid_columns,
        )


def convert_file(dbml_file, drawio_file=None, remove_common_prefix=True, grid_columns=0):
    drawio_file = drawio_file or dbml_file.replace('.dbml', '.drawio')
    diagram = Drawio(drawio_file)
    with open(dbml_file) as f:
        dbml = PyDBML(f)

        col = 0
        row = 0
        column_max_y = {}

        common_prefix = ""
        if remove_common_prefix:
            table_names = [x.name for x in dbml.tables]
            common_prefix = os.path.commonprefix(table_names)

        for table in dbml.tables:
            table_name = table.name.replace(common_prefix, "")

            prefix = table_name[:3]
            color_default = styles.get_default_color()
            color_map = styles.get_default_color_map()
            color = color_map.get(prefix, color_default)

            column_list = []
            for column in table.columns:
                column_list.append(["", column.name])

            x = styles.ROW_WIDTH * col
            y = column_max_y[col] if col in column_max_y else 0

            if table_name not in diagram.tables.keys():
                diagram.add_table(
                    name=table_name,
                    data=column_list,
                    style=color,
                    x=x,
                    y=y,
                )
            else:
                diagram.replace_table(
                    name=table_name,
                    data=column_list,
                    style=color,
                )

            column_max_y[col] = y + styles.ROW_HEIGHT * len(table.columns) + 40
            if grid_columns:
                col += 1
                if col == grid_columns:
                    col = 0
                    row += 1

    diagram.save()
