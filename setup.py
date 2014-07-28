# -*- coding: utf-8 -*-
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(name             = "fca",
      version          = "0.0.2",
      author           = ["Sergei Obiedkov", "Nikita Romashkin", "Artem Revenko"],
      author_email     = ["not given", "romashkin.nikita@gmail.com", "artreven@gmail.com"],
      description      = "Python package for formal concept analysis",
      keywords         = ["Formal Concept Analysis", "Data Analysis",
                          "Computer Science", "Algebraic Lattices",
                          "Implications", "Artificial Intelligence"],
      license          = "LGPL",
      platforms        = ["Linux", "Mac OS X", "Windows XP/2000/NT"],
)