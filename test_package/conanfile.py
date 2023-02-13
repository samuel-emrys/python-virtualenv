import os
import json

from conan import ConanFile
from conan.tools.build import cross_building


class PythonVirtualenvTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    apply_env = False
    test_type = "explicit"

    def configure(self):
        self.options["python-virtualenv"].requirements = json.dumps([
            "sphinx",
            "sphinx-rtd-theme",
        ])

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            path = "$PATH"
            if self.settings.os == "Windows":
                path = "%PATH%"
            self.output.info(f"Executing `echo {path}` with env=\"conanrun\"")
            self.run(f"echo {path}", env="conanrun")
            self.output.info(f"Executing `echo {path}` with env=\"conanbuild\"")
            self.run(f"echo {path}", env="conanbuild")
            # This should exist on the path in the build environment
            requirements = self.conf.get("user.env.pythonenv:requirements")
            env_dir = self.conf.get("user.env.pythonenv:dir")
            self.output.info(f"user.env.pythonenv:dir={env_dir}")
            self.output.info(f"user.env.pythonenv:requirements={requirements}")
            self.output.info("Executing `python --version`")
            self.run("python --version", env="conanbuild")
            self.output.info("Executing `sphinx-build --help`")
            self.run("sphinx-build --help", env="conanbuild")
