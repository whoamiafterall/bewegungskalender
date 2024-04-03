import logging
import os
from git import Remote, Repo, GitCommandError

def init_git_repo(localdir: str, remote:str) -> Repo:
    # Initialize git repository if necessary
    if os.path.isdir(s=f"{localdir}/.git") == True: # if git repository already exists in localdir
        repo = Repo(path=localdir)
        logging.debug(f"Using existing git repo in {localdir}...")
    else: # if git repository doesn't exist in localdir
        try: # try cloning git repository from remote repository
            repo = Repo.clone_from(url=remote, to_path=localdir)
            logging.info(f"Sucessfully cloned git repository from {remote} to {localdir}!")          
        except GitCommandError: # except initialize it if localdir already exists
            repo = Repo.init(path=localdir)
            logging.info(f"Successfully initialised git repo in {localdir}!")
    return repo
            
def get_git_remote(remote:str, repo:Repo) -> Remote:
    try: # if remote already exists in localdir
        origin:Remote = repo.remote(name='origin')
        logging.debug(f"Remote origin:{origin} already exists. Continuing...")
    except ValueError: # if remote doesn't exist in localdir
        origin:Remote = repo.create_remote(name='origin', url=remote)
        logging.info(f"Successfully added Remote origin:{origin} to the Repository!")   
    return origin