import fabric.api as fab


@fab.task
def doc():
    with fab.lcd('docs'):
        fab.local('pipenv run sphinx-build '
                  '-b html '
                  '-d _build/doctrees . '
                  '_build/html')
