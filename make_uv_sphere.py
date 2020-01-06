#!/usr/bin/env python3

import argparse
import numpy as np

from meshIO import writeObj


def make_uv_sphere(radius, longitude_resolution, latitude_resolution):
  """
  Make a mesh of a UV sphere with the given radius, and angular resolutions.

  Parameters
  ----------
  radius : float
    The radius of the sphere centered around the origin.
  longitude_resolution : float
    The angular resolution along the X axis in radians.
  latitude_resolution : float
    The angular resolution along the Y axis in radians.

  Returns
  -------
  tuple
    A (vertices, faces) pair representing the mesh.
  """

  # Create a grid of cells
  columns = np.arange(longitude_resolution, np.pi, longitude_resolution)
  rows = np.arange(0, 2 * np.pi, latitude_resolution)

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
    triangle1 = [upper_left_vertex_index, lower_right_vertex_index, lower_left_vertex_index]
    triangle2 = [lower_right_vertex_index, upper_left_vertex_index, upper_right_vertex_index]

    return (triangle1, triangle2)


  # Go through the grid - in row-major order - and construct vertices
  # While we're at it, construct faces for each grid cell
  # The vertices will along a sphere
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
      vertices.append((radius * np.sin(col) * np.cos(row),
                       radius * np.sin(col) * np.sin(row),
                       radius * np.cos(col)))

      # Increment the vertex index
      vertex_index += 1

  # Connect the rows of the grid together
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

  # Add vertices on the column sides, and close up the sphere
  first_column_vertices = range(0, vertex_index - len(columns) + 1, len(columns))
  last_column_vertices = range(len(columns) - 1, vertex_index, len(columns))

  vertices.append((0, 0, radius))
  for v1, v2 in zip(first_column_vertices[:-1], first_column_vertices[1:]):
    faces.append([v1, v2, vertex_index])
  faces.append([first_column_vertices[-1], first_column_vertices[0], vertex_index])
  vertex_index += 1

  vertices.append((0, 0, -1 * radius))
  for v1, v2 in zip(last_column_vertices[:-1], last_column_vertices[1:]):
    faces.append([vertex_index, v2, v1])
  faces.append([vertex_index, last_column_vertices[0], last_column_vertices[-1]])
  vertex_index += 1

  return (vertices, faces)


if __name__ == "__main__":

  # Parse command-line args
  parser = argparse.ArgumentParser(description="Create a triangular mesh grid "
                                               "of a UV sphere.")
  parser.add_argument('radius', type=float, nargs='?', default=1.0,
                      help='Radius of sphere')
  parser.add_argument('longitude_resolution', type=float, nargs='?', default=0.1,
                      help='The angular resolution along the X axis in radians.')
  parser.add_argument('latitude_resolution', type=float, nargs='?', default=0.1,
                      help='The angular resolution along the Y axis in radians.')
  parser.add_argument('obj_file', type=str, nargs='?', default='grid.obj',
                      help='Output file (defaults to grid.obj)')
  args = parser.parse_args()

  print(f'radius = {args.radius}')
  print(f'longitude_resolution = {args.longitude_resolution}')
  print(f'latitude_resolution = {args.latitude_resolution}')
  print(f'obj_file = {args.obj_file}')

  # Produce mesh grid
  vertices, faces = make_uv_sphere(args.radius, args.longitude_resolution, args.latitude_resolution)

  # Save to .obj file
  writeObj(vertices, faces, args.obj_file)

  print(f'Success! Wrote out mesh to {args.obj_file}')
