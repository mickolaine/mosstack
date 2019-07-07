"""
Full process unit test
"""

from subprocess import call
import unittest
from mosstack import config, Debayer, Registering, Stacker
from mosstack.batch import Batch

# Start by cleaning up old mess
try:
    call(["rm -v ./temp/Autotest*"], shell=True)
except RuntimeError:
    print("No old test runs found")

class FullProcess(unittest.TestCase):
    """
    Test the full process of program

    - Adding files
    - Calibrating
    - Debayering
    - Registering
    - Stacking
    """

    def test_init(self):
        """
        Initialize full process unit tests
        """

        self.setup = config.Setup()
        self.wdir = config.Global.get("Default", "Path")
        self.project = config.Project()
        self.project_name = "Autotest"
        self.project.initproject(self.project_name)
        config.Global.set("Default", "Project", self.project_name)
        config.Global.set("Default", "Project file", self.project.projectfile)

        self.datapath = "./data/"

        self.batch = {}

        self.add_frames()
        self.set_algorithms()
        self.calibrate()
        self.register()
        self.stack()

    def add_frames(self):
        """
        Add all the frames
        """

        self.batch["light"] = Batch(self.project, "light")
        self.batch["bias"] = Batch(self.project, "bias")
        self.batch["flat"] = Batch(self.project, "flat")
        self.batch["dark"] = Batch(self.project, "dark")

        light = {
            self.datapath + "/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.08.18.010282.cr2",
            self.datapath + "/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.09.27.999435.cr2",
            self.datapath + "/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.10.39.472035.cr2",
        }

        bias = {
            self.datapath + "/2015-02-10/Bias/IMG_3321.CR2",
            self.datapath + "/2015-02-10/Bias/IMG_3323.CR2",
            self.datapath + "/2015-02-10/Bias/IMG_3325.CR2", }

        flat = {
            self.datapath + "/2015-02-10/Flat/IMG_3331.CR2",
            self.datapath + "/2015-02-10/Flat/IMG_3333.CR2",
            self.datapath + "/2015-02-10/Flat/IMG_3335.CR2", }

        for i in light:
            print("Adding file " + i)
            self.batch["light"].addfile(i, "light")
        for i in bias:
            self.batch["bias"].addfile(i, "bias")
        for i in flat:
            self.batch["flat"].addfile(i, "flat")

    def set_algorithms(self):
        """
        Set the algorithms. Method tests if all the algorithms can be
        initialized and if setting the tools propagates to batches and frames
        """
        # Setting algorithms
        self.debayertool = Debayer.VNGC()
        self.registertool = Registering.Groth()
        self.transformer = Registering.SkTransform
        self.registertool.tform = self.transformer
        self.stackingtool = Stacker.SigmaMedian()

        for i in self.batch:
            self.batch[i].stackingtool = self.stackingtool
            self.batch[i].debayertool = self.debayertool
            self.batch[i].registertool = self.registertool

        self.assertEqual(self.batch["light"].framearray["0"].debayertool, self.debayertool)
        self.assertEqual(self.batch["light"].framearray["0"].registertool, self.registertool)
        self.assertEqual(self.batch["light"].framearray["0"].registertool.tform, self.transformer)
        self.assertEqual(self.batch["light"].framearray["0"].stackingtool, self.stackingtool)
        self.assertEqual(self.batch["bias"].framearray["0"].stackingtool, self.stackingtool)

    def calibrate(self):
        """
        Calibrate frames
        """

        self.batch["bias"].calibrate()
        self.assertTrue(self.batch["bias"].master)

        self.batch["flat"].add_master_for_calib(self.batch["bias"].master)
        self.assertIsNotNone(self.batch["flat"].masterbias)
        self.batch["flat"].calibrate()
        self.assertIsNotNone(self.batch["flat"].master)

        self.batch["light"].add_master_for_calib(self.batch["bias"].master)
        self.batch["light"].add_master_for_calib(self.batch["flat"].master)
        self.assertIsNotNone(self.batch["light"].masterbias)
        self.assertIsNotNone(self.batch["light"].masterflat)
        self.batch["light"].calibrate()
        self.assertEqual(self.batch["light"].framearray["0"].state["calibrate"], 2)

    def register(self):
        """
        Register frames
        """
        self.batch["light"].register()

    def stack(self):
        """
        Stack the frames
        """
        self.batch["light"].stack_new()

if __name__ == '__main__':
    unittest.main()
