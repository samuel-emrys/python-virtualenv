# python-virtualenv

A conan recipe to build a python virtual environment. This should be used in conjunction with the [CMakePythonDeps](https://github.com/samuel-emrys/cmake-python-deps) generator.

## Usage

First, add the `mtolympus` remote to your conan configuration

```
$ conan remote add mtolympus-conan https://mtolympus.jfrog.io/artifactory/api/conan/mtolympus-conan
```

Below are two minimal examples of how to use this package. This essentially requires the consumer to specify this package as a requirement, and then to customise the environment by providing a JSON list of requirements to be installed into the python virtual environment.

The first, below, demonstrates how to specify these requirements directly in the consumer `conanfile.py`:

```python
class VirtualenvConsumerConan(ConanFile):
    name = "venv-consumer"
    version = "0.1.0"
    python_requires = "cmake-python-deps/[>=0.3.0]@mtolympus/stable"

    def requirements(self):
        self.requires("python-virtualenv/system@mtolympus/stable")
        # Specify the requirements directly within the consumer conanfile.py
        self.options["python-virtualenv"].requirements = json.dumps([
            "sphinx==5.0.1",
            "sphinx-book-theme==0.3.2",
        ])

    def generate(self):
        py = self.python_requires["cmake-python-deps"].module.CMakePythonDeps(self)
        py.generate()
```

The second, below, demonstrates how to read these requirements in from a `requirements.txt` that lives within the project root. Note that in this example, the `requirements.txt` file needs to be included in the `exports_sources` field in order to be read.

```python
class VirtualenvConsumerConan(ConanFile):
    name = "venv-consumer"
    version = "0.1.0"
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "requirements.txt"
    python_requires = "cmake-python-deps/[>=0.3.0]@mtolympus/stable"

    def requirements(self):
        self.requires("python-virtualenv/system@mtolympus/stable")
        # Read the requirements from a requirements.txt within the project root
        with pathlib.Path("requirements.txt").open() as requirements_txt:
            self.options["python-virtualenv"].requirements = json.dumps([
                str(requirement) for requirement in pkg_resources.parse_requirements(requirements_txt)
            ])

    def generate(self):
        py = self.python_requires["cmake-python-deps"].module.CMakePythonDeps(self)
        py.generate()
```

Both of these examples utilise the [CMakePythonDeps](https://github.com/samuel-emrys/pyvenv) generator, which is shipped with the [pyvenv](https://github.com/samuel-emrys/pyvenv) python_requires package. This will generate CMake targets for the executables installed into this virtual environment.

A working exemplar recipe can be found in [`sphinx-consumer`](https://github.com/samuel-emrys/sphinx-consumer).

