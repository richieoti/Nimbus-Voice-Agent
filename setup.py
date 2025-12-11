from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    name="NimbusVoice",
    sources=[
        "NimbusVoice.pyx",
        "NimbusCommands.cpp",
    ],
    language="c++",
    include_dirs=["."], 
    libraries=["user32"],
)

setup(
    name="NimbusVoice",
    ext_modules=cythonize(ext),
)


