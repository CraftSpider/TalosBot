
import pathlib
import inspect
import tests.reflection as reflection


def test_discord_docs():
    result = reflection.get_undoced("discord_talos")
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


def test_util_docs():
    result = reflection.get_undoced("utils")
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


def test_website_docs():
    result = reflection.get_undoced("website")
    assert len(result) is 0, f"Missing documentation on: {', '.join(map(lambda x: x[0], result))}"


SKIP_DIRS = {"stub_files", "__pycache__", "tests"}


def test_stub_files():
    missing = []

    for code, stub in reflection.walk_with_stub_files(".", skip_dirs=SKIP_DIRS):
        if not stub.exists() or not stub.is_file():
            missing.append(code)

    assert len(missing) == 0, f"Missing stub files for files: {', '.join(map(lambda x: x.name, missing))}"


def _format_missing(func):
    return f"{func.__name__} in {inspect.getfile(func)}"


def _format_wrong(args):
    return f"{args[0]}: Real {'async' if args[1] else 'sync'}, Stub {'async' if args[2] else 'sync'}"


def _file_matches(obj, mod):
    modpath = pathlib.Path(mod.__file__).absolute()
    objpath = pathlib.Path(inspect.getfile(obj)).absolute()
    return objpath.parts == modpath.parts


def test_stub_funcs():
    missing = []
    wrong_type = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        for name, func in inspect.getmembers(code,
                                             predicate=lambda x: inspect.isroutine(x) and _file_matches(x, code)):
            sfunc = getattr(stub, name, None)
            if sfunc is None:
                missing.append(func)
                continue
            casync = inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func)
            sasync = inspect.iscoroutinefunction(sfunc)
            if casync != sasync:
                wrong_type.append((func.__name__, casync, sasync))

    assert len(missing) == 0, f"Missing stubs for functions: {', '.join(map(_format_missing, missing))}"
    assert len(wrong_type) == 0, f"Type mismatch for functions: {', '.join(map(_format_wrong, wrong_type))}"


def test_stub_funcs_extra():
    extra = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        for name, func in inspect.getmembers(stub,
                                             predicate=lambda x: inspect.isroutine(x) and _file_matches(x, stub)):
            cfunc = getattr(code, name, None)
            if cfunc is None:
                extra.append(func)

    assert len(extra) == 0, f"Extra stubs for functions: {', '.join(map(_format_missing, extra))}"


def test_stub_classes():
    missing = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        for name, cls in inspect.getmembers(code, predicate=lambda x: inspect.isclass(x) and _file_matches(x, code)):
            scls = getattr(stub, name, None)
            if scls is None:
                missing.append(cls)

    assert len(missing) == 0, f"Missing stubs for classes: {', '.join(map(_format_missing, missing))}"


def test_stub_classes_extra():
    extra = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        for name, cls in inspect.getmembers(stub, predicate=lambda x: inspect.isclass(x) and _file_matches(x, stub)):
            ccls = getattr(code, name, None)
            if ccls is None:
                extra.append(cls)

    assert len(extra) == 0, f"Extra stubs for classes: {', '.join(map(_format_missing, extra))}"


def test_stub_methods():
    missing = []
    wrong_type = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        for cls_name, cls in inspect.getmembers(code,
                                                predicate=lambda x: inspect.isclass(x) and _file_matches(x, code)):
            scls = getattr(stub, cls_name, None)
            if scls is None:
                continue
            for name in reflection.get_declared(cls, lambda x: inspect.isroutine(x.object)):
                name = name.name
                sub = getattr(cls, name)
                ssub = reflection.classify_attr(scls, name, None)
                if ssub is None or ssub.defining_class != scls:
                    missing.append(sub)
                    continue
                casync = inspect.iscoroutinefunction(sub) or inspect.isasyncgenfunction(sub)
                sasync = inspect.iscoroutinefunction(ssub.object)
                if casync != sasync:
                    wrong_type.append((sub.__name__, casync, sasync))

    assert len(missing) == 0, f"Missing stubs for methods: {', '.join(map(_format_missing, missing))}"
    assert len(wrong_type) == 0, f"Type mismatch for functions: {', '.join(map(_format_wrong, wrong_type))}"


def test_stub_methods_extra():
    extra = []

    for code, stub in reflection.walk_with_modules(".", skip_dirs=SKIP_DIRS):
        for cls_name, cls in inspect.getmembers(stub,
                                                predicate=lambda x: inspect.isclass(x) and _file_matches(x, stub)):
            ccls = getattr(code, cls_name, None)
            if ccls is None:
                continue
            for name in reflection.get_declared(cls, lambda x: inspect.isroutine(x.object)):
                name = name.name
                sub = getattr(cls, name)
                csub = reflection.classify_attr(ccls, name, None)
                if csub is None or csub.defining_class != ccls:
                    extra.append(sub)
                    continue

    assert len(extra) == 0, f"Extra stubs for methods: {', '.join(map(_format_missing, extra))}"
