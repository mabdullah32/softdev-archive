import math
from display import *


  # IMPORANT NOTE

  # Ambient light is represeneted by a color value

  # Point light sources are 2D arrays of doubles.
  #      - The fist index (LOCATION) represents the vector to the light.
  #      - The second index (COLOR) represents the color.

  # Reflection constants (ka, kd, ks) are represened as arrays of
  # doubles (red, green, blue)

AMBIENT = 0
DIFFUSE = 1
SPECULAR = 2
LOCATION = 0
COLOR = 1
SPECULAR_EXP = 4

#lighting functions
def get_lighting(normal, view, ambient, lights, symbols, reflect):
    """
    Calculate lighting with support for multiple light sources
    lights: list of light sources, each is [[x,y,z], [r,g,b]]
    """
    n = normal[:]
    normalize(n)
    normalize(view)
    r = symbols[reflect][1]

    total_light = calculate_ambient(ambient, r)

    for light in lights:

        light_dir = light[0][:]
        normalize(light_dir)

        d = calculate_diffuse(light, r, n)
        s = calculate_specular(light, r, view, n)

        total_light[RED] += d[RED] + s[RED]
        total_light[GREEN] += d[GREEN] + s[GREEN]
        total_light[BLUE] += d[BLUE] + s[BLUE]

    i = [0, 0, 0]
    i[RED] = int(total_light[RED])
    i[GREEN] = int(total_light[GREEN])
    i[BLUE] = int(total_light[BLUE])
    limit_color(i)

    return i

def get_lighting_phong(normal, view, ambient, lights, symbols, reflect):
    """
    Calculate lighting for Phong shading with multiple lights
    (per-pixel with interpolated normal)
    """
    n = normal[:]
    normalize(n)
    normalize(view)
    r = symbols[reflect][1]

    total_light = calculate_ambient(ambient, r)
    
    for light in lights:
        light_dir = light[0][:]
        normalize(light_dir)
        
        d = calculate_diffuse(light, r, n)
        s = calculate_specular(light, r, view, n)
        
        total_light[RED] += d[RED] + s[RED]
        total_light[GREEN] += d[GREEN] + s[GREEN]
        total_light[BLUE] += d[BLUE] + s[BLUE]
    
    i = [0, 0, 0]
    i[RED] = int(total_light[RED])
    i[GREEN] = int(total_light[GREEN])
    i[BLUE] = int(total_light[BLUE])
    limit_color(i)

    return i


def interpolate_normal(n0, n1, n2, bary_coords):
    """
    Interpolate normals using barycentric coordinates
    n0, n1, n2: vertex normals
    bary_coords: (alpha, beta, gamma) barycentric coordinates
    """
    alpha, beta, gamma = bary_coords
    
    normal = [0, 0, 0]
    normal[0] = alpha * n0[0] + beta * n1[0] + gamma * n2[0]
    normal[1] = alpha * n0[1] + beta * n1[1] + gamma * n2[1]
    normal[2] = alpha * n0[2] + beta * n1[2] + gamma * n2[2]
    
    return normal


def calculate_barycentric(x, y, p0, p1, p2):
    """
    Calculate barycentric coordinates for point (x, y) in triangle (p0, p1, p2)
    Returns: (alpha, beta, gamma)
    """
    x0, y0 = p0[0], p0[1]
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    
    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denom) < 0.0001:
        return (1.0/3, 1.0/3, 1.0/3)
    
    alpha = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / denom
    beta = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / denom
    gamma = 1 - alpha - beta
    
    return (alpha, beta, gamma)

def calculate_ambient(alight, reflect):
    a = [0, 0, 0]
    a[RED] = alight[RED] * reflect['red'][AMBIENT]
    a[GREEN] = alight[GREEN] * reflect['green'][AMBIENT]
    a[BLUE] = alight[BLUE] * reflect['blue'][AMBIENT]
    return a

def calculate_diffuse(light, reflect, normal):
    d = [0, 0, 0]

    dot = dot_product( light[LOCATION], normal)

    dot = dot if dot > 0 else 0
    d[RED] = light[COLOR][RED] * reflect['red'][DIFFUSE] * dot
    d[GREEN] = light[COLOR][GREEN] * reflect['green'][DIFFUSE] * dot
    d[BLUE] = light[COLOR][BLUE] * reflect['blue'][DIFFUSE] * dot
    return d

def calculate_specular(light, reflect, view, normal):
    s = [0, 0, 0]
    n = [0, 0, 0]

    result = 2 * dot_product(light[LOCATION], normal)
    n[0] = (normal[0] * result) - light[LOCATION][0]
    n[1] = (normal[1] * result) - light[LOCATION][1]
    n[2] = (normal[2] * result) - light[LOCATION][2]

    result = dot_product(n, view)
    result = result if result > 0 else 0
    result = pow( result, SPECULAR_EXP )

    s[RED] = light[COLOR][RED] * reflect['red'][SPECULAR] * result
    s[GREEN] = light[COLOR][GREEN] * reflect['green'][SPECULAR] * result
    s[BLUE] = light[COLOR][BLUE] * reflect['blue'][SPECULAR] * result
    return s

def limit_color(color):
    color[RED] = 255 if color[RED] > 255 else color[RED]
    color[GREEN] = 255 if color[GREEN] > 255 else color[GREEN]
    color[BLUE] = 255 if color[BLUE] > 255 else color[BLUE]

#vector functions
#normalize vetor, should modify the parameter
def normalize(vector):
    magnitude = math.sqrt( vector[0] * vector[0] +
                           vector[1] * vector[1] +
                           vector[2] * vector[2])
    for i in range(3):
        vector[i] = vector[i] / magnitude

#Return the dot porduct of a . b
def dot_product(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

#Calculate the surface normal for the triangle whose first
#point is located at index i in polygons
def calculate_normal(polygons, i):

    A = [0, 0, 0]
    B = [0, 0, 0]
    N = [0, 0, 0]

    A[0] = polygons[i+1][0] - polygons[i][0]
    A[1] = polygons[i+1][1] - polygons[i][1]
    A[2] = polygons[i+1][2] - polygons[i][2]

    B[0] = polygons[i+2][0] - polygons[i][0]
    B[1] = polygons[i+2][1] - polygons[i][1]
    B[2] = polygons[i+2][2] - polygons[i][2]

    N[0] = A[1] * B[2] - A[2] * B[1]
    N[1] = A[2] * B[0] - A[0] * B[2]
    N[2] = A[0] * B[1] - A[1] * B[0]

    return N
