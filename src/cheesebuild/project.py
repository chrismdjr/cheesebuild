from . import compilers
from . import _builder

import os

class Project:
    """A cheesebuild project. Can be turned into a binary with the `build()` method."""
    def __init__(
            self,
            compiler: str="gcc",
            dir: str="cheesebuild",
            files: list[str]=[],
            worker_count: int=5,
            auto_initialize=True,
        ):
        self._project_dir = dir

        self.compiler = compiler
        self.source_files = files
        self.worker_count = worker_count

        # Init stuff:
        if not compilers.is_supported_compiler(self.compiler): # True if the user said something that is_supported_compiler() didn't like
            print(f"Compiler \"{self.compiler}\" is not currently supported by cheesebuild. Any attempts at building will fail.")
            return

        print(f"Searching for cheese project at \"{self._project_dir}\"...")

        if self.is_initialized:
            print(f"Found project, ready for building")

        else:
            print(f"Project was not found, auto_initialize={auto_initialize}...")
            if auto_initialize: # Only init it automatically if explicitly said
                self.initialize()

        # Project is ready if we get past here

    @property
    def project_dir(self) -> str:
        return self._project_dir
    
    @property
    def is_initialized(self) -> bool: # Returns if the project is already initialized or not
        return os.path.isdir(self._project_dir)
    
    def initialize(self) -> None: # Set up a project in the project directory
        """Creates necessary files and folders for the cheesebuild project to live in the filesystem."""
        print("Initializing project...")
        os.makedirs(os.path.join(self._project_dir, "cache"), exist_ok=True) # Make our project cache folder

    def build(self, executable_path: str, compiler_args: list[str]=[], linker_args: list[str]=[]) -> None: # Build a project to an executable
        """Builds the cheesebuild project to a binary using the `g++` command."""
        # Run a quick check to make sure they are using a supported compiler:
        if not compilers.is_supported_compiler(self.compiler):
            print(f"Compiler \"{self.compiler}\" is not currently supported by cheesebuild, aborting build")
            return

        # Validate build args:
        valid_type = True
        for arg in compiler_args:
            if type(arg) != str:
                valid_type = False

        if type(compiler_args) != list or type(linker_args) != list:
            valid_type = False

        if not valid_type: # subprocess.run will only work if the args are valid
            raise TypeError("Compiler / linker args must be a list of strings.")

        _builder.build_project(self, executable_path, compiler_args, linker_args)

    def clear_cache(self) -> None:
        """Clears the source file cache stored in the cheesebuild project's `cache/` directory.

Call this if your cache is taking up too much space or contains too many garbage files."""
        cache_path = os.path.join(self._project_dir, "cache")
        cached_source_files = os.listdir(cache_path)
        
        print(f"Clearing project cache ({len(cached_source_files)} files)...")
        for cached_source_file in cached_source_files: # Iterate over all cache files and KILL THEM!
            os.remove(os.path.join(cache_path, cached_source_file))

        print("Cache is now empty!")