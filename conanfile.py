from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy
import os
import sys
import json
import textwrap

class PythonVirtualEnvironment(ConanFile):
    name = "python-virtualenv"
    version = "system"
    description = "Install python packages into a virtual environment"
    url = "https://github.com/samuel-emrys/python-virtualenv.git"
    homepage = "https://github.com/samuel-emrys/python-virtualenv.git"
    license = "MIT"
    topics = ("python", "virtual environment", "venv")

    settings = "arch", "os"
    options = {"requirements": ["ANY"]}
    default_options = {"requirements": "[]"}

    python_requires = "pyvenv/[>=0.2.2]@mtolympus/stable"
    # python venvs are not relocatable across environments, so we will not have binaries for this on artifactory.
    # Just build it on first use
    build_policy = "missing"
    upload_policy = "skip"
    _venv = None

    def validate(self):
        try:
            json.loads(str(self.options.requirements))
        except Exception as e:
            raise ConanInvalidConfiguration(
                f"Failed to parse requirements '{self.options.requirements}'. Ensure requirements are passed as valid JSON."
            )

    @property
    def _bindir(self):
        return "Scripts" if self.settings.os == "Windows" else "bin"

    def _configure_venv(self):
        venv = self.python_requires["pyvenv"].module.PythonVirtualEnv
        if not self._venv:
            self._venv = venv(self)
        return self._venv

    def build(self):
        args_to_string = self.python_requires["pyvenv"].module.args_to_string
        requirements = json.loads(str(self.options.get_safe("requirements", "[]")))
        venv = self._configure_venv()
        venv.create(folder=os.path.join(self.package_folder), requirements=requirements)

    def package(self):
        copy(self, "*", src=self.build_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = [self._bindir]
        self.conf_info.define("user.env.pythonenv:requirements", str(self.options.get_safe("requirements", "[]")))
        self.conf_info.define("user.env.pythonenv:dir", self.package_folder)
