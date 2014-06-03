from __future__ import division
from astropy.io import fits
from os.path import splitext, exists
from shutil import move
from subprocess import call, check_output
from . import Config
import numpy as np
from PIL import Image as Im
import gc
import ast


class Frame(object):
    """
    Frame has all the information of a single photo frame and all the methods to read and write data on disk
    """

    def __init__(self, project=None, rawpath=None, infopath=None, ftype="light", number=None, fphase="orig"):
        """
        Create a Frame object from rawpath or frame info file

        Arguments
        rawpath = Unix path to raw file
        infopath = Unix path to frame info file
        ftype = frame type: light, bias, dark or flat
        fphase = process phase: orig, calib#, rgb, reg, master
        """

        self.state = {         # Dict to hold information about process state
            "prepare": 0,       # 0 = not started
            "calibrate": 0,     # 1 = under process
            "debayer": 0,       # 2 = done
            "register": 0       # -1 = failed
        }                       # -2 = invalid (eg. registration for darks)

        self.rawpath = rawpath
        self.infopath = infopath
        self.ftype = ftype
        self.fphase = fphase
        self.project = project
        self.format = ".fits"       # TODO: Remove this legacy

        # TODO: Get rid of this:
        self.wdir = self.project.get("Setup", "Path")
        self.name = self.project.get("Default", "Project name")

        # Instance variables required later
        self.rgb       = False      # Is image rgb or monochrome (Boolean)
        self.clip      = []
        self.tri       = []         # List of triangles
        self.match     = []         # List of matching triangles with reference picture
        self._pairs    = None
        self._points   = None       # String to pass to ImageMagick convert, if star matching is already done.
        self._x        = None
        self._y        = None       # Dimensions for image

        self.number = number

        # The following objects are lists because colour channels are separate
        self.hdu   = None      # HDU-object for loading fits. Not required for tiff
        self.image = None      # Image object. Required for Tiff and Fits
        self._data = None      # Image data as an numpy.array

        if self.infopath is not None:
            self.frameinfo = Config.Frame(infopath)
        else:
            self.frameinfo = None

        if (self.rawpath is not None) or (self.infopath is not None):
            self.prepare()

    def prepare(self):
        """
        Prepare the frame.

        Returns signal or something where Gui knows to update itself

        1. Check if there already is an .info file
            1.1. Check if everything .info file says is really done and found
            1.2. Update all variables to match .info's state
            1.3. Inform Gui to update itself
        2. Decode raw to FITS
        3. Read raw's properties (dimensions, bayer filter...)
        4. Write everything to .info
        5. Inform Gui that state has changed
        """
        self.state["prepare"] = 1

        if self.frameinfo is not None:
            self.readinfo()                     # 1.1. -- 1.2.
            # 1.3.
            return

        if not Frame.checkraw(self.rawpath):
            self.state["prepare"] = -1
            # TODO: Tell UI the file's not good
            return

        self._decode()                          # 2.
        self.extractinfo()                      # 3.
        self.writeinfo()                        # 4.

        self.state["prepare"] = 2
        self.update_ui()

        return

    def calibrate(self, stacker, bias=None, dark=None, flat=None):
        """
        Calibrate the frame. Project tells how.

        All stages are optional except the last one
        1. Subtract master bias
        2. Subtract master dark
        3. Divide with master flat
        4. Inform Gui that state has changed
        """

        self.state["calibrate"] = 1

        data = self.data

        if bias is not None:
            data = stacker.subtract(data, bias.data)

        if dark is not None:
            data = stacker.subtract(data, dark.data)

        if flat is not None:
            data = stacker.divide(data, flat.data)

        self.data = data
        self.fphase = "calib"
        self.write()
        self.state["calibrate"] = 2

        self.update_ui()
        return

    def debayer(self, debayer):
        """
        Debayer the frame. Project tells how.

        1. Check what Debayer function to use
        2. Do the thing
        3. Inform Gui that state has changed
        """

        self.state["debayer"] = 1

        self.data = debayer.debayer(self.data)
        self.fphase = "rgb"
        self.write()
        self.state["debayer"] = 2

        self.update_ui()
        return

    def register(self, register):
        """
        Register the frame. Project tells how.

        1. Step 1
        2. Check if reference frame.
            2.(If)   Copy file
            2.(Else) Step 2
        3. Inform Gui that state has changed
        """

        self.state["register"] = 1

        self.data = register.register_single(self)

        self.state["register"] = 2

        self.update_ui()

        return

    def path(self, fformat="fits"):
        """
        Return path, which is constructed on the fly
        """
        if self.number is None:
            return self.wdir + "/" + self.name + "_" + self.ftype + "_" + self.fphase + "." + fformat
        else:
            return self.wdir + "/" + self.name + "_" + self.ftype \
                             + "_" + str(self.number) + "_" + self.fphase + "." + fformat

    def rgbpath(self, fileformat=None):
        """
        Return list of file paths where "_[rgb]" is placed before the extension

        eg. if self.path is /path/to/file_2_reg.tiff this returns
         [/path/to/file_2_reg_r.tiff, /path/to/file_2_reg_g.tiff, /path/to/file_2_reg_b.tiff]
        This is required for ImageMagicks inability to understand rgb fits, or actually fits' in general
        Arguments:
        format = if specified, change the extension to this
        """

        base, ext = splitext(self.path())
        if fileformat:
            ext = "." + fileformat
        pathlist = []
        for i in ("_r", "_g", "_b"):
            pathlist.append(base + i + ext)
        return pathlist

    def combine(self, newpath):
        """
        Combine channels from three fits files into one.
        """
        hdu = []
        data = []

        for i in (0, 1, 2):
            hdu.append(fits.open(newpath[i]))
            data.append(hdu[i][0].data)

        self.data = np.array(data) - 32768
        self.write(skimage=True)
        self._release_data()

    def getpath(self, genname):
        """
        Return path by some other genname than self.genname. Read from .info
        """

        try:
            return self.frameinfo.get("Paths", genname)
        except:
            return self.wdir + self.name + "_" + str(self.number) + "_" + genname + ".fits"

    def readinfo(self):
        """
        Read frame info from specified file
        """

        self.number = self.frameinfo.get("Default", "Number")

        self.bayer = self.frameinfo.get("Properties", "Filter pattern")
        self.timestamp = self.frameinfo.get("Properties", "Timestamp")
        self.camera = self.frameinfo.get("Properties", "Camera")
        self.isospeed = self.frameinfo.get("Properties", "ISO speed")
        self.shutter = self.frameinfo.get("Properties", "Shutter")
        self.aperture = self.frameinfo.get("Properties", "Aperture")
        self.focallength = self.frameinfo.get("Properties", "Focal length")
        self.dlmulti = self.frameinfo.get("Properties", "Daylight multipliers")

        self.x = int(self.frameinfo.get("Properties", "X"))
        self.y = int(self.frameinfo.get("Properties", "Y"))

        try:
            self.pairs = ast.literal_eval(self.frameinfo.get("Registering", "pairs"))
        except KeyError:
            pass

    @staticmethod
    def checkraw(rawpath):
        """
        Check if source file is something dcraw can decode

        Arguments:
        rawpath - Unix path to raw file

        Returns:
        Boolean
        """

        try:
            if exists(rawpath):
                if call(["dcraw", "-i", rawpath]):
                    return False
                else:
                    return True
        except:
            return 0

    def extractinfo(self):
        """
        Read the file into memory and extract all required information.
        """

        rawoutput = check_output(["dcraw", "-i", "-v", self.rawpath]).decode()

        output = str.split(str(rawoutput), "\n")

        for i in output:                        # Some of these are extracted for possible future use
            line = str.split(i, ": ")
            if line[0] == "Timestamp":
                self.timestamp = line[1]
            if line[0] == "Camera":
                self.camera = line[1]
            if line[0] == "ISO speed":
                self.isospeed = line[1]
            if line[0] == "Shutter":
                self.shutter = line[1]
            if line[0] == "Aperture":
                self.aperture = line[1]
            if line[0] == "Focal length":
                self.focallength = line[1]
            if line[0] == "Filter pattern":
                self.bayer = line[1][:4]
            if line[0] == "Daylight multipliers":
                self.dlmulti = line[1]

        self._load_data()

        # Image dimensions
        if len(self.image.shape) == 3:
            self.x = self.image.shape[2]
            self.y = self.image.shape[1]
        else:
            self.x = self.image.shape[1]
            self.y = self.image.shape[0]

        self._release_data()
        print("Done!")
        print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))

    def writeinfo(self):
        """
        Write frame info to specified file
        """

        if self.infopath is None:
            self.infopath = self.wdir + "/" + self.name + "_" + self.ftype + "_" + str(self.number) + ".info"
        self.frameinfo = Config.Frame(self.infopath)

        self.frameinfo.set("Paths", "Raw", self.rawpath)
        self.frameinfo.set("Default", "Number", str(self.number))
        self.frameinfo.set("Paths", self.fphase, self.path())
        self.frameinfo.set("Properties", "Filter pattern", self.bayer)
        self.frameinfo.set("Properties", "Timestamp", self.timestamp)
        self.frameinfo.set("Properties", "Camera", self.camera)
        self.frameinfo.set("Properties", "ISO speed", self.isospeed)
        self.frameinfo.set("Properties", "Shutter", self.shutter)
        self.frameinfo.set("Properties", "Aperture", self.aperture)
        self.frameinfo.set("Properties", "Focal length", self.focallength)
        self.frameinfo.set("Properties", "Daylight multipliers", self.dlmulti)

        self.frameinfo.set("Properties", "X", str(self.x))
        self.frameinfo.set("Properties", "Y", str(self.y))

    def fromraw(self, path):
        """
        Create a Frame object from raw photo

        Arguments:
        path - Unix path of the photo

        Returns:
        Frame
        """

        self._convert(path)
        self.extractinfo()
        self.rawpath = path
        self.writeinfo()

    def setclip(self, clip):
        """
        Set the data clip coordinates
        """

        self.clip = clip

    def getpoints(self):
        if self._points is None:
            try:
                return self.frameinfo.get("Registering", "Points")
            except KeyError:
                return None

    def setpoints(self, points):
        self._points = points
        self.frameinfo.set("Registering", "Points", self._points)

    points = property(getpoints, setpoints)

    def getdata(self):
        """
        Getter for data.

        Data can't be loaded in memory all the time because of the size of it. This getter handles reading data
        from disk and returning it as if it were just Frame.data
        """

        if self._data is None:
            self._load_data()
        data = self._data.copy()
        self._release_data()
        return data

    def setdata(self, data):
        """
        Setter for data.
        """
        if len(data.shape) == 3:
            self._data = data
        else:
            self._data = np.array([data])

    def deldata(self):
        """
        Destructor for data
        """

        self._data = None

    data = property(getdata, setdata, deldata)

    def getgenname(self):
        return self.fphase

    def setgenname(self, genname):
        """
        Set genname and take care of info file changes
        """
        self._fphase = genname
        print("Changing path to " + self.wdir + self.name + "_" + self.number + "_" + genname + ".fits")
        self.frameinfo.set("Paths", genname, self.path())

    genname = property(fget=getgenname, fset=setgenname)

    def get_x(self):
        if self._x:
            return self._x
        else:
            self.x = self.frameinfo.get("Properties", "X")
            return self._x

    def set_x(self, x):
        self._x = x

    x = property(fget=get_x, fset=set_x)

    def get_y(self):
        if self._y:
            return self._y
        else:
            self.y = self.frameinfo.get("Properties", "Y")
            return self._y

    def set_y(self, y):
        self._y = y

    y = property(fget=get_y, fset=set_y)

    def getpairs(self):
        if self._pairs is None:
            try:
                self._pairs = ast.literal_eval(self.frameinfo.get("Registering", "pairs"))
            except KeyError:
                pass

        return self._pairs

    def setpairs(self, pairs):
        self._pairs = pairs
        self.frameinfo.set("Registering", "pairs", str(pairs))

    pairs = property(fget=getpairs, fset=setpairs)

    def _decode(self):
        """
        Convert the raw file into FITS via PGM.
        """

        if exists(self.path()):
            print("Image already converted.")
            return

        print("Converting RAW image...")
        if call(["dcraw -v -4 -t 0 -D '" + self.rawpath + "'"], shell=True):
            print("Something went wrong... There might be helpful output from Rawtran above this line.")
            if exists(self.path()):
                print("File " + self.path() + " was created but dcraw returned an error.")
            else:
                print("Unable to continue.")
        else:
            move(self.rawpath[:-3] + "pgm", self.path(fformat="pgm"))
            call(["convert", self.path(fformat="pgm"), self.path()])
            print("Conversion successful!")

    def _convert(self, srcpath):
        """
        Convert the raw file into FITS via PGM.

        There are some problems with TIFF format. That's why via PGM.

        Arguments:
        srcpath - Full unix path where to find source file

        Return:
        Nothing. File is created or program crashed. Perhaps this is a good place for try-except...
        """

        if exists(srcpath):

            if exists(self.path()):
                print("Image already converted.")
                return

            print("Converting RAW image...")
            if call(["dcraw -v -4 -t 0 -D " + srcpath], shell=True):
                print("Something went wrong... There might be helpful output from Rawtran above this line.")
                if exists(self.path()):
                    print("File " + self.path() + " was created but dcraw returned an error.")
                else:
                    print("Unable to continue.")
            else:
                move(srcpath[:-3] + "pgm", self.path(fformat="pgm"))
                call(["convert", self.path(fformat="pgm"), self.path()])
                print("Conversion successful!")
        else:
            print("Unable to find file in given path: " + srcpath + ". Find out what's wrong and try again.")
            print("Can't continue. Exiting.")
            exit()

    def _load_fits(self):
        """
        Load a fits file created by this program

        Arguments:
        suffix - file name suffix indicating progress of process. eg. calib, reg, rgb
        number - number of file
        """

        self.hdu = fits.open(self.path(), memmap=True)
        self.image = self.hdu[0]

    def _load_data(self):
        """
        Load portion of FITS-data into memory. Does not work with TIFF

        Arguments:
        rangetuple - coordinates of the clipping area (x0, x1, y0, y1)
        """

        if self.format != ".fits":
            print("This method works only with FITS files.")

        if self.clip:
            y0 = self.clip[0]
            y1 = self.clip[1]
            x0 = self.clip[2]
            x1 = self.clip[3]

            self._load_fits()

            if len(self.image.shape) == 3:
                self._data = self.image.data[0:3, x0:x1, y0:y1]
            else:
                self._data = np.array([self.image.data[x0:x1, y0:y1]])
        else:
            self._load_fits()
            if len(self.image.shape) == 3:
                self._data = self.image.data
            else:
                self._data = np.array([self.image.data])
        if np.amin(self._data) >= 32768:
            self._data -= 32768
            #print(self._data)

    def _release_data(self):
        """
        Release data from memory and delete even the hdu
        """
        if self.hdu is not None:
            self.hdu.close()
        self.image = None
        del self.data
        self.hdu = None

        gc.collect()

    def _write_fits(self):
        """
        Write self.data to disk as a fits file
        """

        hdu = fits.PrimaryHDU()  # To create a default header

        if self._data is None:
            print("No data set! Exiting...")
            exit()
        fits.writeto(self.path(), np.uint16(self._data), hdu.header, clobber=True)
        self._release_data()

    def _write_tiff(self, skimage=True):
        """
        Write self.data to disk as a tiff file
        """

        if check_output(["convert -version | grep Version"], shell=True).split()[2].decode()[2] == "7":
            im_version = "6.7"
        else:
            im_version = "6.8"

        if self.data.shape[0] == 1:
            imagedata = np.flipud(np.int16(self.data[0] - 32768))
            image = Im.fromarray(imagedata)
            image.save(self.path(fformat="tiff"), format="tiff")

        elif self.data.shape[0] == 3:
            rgbpath = self.rgbpath(fileformat="tiff")
            for i in (0, 1, 2):
                if im_version == "6.7" and not skimage:
                    imagedata = np.flipud(np.int16(self.data[i] - 32768))
                else:
                    imagedata = np.flipud(np.int16(self.data[i]))
                image = Im.fromarray(imagedata)
                image.save(rgbpath[i], format="tiff")
            call(["convert", rgbpath[0], rgbpath[1], rgbpath[2],
                  "-channel", "RGB", "-depth", "16", "-combine", self.path(fformat="tiff")])
            call(["rm", rgbpath[0], rgbpath[1], rgbpath[2]])

    def write_tiff(self):
        """
        Load data from current fits and save it as a tiff. Required because ImageMagick
        doesn't work with fits too well.
        """
        #self._load_data()

        image = []
        rgbpath = self.rgbpath(fileformat="tiff")
        #data = self.data
        for i in [0, 1, 2]:
            image.append(Im.fromarray(np.flipud(np.int16(self.data[i]))))
            image[i].save(rgbpath[i], format="tiff")

        self._release_data()

    def write(self, tiff=False, skimage=True):
        """
        Wrapper function to relay writing of the image on disk. This is remnants of something much more complicated...

        Arguments:
        tiff     = Write also a tiff file in addition to fits
        """

        self._write_fits()
        if tiff:
            self._write_tiff(skimage=skimage)

    def update_ui(self):
        """
        Update the user interface. Empty for now, but inheriting classes might replace this to something useful
        """
        pass