from . Frame import Frame
from os import listdir
import datetime   # For profiling
from os.path import splitext


class Batch(object):
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
        self.master = None

        self.name = self.project.get("Default", key="project name")    # Name for the resulting image

        self.frames = {}                                               # Empty dict for Photos

        if ftype is not None:
            self.ftype = ftype

        if fphase is not None:
            self.fphase = fphase

        try:
            self.refId = project.get("Reference", key=self.ftype)  # Number of reference frame
        except KeyError:

            self.refId = "1"

        try:
            files = self.project.get(self.ftype)                       # Paths for the frame info files

            for key in files:
                frame = Frame(self.project, infopath=files[key], fphase=self.fphase)
                self.frames[key] = frame
            self.setRef(self.refId)

        except KeyError:
            #print("Error")
            pass

    def setRef(self, refId):
        """
        Set the reference frame.

        Arguments:
        refId: Id of the reference frame. Id is the same as in project file and key in frames dict
        """

        try:
            self.frames[self.refId].isref = False
            self.refId = refId
            self.frames[self.refId].isref = True
            self.project.set("Reference", self.ftype, str(self.refId))
        except KeyError:
            raise

    def debayerAll(self, debayer):
        """
        Debayer CFA-images into RGB.

        Arguments
        debayer: a Debayer-type object
        """

        for i in self.frames:
            print("Processing image " + self.frames[i].path())
            t1 = datetime.datetime.now()
            self.frames[i].data = debayer.debayer(self.frames[i].data[0])
            t2 = datetime.datetime.now()
            print("...Done")
            print("Debayering took " + str(t2 - t1) + " seconds.")
            self.frames[i].fphase = "rgb"
            self.frames[i].write()

        print("Debayered images saved with generic name 'rgb'.")

    '''
    def registerAll(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.frames, self.project)

        print("Registered images saved with generic name 'reg'.")
    '''

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker = Stacking type object
        """

        # Create new empty frame for the result
        self.master = Frame(self.project, ftype=self.ftype, number="master")
        self.master.data = stacker.stack(self.frames, self.project)
        self.master.write(tiff=True)
        dim, self.master.x, self.master.y = self.master.data.shape
        self.master.writeinfo()
        self.project.set("Masters", self.ftype, self.master.infopath)
        print("Result image saved to " + self.master.path())
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

        print("Calibrated images saved with generic name 'calib'.")

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
            if splitext(i)[1] in (".cr2", ".CR2", ".nef", ".NEF"):
                rawfiles.append(path + i)

        if len(rawfiles) != 0:
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

    def addmaster(self, file, ftype):
        """
        Add a ready master to batch
        """

        frame = Frame.createmaster(self.project, file, ftype)

        self.project.set("Masters", ftype, frame.infopath)

    def nextkey(self):
        """
        Return next free key for frame in dict

        This is required because if a frame is removed, total number of frames will be less than the highest key. Also
        the keys are string representations of numbers for compatibility reasons, so this won't be a oneliner.
        """

        keys = list(self.frames.keys())
        if len(keys) == 0:
            return "0"
        for i in range(len(keys)):
            keys[i] = int(keys[i])

        return str(max(keys) + 1)

    def removeFrame(self, frameId):
        """
        Remove frame by id from the project.
        """

        self.project.remove(self.ftype, frameId)
        del self.frames[frameId]

        # If reference frame is removed, choose a new one.
        if frameId == self.refId:
            self.setRef(list(self.frames.keys())[0])
            print("Reference frame " + frameId + " removed. New reference frame is " + self.refId + ".")
