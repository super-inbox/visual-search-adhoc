import pickle, io
ALLOWED = {("numpy.core.multiarray", "_reconstruct"), ("numpy._core.multiarray", "_reconstruct"),
           ("numpy", "ndarray"), ("numpy", "dtype"), ("numpy.core.multiarray", "scalar"),
           ("numpy._core.multiarray", "scalar"), ("builtins", "list"), ("builtins", "dict"), ("builtins", "tuple")}
class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED: return super().find_class(module, name)
        raise pickle.UnpicklingError(f"blocked {module}.{name}")
def load(path):
    with open(path, 'rb') as f: return SafeUnpickler(f).load()
