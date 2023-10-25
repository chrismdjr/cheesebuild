from ._builder import *

import os

class Project:
    def __init__(
            self,
            dir: str="cheese",
            files: list[str]=[],
            worker_count: int=5,
            auto_initialize=True
        ):
        self._project_dir = dir

        self.source_files = files
        self.worker_count = worker_count

        # Init stuff:
        print(f"Searching for cheese project at \"{self._project_dir}\"...")

        if self.is_initialized:
            print(f"Found project, ready for building")

        else:
            print(f"Project was not found, auto_initialize={auto_initialize}...")
            if auto_initialize: # Only init it automatically if explicitly said
                self.initialize()

        # Project is initialized past here

    @property
    def project_dir(self):
        return self._project_dir
    
    @property
    def is_initialized(self): # Returns if the project is already initialized or not
        return os.path.isdir(self._project_dir)
    
    def initialize(self): # Set up a project in the project directory
        print("Initializing project...")
        os.makedirs(os.path.join(self._project_dir, "cache"), exist_ok=True) # Make our project cache folder
        os.makedirs(os.path.join(self._project_dir, "objects"), exist_ok=True) # Make our object file foleer

    def build(self, executable_path: str, compiler_args: list[str]=[], linker_args: list[str]=[]): # Build a project to an executable
        # Validate build args:
        valid_type = True
        for arg in compiler_args:
            if type(arg) != str:
                valid_type = False

        if type(compiler_args) != list or type(linker_args) != list:
            valid_type = False

        if not valid_type: # subprocess.run will only work if the args are valid
            raise TypeError("Compiler / linker args must be a list of strings.")

        build_project(self, executable_path, compiler_args, linker_args)