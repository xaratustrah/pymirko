# PyMIRKO

Python tools for post processing of **MIRKO** results.

![pymirko](https://raw.githubusercontent.com/xaratustrah/pymirko/master/rsrc/screenshot.png)

####About

`mirko` is a fortran based powerful (albeit **closed source**) optics program for designing particle accelerators and storage rings. This repository **does not** contain the source code for `mirko`. It only contains python tools for automatic execution and post processing of the calculation results. `pymirko` allows:

* run `mirko` for arbitrary number of turns around the storage ring and get a single result
* determine particle losses after decay due to aperture
* determine hits on particle (pocket) detectors
* Flexible graphical representation
* easily adaptable for other tasks

#### Installation

The Java version of `mirko` needs to be installed properly in order for `pymirko` to work. You need a working Java installation as well. Under OSX `libjmirko.dylib` must be available in one of the following places (Java library paths):

    /Users/XXXX/Library/Java/Extensions
    /Library/Java/Extensions
    /Network/Library/Java/Extensions
    /System/Library/Java/Extensions
    /usr/lib/java
    .

I personally choose the first one. You can create a run script and call it `mirko` with the following contents:

    #!/bin/bash
    java -jar /PATH/TO/jMirkoF90/jMirko/dist/jMirko.jar $1

Then you can give execution permission and put it in the path, e.g. in `/opt/local/bin/`.

Enjoy.
:-)
