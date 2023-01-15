from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
import os
import sys
import json
import textwrap

def _args_to_string(args):
    if not args:
        return ""
    if sys.platform == 'win32':
        return subprocess.list2cmdline(args)
    else:
        return " ".join("'" + arg.replace("'", r"'\''") + "'" for arg in args)

class PythonVirtualEnvironment(ConanFile):
    name = "python-virtualenv"
    version = "system"
    description = "Install python packages into a virtual environment"
    url = "https://github.com/samuel-emrys/python-virtualenv.git"
    homepage = "https://github.com/samuel-emrys/python-virtualenv.git"
    license = "MIT"
    topics = ("python", "virtual environment", "venv")

    settings = "os_build", "arch_build", "os"
    options = {"requirements": "ANY"}
    default_options = {"requirements": "[]"}

    python_requires = "pyvenv/0.1.0@mtolympus/stable"
    # python venvs are not relocatable, so we will not have binaries for this on artifactory. Just build it on first use
    build_policy = "missing"
    _venv = None

    def validate(self):
        try:
            json.loads(str(self.options.requirements))
        except Exception as e:
            raise ConanInvalidConfiguration(
                "Failed to parse requirements. Ensure requirements are passed as valid JSON."
            )

    def _configure_venv(self):
        venv = self.python_requires["pyvenv"].module.PythonVirtualEnv
        if not self._venv:
            self._venv = venv(self)
        return self._venv

    def package(self):
        # Create the virtualenv in the package method because virtualenv's are not relocatable.
        venv = self._configure_venv()
        venv.create(folder=os.path.join(self.package_folder))

        requirements = json.loads(str(self.options.get_safe("requirements", "[]")))
        if requirements:
            self.run(
                _args_to_string(
                    [
                        venv.pip,
                        "install",
                        *(requirement for requirement in requirements),
                    ]
                )
            )

        bindir = "Scripts" if self.settings.os_build == "Windows" else "bin"
        for requirement in requirements:
            package = requirement.split("==")[0]
            # Ensure that there's an entry point for everything we've just installed.
            venv.setup_entry_points(
                str(package), os.path.join(self.package_folder, bindir)
            )

    def package_info(self):
        self.conf_info.define("user.env.pythonenv:requirements", str(self.options.get_safe("requirements", "[]")))
        self.conf_info.define("user.env.pythonenv:dir", self.package_folder)
