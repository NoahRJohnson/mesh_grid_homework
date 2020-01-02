#!/usr/bin/env python3

import argparse
import numpy as np

from meshIO import writeObj


def make_cylinder(length, radius, linear_resolution, angular_resolution):
  """
  Make a mesh of a cylinder with the given dimensions.

  The heights of the grid will follow a sine wave along the
  x axis.

  Parameters
  ----------
  length : float
    How long the cylinder will be along its major axis.
  radius : float
    The radius of the circle extruded to create the cylinder.
  linear_resolution : float
    The spacing between vertices along the major axis.
  angular_resolution : float
    The spacing between vertices around the circumference (in radians).

  Returns
  -------
  tuple
    A (vertices, faces) pair representing the mesh.
  """

  # Create a grid of cells, each cell is grid_spacing by grid_spacing
  columns = np.arange(0, length, linear_resolution)
  rows = np.arange(0, 2 * np.pi, angular_resolution)

  # Add smaller cells to the margin
  np.append(columns, length)

  ####################
  # Helper functions #
  ####################

  def back_a_row(vertex_index):
    """
    Get the index of the vertex in the same column position, but on the previous row.
    """
    back_index = vertex_index - len(columns)
    if back_index < 0:
      # We've gone before the first row
      raise IndexError
    else:
      return back_index

  def back_a_column(vertex_index):
    """
    Get the index of the vertex in the same row position, but on the previous column.
    """
    if vertex_index % len(columns) == 0:
      # We are the first column in a row, so we can't go back
      raise IndexError
    else:
      return vertex_index - 1

  def create_cell(lower_right_vertex_index):
    """
    Create a rectangular face made of two triangles.
    """

    # Figure out the IDs of the vertices that will make up the grid cell
    lower_left_vertex_index = back_a_column(vertex_index)
    upper_right_vertex_index = back_a_row(vertex_index)
    upper_left_vertex_index = back_a_column(upper_right_vertex_index)

    # Create the two triangular faces of the grid cell
    # triangle1 = [lower_left_vertex_index, lower_right_vertex_index, upper_left_vertex_index]
    triangle1 = [upper_left_vertex_index, lower_right_vertex_index, lower_left_vertex_index]
    # triangle2 = [upper_right_vertex_index, upper_left_vertex_index, lower_right_vertex_index]
    triangle2 = [lower_right_vertex_index, upper_left_vertex_index, upper_right_vertex_index]

    return (triangle1, triangle2)


  # Go through the grid - in row-major order - and construct vertices
  # While we're at it, construct faces for each grid cell
  # The vertices will move linearly along the X axis, and along a circle in the Y-Z plane
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
      vertices.append((col, radius * np.sin(row), radius * np.cos(row)))

      # Increment the vertex index
      vertex_index += 1

  # Connect the edges of the grid to complete the circle
  first_row_vertices = range(len(columns))
  last_row_vertices = range(vertex_index - len(columns), vertex_index)
  for i in range(len(first_row_vertices) - 1):

    # Figure out the IDs of the vertices that will make up the grid cell
    lower_left_vertex_index = last_row_vertices[i]
    lower_right_vertex_index = last_row_vertices[i + 1]
    upper_left_vertex_index = first_row_vertices[i]
    upper_right_vertex_index = first_row_vertices[i + 1]

    # Create the two triangular faces of the grid cell
    triangle1 = [lower_left_vertex_index, lower_right_vertex_index, upper_right_vertex_index]
    triangle2 = [upper_right_vertex_index, upper_left_vertex_index, lower_left_vertex_index]

    faces.append(triangle1)
    faces.append(triangle2)

  # Put a top and bottom face on the cylinder
  top_face = range(0, vertex_index, len(columns))
  bottom_face = range(vertex_index - 1, len(columns) - 2, -1 * len(columns))

  faces.append(top_face)
  faces.append(bottom_face)

  return (vertices, faces)


if __name__ == "__main__":

  # Test run example: "./make_grid.py 123 123"

  # Parse command-line args
  parser = argparse.ArgumentParser(description="Create a triangular mesh grid "
                                               "of x width and y height.")
  parser.add_argument('length', type=float, help='Width of grid')
  parser.add_argument('radius', type=float, help='Height of grid')
  parser.add_argument('linear_resolution', type=float, help='Height of grid')
  parser.add_argument('angular_resolution', type=float, help='Height of grid')
  parser.add_argument('obj_file', type=str, nargs='?', default='grid.obj',
                      help='Output file (defaults to grid.obj)')
  args = parser.parse_args()

  print(f'length = {args.length}')
  print(f'radius = {args.radius}')
  print(f'linear_resolution = {args.linear_resolution}')
  print(f'angular_resolution = {args.angular_resolution}')
  print(f'obj_file = {args.obj_file}')

  # Produce mesh grid
  vertices, faces = make_cylinder(args.length, args.radius, args.linear_resolution, args.angular_resolution)

  # Save to .obj file
  writeObj(vertices, faces, args.obj_file)

  print(f'Success! Wrote out mesh to {args.obj_file}')
