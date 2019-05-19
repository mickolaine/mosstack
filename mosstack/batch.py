"""
Batch is a series of frames that will be stacked in to a single frame.
"""

from os import listdir
from os.path import splitext
import threading
from . frame import Frame


class Batch():
    """
    Batch holds a list of frames and handles connections to project files
    """

    def __init__(self, project, ftype="light", fphase="orig"):
        """
        Constructor loads Frames according to arguments.

        Arguments:
        project = Configuration object for the project
        fphase = Generic name of the files
        """

        self.project = project
        self.fphase = fphase
        self.master = None      # Master for this batch
        self.masterbias = None  # Master frames to be used
        self.masterdark = None  # in calibration
        self.masterflat = None

        self.name = self.project.get("Default", key="project name")   # Name for the resulting image

        self.frames = {}                                              # Empty dict for Photos

        # Variables for the tools
        self._debayertool = None
        self._registertool = None
        self._stackingtool = None

        if ftype is not None:
            self.ftype = ftype

        if fphase is not None:
            self.fphase = fphase

        self.ref_id = "0"
        try:
            self.set_ref(project.get("Reference", key=self.ftype))  # Number of reference frame
        except KeyError:
            pass

        try:
            files = self.project.get(self.ftype) # Paths for the frame info files

            for key in files:
                frame = Frame(self.project, infopath=files[key], fphase=self.fphase)
                self.frames[key] = frame
            self.set_ref(self.ref_id)

        except KeyError:
            #print("Error")
            pass

    def set_ref(self, ref_id):
        """
        Set the reference frame.

        Arguments:
        ref_id: Id of the reference frame. Id is the same as in project file and key in frames dict
        """

        try:
            self.frames[self.ref_id].isref = False
            self.ref_id = ref_id
            self.frames[self.ref_id].isref = True
            self.project.set("Reference", self.ftype, str(self.ref_id))
        except KeyError:
            raise

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker = Stacking type object
        """

        # Create new empty frame for the result
        self.master = Frame(self.project, ftype=self.ftype, number="master")

        # Call stacker
        data = stacker.stack(self.frames, self.project)

        self.master.data = data
        # Save file
        self.master.write(tiff=True)

        # Metadata and printouts
        self.project.addfile(self.master.path()[0], final=True)
        dim, self.master.x, self.master.y = self.master.data.shape
        print("Dimensions : " + str(self.master.x) + " x " + str(self.master.y))
        totalexposure = 0.0
        for i in self.frames:
            try:
                totalexposure += float(self.frames[i].shutter.split()[0])
            except ValueError:
                totalexposure = None
                break

        self.master.totalexposure = totalexposure
        self.master.writeinfo()
        self.project.set("Masters", self.ftype, self.master.infopath)
        print("Result image saved to " + self.master.path()[0])
        print("                  and " + self.master.path(fformat="tiff"))

    def stack_new(self):
        """
        Stack images using stackertool
        """

        # Create new empty frame for the result
        self.master = Frame(self.project, ftype=self.ftype, number="master")

        # Call stacker
        data = self.stackingtool.stack(self.frames, self.project)

        self.master.data = data
        # Save file
        self.master.write(tiff=True)

        # Metadata and printouts
        self.project.addfile(self.master.path()[0], final=True)
        dim, self.master.x, self.master.y = self.master.data.shape
        print("Dimensions : " + str(self.master.x) + " x " + str(self.master.y))
        totalexposure = 0.0
        for i in self.frames:
            try:
                totalexposure += float(self.frames[i].shutter.split()[0])
            except ValueError:
                totalexposure = None
                break

        self.master.totalexposure = totalexposure
        self.master.writeinfo()
        self.project.set("Masters", self.ftype, self.master.infopath)
        print("Result image saved to " + self.master.path()[0])
        print("                  and " + self.master.path(fformat="tiff"))

    def subtract(self, calib, stacker):
        """
        Subtract calib from images in imagelist
        """

        calibinfo = self.project.get("Masters", calib)
        cframe = Frame(self.project, infopath=calibinfo, ftype=calib, number="master")

        for i in self.frames:
            print("Subtracting " + calib + " from image " + str(self.frames[i].number))
            self.frames[i].data = stacker.subtract(self.frames[i].data, cframe.data)

            if self.frames[i].fphase not in ("bias", "dark", "flat"):
                self.frames[i].fphase = "calib"
            self.frames[i].write()
            self.project.addfile(self.frames[i].path())

        print("Calibrated images saved with generic name 'calib'.")

    def divide(self, calib, stacker):
        """
        Divide images in imagelist with calib
        """

        calibinfo = self.project.get("Masters", calib)
        cframe = Frame(self.project, infopath=calibinfo, ftype=calib, number="master")

        for i in self.frames:
            print("Dividing image " + str(self.frames[i].number) + " with " + calib)
            self.frames[i].data = stacker.divide(self.frames[i].data, cframe.data)
            if self.frames[i].fphase not in ("bias", "dark", "flat"):
                self.frames[i].fphase = "calib"
            self.frames[i].write()
            self.project.addfile(self.frames[i].path())

        print("Calibrated images saved with generic name 'calib'.")

    def setbiaslevel(self, level):
        """
        Set bias level to the batch.

        Bias level can be set to Frames individually, if fore some reason that is required.

        :param level: Float or None expected
        :return: Nothing
        """

        try:
            biaslevel = float(level)
        except ValueError:
            raise

        for i in self.frames:
            self.frames[i].biaslevel = biaslevel

    def directory(self, path, ftype):
        """
        Add directory to Batch

        Arguments:
        path - Unix path where the photos are (Must end in "/")
        type - Type of photo frames (light, dark, bias, flat)
        """

        allfiles = listdir(path)
        rawfiles = []

        for i in allfiles:
            if Frame.identify(path + i) in ("tiff", "fits", "raw"):
                rawfiles.append(path + i)

        if not rawfiles:
            print("Found files :")
            for i in rawfiles:
                print(i)
        else:
            print("No supported RAW files found. All files found are listed here: " + str(allfiles))
            return

        self.addfiles(rawfiles, ftype)

        # Set reference frame key if not set already. Defaults to the first frame added.
        try:
            self.project.get("Reference", ftype)
        except KeyError:
            self.project.set("Reference", ftype, list(self.frames.keys())[0])

    def addfiles(self, allfiles, ftype):
        """
        Add list of files to Batch
        """

        for i in allfiles:
            self.addfile(i, ftype)

    def addfile(self, file, ftype):
        """
        Add a single file.
        """

        # If .info file given, give only that as an argument. Uses only information from this file and returns
        if splitext(file)[1] == ".info":
            frame = Frame(self.project, infopath=file)
            self.frames[str(frame.number)] = frame
            return

        # If file already in the project, ignore it and return
        for i in self.frames:
            if file == self.frames[i].rawpath:
                print("Trying to add a file that's already in the project. Ignoring.")
                return

        n = self.nextkey()

        # Other than .info files
        frame = Frame(self.project, rawpath=file, ftype=ftype, fphase=self.fphase, number=n)

        # Try to prepare the file. Do not add if preparing fails. This means file's not valid
        try:
            frame.prepare()
        except RuntimeError as error:
            print(error.args[0])
            print(error.args[1])
            print("File " + file + " not added!")
            return
        frame.decode()

        self.project.set(ftype, str(n), frame.infopath)

        self.frames[n] = frame
        if len(self.frames) == 1:
            self.set_ref(n)

    def addmaster(self, file, ftype):
        """
        Add a ready master to batch
        """

        self.master = Frame.createmaster(self.project, file, ftype)
        self.project.set("Masters", ftype, self.master.infopath)

    def add_master_for_calib(self, master):
        """
        Add master frame for calibration
        """

        if master.ftype == "bias":
            self.masterbias = master
        elif master.ftype == "dark":
            self.masterdark = master
        elif master.ftype == "flat":
            self.masterflat = master
        
    def nextkey(self):
        """
        Return next free key for frame in dict

        This is required because if a frame is removed, total number of
        frames will be less than the highest key. Also the keys are string
        representations of numbers for compatibility reasons, so this
        won't be a oneliner.
        """

        keys = list(self.frames.keys())
        if not keys:
            return "0"
        for i in range(len(keys)):
            keys[i] = int(keys[i])

        return str(max(keys) + 1)

    def remove_frame(self, frame_id):
        """
        Remove frame by id from the project.
        """

        self.project.remove(self.ftype, frame_id)
        del self.frames[frame_id]

        # If reference frame is removed, choose a new one.
        if frame_id == self.ref_id:
            self.set_ref(list(self.frames.keys())[0])
            print("Reference frame " + frame_id + " removed. New reference frame is " + self.ref_id + ".")

    # @profile
    def debayer_old(self, debayertool):
        """
        Debayer all frames
        """

        for frame in sorted(self.frames):

            print("Processing image " + self.frames[frame].path())
            self.frames[frame].debayertool = debayertool
            self.frames[frame].debayer()
            print("...Done")

        self.frames[self.ref_id].isref = True
        print("Debayered images saved with generic name 'rgb'.")

    def debayer_threaded(self):
        """
        Debayer images using threads

        Arguments:
        stacker = Stacking type object
        """
        threadlist = []

        for i in sorted(self.frames):
            print("Debayering threadlist lenght: " + str(len(threadlist)))
            t = threading.Thread(target=self.frames[i].debayer_worker)
            threadlist.append(t)
            t.start()

        for t in threadlist:
            t.join()

    def debayer(self):
        """
        Wrapper to choose between threaded and non-threaded.
        Non-threaded will be removed and so will this when it's done.
        """
        self.debayer_threaded()

    def register_old(self, register):
        """
        Register all frames
        """

        self.frames[self.ref_id].register(register)

        for frame in self.frames:
            if frame != self.ref_id:
                self.frames[frame].register(register)
 
    def register_threaded(self):
        """
        Register all frames using threads
        """
        threadlist = []
        print(self.ref_id)
        print(self.frames[self.ref_id].isref)
        self.frames[self.ref_id].register_worker()

        for i in sorted(self.frames):
            if i == self.ref_id:
                continue
            t = threading.Thread(target=self.frames[i].register_worker)
            threadlist.append(t)
            t.start()

        for t in threadlist:
            t.join()
    
    def register(self):
        """
        Wrapper to choose from threded and non-threaded registers

        Remove when threading works and done
        """
        self.register_threaded()

    def calibrate_threaded(self, bias=None, dark=None, flat=None):
        """
        Calibrate all frames in batch

        Calibrating includes bias, dark and flat frame calculations and stacking
        the master frame, except for light frames
        """

        threadlist = []

        for i in sorted(self.frames):
            print("Calibrating threadlist lenght: " + str(len(threadlist)))
            self.frames[i].stackingtool = self.stackingtool
            t = threading.Thread(target=self.frames[i].calibrate_worker,
                                 args=(bias, dark, flat))
            threadlist.append(t)
            t.start()

        for t in threadlist:
            t.join()
        if self.ftype != "light":
            self.stack_new()

    def calibrate(self, bias=None, dark=None, flat=None):
        """
        This exists for debugging. Remove and change calibrate_threaded
        to calibrate when threading works
        """
        self.calibrate_threaded(bias, dark, flat)

    # PROPERTIES

    def setstackingtool(self, stackingtool):
        try:
            self._stackingtool = stackingtool
            for i in self.frames:
                self.frames[i].stackingtool = self.stackingtool 
        except Exception as err:
            print(err)

    def getstackingtool(self):
        return self._stackingtool

    stackingtool = property(fget=getstackingtool, fset=setstackingtool)

    def setdebayertool(self, debayertool):
        try:
            self._debayertool = debayertool
            for i in self.frames:
                self.frames[i].debayertool = self.debayertool              
        except Exception as err:
            print(err)

    def getdebayertool(self):
        return self._debayertool

    debayertool = property(fget=getdebayertool, fset=setdebayertool)

    def setregistertool(self, registertool):
        try:
            self._registertool = registertool
            for i in self.frames:
                self.frames[i].registertool = self.registertool              
        except Exception as err:
            print(err)

    def getregistertool(self):
        return self._registertool

    registertool = property(fget=getregistertool, fset=setregistertool)