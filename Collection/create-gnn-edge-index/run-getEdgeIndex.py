'''
Aug 20, 2024
This is for automating the creation of the Edge Index from STL files
'''

import bpy
import os
import sys

## ------------ MAIN ------------ ##
## Declare all the needed information

file_loc = os.path.abspath(__file__) # location of this running file (i.e., run-getEdgeIndex)

## directory of the blender-getEdgeIndex-api
scripts_directory = file_loc[:file_loc.rfind('/')] + '/'

## location of the stl files (one folder for a one whole example)
stlfiles_directory = file_loc[:file_loc.rfind('/')] + '/stl_files/cad_example/'

## where the results will be placed (if None, the folder of the stl will be used)
results_directory = None

## ------------ END ------------ ##


## temporarily import files from directory
class add_path():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass

with add_path(scripts_directory): #+'utils/'): 
    module = __import__('blender-getEdgeIndex-api')
    ## load all the functions inside the module
    import_stl_files = getattr(module, 'import_stl_files')
    getEdgeIndex = getattr(module, 'getEdgeIndex')


## ---------------- RUN!!!! ---------------- ##

## delete objects in the scene
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

## import stl files
import_stl_files(stlfiles_directory)

## get the edge index    
results_directory = stlfiles_directory if results_directory == None else results_directory

getEdgeIndex(save_name='result_edgeindex', save_location=results_directory)


print('Finished processing all files!')