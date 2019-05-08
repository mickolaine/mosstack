from __future__ import division
from astropy.io import fits
from os.path import splitext, exists
from subprocess import call, check_output
from threading import RLock
from . import config
from . Decoding import Raw2fits_cpp
import numpy as np
from PIL import Image as Im
import gc
import ast
import magic


class Frame(object):
    """
    Frame has all the information of a single photo frame and all the
    methods to read and write data on disk
    """

    def __init__(self, project=None, rawpath=None, infopath=None,
                 ftype="light", number=None, fphase="orig"):
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
        self.rawtype = None
        self.project = project
        self.format = ".fits"
        self.isref = False
        self.staticpath = False
        self.timestamp = None
        self.camera = None
        self.isospeed = None
        self.shutter = None
        self.aperture = None
        self.focallength = None
        self.bayer = None
        self.dlmulti = None
        self.totalexposure = None
        self.biaslevel = None
        self.step1 = False
        self.step2 = False
        self.staticpath = False

        self.wdir = config.Global.get("Default", "Path")

        if project is not None:
            self.name = self.project.get("Default", "Project name")

        # Variables for the tools
        self._debayertool = None
        self._registertool = None
        self._stackingtool = None

        # Instance variables required later
        self.rgb = False      # Is image rgb or monochrome (Boolean)
        self.clip = []
        self.tri = []         # List of triangles
        self.match = []         # List of matching triangles with reference picture
        self._pairs = None
        self._points = None       # String to pass to ImageMagick convert, if star matching is already done.
        self._x = None
        self._y = None       # Dimensions for image
        self._path = None

        self.number = number

        # The following objects are lists because colour channels are separate
        self.hdu = None      # HDU-object for loading fits. Not required for tiff
        self.image = None      # Image object. Required for Tiff and Fits
        self._data = None      # Image data as an numpy.array

        self.lock = RLock()

        if self.infopath is not None:
            self.frameinfo = config.Frame(infopath)
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
        2. Read raw's properties (dimensions, bayer filter...)
        3. Write everything to .info
        """
        self.state["prepare"] = 1

        if self.frameinfo is not None:
            self.readinfo()                     # 1.1. -- 1.2.
            return

        if not self.checkraw(self.rawpath):
            self.state["prepare"] = -1
            raise RuntimeError("Can't read file.", "Dcraw does not recognize this as a DSLR raw photo.")
            # TODO: Tell UI the file's not good

        self.extractinfo()                      # 2.
        self.writeinfo()                        # 3.

        self.state["prepare"] = 1

        return

    def decode(self):
        """
        Decode the frame. Now just calls _decode
        """

        Raw2fits_cpp.decode(self.rawpath, self.path())
        self.getdimensions()
        self.writeinfo()
        self.state["prepare"] = 2
        self.project.set("Phase", "Decoded", "1")

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
        biaslevel = self.biaslevel

        if bias is not None:
            data = self.stackingtool.subtract(data, bias.data)
        elif biaslevel is not None:
            try:
                data -= float(biaslevel)
            except ValueError:
                pass

        if dark is not None:
            data = self.stackingtool.subtract(data, dark.data)

        if flat is not None:
            data = self.stackingtool.divide(data, flat.data)

        self.data = data
        self.fphase = "calib"
        self.write()
        self.project.addfile(self.path())
        self.state["calibrate"] = 2

        self.project.set("Phase", "Calibrated", "1")

        #return

    def calibrate_worker(self, bias=None, dark=None, flat=None):
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
        biaslevel = self.biaslevel

        if bias is not None:
            data = self.stackingtool.subtract(data, bias.data)
        elif biaslevel is not None:
            try:
                data -= float(biaslevel)
            except ValueError:
                pass

        if dark is not None:
            data = self.stackingtool.subtract(data, dark.data)

        if flat is not None:
            data = self.stackingtool.divide(data, flat.data)

        self.data = data
        self.fphase = "calib"
        self.write()
        self.project.addfile(self.path())
        self.state["calibrate"] = 2

        self.project.set("Phase", "Calibrated", "1")

        #return

    def debayer(self, debayertool=None):
        """
        Debayer the frame. Project tells how.

        1. Check what Debayer function to use
        2. Do the thing
        3. Inform Gui that state has changed
        """

        self.state["debayer"] = 1
        print("Debayering frame " + self.number)
        #print(self._debayertool)
        if debayertool:
            self.debayertool = debayertool
        data = self.debayertool.debayer(self)     
        self.fphase = "rgb"

        if data is not None:
            self.data = data
            self.write()

        self.project.addfile(self.path())
        self.state["debayer"] = 2
        self.project.set("Phase", "Debayered", "1")
        #return

    def debayer_worker(self):
        """
        Debayer the frame using threads.

        1. Check what Debayer function to use
        2. Do the thing
        3. Inform Gui that state has changed
        """

        self.state["debayer"] = 1
        print("Debayering frame " + self.number)
        
        data = self.debayertool.debayer(self)
        self.fphase = "rgb"

        if data is not None:
            self.data = data
            self.write()

        self.project.addfile(self.path())
        self.state["debayer"] = 2
        self.project.set("Phase", "Debayered", "1")
        #return

    def register(self):
        """
        Register the frame. Project tells how.

        1. Step 1
        2. Call for register
        3. Inform Gui that state has changed
        """

        self.state["register"] = 1
        data = self.registertool.register(self)
        self.fphase = "reg"
        self.state["register"] = 2
        if data is not None:
            self.data = data
            self.write()
            self.project.addfile(self.path())
            del data
        self.project.set("Phase", "Registered", "1")
        #return

    def register_worker(self):
        """
        Register the frame using threads

        1. Step 1
        2. Call for register
        3. Inform Gui that state has changed
        """

        self.state["register"] = 1
        data = self.registertool.register(self)
        self.fphase = "reg"
        self.state["register"] = 2
        if data is not None:
            self.data = data
            self.write()
            self.project.addfile(self.path())
            del data
        self.project.set("Phase", "Registered", "1")
        #return

    def crop(self, xrange, yrange):
        """
        Crop the data by given coordinates. Save cropped data to self.data and write to disc with fphase="crop".

        Assume data is 3 dimensional. TODO: Make it work with 2d data as well

        Cropping is reasonable to do only for aligned data. Either with data that's already aligned or after registering

        Arguments:
        xrange: (x_0, x_1)
        yrange: (y_0, y_1)
        """

        # Crop data
        print("Cropping frame number " + self.number)

        data = self.data[:, yrange[0]:yrange[1], xrange[0]:xrange[1]]
        self.data = data

        self.fphase = "crop"
        self.write()
        self.project.addfile(self.path())

        # Alter metadata
        self.x = self.data.shape[2]
        self.y = self.data.shape[1]

        self.writeinfo()

    @staticmethod
    def createmaster(project, path, ftype):
        """
        Return a Frame object with a master frame

        Arguments:
        project - a Project class object
        path - unix path to fits or tiff master frame
        ftype - type of master: bias, dark or flat
        """
        if isinstance(path, list):
            pathstr = path[0]
        else:
            pathstr = path
        frame = Frame(project, ftype=ftype, number="master")
        fileformat = Frame.identify(pathstr)
        frame._path = pathstr
        if fileformat == "fits":
            frame.rawtype = "fits"
            frame.staticpath = True
            frame._load_fits(path=pathstr)
            frame.extractinfo()
            frame.writeinfo()
        elif fileformat == "tiff":
            frame.rawtype = "tiff"
            frame._load_tiff(path=pathstr)
            frame.extractinfo()
            frame.writeinfo()
            frame.write()

        return frame

    def getpath(self, fformat="fits", fphase=None):
        """
        Return path, which is constructed on the fly

        Will replace self.path
        """

        if fphase is None:
            fphase = self.fphase

        if fformat == "fits":

            if self.staticpath:
                return self._path
            try:
                return self.frameinfo.get("Paths", fphase)
            except (KeyError, AttributeError):
                pass

        if self.number is None:
            return self.wdir + "/" + self.name + "_" + self.ftype + "_" + fphase + "." + fformat
        else:
            return self.wdir + "/" + self.name + "_" + self.ftype \
                             + "_" + str(self.number) + "_" + fphase + "." + fformat

    def path(self, fformat="fits", ):
        """
        Return path, which is constructed on the fly
        """

        if fformat == "fits":

            if self.staticpath:
                return self._path
            try:
                return self.frameinfo.get("Paths", self.fphase)
            except (KeyError, AttributeError):
                pass

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

    @staticmethod
    def identify(path):
        """
        Identify the file in path. Return format.

        Supported formats are TIFF, FITS and RAW (which means everything recognized by dcraw).
        If not recognized, will return file magic's description
        """

        # There are two different libraries called magic.
        #  Try statement expects filemagic, in case that fails except tries python_magic
        #TODO: This magic thing
        if isinstance(path, list):
            pathstr = path[0]
        else:
            pathstr = path
        try:
            #mg = magic.open(magic.NONE)
            #mg.load()
            #ms = mg.file(path)
            ms = magic.from_file(pathstr)
        except AttributeError:
            ms = magic.from_file(pathstr)

        if ms.split()[0] == "TIFF":
            return "tiff"
        if ms.split()[0] == "FITS":
            return "fits"
        if not call(["dcraw", "-i", path]):
            return "raw"
        return ms

    def readinfo(self):
        """
        Read frame info from specified file
        """

        self.number = self.frameinfo.get("Default", "Number")
        self.rawpath = self.frameinfo.get("Paths", "Raw")
        self.ftype = self.frameinfo.get("Default", "Ftype")

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

    def checkraw(self, rawpath):
        """
        Check the type of the raw file

        Arguments:
        rawpath - Unix path to raw file

        Returns:
        True if file recognized
        False if file invalid
        """

        try:
            if exists(rawpath):
                if splitext(rawpath)[1] in (".fits", ".FITS"):
                    self.rawtype = "fits"
                    return True
                elif splitext(rawpath)[1] in (".tif", ".TIF", ".tiff", ".TIFF"):
                    self.rawtype = "tiff"
                    return True
                if call(["dcraw", "-i", rawpath]):
                    return False
                else:
                    return True
        except:
            return False

    def extractinfo(self):
        """
        Read the file into memory and extract all required information.
        """

        if self.rawtype == "fits":
            data = self.image.data

            if len(data.shape) == 2:
                self.x, self.y = data.shape

            elif len(data.shape) == 3:
                temp, self.x, self.y = data.shape

            self.data = data
            return

        if self.rawtype == "tiff":

            if len(self._data) == 2:
                self.x, self.y = self._data.shape

            elif len(self._data.shape) == 3:
                temp, self.x, self.y = self._data.shape

            return

        rawoutput = check_output(["dcraw", "-i", "-v", self.rawpath]).decode()

        output = str.split(str(rawoutput), "\n")

        for i in output: # Some of these are extracted for possible future use
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
            if line[0] == "Image size":
                self.x = int(line[1].strip().split(" x ")[0])
                self.y = int(line[1].strip().split(" x ")[1])

        print("Done!")
        print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))

    #TODO: get rid of this once decoding is done better
    def getdimensions(self):
        """
        Get X and Y dimensions from FITS instead of DCRaw output.

        This is needed to fix problems with temporary raw2fits.cpp-solution
        """
        self._load_fits(self.path())
        data = self.image.data

        if len(data.shape) == 2:
            self.y, self.x = data.shape

        elif len(data.shape) == 3:
            temp, self.y, self.x = data.shape

        self.data = data

    def writeinfo(self):
        """
        Write frame info to specified file
        """

        if self.project is None:
            print("Project not set. This might not be a problem if you know what you're doing.")
            return

        if self.infopath is None:
            self.infopath = self.wdir + "/" + self.name + "_" + self.ftype + "_" + str(self.number) + ".info"
        self.frameinfo = config.Frame(self.infopath)
        self.project.addfile(self.infopath)

        self.frameinfo.set("Paths", "Raw", str(self.rawpath))
        self.frameinfo.set("Default", "Number", str(self.number))
        self.frameinfo.set("Default", "Ftype", str(self.ftype))
        self.frameinfo.set("Paths", self.fphase, str(self.path()))
        self.frameinfo.set("Properties", "Filter pattern", str(self.bayer))
        self.frameinfo.set("Properties", "Timestamp", str(self.timestamp))
        self.frameinfo.set("Properties", "Camera", str(self.camera))
        self.frameinfo.set("Properties", "ISO speed", str(self.isospeed))
        self.frameinfo.set("Properties", "Shutter", str(self.shutter))
        self.frameinfo.set("Properties", "Aperture", str(self.aperture))
        self.frameinfo.set("Properties", "Focal length", str(self.focallength))
        self.frameinfo.set("Properties", "Daylight multipliers", str(self.dlmulti))

        try:
            self.frameinfo.set("Properties", "X", str(self.x))
            self.frameinfo.set("Properties", "Y", str(self.y))
        except KeyError:
            pass

        if self.totalexposure is not None:
            self.frameinfo.set("Properties", "Total exposure", str(self.totalexposure))

    def infotable(self):
        """
        Return all the possible information extracted in one table (2d array)
        """

        table = [["Path to image", self.path()],
                 ["Path to original raw photo", self.rawpath],
                 ["Image number", self.number],
                 ["Dimensions", str(self.x) + "x" + str(self.y)],
                 ["Frame type", self.ftype],
                 ["Time stamp", self.timestamp],
                 ["Camera", self.camera],
                 ["Filter pattern", self.bayer],
                 ["ISO speed", self.isospeed],
                 ["Shutter speed", self.shutter],
                 ["Aperture", self.aperture],
                 ["Focal length", self.focallength],
                 ["Daylight multipliers", self.dlmulti]]

        return table

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

        Data can't be loaded in memory all the time because of the size of it.
        This getter handles reading data from disk and returning it as if it were just Frame.data
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
        if data is None:
            self._data = None
        elif len(data.shape) == 3:
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
        self.fphase = genname
        print("Changing path to " + self.wdir +
              self.name + "_" + self.ftype + "_" + str(self.number) + "_" + genname + ".fits")
        self.frameinfo.set("Paths", genname, self.path())

    genname = property(fget=getgenname, fset=setgenname)

    def get_x(self):
        if self._x:
            return self._x
        else:
            self.x = int(self.frameinfo.get("Properties", "X"))
            return self._x

    def set_x(self, x):
        self._x = x

    x = property(fget=get_x, fset=set_x)

    def get_y(self):
        if self._y:
            return self._y
        else:
            self.y = int(self.frameinfo.get("Properties", "Y"))
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

    def setdebayertool(self, debayertool):
        try:
            self._debayertool = debayertool
        except:
            pass
    
    def getdebayertool(self):
        return self._debayertool
    
    debayertool = property(fget=getdebayertool, fset=setdebayertool)

    def setregistertool(self, registertool):
        try:
            self._registertool = registertool
        except:
            pass
    
    def getregistertool(self):
        return self._registertool

    registertool = property(fget=getregistertool, fset=setregistertool)

    def setstackingtool(self, stackingtool):
        try:
            self._stackingtool = stackingtool
            
        except:
            pass
    
    def getstackingtool(self):
        return self._stackingtool

    stackingtool = property(fget=getstackingtool, fset=setstackingtool)

    def _load_fits(self, path=None):
        """
        Load a fits file created by this program
        """
        if path is None:
            path = self.path()
        if isinstance(path, list):
            pathstr = path[0]
        else:
            pathstr = path
        
        self.hdu = fits.open(pathstr, memmap=True)
        self.image = self.hdu[0]
        #self.image = self.hdu[1]

    def _load_tiff(self, path=None):
        """
        Load a tiff file
        """

        if path is None:
            self.data = np.array(Im.open(self.rawpath))
        else:
            self.data = np.array(Im.open(path))

    def _load_data(self):
        """
        Load portion of FITS-data into memory. Does not work with TIFF

        If self.clip is set, load only piece of data.
        """

        if self.format != ".fits":
            print("This method works only with FITS files.")

        # If self.clip is set, load only piece of data
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

        # Load the whole image
        else:
            self._load_fits()
            if len(self.image.shape) == 3:
                self._data = self.image.data
            else:
                self._data = np.array([self.image.data])

    def _release_data(self):
        """
        Release data from memory and delete even the hdu
        
        Lock used to prevent other threads using while memory is released
        """

        self.lock.acquire()
        if self.hdu is not None:
            self.hdu.close()
        self.image = None
        self.hdu = None
        
        del self.image
        del self.hdu
        del self.data

        gc.collect()
        self.hdu = None
        self.image = None
        self.lock.release()

    def _write_fits(self):
        """
        Write self.data to disk as a fits file
        """

        hdu = fits.PrimaryHDU()  # To create a default header

        if self._data is None:
            print("No data set! Exiting...")
            exit()

        # Changed datatype to int32 since uint16 isn't supported by standard
        if self._data.shape[0] == 1:
            fits.writeto(self.path(), np.int32(self._data[0]), hdu.header, overwrite=True)
        else:
            fits.writeto(self.path(), np.int32(self._data), hdu.header, overwrite=True)

        self._release_data()

    def _write_tiff(self, skimage=True):
        """
        Write self.data to disk as a tiff file
        """

        # Convert data from int32 to int16
        maxim = np.amax(self.data)
        data = np.int16(self.data / maxim * 32768)

        if self.data.shape[0] == 1:

            imagedata = np.flipud(data[0])
            image = Im.fromarray(imagedata)
            image.save(self.path(fformat="tiff"), format="tiff")

        elif self.data.shape[0] == 3:

            rgbpath = self.rgbpath(fileformat="tiff")
            for i in (0, 1, 2):
                imagedata = np.flipud(data[i])
                image = Im.fromarray(imagedata)
                image.save(rgbpath[i], format="tiff")
            call(["convert", rgbpath[0], rgbpath[1], rgbpath[2], "-channel", "RGB", "-combine", self.path(fformat="tiff")])
            #      "-channel", "RGB", "-depth", "16", "-combine", self.path(fformat="tiff")])
            #call(["rm", rgbpath[0], rgbpath[1], rgbpath[2]])
        self.project.addfile(self.path(fformat="tiff"), final=True)

    def _write_tiff_old(self, skimage=True):
        """
        Write self.data to disk as a tiff file
        """

        if check_output(["convert -version | grep Version"], shell=True).split()[2].decode()[2] == "7":
            im_version = "6.7"
        else:
            im_version = "6.8"
        print(self.data.shape)
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
            print("convert " + rgbpath[0] + rgbpath[1] + rgbpath[2] + " -channel RGB -combine " + self.path(fformat="tiff"))
            call(["convert", rgbpath[0], rgbpath[1], rgbpath[2], "-channel", "RGB", "-combine", self.path(fformat="tiff")])
            #      "-channel", "RGB", "-depth", "16", "-combine", self.path(fformat="tiff")])
            #call(["rm", rgbpath[0], rgbpath[1], rgbpath[2]])
        self.project.addfile(self.path(fformat="tiff"), final=True)

    def write_tiff(self):
        """
        Load data from current fits and save it as a tiff. Required because ImageMagick
        doesn't work with fits too well.
        """

        image = []
        rgbpath = self.rgbpath(fileformat="tiff")
        for i in [0, 1, 2]:
            image.append(Im.fromarray(np.flipud(np.int16(self.data[i]))))
            image[i].save(rgbpath[i], format="tiff")
            self.project.addfile(rgbpath[i])

        self._release_data()

    def write(self, tiff=False, skimage=True):
        """
        Wrapper function to relay writing of the image on disk.
        This is remnants of something much more complicated...

        Arguments:
        tiff     = Write also a tiff file in addition to fits
        """
        if self._data is None:
            return
        self._write_fits()
        if tiff:
            self._write_tiff(skimage=skimage)

    def _print_all_values(self):
        """
        Print all the values saved in variables. Debugging
        """
        print(self.state)
        print(self.rawpath)
        print(self.infopath)
        print(self.ftype)
        print(self.fphase)
        print(self.rawtype)
        print(self.project)
        print(self.format)
        print(self.isref)
        print(self.staticpath)
        print(self.timestamp)
        print(self.camera)
        print(self.isospeed)
        print(self.shutter)
        print(self.aperture)
        print(self.focallength)
        print(self.bayer)
        print(self.dlmulti)
        print(self.totalexposure)
        print(self.biaslevel)
        print(self.step1)
        print(self.step2)
        print(self.staticpath)
        print(self.wdir)
        print(self.name)
        print(self.rgb)
        print(self.clip)
        print(self.tri)
        print(self.match)
        print(self._pairs)
        print(self._points)
        print(self._x)
        print(self._y)
        print(self._path)
        print(self.number)
        print(self.hdu)
        print(self.image)
        print(self._data)
        print(self.frameinfo)
        print(dict(self.frameinfo.conf.items('Default')))
        print(dict(self.frameinfo.conf.items('Properties')))
        print(dict(self.frameinfo.conf.items('Paths')))
        print(dict(self.frameinfo.conf.items('DEFAULT')))
