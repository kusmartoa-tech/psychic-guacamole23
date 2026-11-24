import bpy
import math
from mathutils import Vector

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.fps = 30
    scene.view_settings.view_transform = 'Standard'

def create_toon_material(name, base_color, shadow_color=None):
    if shadow_color is None:
        shadow_color = (base_color[0]*0.65, base_color[1]*0.65, base_color[2]*0.65, 1.0)
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    shader_to_rgb = nodes.new('ShaderNodeShaderToRGB')
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = shadow_color
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = base_color
    links.new(diffuse.outputs['BSDF'], shader_to_rgb.inputs['Shader'])
    links.new(shader_to_rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])
    return mat

def add_solidify_outline(obj, thickness=0.025):
    mat_outline = bpy.data.materials.get("Outline_Black")
    if not mat_outline:
        mat_outline = bpy.data.materials.new(name="Outline_Black")
        mat_outline.use_nodes = True
        mat_outline.use_backface_culling = True
        bsdf = mat_outline.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1.0)
        bsdf.inputs['Roughness'].default_value = 1.0
    obj.data.materials.append(mat_outline)
    mod = obj.modifiers.new(name="Outline", type='SOLIDIFY')
    mod.thickness = thickness
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.material_offset = len(obj.data.materials) - 1

def build_environment():
    mat_grass = create_toon_material("Grass_Toon", (0.32, 0.48, 0.22, 1.0))
    mat_road = create_toon_material("Road_Toon", (0.58, 0.46, 0.32, 1.0))
    mat_red = create_toon_material("Border_Red", (0.78, 0.28, 0.22, 1.0))
    mat_teal = create_toon_material("Border_Teal", (0.22, 0.58, 0.56, 1.0))

    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 25, 0))
    ground = bpy.context.active_object
    ground.name = "Ground_Grass"
    ground.data.materials.append(mat_grass)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 25, 0.01))
    road = bpy.context.active_object
    road.name = "Border_Road"
    road.scale = (3.5, 80, 1)
    road.data.materials.append(mat_road)

    for i in range(12):
        y_pos = 2.0 + (i * 3.2)
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(-0.125, y_pos, 0.25))
        box_l = bpy.context.active_object
        box_l.scale = (0.5, 1.0, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        box_l.data.materials.append(mat_red)
        add_solidify_outline(box_l, 0.015)

        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0.125, y_pos, 0.25))
        box_r = bpy.context.active_object
        box_r.scale = (0.5, 1.0, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        box_r.data.materials.append(mat_teal)
        add_solidify_outline(box_r, 0.015)

def create_stickman_king(location=(-1.6, 4.5, 0)):
    king_empty = bpy.data.objects.new("King_Red_Root", None)
    bpy.context.collection.objects.link(king_empty)
    king_empty.location = location

    mat_cloak = create_toon_material("King_Cloak", (0.85, 0.2, 0.18, 1.0))
    mat_gold = create_toon_material("Crown_Gold", (0.95, 0.78, 0.2, 1.0))
    mat_wood = create_toon_material("Spear_Wood", (0.45, 0.28, 0.15, 1.0))

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.28, depth=0.9, location=(0, 0, 0.85))
    body = bpy.context.active_object
    body.name = "King_Body"
    body.scale = (1.0, 0.6, 1.0)
    body.parent = king_empty
    body.data.materials.append(mat_cloak)
    add_solidify_outline(body, 0.02)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.22, depth=0.22, location=(0, 0, 1.98))
    crown = bpy.context.active_object
    crown.name = "King_Crown"
    crown.parent = king_empty
    crown.data.materials.append(mat_gold)
    add_solidify_outline(crown, 0.015)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=2.6, location=(0.2, -0.25, 1.05))
    spear = bpy.context.active_object
    spear.name = "King_Spear"
    spear.rotation_euler = (0, math.radians(85), 0)
    spear.parent = king_empty
    spear.data.materials.append(mat_wood)
    add_solidify_outline(spear, 0.01)

    gp_data = bpy.data.grease_pencils.new("King_2D_Parts")
    gp_obj = bpy.data.objects.new("King_2D_Parts", gp_data)
    bpy.context.collection.objects.link(gp_obj)
    gp_obj.parent = king_empty

    mat_gp_line = bpy.data.materials.new("GP_Black")
    bpy.data.materials.create_gpencil_data(mat_gp_line)
    mat_gp_line.grease_pencil.color = (0.05, 0.05, 0.05, 1.0)

    mat_gp_head = bpy.data.materials.new("GP_Head_Fill")
    bpy.data.materials.create_gpencil_data(mat_gp_head)
    mat_gp_head.grease_pencil.color = (0.05, 0.05, 0.05, 1.0)
    mat_gp_head.grease_pencil.show_fill = True
    mat_gp_head.grease_pencil.fill_color = (0.98, 0.98, 0.98, 1.0)

    gp_obj.data.materials.append(mat_gp_line)
    gp_obj.data.materials.append(mat_gp_head)

    layer = gp_data.layers.new("Character_Lines", set_active=True)
    frame = layer.frames.new(1)

    def add_stroke(points, mat_idx=0, width=25, cyclic=False):
        s = frame.strokes.new()
        s.material_index = mat_idx
        s.line_width = width
        s.use_cyclic = cyclic
        s.points.add(len(points))
        for i, pt in enumerate(points):
            s.points[i].co = pt

    head_pts = []
    for a in range(24):
        ang = (a / 24) * 2 * math.pi
        head_pts.append((math.cos(ang)*0.32, -0.05, 1.62 + math.sin(ang)*0.34))
    add_stroke(head_pts, mat_idx=1, width=30, cyclic=True)

    add_stroke([(-0.14, -0.08, 1.72), (-0.02, -0.08, 1.68)], width=22)
    add_stroke([(0.04, -0.08, 1.68), (0.16, -0.08, 1.72)], width=22)
    add_stroke([(-0.11, -0.08, 1.64), (-0.04, -0.08, 1.64)], width=28)
    add_stroke([(0.05, -0.08, 1.64), (0.12, -0.08, 1.64)], width=28)
    add_stroke([(-0.06, -0.08, 1.52), (0.08, -0.08, 1.54)], width=20)
    add_stroke([(0.0, -0.08, 1.46), (0.02, -0.08, 1.38)], width=22)

    add_stroke([(-0.1, 0, 0.4), (-0.1, 0, 0.02), (-0.02, -0.05, 0.02)], width=28)
    add_stroke([(0.1, 0, 0.4), (0.1, 0, 0.02), (0.18, -0.05, 0.02)], width=28)

    add_stroke([(-0.22, -0.1, 1.15), (-0.42, -0.2, 1.05), (-0.25, -0.25, 1.02)], width=28)
    add_stroke([(0.22, -0.1, 1.15), (0.4, -0.2, 1.08), (0.35, -0.25, 1.05)], width=28)
    return king_empty

def setup_lighting_and_camera():
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(-30))

    world = bpy.data.worlds.new("Cartoon_Sky")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs['Color'].default_value = (0.58, 0.74, 0.88, 1.0)
    bg.inputs['Strength'].default_value = 1.1

    bpy.ops.object.camera_add(location=(0.0, -1.5, 1.45))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(82), 0, 0)
    cam.data.lens = 35
    bpy.context.scene.camera = cam

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 90
    cam.keyframe_insert(data_path="location", frame=1)
    cam.location.y = 0.8
    cam.keyframe_insert(data_path="location", frame=90)

if __name__ == "__main__":
    reset_scene()
    build_environment()
    king = create_stickman_king(location=(-1.2, 4.2, 0))
    setup_lighting_and_camera()
    print("Scene 2.5D Rick Clips berhasil dibuat di Blender!")
    bpy.context.scene.render.filepath = "//out/frame_"
    bpy.context.scene.render.image_settings.file_format = 'PNG'
