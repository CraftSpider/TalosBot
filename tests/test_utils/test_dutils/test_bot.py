

def test_extension_load(testlos):

    assert len(testlos.extensions) == len(testlos.startup_extensions), "Didn't load all extensions"
    for extension in testlos.startup_extensions:
        assert testlos.extension_dir + "." + extension in testlos.extensions,\
            "Didn't load {} extension".format(extension)

    testlos.unload_extensions(["Commands", "AdminCommands", "DubDub"])

    testlos.unload_extensions()
    assert len(testlos.extensions) == 0, "Didn't unload all extensions"
    for extension in testlos.startup_extensions:
        assert testlos.extension_dir + "." + extension not in testlos.extensions,\
            "Didn't unload {} extension".format(extension)
