import os
import sys
import importlib


class Manager:
    """
    Dynamic Module Manger to handle all modules loaded in dynamically
    """
    def __init__(self, abs_module_path):
        sys.path.insert(0, abs_module_path)

        # Holds absolute file path to module folder
        self.module_dir_path = abs_module_path

        # Dictionary where keys are module names relative to absModulePath
        # and values are module import references
        self.module_list = {}

        self.__load_modules_from_path(self.module_dir_path)

        # Invalidate Python's caches so the new modules can be found
        importlib.invalidate_caches()

    def __load_modules_from_path(self, module_root_path):
        # Load in modules dynamically from path
        for dir_path, _, files in os.walk(module_root_path):
            # Import all python files
            for file in files:
                if file.endswith(".py"):
                    # Create a python module import path relative to the absModulePath
                    import_path = os.path.join(
                        dir_path.replace(module_root_path, "")[1:],
                        os.path.splitext(file)[0]
                    ).replace("/", ".")

                    cur_module = self.module_list.get(import_path)

                    # Import the python module and keep a reference to it
                    # if it is not already imported by us
                    if not cur_module:
                        self.add_module(import_path)
                    # If found module but the modified time changed then reload it
                    elif cur_module and cur_module["mtime"] != os.path.getmtime(self.get_os_path(import_path)):
                        self.reload_module(import_path)

    @staticmethod
    def get_os_path(module_root_path, module_path):
        # Convert dot-notation back to path-notation
        module_path = module_path.replace(".", "/")

        # Add extension back to path
        module_path += ".py"

        # Join from the absolute path to the module path
        return os.path.join(module_root_path, module_path)

    @staticmethod
    def get_module_path(module_root_path, os_path):
        # Remove the base path since that is not included in the module_path
        os_path = os_path.replace(module_root_path, "")

        # If absolute path truncate root
        if os_path[0] == "/":
            os_path = os_path[1:]

        # Swap to dot notation
        os_path = os_path.replace("/", ".")

        return os.path.splitext(os_path)[0]

    def get_modules(self):
        return self.module_list

    def add_module(self, module_path):
        # Get the module class from the module file name
        module_class_name = module_path
        # If it is in sub directories then just get the module's name
        if module_path.count("."):
            module_class_name = module_path.split(".")[-1]


        # Get's the module's class to call functions on
        module = importlib.import_module(module_path)
        module_class = getattr(module, module_class_name.capitalize())

        # Create's an instance of that module's class
        module_instance = module_class()

        self.module_list[module_path] = {
            "ref": module,
            "instance": module_instance,
            "mtime": os.path.getmtime(os.path.join(self.get_os_path(self.module_dir_path, module_path)))
        }

        # Initialize Module
        module_instance.init()

    def remove_module(self, module_path):
        # Get our module reference
        module = self.module_list[module_path]["ref"]

        # Shutdown any work on that module
        module.shutdown()

        # Remove references to module
        del module
        del self.module_list[module_path]

    def reload_modules(self):
        # Reload all modules in our list
        for module in self.module_list.values():
            importlib.reload(module["ref"])

        # Invalidate any caches
        importlib.invalidate_caches()

    def reload_module(self, module_path):
        # Reload module
        importlib.reload(module_path)

        # Update new module time
        self.module_list[module_path]["mtime"] = os.path.getmtime(self.get_os_path(self.module_dir_path, module_path))

        # Invalidate Cache
        importlib.invalidate_caches()

    def shutdown(self):
        for module in self.module_list.values():
            module["instance"].shutdown()


def Init(modules_dir_path):
    """
    Create a new instance of the Dynamic Module Loader Manager
    :param modules_dir_path: Path where dynamic modules should be loaded from, absolute or relative
    :return: new instance of Manager class
    """
    # Get absolute path to reference
    abs_mod_dir_path = os.path.abspath(modules_dir_path)

    # Check if the directory exists
    if not os.path.exists(modules_dir_path) or not os.path.exists(abs_mod_dir_path):
        print("Error: cannot find module path '{}'".format(abs_mod_dir_path))
        return None

    # Check to see if path is a directory
    if not os.path.isdir(abs_mod_dir_path):
        print("Error: provided path is not a directory")
        return None

    return Manager(abs_mod_dir_path)


if __name__ == "__main__":
    manager = Init("/Users/kainoa/Workspace/code/python/DynamicModules/modules")
    manager.shutdown()
