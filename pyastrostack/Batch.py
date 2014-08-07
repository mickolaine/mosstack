from . Frame import Frame
from os import listdir
import datetime   # For profiling
from os.path import splitext


class Batch(object):
    """
    Batch holds a list of frames and handles connections to project files
    """

    extensions = (".CR2", ".cr2", ".NEF", ".nef")   # TODO: Add here all supported extensions,
                                                    # and move this to a better place
                                                    # TODO: Better idea: Have dcraw check if it can read the files

    def __init__(self, project, ftype="light", fphase="orig"):
        """
        Constructor loads Frames according to arguments.

        Arguments:
        project = Configuration object for the project
        fphase = Generic name of the files
        """

        self.project = project
        self.fphase = fphase

        self.name    = self.project.get("Default", key="project name")    # Name for the resulting image

        self.frames  = {}                                                 # Empty dict for Photos

        if ftype is not None:
            self.ftype = ftype

        if fphase is not None:
            self.fphase = fphase

        try:
            self.refnum  = int(project.get("Reference images", key=self.ftype))  # Number of reference frame
        except KeyError:
            self.refnum = "1"

        try:
            files = self.project.get(self.ftype)                       # Paths for the frame info files

            for key in files:
                frame = Frame(self.project, infopath=files[key], fphase=self.fphase)
                self.frames[key] = frame

        except KeyError:
            #print("Error")
            pass

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
        self.project.set("Reference images", self.fphase, str(self.refnum))
        print("Debayered images saved with generic name 'rgb'.")

    def registerAll(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.frames, self.project)
        self.project.set("Reference images", self.fphase, str(self.refnum))
        print("Registered images saved with generic name 'reg'.")

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker = Stacking type object
        """

        # Create new empty frame for the result
        new = Frame(self.project, ftype=self.ftype, number="master")
        new.data = stacker.stack(self.frames, self.project)
        new.write(tiff=True)
        dim, new.x, new.y = new.data.shape
        new.writeinfo()
        self.project.set("Masters", self.ftype, new.infopath)
        print("Result image saved to " + new.path())
        print("                  and " + splitext(new.path())[0] + ".tiff")

    def subtract(self, calib, stacker):
        """
        Subtract calib from images in imagelist
        """

        cframe = Frame(self.project, ftype=calib, number="master")

        for i in self.frames:
            print("Subtracting " + calib + " from image " + str(self.frames[i].number))
            self.frames[i].data = stacker.subtract(self.frames[i].data, cframe.data)

            if self.frames[i].fphase not in ("bias", "dark", "flat"):
                self.frames[i].fphase = "calib"
            self.frames[i].write()

        self.project.set("Reference images", "calib", str(self.refnum))
        print("Calibrated images saved with generic name 'calib'.")

    def divide(self, calib, stacker):
        """
        Divide images in imagelist with calib
        """

        cframe = Frame(self.project, ftype=calib, number="master")

        for i in self.frames:
            print("Dividing image " + str(self.frames[i].number) + " with " + calib)
            self.frames[i].data = stacker.divide(self.frames[i].data, cframe.data)
            if self.frames[i].fphase not in ("bias", "dark", "flat"):
                self.frames[i].fphase = "calib"
            self.frames[i].write()
        self.project.set("Reference images", "calib", str(self.refnum))
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
            if splitext(i)[1] in self.extensions:
                rawfiles.append(path + i)

        if len(rawfiles) != 0:
            print("Found files :")
            for i in rawfiles:
                print(i)
        else:
            print("No supported RAW files found. All files found are listed here: " + str(allfiles))
            return

        n = len(self.frames)

        self.addfiles(rawfiles, ftype)

        self.project.set("Reference images", ftype, "1")
        self.frames["1"].isref = True

    def addfiles(self, allfiles, ftype):
        """
        Add list of files to Batch
        """

        try:
            n = len(self.project.get(ftype).keys())
        except KeyError:
            n = 0

        for i in allfiles:
            self.addfile(i, ftype, n)
            n += 1

        '''
        if splitext(allfiles[0])[1] == ".info":
            pass

        rawfiles = []
        for i in allfiles:
            if splitext(i)[1] in self.extensions:
                rawfiles.append(i)

        if len(rawfiles) != 0:
            print("Found files :")
            for i in rawfiles:
                print(i)
        else:
            print("No supported RAW files found. All files found are listed here: " + str(allfiles))
            return

        n = len(self.frames)

        for i in rawfiles:
            frame = Frame(self.project, self.fphase, number=n)
            frame.fromraw(i)
            self.project.set(ftype, str(n), frame.infopath)
            self.frames[n] = Frame(self.project, ftype, infopath=frame.infopath, number=n)
            n += 1

        self.project.set("Reference images", ftype, "1")
        '''

    def addfile(self, file, ftype, number):
        """
        Add a single file.
        """

        # If .info file given, give only that as an argument. Uses only information from this file and returns
        if splitext(file)[1] == ".info":
            frame = Frame(self.project, infopath=file)
            self.frames[frame.number] = frame
            return

        # Check how many frames there are already in the batch. Needed for new index key for frames dict
        try:
            n = len(self.project.get(ftype).keys())
        except KeyError:
            n = 0

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

        self.frames[str(n)] = frame

        self.project.set("Reference images", ftype, "1")
        self.frames["1"].isref = True