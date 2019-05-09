"""
Full process unit test
"""

from subprocess import call
import unittest
from mosstack import config, Debayer, Registering, Stacker
from mosstack.batch import Batch

# Start by cleaning up old mess
call(["rm -v /media/data/astrostack/Autotest*"], shell=True)

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

        self.batch = {}

        self.add_frames()
        self.set_algorithms()
        self.calibrate()

    def add_frames(self):
        """
        Add all the frames
        """

        self.batch["light"] = Batch(self.project, "light")
        self.batch["bias"] = Batch(self.project, "bias")
        self.batch["flat"] = Batch(self.project, "flat")
        self.batch["dark"] = Batch(self.project, "dark")

        light = {
            "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.08.18.010282.cr2",
            "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.09.27.999435.cr2",
            "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.10.39.472035.cr2",
        }

        bias = {
            "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3321.CR2",
            "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3323.CR2",
            "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3325.CR2", }

        flat = {
            "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3331.CR2",
            "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3333.CR2",
            "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3335.CR2", }

        for i in light:
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
        self.stackingtool = Stacker.SigmaMedian()

        for i in self.batch:
            self.batch[i].stackingtool = self.stackingtool
            self.batch[i].debayertool = self.debayertool
            self.batch[i].registertool = self.registertool

        self.assertEqual(self.batch["light"].frames["0"].debayertool, self.debayertool)
        self.assertEqual(self.batch["light"].frames["0"].registertool, self.registertool)
        self.assertEqual(self.batch["light"].frames["0"].stackingtool, self.stackingtool)
        self.assertEqual(self.batch["bias"].frames["0"].stackingtool, self.stackingtool)

    def calibrate(self):
        """
        Calibrate frames
        """

        self.batch["bias"].calibrate()
        self.assertTrue(self.batch["bias"].master)

        #self.batch["dark"].calibrate(bias=self.batch["bias"].master)
        #self.assertTrue(self.batch["dark"].master)

        self.batch["flat"].calibrate(bias=self.batch["bias"].master)
        self.assertTrue(self.batch["flat"].master)

        self.batch["light"].calibrate(bias=self.batch["bias"].master, flat=self.batch["flat"].master)
        self.assertEqual(self.batch["light"].frames[0].state["calibrate"], 2)



"""
    def test(self):

        for i in batch["light"].frames:
            batch["bias"].stack(stackerwrap())
        #    batch["flat"].subtract("bias", stackerwrap())
        #    batch["flat"].stack(stackerwrap())
        #    batch["light"].frames[i].calibrate(stackerwrap(), bias=batch["bias"].master, flat=batch["flat"].master)

        batch["light"].debayertool = debayerwrap()

        batch["light"].frames[batch["light"].refId].isref = True

        matcher = matcher()
        matcher.tform = transformer
        batch["light"].registertool = matcher
        batch["light"].register()
        batch["light"].stackingtool = stackerwrap()
        batch["light"].stack(stackerwrap())
"""
if __name__ == '__main__':
    unittest.main()
