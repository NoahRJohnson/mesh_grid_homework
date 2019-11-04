#!/usr/bin/env python3

import argparse
import math
import numpy as np

from meshIO import writeObj


def make_grid(width, height, grid_spacing, sin_frequency):
  """
  Make a mesh grid of squares with the given dimensions.
  Since the dimensions can be floats, there may be squished
  rectangles on the margins of the grid.

  The heights of the grid will follow a sine wave along the
  x axis.

  Parameters
  ----------
  height : float
    Width of grid.
  width : float
    Height of grid.
  grid_spacing : float
    The spacing between vertices in the mesh grid.
  sin_frequency : float
    The frequency of the sine wave that will give the grid's Z value.

  Returns
  -------
  tuple
    A (vertices, faces) pair representing the mesh grid.
  """

  # Create a grid of cells, each cell is grid_spacing by grid_spacing
  columns = np.arange(0, width, grid_spacing)
  rows = np.arange(0, height, grid_spacing)

  # Add smaller cells to the margin
  np.append(columns, width)
  np.append(rows, height)

  # Make helper functions for traversing the grid connections
  def back_a_row(vertex_index):
    """ Get the index of the vertex one row above this vertex. """
    back_index = vertex_index - len(columns)
    if back_index < 0:
      # We've gone above the first row
      raise IndexError
    else:
      return back_index

  def to_the_left(vertex_index):
    """ Get the index of the vertex one column to the left of this vertex. """
    if vertex_index % len(columns) == 0:
      # We are the first column in a row, so we can't go left
      raise IndexError
    else:
      return vertex_index - 1

  # Make a helper function for creating a grid cell
  def create_cell(lower_right_vertex_index):
    """ Create a grid cell made of two triangles. """

    # Figure out the IDs of the vertices that will make up the grid cell
    lower_left_vertex_index = to_the_left(vertex_index)
    upper_right_vertex_index = back_a_row(vertex_index)
    upper_left_vertex_index = to_the_left(upper_right_vertex_index)

    # Create the two triangular faces of the grid cell
    triangle1 = [upper_left_vertex_index, lower_right_vertex_index, lower_left_vertex_index]
    triangle2 = [lower_right_vertex_index, upper_left_vertex_index, upper_right_vertex_index ]

    return (triangle1, triangle2)


  # Go through the grid - in row-major order - and construct vertices
  # While we're at it, construct faces for each grid cell
  vertices = list()
  faces = list()
  vertex_index = 0  # the index of the current vertex
  for row in rows:
    for col in columns:

      # Try to make a cell using the vertices above and to the left of this
      # vertex
      try:
        for face in create_cell(vertex_index):
          faces.append(face)
      except IndexError:
        # These helper functions raise index errors when they go out of bounds.
        # If they went out of bounds, this vertex isn't on the lower right
        # of a cell. So just skip the cell creation for this vertex.
        pass

      # Store the geometry for this vertex
      vertices.append((col, row, math.sin(col / sin_frequency)))

      # Increment the vertex index
      vertex_index += 1

  return (vertices, faces)


if __name__ == "__main__":

  # Test run example: "./make_grid.py 123 123"

  # Parse command-line args
  parser = argparse.ArgumentParser(description="Create a triangular mesh grid "
                                               "of x width and y height.")
  parser.add_argument('width', type=float, help='Width of grid')
  parser.add_argument('height', type=float, help='Height of grid')
  parser.add_argument('obj_file', type=str, nargs='?', default='grid.obj',
                      help='Output file (defaults to grid.obj)')
  parser.add_argument('--grid_spacing', type=float, default=1.0,
                      help='Spacing between vertices in the grid.')
  parser.add_argument('-f', '--frequency', type=float, default=1.0,
                      help='Frequency of sine wave (defaults to 1.0)')
  args = parser.parse_args()

  print(f'width = {args.width}')
  print(f'height = {args.height}')
  print(f'obj_file = {args.obj_file}')
  print(f'grid_spacing = {args.grid_spacing}')
  print(f'frequency = {args.frequency}')

  # Produce mesh grid
  vertices, faces = make_grid(args.width, args.height, args.grid_spacing, args.frequency)

  # Save to .obj file
  writeObj(vertices, faces, args.obj_file)

  print(f'Success! Wrote out mesh to {args.obj_file}')
