def pythonizing_cython(pyxfile):
    """
    A wrapper method to convert cython's .pyx files into .so files,
    such that it is import-able without relying on setup.py
    """
    import os, shutil
    # Creates ssetup_pyx.py file.
    setup_py = "\n".join(["from distutils.core import setup",
                          "from Cython.Build import cythonize",
                          "setup(ext_modules = cythonize('"+\
                          pyxfile+".pyx'))"])   
    
    with open('setup_pyx.py', 'w') as fout:
        fout.write(setup_py)

    # Compiles the .c file from .pyx file.
    os.system('python setup_pyx.py build_ext --inplace')
    
    # Finds the pyconfig.h file.
    pyconfig = os.popen('find /usr/include -name pyconfig.h'\
                        ).readline().rpartition('/')[0]

    # Builds the .so file.
    cmd = " ".join(["gcc -shared -o", pyxfile+".so",
                    "-fPIC", pyxfile+".c",
                    "-I", pyconfig])
    os.system(cmd)
    
    # Removing temporary .c and setup_pyx.py files.
    os.remove('setup_pyx.py')
    os.remove(pyxfile+'.c')
    shutil.rmtree('./build')
    # This is a strange thing that was created while compiling the .pyx ...
    shutil.rmtree('./'+os.path.dirname(\
                    os.path.abspath(__file__)).rpartition('/')[2]) 