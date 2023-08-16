import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version


class ConanUStore(ConanFile):

    exports = 'VERSION', 'LICENSE', 'README.md'
    exports_sources = 'CMakeLists.txt', 'src/*', 'include/*', 'cmake/*', 'VERSION'
    name = 'ustore_deps'
    version = open('VERSION').read()
    # Take just the first line
    license = open('LICENSE').read().split('\n', 1)[0]
    description = open('README.md').read()
    url = 'https://github.com/unum-cloud/ustore.git'
    homepage = 'https://unum.cloud/ustore'

    # Complete list of possible settings:
    # https://docs.conan.io/en/latest/extending/custom_settings.html
    settings = {
        # https://docs.conan.io/en/latest/introduction.html#all-platforms-all-build-systems-and-compilers
        'os': ['Linux'],
        # https://docs.conan.io/en/latest/integrations/compilers.html
        'compiler': [
            'gcc', 'clang', 'intel',
            # Not fully supported yet:
            # 'intel-cc'
        ],
        # https://github.com/conan-io/conan/issues/2500
        'build_type': ['Release'],
        'arch': ['x86', 'x86_64', 'armv8', 'armv8_32', 'armv8.3'],
    }
    generators = 'CMakeDeps', 'deploy'
    options = {'with_arrow': [True, False]}
    default_options = {
        'with_arrow': False,
    }


    def layout(self):
        cmake_layout(self)


    def generate(self):
        tc = CMakeToolchain(self)
        if cross_building(self):
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            if cmake_system_processor == "aarch64":
                tc.variables["ARROW_CPU_FLAG"] = "armv8"
        tc.variables["ARROW_DEPENDENCY_SOURCE"] = "AUTO"
        tc.variables['ARROW_BUILD_STATIC'] = True
        tc.variables['ARROW_BUILD_SHARED'] = False
        tc.variables['ARROW_SIMD_LEVEL'] = "AVX2"
        tc.variables["ARROW_DEPENDENCY_USE_SHARED"] = False
        tc.variables["ARROW_BUNDLED_STATIC_LIBS"] = True
        tc.variables["ARROW_OPENSSL_USE_SHARED"] = False
        tc.variables["ARROW_BUILD_TESTS"] = False
        tc.variables["ARROW_ENABLE_TIMING_TESTS"] = False
        tc.variables["ARROW_BUILD_EXAMPLES"] = False
        tc.variables["ARROW_BUILD_BENCHMARKS"] = False
        tc.variables["ARROW_BUILD_INTEGRATION"] = False
        tc.variables["ARROW_EXTRA_ERROR_CONTEXT"] = False
        tc.variables['ARROW_DATASET'] = True
        tc.variables['ARROW_PARQUET'] = True
        tc.variables['ARROW_WITH_RE2'] = True
        tc.variables['ARROW_COMPUTE'] = True
        tc.variables['ARROW_FLIGHT'] = True
        tc.variables['ARROW_WITH_UTF8PROC'] = True
        tc.variables["PARQUET_REQUIRE_ENCRYPTION"] = bool(
            self.options['arrow:encryption'])  # False
        tc.variables["ARROW_CUDA"] = False
        tc.variables["ARROW_JEMALLOC"] = False
        tc.variables["ARROW_IPC"] = False
        tc.variables["ARROW_JSON"] = False
        tc.variables["ARROW_CSV"] = True
        tc.variables["ARROW_FLIGHT_SQL"] = False
        tc.variables["ARROW_WITH_UCX"] = False
        tc.variables["ARROW_WITH_SNAPPY"] = True
        tc.variables["ARROW_BUILD_UTILITIES"] = bool(
            self.options['arrow:cli'])  # False
        tc.variables["ARROW_GANDIVA"] = False
        tc.variables["ARROW_S3"] = False
        tc.variables["ABS_VENDORED"] = True
        tc.variables["ARROW_DEPENDENCY_SOURCE"] = "BUNDLED"
        tc.variables["c-ares_SOURCE"] = "BUNDLED"
        tc.variables["re2_SOURCE"] = "BUNDLED"
        tc.variables["absl_SOURCE"] = "BUNDLED"
        tc.variables["Protobuf_SOURCE"] = "BUNDLED"
        tc.variables["Snappy_SOURCE"] = "BUNDLED"
        tc.variables["gRPC_SOURCE"] = "BUNDLED"
        tc.variables["ZLIB_SOURCE"] = "BUNDLED"
        tc.variables["Thrift_SOURCE"] = "BUNDLED"
        tc.variables["utf8proc_SOURCE"] = "BUNDLED"
        tc.variables["ARROW_INCLUDE_DIR"] = True
        tc.variables["ARROW_UTF8PROC_USE_SHARED"] = False
        tc.cache_variables["ENABLE_STATIC"] = "ON"
        tc.cache_variables["ENABLE_BSON"] = "ON"
        tc.cache_variables["ENABLE_TESTS"] = "OFF"
        tc.cache_variables["ENABLE_EXAMPLES"] = "OFF"
        tc.cache_variables["ENABLE_TRACING"] = "OFF"
        tc.cache_variables["ENABLE_COVERAGE"] = "OFF"
        tc.cache_variables["ENABLE_SHM_COUNTERS"] = "OFF"
        tc.cache_variables["ENABLE_MONGOC"] = "OFF"
        tc.cache_variables["ENABLE_MAN_PAGES"] = "OFF"
        tc.cache_variables["ENABLE_HTML_DOCS"] = "OFF"
        tc.generate()


    def configure(self):
        self.options["openssl"].shared = False

        self.options["pcre2"].fPIC = True
        self.options["pcre2"].support_jit = True
        self.options["pcre2"].build_pcre2grep = True

        self.options['xsimd'].xtl_complex = False
        
        self.options["mongo-c-driver"].with_ssl = False
        self.options["mongo-c-driver"].with_sasl = False
        self.options["mongo-c-driver"].srv = False
        self.options["mongo-c-driver"].with_snappy = False
        self.options["mongo-c-driver"].with_zlib = False
        self.options["mongo-c-driver"].with_zstd = False


    def requirements(self):
        self.requires('xsimd/9.0.1')
        self.requires('jemalloc/5.3.0')
        self.requires('pcre2/10.42')
        self.requires('mongo-c-driver/1.23.2')
        self.requires('nlohmann_json/3.11.2')
        self.requires('yyjson/0.6.0')
        self.requires('simdjson/3.1.7')
        self.requires('benchmark/1.7.1')
        self.requires('argparse/2.9')
        self.requires('clipp/1.2.3')
        self.requires('libcurl/7.80.0')
        self.requires('zlib/1.2.13')
        self.requires('openssl/3.1.0')


    def build(self):
#        cmake = CMake(self)
#        cmake.configure()
#        cmake.build()
        pass

    def system_requirements(self):
        pass


    def package_info(self):
        pass

    def package(self):
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.h", dst="lib", keep_path=False)
        self.copy(pattern="*.hpp", dst="lib", keep_path=False)


    def _parquet(self, required=False):
        pass
