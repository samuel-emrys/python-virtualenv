# python-virtualenv

A conan recipe to build a python virtual environment. This should be used in conjunction with the [CMakePythonEnvironment](https://github.com/samuel-emrys/CMakePythonEnvironment) generator.

## Usage

Below are two minimal examples of how to use this package. This essentially requires the consumer to specify this package as a requirement, and then to customise the environment by providing a JSON list of requirements to be installed into the python virtual environment.

The first, below, demonstrates how to specify these requirements directly in the consumer `conanfile.py`:

```python
class VirtualenvConsumerConan(ConanFile):
    name = "venv-consumer"
    version = "0.1.0"

    generators = "CMakePythonEnvironment"
    def requirements(self):
        self.requires("python-virtualenv/system")
        # Specify the requirements directly within the consumer conanfile.py
        self.options["python-virtualenv"].requirements = json.dumps([
            "sphinx==5.0.1",
            "sphinx-book-theme==0.3.2",
        ])
```

The second, below, demonstrates how to read these requirements in from a `requirements.txt` that lives within the project root. Note that in this example, the `requirements.txt` file needs to be included in the `exports_sources` field in order to be read.

```python
class VirtualenvConsumerConan(ConanFile):
    name = "venv-consumer"
    version = "0.1.0"
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "requirements.txt"
    generators = "CMakePythonEnvironment"

    def requirements(self):
        self.requires("python-virtualenv/system")
        # Read the requirements from a requirements.txt within the project root
        with pathlib.Path("requirements.txt").open() as requirements_txt:
            self.options["python-virtualenv"].requirements = json.dumps([
                str(requirement) for requirement in pkg_resources.parse_requirements(requirements_txt)
            ])
```

Both of these examples utilise the [CMakePythonEnvironment](https://github.com/samuel-emrys/CMakePythonEnvironment) generator to generate CMake targets for the executables installed into this virtual environment.

A working exemplar recipe can be found in [`sphinx-consumer`](https://github.com/samuel-emrys/sphinx-consumer).

