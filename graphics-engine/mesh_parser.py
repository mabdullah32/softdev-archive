from draw import add_polygon
from matrix import print_matrix

def add_mesh(filename, polygons):
    mesh_file = open(filename).read().strip().split('\n')

    format = filename[filename.rfind('.'):]

    if (format == '.obj'):
        parse_obj(mesh_file, polygons)
    elif (format == '.stl'):
        parse_stl(mesh_file, polygons)
    else:
        print('not a valid mesh file')

#stl fucntions
def parse_stl(mesh_file, polygons):
    i=0
    while i < len(mesh_file):
        line = mesh_file[i].strip()
        if line == 'outer loop':
            vertices = mesh_file[i+1:i+4]
            vertices = prase_stl_vertices(vertices)
            p0 = vertices[0]
            p1 = vertices[1]
            p2 = vertices[2]
            add_polygon(polygons,
                        p0[0], p0[1], p0[2],
                        p1[0], p1[1], p1[2],
                        p2[0], p2[1], p2[2])
            i+= 3
        i+= 1

def prase_stl_vertices(vlist):
    vertices = []
    for vertex in vlist:
        vertex = vertex.split()
        vertex = [float(x) for x in vertex[1:]]
        vertices.append(vertex)
    return vertices

#obj functions
def parse_obj(mesh_file, polygons):
    #get vertices
    vertices = get_vertices(mesh_file)
    #parse triangles
    add_faces(mesh_file, vertices, polygons)

def get_vertices(mesh_file):
    vertices = []
    for line in mesh_file:
        if (len(line) > 0):
            if (line[0] == 'v'):
                line = line[2:].split()
                vs = [float(x) for x in line]
                vertices.append(vs)
    return vertices

def add_faces(mesh_file, vertices, polygons):
    for line in mesh_file:
        if (len(line) > 0):
            if (line[0] == 'f'):
                line = line[2:].split()
                face_vertices = [int(x) for x in line]
                p0 = vertices[face_vertices[0]-1]
                p1 = vertices[face_vertices[1]-1]
                p2 = vertices[face_vertices[2]-1]
                add_polygon(polygons,
                            p0[0], p0[1], p0[2],
                            p1[0], p1[1], p1[2],
                            p2[0], p2[1], p2[2])
