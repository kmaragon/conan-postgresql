from conans import ConanFile, tools
import os
import re

class LibpqxxConan(ConanFile):
    name = "libpqxx"
    version = "5.0.1"
    license = "BSD"
    url = "https://github.com/kmaragon/conan-postgresql"
    description = "Conan packages for pqxx"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "virtualbuildenv", "virtualrunenv"
    requires = "postgresql/10.1@kmaragon/stable"

    def source(self):
        tools.download("https://github.com/jtv/libpqxx/archive/%s.tar.gz" % self.version, "libpqxx.tar.gz")
        tools.unzip("libpqxx.tar.gz")
        os.unlink("libpqxx.tar.gz")

    def build(self):
        flags = ""
        if self.options.shared:
            flags += " --enable-shared --disable-static"
        else:
            flags += " --disable-shared --enable-static"

        make_options = os.getenv("MAKEOPTS") or ""
        if not re.match("/[^A-z-a-z_-]-j", make_options):
            cpucount = tools.cpu_count()
            make_options += " -j %s" % cpucount
        
        # configure
        self.run("source activate_build.* && source activate_run.* && cd libpqxx-%s && ./configure --prefix=%s %s" % (self.version, self.package_folder, flags))

        # build
        self.run("source activate_build.* && cd libpqxx-%s && make %s" % (self.version, make_options))

    def package(self):
        self.run("cd libpqxx-%s && make install" % self.version)

    def package_info(self):
        self.cpp_info.libs = ["pqxx"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
