from . Photo import Frame
from os import listdir
import datetime   # For profiling
from os.path import splitext


class Batch(object):
    """
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    """

    extensions = (".CR2", ".cr2", ".NEF", ".nef")   # TODO: Add here all supported extensions,
                                                    # and move this to a better place
                                                    # TODO: Better idea: Have dcraw check if it can read the files

    def __init__(self, project, genname):
        """
        Constructor loads Frames according to arguments.

        Arguments:
        project = Configuration object for the project
        genname = Generic name of the files
        """

        self.project = project
        self.genname = genname

        self.name    = self.project.get("Default", key="project name")    # Name for the resulting image

        self.list    = {}                                                 # Empty dict for Photos

        if genname in ("flat", "dark", "bias"):
            self.category = genname
        else:
            self.category = "light"

        try:
            self.refnum  = int(project.get("Reference images", key=self.genname))  # Number of reference frame
        except KeyError:
            self.refnum = "1"

        try:
            files = self.project.get(self.category)                       # Paths for the frame info files
            for key in files:
                self.list[key] = Frame(self.project, self.genname, infopath=files[key], number=key)
        except KeyError:
            pass

    def debayer(self, debayer):
        """
        Debayer CFA-image into RGB.

        Arguments
        debayer: a Debayer-type object
        """

        for i in self.list:
            print("Processing image " + self.list[i].path)
            t1 = datetime.datetime.now()
            self.list[i].data = debayer.debayer(self.list[i].data[0])
            t2 = datetime.datetime.now()
            print("...Done")
            print("Debayering took " + str(t2 - t1) + " seconds.")
            self.list[i].genname = "rgb"
            self.list[i].write()
        self.project.set("Reference images", self.genname, str(self.refnum))
        print("Debayered images saved with generic name 'rgb'.")

    def register(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.list, self.project)
        self.project.set("Reference images", self.genname, str(self.refnum))
        print("Registered images saved with generic name 'reg'.")

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker = Stacking type object
        """

        new = Frame(self.project, self.genname, number="master")
        new.data = stacker.stack(self.list, self.project)
        new.write(tiff=True)
        print("Result image saved to " + new.path)
        print("                  and " + splitext(new.path)[0] + ".tiff")

    def subtract(self, calib, stacker):
        """
        Subtract calib from images in imagelist
        """

        cframe = Frame(self.project, calib, number="master")

        for i in self.list:
            print("Subtracting " + calib + " from image " + str(self.list[i].number))
            self.list[i].data = stacker.subtract(self.list[i], cframe)
            if self.list[i].genname not in ("bias", "dark", "flat"):
                self.list[i].genname = "calib"
            self.list[i].write()
        self.project.set("Reference images", "calib", str(self.refnum))
        print("Calibrated images saved with generic name 'calib'.")

    def divide(self, calib, stacker):
        """
        Divide images in imagelist with calib
        """

        cframe = Frame(self.project, calib, number="master")

        for i in self.list:
            print("Dividing image " + str(self.list[i].number) + " with " + calib)
            self.list[i].data = stacker.divide(self.list[i], cframe)
            if self.list[i].genname not in ("bias", "dark", "flat"):
                self.list[i].genname = "calib"
            self.list[i].write()
        self.project.set("Reference images", "calib", str(self.refnum))
        print("Calibrated images saved with generic name 'calib'.")

    def directory(self, path, itype):
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

        n = len(self.list)

        for i in rawfiles:
            frame = Frame(self.project, self.genname, number=n)
            frame.fromraw(i)
            self.project.set(itype, str(n), frame.infopath)
            n += 1

        self.project.set("Reference images", itype, "1")

    def addfiles(self, allfiles, itype):
        """
        Add list of files to Batch
        """

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

        n = len(self.list)

        for i in rawfiles:
            frame = Frame(self.project, self.genname, number=n)
            frame.fromraw(i)
            self.project.set(itype, str(n), frame.infopath)
            self.list[n] = Frame(self.project, itype, infopath=frame.infopath, number=n)
            n += 1

        self.project.set("Reference images", itype, "1")

    def addfile(self, file, itype):
        """
        Add a single file. Internal use only
        """

        if splitext(file)[1] not in self.extensions:
            return

        try:
            n = len(self.project.get(itype).keys())
        except KeyError:
            n = 0

        frame = Frame(self.project, self.genname, number=n)
        frame.fromraw(file)
        self.project.set(itype, str(n), frame.infopath)

        self.list[str(n)] = Frame(self.project, itype, infopath=frame.infopath, number=str(n))

        self.project.set("Reference images", itype, "1")