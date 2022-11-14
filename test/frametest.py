"""
Unit tests for frame.py
"""

from subprocess import call
import unittest
from mosstack.frame import Frame
from mosstack import config


class FrameTest(unittest.TestCase):
    """
    Test everything in frame.py that is possible to test.
    """

    def initialize_tests(self):
        """
        Do everything required for running the tests:
         - Define datafiles
         - Create project
        """

        try:
            call(["rm -v ./temp/Frame_tests*"], shell=True)
        except RuntimeError:
            print("No old test runs found")

        self.setup = config.Setup()
        self.wdir = config.Global.get("Default", "Path")
        self.project = config.Project()
        self.project_name = "Frame_tests"
        self.project.initproject(self.project_name)
        config.Global.set("Default", "Project", self.project_name)
        config.Global.set("Default", "Project file", self.project.projectfile)

        self.datapath = "/mnt/Astrokuvat/"
        self.lightframes = [
            self.datapath + "2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.08.18.010282.cr2",
            self.datapath + "2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.09.27.999435.cr2",
            self.datapath + "2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.10.39.472035.cr2"
        ]
        self.biasframes = [
            self.datapath + "2015-02-10/Bias/IMG_3321.CR2",
            self.datapath + "2015-02-10/Bias/IMG_3323.CR2",
            self.datapath + "2015-02-10/Bias/IMG_3325.CR2"
        ]
        self.flatframes = [
            self.datapath + "2015-02-10/Flat/IMG_3331.CR2",
            self.datapath + "2015-02-10/Flat/IMG_3333.CR2",
            self.datapath + "2015-02-10/Flat/IMG_3335.CR2"
        ]
        self.infofile = self.datapath + "Frame_tests_light_None.info"

    def test_empty(self):
        """
        Test initializing frame in all different ways
        """
        self.initialize_tests()
        frame_empty = Frame(self.project)
        self.assertEqual(frame_empty.workdir, config.Global.get("Default", "Path"))

    def test_frame_light(self):
        """
        Test adding light frame
        """
        self.initialize_tests()
        frame_light = Frame.from_raw(self.project,
                                     self.lightframes[0],
                                     "light")
        self.assertEqual(frame_light.raw_format, "raw")
        frame_light.prepare()
        self.assertEqual(frame_light.state["prepare"], 1)

    def test_info_file_raw(self):
        """
        Test adding info file of an existing frame, phase raw
        """
        self.initialize_tests()

        frame_light = Frame.from_info(self.project,
                                      self.infofile,
                                      "light")
        self.assertEqual(frame_light.raw_format, "raw")
        frame_light.prepare()
        self.assertEqual(frame_light.state["prepare"], 1)

    def test_info_file_decoded(self):
        return

    def test_info_file_calib(self):
        return
    
    def test_info_file_rgb(self):
        return

    def test_info_file_master(self):
        return

if __name__ == '__main__':
    unittest.main()
