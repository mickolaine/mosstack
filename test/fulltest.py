"""
Full process tester
"""

from mosstack import Config, Debayer, Registering, Stacker, Batch
from subprocess import call
#from memory_profiler import profile

# Start by cleaning up old mess
call(["rm -v /media/data/astrostack/Autotest*"], shell=True)

#@profile
def test():
    setup = Config.Setup()

    # Setting algorithms
    debayerwrap = Debayer.VNGCython
    matcher = Registering.Groth
    transformer = Registering.SkTransform
    stackerwrap = Stacker.SigmaMedian

    #
    # Configuring the project
    #

    wdir = Config.Global.get("Default", "Path")
    project = Config.Project()
    project_name = "Autotest"
    project.initproject(project_name)
    Config.Global.set("Default", "Project", project_name)
    Config.Global.set("Default", "Project file", project.projectfile)

    #
    # Adding frames
    #

    batch = {}

    batch["light"] = Batch.Batch(project, "light")
    batch["bias"] = Batch.Batch(project, "bias")
    batch["flat"] = Batch.Batch(project, "flat")
    batch["dark"] = Batch.Batch(project, "dark")

    light = {
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.08.18.010282.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.09.27.999435.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.10.39.472035.cr2",
    }
    """
    "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.11.49.951803.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.12.59.907589.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.14.10.531233.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.15.20.487290.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.16.30.560132.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.17.41.603583.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.18.51.467650.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.20.01.527596.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.21.11.199286.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.22.21.375323.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.23.31.415492.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.24.41.543546.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.25.51.611742.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.27.01.603322.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.28.11.475449.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.29.22.391676.cr2",
        "/media/Dee/Astrokuvat/2015-02-10/OrionNebula/OrionNebula_2015-02-10_20.30.33.771566.cr2"
    }
    """
    bias = {
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3321.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3323.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3325.CR2", }
    """
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3327.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3329.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3322.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3324.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3326.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3328.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Bias/IMG_3330.CR2"
    }
    """
    flat = {
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3331.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3333.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3335.CR2", }
    """
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3337.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3339.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3332.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3334.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3336.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3338.CR2",
        "/media/Dee/Astrokuvat/2015-02-10/Flat/IMG_3340.CR2"
    }
    """

    for i in light:
        batch["light"].addfile(i, "light")
    for i in bias:
        batch["bias"].addfile(i, "bias")
    for i in flat:
        batch["flat"].addfile(i, "flat")

    #for i in batch["light"].frames:
    #    batch["bias"].stack(stackerwrap())
    #    batch["flat"].subtract("bias", stackerwrap())
    #    batch["flat"].stack(stackerwrap())
    #    batch["light"].frames[i].calibrate(stackerwrap(), bias=batch["bias"].master, flat=batch["flat"].master)


    batch["light"].debayer(debayerwrap)

    matcher = matcher()
    matcher.tform = transformer
    batch["light"].register(matcher)

    batch["light"].stack(stackerwrap())

test()
