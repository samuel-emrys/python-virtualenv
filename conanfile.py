from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import json
import textwrap


class PythonVirtualEnvironment(ConanFile):
    name = "python-virtualenv"
    version = "system"
    description = "Sphinx is used to generate the help documentation"
    settings = "os_build", "arch_build", "os"
    options = {"requirements": "ANY"}
    default_options = {"requirements": "[]"}

    build_requires = ["pyvenv/0.3.1"]
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
        from pyvenv import venv
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
                tools.args_to_string(
                    [
                        venv.pip,
                        "install",
                        *(requirement for requirement in requirements),
                    ]
                )
            )

        package_targets = {}
        for requirement in requirements:
            package = requirement.split("==")[0]
            # Ensure that there's an entry point for everything we've just installed.
            venv.setup_entry_points(
                str(package), os.path.join(self.package_folder, "bin")
            )
            entry_points = venv.entry_points(package)
            package_targets[package] = entry_points.get("console_scripts", [])

    def package_info(self):
        self.user_info.python_requirements = self.options.get_safe("requirements", "[]")
        self.user_info.python_envdir = self.package_folder
