import threading
import subprocess
import queue
import time
import os

def _worker_thread_func(
        worker_id,
        project,
        source_file_queue,
        processed_file_queue,
        failed_file_queue,
        compiler_args
    ):
    while True: # Keep compiling until we can't anymore
        try:
            file_path = source_file_queue.get(block=False)

        except queue.Empty: # Stop working if we have no more files to compile
            return
        
        print(f"\tCompiling \"{file_path}\" (worker {worker_id})...")
        # Cache file so we might not have to rebuild:
        # We don't need to check if file_path is valid since we do that earlier

        file_name = os.path.basename(file_path)
        file_contents = open(file_path, "r").read()

        cache_file_path = os.path.join(project.project_dir, f"cache/{file_name}")
        if os.path.isfile(cache_file_path): # See if we need to recompile or not if we've cached it before
            cache_file_contents = open(cache_file_path, "r").read()
            if file_contents == cache_file_contents: # True if we skip this file since we do not need to recompile
                print(f"\t\"{file_path}\" has not changed, skipping it (worker {worker_id})")
                processed_file_queue.put(file_path) # Skip file and just say we processed it
                continue

        # Run g++:
        object_file_path = os.path.join(project.project_dir, f"cache/{os.path.splitext(file_name)[0]}.o")
        compilation_result = subprocess.run([project.compiler, "-c", file_path, "-o", object_file_path, *compiler_args], capture_output=True)

        if compilation_result.returncode == 0: # Only cache file if it compile successfully
            with open(cache_file_path, "w") as f:
                f.write(file_contents) # Cache contents of file

        else:
            print(f"\nCompilation of \"{file_name}\" failed (status code {compilation_result.returncode}):\n\n{compilation_result.stderr.decode()}")
            failed_file_queue.put(file_path) # It failed, sad :(
            
        processed_file_queue.put(object_file_path) # We have processed the file!!!

def build_project(project, executable_path, compiler_args, linker_args):
    build_started_time = time.time()
    print(f"Building project to executable path \"{executable_path}\" ({project.worker_count} worker(s)):")

    if len(project.source_files) == 0:
        print("No source files in the project, aborting build")
        return

    source_file_queue = queue.Queue()
    for project_file in project.source_files:
        if not os.path.isfile(project_file):
            print(f"\"{project_file}\" does not exist, aborting build")
            return

        source_file_queue.put(project_file)

    # Compilation stage:
    print(f"\n***** Compilation Stage *****")
    source_files_remaining = source_file_queue.qsize() # How many files we still need to compile / handle

    processed_file_queue = queue.Queue()
    failed_file_queue = queue.Queue()
    living_worker_threads = []
    for worker_id in range(project.worker_count): # Spawn workers
        worker_thread = threading.Thread(target=_worker_thread_func, args=(
            worker_id,
            project,
            source_file_queue,
            processed_file_queue,
            failed_file_queue,
            compiler_args,
        ), daemon=True)
        
        living_worker_threads.append(worker_thread) # Keep track of it
        worker_thread.start()

    compiled_files = []
    while True: # Figure out when we finish compilation and if it was successful or not 
        compiled_file = processed_file_queue.get()
        compiled_files.append(compiled_file)

        source_files_remaining -= 1
        if source_files_remaining <= 0: # True if we're finished with compilation
            compilation_fails = failed_file_queue.qsize()
            if compilation_fails == 0:
                print(f"\tCompilation stage successful!")
                break

            else:
                print(f"\n\tFailed to compile {compilation_fails} file(s)\n\nBuild failed.\n")
                return

    # Linking stage:
    print("\n***** Linking Stage *****")

    print(f"\tLinking {len(compiled_files)} object file(s)...")
    linking_result = subprocess.run([project.compiler, *compiled_files, "-o", executable_path, *linker_args], capture_output=True)
    if linking_result.returncode == 0: # True if we have successfully linked!
        build_elapsed_time = round(time.time() - build_started_time, 3)
        print(f"\tLinking stage successful (build took {build_elapsed_time}s)!\n")

    else:
        print(f"\nLinking stage failed (status code {linking_result.returncode}):\n\n{linking_result.stderr.decode()}\nBuild failed.\n")