import mdl
from display import *
from matrix import *
from draw import *
from mesh_parser import *
from sys import exit
import math

"""======== first_pass() ==========
  loop through opcodes looking for frames, basename, vary.

  set instance variables where appropriate.
  display error messages or warnings if needed
  ===================="""
def first_pass(commands):
    frames = 1
    basename = 'frame'
    has_vary = False
    has_frames = False
    
    # Loop through all commands
    for command in commands:
        if command['op'] == 'frames':
            frames = int(command['args'][0])
            has_frames = True
        elif command['op'] == 'basename':
            basename = command['args'][0]
        elif command['op'] == 'vary':
            has_vary = True

    if has_vary and not has_frames:
        print("ERROR: vary command used but frames not set")
        exit()
    
    return (frames, basename)

"""======== second_pass() ==========
handle all vary commands.

In order to set the knobs for animation, we need to keep
a separate value for each knob for each frame. We can do
this by using a List of dictionaries. Each list index
will correspond to a frame (eg. knobs[0] would be the first
frame, knobs[2] would be the 3rd frame and so on).

Each index should contain a dictionary where each key is
a knob name, and the value is the calculated value.
===================="""
def second_pass(commands, frames):
    knob_frames = [{} for f in range(frames)]

    for command in commands:
        if command['op'] == 'vary':
            knob_name = command['knob']
            start_frame = int(command['args'][0])
            end_frame = int(command['args'][1])
            start_val = float(command['args'][2])
            end_val = float(command['args'][3])
            
            # Get interpolation type (default to linear)
            interp_type = 'linear'
            interp_param = None
            
            if len(command['args']) > 4:
                interp_type = command['args'][4]
                if len(command['args']) > 5:
                    interp_param = command['args'][5]

            if start_frame < 0 or end_frame >= frames:
                print(f"ERROR: vary command has invalid frame range: {start_frame} to {end_frame}")
                exit()
            
            if start_frame > end_frame:
                print(f"ERROR: vary command has start_frame > end_frame")
                exit()

            frame_range = end_frame - start_frame
            
            if frame_range == 0:
                knob_frames[start_frame][knob_name] = start_val
            else:
                value_change = end_val - start_val
                
                for frame_num in range(start_frame, end_frame + 1):
                    # Calculate normalized progress (0 to 1)
                    t = (frame_num - start_frame) / frame_range
                    
                    # Apply interpolation based on type
                    if interp_type == 'linear':
                        progress = t
                    
                    elif interp_type == 'exponential':

                        base = float(interp_param) if interp_param else 2.0
                        if base <= 0:
                            base = 2.0
                        progress = (base ** t - 1) / (base - 1) if base != 1 else t
                    
                    elif interp_type == 'logarithmic':
                        # Logarithmic (inverse of exponential)
                        # Fast at start, slow at end
                        progress = math.log(1 + t * 9) / math.log(10)  # log10(1 + 9t)
                    
                    elif interp_type == 'cosine':
                        # Smooth ease in/out using cosine
                        progress = (1 - math.cos(t * math.pi)) / 2
                                        
                    else:
                        print(f"WARNING: Unknown interpolation type '{interp_type}', using linear")
                        progress = t
                    
                    knob_value = start_val + (progress * value_change)
                    knob_frames[frame_num][knob_name] = knob_value
    
    return knob_frames

def draw_polygons_phong(polygons, screen, zbuffer, view, ambient, light, 
                       symbols, reflect, vertex_normals):
    """Draw polygons using Phong shading"""
    if len(polygons) < 2:
        print('Need at least 3 points to draw')
        return

    point = 0
    while point < len(polygons) - 2:
        normal = calculate_normal(polygons, point)[:]
        
        if normal[2] > 0:
            # Get vertex normals for this triangle
            tri_normals = [vertex_normals[point], 
                          vertex_normals[point+1], 
                          vertex_normals[point+2]]
            
            scanline_convert_phong(polygons, point, screen, zbuffer, 
                                  view, ambient, light, symbols, reflect, tri_normals)
        point += 3

def calculate_cone_normals(polygons):
    """
    Calculate smooth vertex normals for cone by averaging face normals
    """
    vertex_normals = []
    
    # For each vertex, calculate average of adjacent face normals
    for i in range(0, len(polygons), 3):
        # Get face normal
        face_normal = calculate_normal(polygons, i)
        
        # For simplicity, use face normal as vertex normal
        # (In production, you'd average normals from all adjacent faces)
        vertex_normals.append(face_normal[:])
        vertex_normals.append(face_normal[:])
        vertex_normals.append(face_normal[:])
    
    return vertex_normals

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    default_light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]
    
    lights = []

    color = [0, 255, 0]

    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    frames, basename = first_pass(commands)
    knob_list = second_pass(commands, frames)

    for frame_num in range(frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [[x[:] for x in tmp]]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        step_2d = 100
        consts = ''
        coords = []
        coords1 = []
        reflect = '.white'

        lights = []
        
        for command in commands:
            c = command['op']
            args = command['args']

            if c == 'mesh':
                if command['constants']:
                    reflect = command['constants']
                add_mesh(args[0], tmp)
                matrix_mult(stack[-1], tmp)
                current_lights = lights if lights else [default_light]
                draw_polygons(tmp, screen, zbuffer, view, ambient, current_lights, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult(stack[-1], tmp)
                current_lights = lights if lights else [default_light]
                draw_polygons(tmp, screen, zbuffer, view, ambient, current_lights, symbols, reflect)
                tmp = []
                reflect = '.white'
                
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult(stack[-1], tmp)
                current_lights = lights if lights else [default_light]
                draw_polygons(tmp, screen, zbuffer, view, ambient, current_lights, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'cone':
                if command['constants']:
                    reflect = command['constants']
                add_cone(tmp, args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult(stack[-1], tmp)
                current_lights = lights if lights else [default_light]
                draw_polygons(tmp, screen, zbuffer, view, ambient, 
                            current_lights, symbols, reflect)
                tmp = []
                reflect = '.white'

            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult(stack[-1], tmp)
                current_lights = lights if lights else [default_light]
                draw_polygons(tmp, screen, zbuffer, view, ambient, current_lights, symbols, reflect)
                tmp = []
                reflect = '.white'
                
            elif c == 'line':
                if command['constants']:
                    reflect = command['constants']
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult(stack[-1], tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
                reflect = '.white'
                
            elif c == 'circle':
                if command['constants']:
                    reflect = command['constants']
                add_circle(tmp,
                           args[0], args[1], args[2], args[3], step_2d)
                matrix_mult(stack[-1], tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
                reflect = '.white'
                
            elif c == 'bezier':
                if command['constants']:
                    reflect = command['constants']
                add_curve(tmp,
                         args[0], args[1], args[3], args[4], args[6], args[7], args[9], args[10], step_2d, 'bezier')
                matrix_mult(stack[-1], tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
                reflect = '.white'
                
            elif c == 'hermite':
                if command['constants']:
                    reflect = command['constants']
                add_curve(tmp,
                         args[0], args[1], args[3], args[4], args[6], args[7], args[9], args[10], step_2d, 'hermite')
                matrix_mult(stack[-1], tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
                reflect = '.white'
                
            elif c == 'move':
                kval = 1

                if command['knob']:
                    knob_name = command['knob']
                    kval = knob_list[frame_num].get(knob_name, 1)

                tmp = make_translate(args[0]*kval, args[1]*kval, args[2]*kval)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                
            elif c == 'scale':

                if command['knob']:
                    knob_name = command['knob']
                    kval = knob_list[frame_num].get(knob_name, 1)

                tmp = make_scale(args[0]*kval, args[1]*kval, args[2]*kval)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                
            elif c == 'rotate':
                kval = 1

                if command['knob']:
                    knob_name = command['knob']
                    kval = knob_list[frame_num].get(knob_name, 1)

                theta = args[1] * (math.pi/180) * kval
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                
            elif c == 'set':

                knob_name = command['knob']
                value = float(command['args'][0])
                knob_list[frame_num][knob_name] = value
                
            elif c == 'light':
                # light name x y z r g b
                # args[0] = name (we can ignore for now)
                # args[1:4] = location (x, y, z)
                # args[4:7] = color (r, g, b)
                light_location = [float(args[1]), float(args[2]), float(args[3])]
                light_color = [int(args[4]), int(args[5]), int(args[6])]
                lights.append([light_location, light_color])

            elif c == 'shading':
                shading_mode = args[0]    

            elif c == 'push':
                stack.append([x[:] for x in stack[-1]])
                
            elif c == 'pop':
                stack.pop()
                
            elif c == 'display':
                if frames == 1:
                    display(screen)
                    
            elif c == 'save':
                if frames == 1:
                    save_extension(screen, args[0])

        if frames > 1:
            filename = f"anim/{basename}{frame_num:03d}.png"
            save_extension(screen, filename)
            print(f"Saved frame {frame_num}: {filename}")

    if frames > 1:
        make_animation(basename)