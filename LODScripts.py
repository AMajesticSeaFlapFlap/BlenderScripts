import bpy
import os

from bpy.types import Panel


# percentages to use for the decimation process
LODs = [80, 50, 30, 20]


class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    
class VIEW3D_PT_tools_LOD(View3DPanel, Panel):
    """Simple Script to enhance LOD creation workflow"""
    bl_category = "Tools"
    bl_context = "objectmode"
    bl_label = "Level of Detail tools"

    def draw(self, context):
        layout = self.layout
     
        row = layout.row()
        row.operator("mesh.create_lods")
        
        col = layout.column()
        col.prop(context.scene, 'filepath', text='Export')
        
        row = layout.row()
        row.operator("mesh.export_lods")
        
        col = layout.column()
        col.prop(context.scene, 'filepath_import', text='Import')

        row = layout.row()
        row.operator("mesh.batch_create_lods")


class LODCreationWidget(bpy.types.Operator):
    """Generate the LODs"""
    bl_idname = "mesh.create_lods"
    bl_label = "Create LOD Meshes"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        # ensure that the LOD percentage data is in order so that the naming is correct
        LODs.sort()
        LODs.reverse()

        self.create_lod_meshes(bpy.context.object)
            
        return {'FINISHED'}
    
    def create_lod_meshes(self, obj):
        group_name = "LODs_" + obj.name
        if group_name in bpy.data.groups:
            group = bpy.data.groups[group_name]
        else:
            group = bpy.data.groups.new(group_name)
        group.objects.link(bpy.context.object)

        i = 1
        for lod_percentage in LODs:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            
            bpy.ops.object.duplicate(linked=False)
            
            bpy.context.object.name = bpy.context.object.name.split('.', 1)[0] + "_LOD" + str(i)

            bpy.context.scene.objects.active = bpy.context.object
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = lod_percentage / 100.0
            bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
            
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        
            i = i + 1
        obj.name = obj.name + "_LOD0"
    

class LODExportWidget(bpy.types.Operator):
    """Export the LODs"""
    bl_idname = "mesh.export_lods"
    bl_label = "Export LOD Meshes"
    
    def execute(self, context):
        self.export_lod_group(bpy.context.object)
        
        return {'FINISHED'}
    
    def export_lod_group(self, obj):
        for object in obj.users_group[0].objects:
            self.export_object_to_fbx(object)
    
    def export_object_to_fbx(self, obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        
        name = bpy.path.clean_name(obj.name)
        file = os.path.join(os.path.dirname(bpy.path.abspath(bpy.context.scene.filepath)), name)

        bpy.ops.export_scene.fbx(filepath=file + ".fbx",
            check_existing=False,
            version='BIN7400',
            use_selection=True,
            mesh_smooth_type='EDGE')

class BatchLODCreationWidget(bpy.types.Operator):
    """batch create LODs"""
    bl_idname = "mesh.batch_create_lods"
    bl_label = "Batch Create LOD Meshes"
    
    def execute(self, context):
        for subdir, dir, files in os.walk(os.path.join(os.path.dirname(bpy.path.abspath(bpy.context.scene.filepath_import)))):
            for file in files:
                self.create_lod_from_file(os.path.join(subdir, file), file[:-4])
                
        return {'FINISHED'}
    
    def create_lod_from_file(self, file_path, object_name):
        bpy.ops.import_scene.fbx(filepath=file_path)
        
        # needs to iterate over visible objects as file name does not have to be object name
        # scene has to be empty for this to work correctly
        for obj in bpy.context.visible_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            # use file naming instead of object
            obj.name = object_name

        LODCreationWidget.create_lod_meshes(self, bpy.context.object)
        for object in obj.users_group[0].objects:
            self.export_object_to_fbx(object)

        self.delete_group(bpy.context.object)
        
    def delete_group(self, obj):
        for obj in obj.users_group[0].objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            
            bpy.ops.object.delete()
            
    def export_object_to_fbx(self, obj):
        # quite redundant here
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        
        name = bpy.path.clean_name(obj.name)
        file = os.path.join(os.path.dirname(bpy.path.abspath(bpy.context.scene.filepath)), name)

        bpy.ops.export_scene.fbx(filepath=file + ".fbx",
            check_existing=False,
            version='BIN7400',
            use_selection=True,
            mesh_smooth_type='EDGE')
        

def register():
    bpy.utils.register_class(VIEW3D_PT_tools_LOD)
    bpy.utils.register_class(LODCreationWidget)
    bpy.utils.register_class(LODExportWidget)
    bpy.utils.register_class(BatchLODCreationWidget)
    
    bpy.types.Scene.filepath = bpy.props.StringProperty(name="Export LODs to", 
        description="Path to export the LODs to",
        subtype='DIR_PATH')
    bpy.types.Scene.filepath_import = bpy.props.StringProperty(name="Import meshes from", 
        description="Path to import the base meshes from",
        subtype='DIR_PATH')

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_tools_LOD)
    bpy.utils.unregister_class(LODCreationWidget)
    bpy.utils.unregister_class(LODExportWidget)
    bpy.utils.unregister_class(BatchLODCreationWidget)

if __name__ == "__main__":
    register()