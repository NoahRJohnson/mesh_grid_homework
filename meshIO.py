def writeObj(vertices, faces, out_fname, commentString = None):
  """
  Writes out a mesh in .obj format.

  Parameters
  ----------
  vertices : list
    A list of vertices in the mesh. Each vertex should have the format
    (x, y, z).
  faces : list
    A list of faces in the mesh. Each face is a list of vertex IDs that make
    up the face. These vertex IDs should be 0-based indices into the vertices
    list.
  out_fname : str
    The file name of the object file.
  commentString : str (optional)
    A string to place at the top of the object file. Ensure that each newline
    in this string begins with a '#'.
  """

  with open(out_fname, 'w') as f:

    # Default header
    header = "# mesh written by writeObj function\n"

    # Optionally extend the header with a user string
    if commentString is not None:
      header += commentString + '\n'

    # Write out the header
    f.write(header)

    # Write out all of the vertices
    for x, y, z in vertices:
      f.write(f"v {x} {y} {z}\n")

    # Then write out all of the faces
    for face in faces:
      f.write("f")
      for vertex_id in face:
        if vertex_id < 0:
          import pdb; pdb.set_trace()
        f.write(" {}".format(vertex_id + 1))  # 1-based indexing
      f.write("\n")
