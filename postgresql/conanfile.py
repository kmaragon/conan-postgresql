from conans import ConanFile, tools
import os
import re

class PostgresqlConan(ConanFile):
    name = "postgresql"
    version = "11.1"
    license = "BSD"
    url = "https://github.com/kmaragon/conan-postgresql"
    description = "Conan packages for postgresql"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "disable_thread_safe": [True, False],
        "disable_largefile": [True, False],
        "disable_zlib": [True, False],
        "icu": [True, False],
        "openssl": [True, False]
    }
    default_options = "shared=False", "disable_thread_safe=False", "disable_largefile=False", "disable_zlib=False", "icu=False", "openssl=True"
    generators = "virtualbuildenv"

    def configure(self):
        if self.options.icu:
            self.requires("icu:60.1@sigmoidal/60.1")
        if self.options.openssl:
            self.requires("OpenSSL/1.0.2q@conan/stable")
        if not self.options.disable_zlib:
            self.requires("zlib/1.2.11@conan/stable")

    def source(self):
        tools.download("https://ftp.postgresql.org/pub/source/v{0}/postgresql-{0}.tar.bz2".format(self.version),
            "postgresql.tar.bz2")
        tools.unzip("postgresql.tar.bz2")
        os.unlink("postgresql.tar.bz2")

    def build(self):
        flags="--without-readline"
        if self.options.disable_thread_safe:
            flags += " --disable-thread-safety"
        if self.options.disable_largefile:
            flags += " --disable-largefile"
        if self.options.disable_zlib:
            flags += " --without-zlib"
        if self.options.icu:
            flags += " --with-icu"
        if self.options.openssl:
            flags += " --with-openssl"

        make_options = os.getenv("MAKEOPTS") or ""
        if not re.match("/[^A-z-a-z_-]-j", make_options):
            cpucount = tools.cpu_count()
            make_options += " -j %s" % cpucount

        # configure
        cdir = os.getcwd()
        image_location = os.path.join(cdir, "buildimg")
        self.run(". ./activate_build.* && cd postgresql-%s && ./configure --prefix=%s %s" % (self.version, image_location, flags))

        # build
        self.run(". ./activate_build.* && cd postgresql-%s && make %s" % (self.version, make_options))

    def package(self):
        self.run("cd postgresql-%s && make install" % self.version)
        if self.options.shared:
            if self.settings.os == "Windows":
                self.copy("*.lib", dst="lib", src="buildimg/lib")
                self.copy("*.dll", dst="lib", src="buildimg/lib")
            elif self.settings.os == "Macos":
                self.copy("*.dylib*", dst="lib", src="buildimg/lib")
            else:
                self.copy("*.so*", dst="lib", src="buildimg/lib")
        else:
            if self.settings.os == "Windows":
                self.copy("*.lib", dst="lib", src="buildimg/lib")
            else:
                self.copy("*.a", dst="lib", src="buildimg/lib")

        self.copy("*", dst="include", src="buildimg/include")
        self.copy("*", dst="bin", src="buildimg/bin")

    def package_info(self):
        self.cpp_info.libs = ["pq"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
