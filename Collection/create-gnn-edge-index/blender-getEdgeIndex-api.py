import bpy
import os
import sys

'''------------------------ IMPORT STL FILES ------------------------'''

def init_stl():
    ## set ORIGIN TO GEOMETRY to recover object positions that was not transported by STL
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Iterate through all objects in the scene
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Select the object
            obj.select_set(True)
            
            # Set the object as the active object
            bpy.context.view_layer.objects.active = obj
            
            # Set origin to geometry
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            
            # Deselect the object
            obj.select_set(False)



## imports STL Files

def import_stl_files(path, init=True, verbose=False):
    objects = os.listdir(path)

    for obj in objects:
        if obj.lower().endswith(".stl"):
            bpy.ops.wm.stl_import(filepath=path + obj)


    if init:
        init_stl()
    if verbose:
        print('Done Importing Files')

'''------------------------ CREATE EDGE INDEX ------------------------'''

import pickle
import numpy as np
import bmesh


def extend_object(obj, revert=False, addnum=[1,1]):
    
    dim_list = np.array(bpy.context.scene.objects[obj].dimensions).round(2)
    max_idx = np.max(dim_list)
    indices = np.where(max_idx == dim_list)[0]
    
    if revert: 
        bpy.context.scene.objects[obj].scale.xyz = 1
    
    else:
        
        for i in indices:    
            if i == 0:
                dim_list[0] += addnum[0]
                dim_list[1] -= addnum[1]
                dim_list[2] -= addnum[1]
    
            elif i == 1:
                dim_list[0] -= addnum[1]
                dim_list[1] += addnum[0]
                dim_list[2] -= addnum[1]
            
            elif i == 2:
                dim_list[0] -= addnum[1]
                dim_list[1] -= addnum[1]
                dim_list[2] += addnum[0]
    
        bpy.context.scene.objects[obj].dimensions.xyz = dim_list
    bpy.context.view_layer.update()   

    
def advancedCollisionCheck(obj1, obj2):

    obj1 = bpy.context.scene.objects[obj1]
    obj2 = bpy.context.scene.objects[obj2]
    
    # Create a copy of the first object
    obj1_copy = obj1.copy()
    obj1_copy.data = obj1.data.copy()
    bpy.context.collection.objects.link(obj1_copy)
    
    # Create a new boolean modifier for the copy
    bool_mod = obj1_copy.modifiers.new(name="IntersectCheck", type='BOOLEAN')
    bool_mod.object = obj2
    bool_mod.operation = 'INTERSECT'
    
    # Apply the modifier
    bpy.context.view_layer.objects.active = obj1_copy
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    
    # Check if the resulting mesh is empty
    bm = bmesh.new()
    bm.from_mesh(obj1_copy.data)
    touching = len(bm.verts) > 0
    bm.free()
    
    # Remove the copied object
    bpy.data.objects.remove(obj1_copy, do_unlink=True)
    
    return touching
 

def collect_objects():
    ## Create a list of the objects
    ## Iterate through the objects and print their names
    object_list = []
    for obj in bpy.context.scene.objects:
        #if 'Light' not in obj.name and 'Camera' not in obj.name:
        object_list.append(obj.name)

    return object_list



def testIndCollision(obj1, obj2):

    # MAIN
    extend_object(obj1, addnum=[1,1])
    bpy.context.view_layer.update()
    collision = advancedCollisionCheck(obj1, obj2)
    extend_object(obj1, revert=True)
    print(collision)



def getEdgeIndex(initStl=False, save_name=None, save_location=None, verbose=False):
    ## get object list
    object_list = collect_objects()

    if initStl:
        init_stl()

    ## check if two objects are touching for all objects
    decreasing_list = object_list
    reference_list = object_list


    edge_index = []
    for ob1 in reference_list:
        for ob2 in decreasing_list:
            if ob1 != ob2:
                ## addnum [x, y] x-extend, y-contract
                extend_object(ob1, addnum=[1,0])
                result = advancedCollisionCheck(ob1, ob2)
                extend_object(ob1, revert=True)
                if result and [ob2, ob1] not in edge_index:
                    edge_index.append([ob1, ob2])
    
    if verbose:
        print(edge_index)
    

    if save_name != None:
        
        addr = 'blenderscripts/edge_index' if save_location == None else save_location

        if not os.path.exists(addr):
            os.makedirs(addr)

        with open(addr + '/' + save_name + '.csv', mode='w') as f:
            for i in edge_index:
                f.write(i[0] + ',' + i[1] + '\n')

    if verbose:
        print('Done Creating Edge Index')