# Blender Scripts

This is a collection of some of the scripts created to enhance my workflow in Blender.

## LODScripts.py

A script to create or batch create LOD meshes using the decimate modifier with set percentages as a base.

By adding/removing elements to/from the LODs list one can modify the number of LODs that are created.

The export button will automatically export the LOD groups (not in the .fbx sense of a LOD group; rather just the grouped LODs) in the scene to the Export directory using some default export settings that work fine with UE4. For Unity etc. or specific use cases one might have to change those.

If one adds an import directory and clicks the batch creation button the script will automatically import .fbx meshes from said directory (going through all the subdirectories as well), create LODs for them (based on the LODs list) and export those to the Export directory.