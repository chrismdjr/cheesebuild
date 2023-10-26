# Contains all compilers currently supported by cheesebuild.
# Keys represent compiler names (lowercased) and values represent the commands to invoke them
_SUPPORTED_COMPILERS = {
    "gcc": "gcc",
    "g++": "g++",
}

def is_supported_compiler(compiler: str) -> bool:
    """Returns `True` if the compiler specified is one currently supported by cheesebuild, and `False` if not."""
    return compiler.lower() in _SUPPORTED_COMPILERS