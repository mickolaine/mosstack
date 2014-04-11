# Copyright 2014 Mikko Laine
# Distributed under the terms of the GNU General Public License v3
# $Header: $

EAPI=5
PYTHON_COMPAT=( python{2_7,3_2,3_3,3_4} )

inherit distutils-r1

DESCRIPTION="PyAstroStack is a stacking software for astronomical images"
HOMEPAGE="https://bitbucket.org/mikko_laine/pyastrostack/"
SRC_URI="http://bitbucket.org/mikko_laine/pyastrostack/downloads/${P}.tar.gz"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"

IUSE="opencl"

DEPEND=">=dev-python/numpy-1.8.0[${PYTHON_USEDEP}]
    dev-python/cython"

RDEPEND=">=dev-python/pillow-2.3.0[${PYTHON_USEDEP}]
	python_targets_python2_7? ( dev-python/configparser )
	sci-libs/scikits_image[${PYTHON_USEDEP}]
	>media-gfx/imagemagick-6.8.0.0
	sci-astronomy/sextractor
	media-gfx/dcraw
	media-libs/exiftool
	dev-python/astropy
	opencl? ( >=dev-python/pyopencl-2013.1[${PYTHON_USEDEP}] )"

DOCS=( CHANGES.txt README.txt )
