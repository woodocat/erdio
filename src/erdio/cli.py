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
    help="Placing tables as grid with number of columns",
    type=int,
)
def run(target, grid_columns):
    """Convert all files in target directory."""
    for filename in os.listdir(target):
        if not filename.endswith('.dbml'):
            continue
        dbml_file = os.path.join(target, filename)
        convert_file(
            dbml_file=dbml_file,
            drawio_file=None,
            project_name=None,
            grid_columns=grid_columns,
        )


@cli.command()
@click.option(
    "--dbml-file",
    help="The diagram-as-code full path to manifest",
    type=click.Path(),
)
@click.option(
    "--drawio-file",
    help="Drawio file full path",
    type=click.Path(),
)
def convert(dbml_file, drawio_file):
    """Run the convertion for single file."""
    convert_file(dbml_file, drawio_file)


def convert_file(dbml_file, drawio_file=None, project_name="project", grid_columns=0):
    drawio_file = drawio_file or dbml_file.replace('.dbml', '.drawio')
    diagram = Drawio(drawio_file)
    with open(dbml_file) as f:
        dbml = PyDBML(f)

        col = 0
        row = 0
        ROW_WIDTH = 240
        ROW_HEIGHT = 30
        column_max_y = {}

        for table in dbml.tables:
            if len(table.columns) < 2:
                # Empty table?
                continue

            table_name = table.name.replace(f"model.{project_name}.", "")

            prefix = table_name[:3]
            color_default = styles.get_default_color()
            color_map = styles.get_default_color_map()
            color = color_map.get(prefix, color_default)

            column_list = []
            for column in table.columns:
                column_list.append(["", column.name])

            x = ROW_WIDTH * col
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

            column_max_y[col] = y + ROW_HEIGHT * len(table.columns) + 40
            if grid_columns:
                col += 1
                if col == grid_columns:
                    col = 0
                    row += 1

    diagram.save()
