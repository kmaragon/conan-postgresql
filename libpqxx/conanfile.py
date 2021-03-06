from conans import ConanFile, tools
import os
import sys
import re

class LibpqxxConan(ConanFile):
    name = "libpqxx"
    version = "6.4.5"
    license = "BSD"
    url = "https://github.com/kmaragon/conan-postgresql"
    description = "Conan packages for pqxx"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "virtualbuildenv", "virtualrunenv"
    requires = "postgresql/12.0@kmaragon/stable"
    #exports = "sed_command_fix.patch"

    def source(self):
        tools.download("https://github.com/jtv/libpqxx/archive/%s.tar.gz" % self.version, "libpqxx.tar.gz")
        tools.unzip("libpqxx.tar.gz")
        os.unlink("libpqxx.tar.gz")

        tools.replace_in_file('libpqxx-{}/tools/template2mak.py'.format(self.version), '#! /usr/bin/env python', '#! /usr/bin/env {}'.format(sys.executable))
        tools.replace_in_file('libpqxx-{}/tools/splitconfig'.format(self.version), '#! /usr/bin/env python', '#! /usr/bin/env {}'.format(sys.executable))

        #self.run("patch -p0 < sed_command_fix.patch")
        self.run("cd libpqxx-%s/ && autoconf" % self.version)

    def build(self):
        flags = "--disable-documentation"
        if self.options.shared:
            flags += " --enable-shared --disable-static"
        else:
            flags += " --disable-shared --enable-static"

        make_options = os.getenv("MAKEOPTS") or ""
        if not re.match("/[^A-z-a-z_-]-j", make_options):
            cpucount = tools.cpu_count()
            make_options += " -j %s" % cpucount
        
        # configure
        self.run(". ./activate_build.* && cd libpqxx-%s && ./configure --prefix=%s %s" % (self.version, self.package_folder, flags), run_environment=True)

        # build
        self.run(". ./activate_build.* && cd libpqxx-%s && make %s" % (self.version, make_options), run_environment=True)

    def package(self):
        self.run("cd libpqxx-%s && make install" % self.version)

    def package_info(self):
        self.cpp_info.libs = ["pqxx"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
