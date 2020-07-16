import numpy
from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "pybasicbayes.util.cstats",
        sources=["pybasicbayes/util/cstats.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-w"],
    )
]

setup(
    name="pybasicbayes",
    version="0.2.4",
    description="Basic utilities for Bayesian inference",
    author="Matthew James Johnson",
    author_email="mattjj@csail.mit.edu",
    url="http://github.com/mattjj/pybasicbayes",
    packages=[
        "pybasicbayes",
        "pybasicbayes.distributions",
        "pybasicbayes.util",
        "pybasicbayes.testing",
        "pybasicbayes.models",
    ],
    platforms="ALL",
    keywords=[
        "bayesian",
        "inference",
        "mcmc",
        "variational inference",
        "mean field",
        "vb",
    ],
    install_requires=["numpy", "scipy", "matplotlib", "nose"],
    ext_modules=cythonize(extensions),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
    ],
)
