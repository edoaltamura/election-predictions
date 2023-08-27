import warnings
import datetime

# Fetch the date of last commit from the parent directory. Initialise to the creation date.
__date_last_update__ = '2023-08-25'

try:
    import git

    repo = git.Repo("../l")
    tree = repo.tree()
    for blob in tree:
        commit = next(repo.iter_commits(paths=blob.path, max_count=1))
        timestamp = commit.committed_date
        __date_last_update__ = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

except ModuleNotFoundError:
    warnings.warn('Git-python module was not found, but you can install it with <pip install GitPython>. Returning '
                  'the date of creation.',
                  UserWarning)

except:
    warnings.warn('Could not retrieve the date of last commit. Returning the date of creation.',
                  UserWarning)

# Fetch the version from the base file
with open("./__version__.py", "r") as fh:
    exec_output = {}
    exec(fh.read(), exec_output)
    __version__ = exec_output["__version__"]

# Check the str format of the variables
assert isinstance(__version__, str)
assert isinstance(__date_last_update__, str)

# Build citation handle for bibtex
__cite__ = (r"@software{altamura_elections," "\n"
            r"  author = {{Altamura}, Edoardo}," "\n"
            r'  title = {"An statistical machine learning framework for election predictions"},' "\n"
            r"  url = {https://github.com/edoaltamura/election-predictions}," "\n"
            f"  version = {{{__version__:s}}}," "\n"
            f"  date = {{{__date_last_update__:s}}}," "\n"
            r"}")
