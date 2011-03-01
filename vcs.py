import os
import datetime

import pysvn
import tarfile

import git

class BuildyVCS:

    def __init__(self, project, config):
        self.project = project
        self.config = config
        self.name = self.config.get(project, 'name')
        self.version = self.config.get(project, 'version')
        self.repository = self.config.get(project, 'vcs-url')
        self.work_dir = self.config.get(project, 'work-dir')
        self.path = os.path.join(self.work_dir, 'vcs', self.name)
        self.info = None
        self.client = None

    def update(self):
        raise NotImplementedError, "This method should be overridden!"

    def export(self, filename, filetype):
        raise NotImplementedError, "This method should be overridden!"

    def get_name(self):
        return self.name

    def get_version(self):
        return self.version

    def get_revision(self):
        raise NotImplementedError, "This method should be overridden!"

    def get_fancy_revision(self):
        raise NotImplementedError, "This method should be overridden!"

    def get_useful_filename(self):
        raise NotImplementedError, "This method should be overridden!"

class BuildySVN(BuildyVCS):

    def __init__(self, project, config):
        BuildyVCS.__init__(self, project, config)
        self.client = pysvn.Client()

    def update(self):
        if os.path.exists(self.path):
            self.client.update(self.path)
        else:
            self.client.checkout(self.repository, self.path)
        self.info = self.client.info(self.path)

    def export(self, filename, filetype):
        exportpath = os.path.join(self.work_dir, 'export')
        exportpath = os.path.join(exportpath, self.get_useful_filename())
        if filetype not in ['', 'gz', 'bz2']:
            raise NotImplementedError, "Only plain tar, gz and bz2 files are supported for now."
        self.client.export(self.path, exportpath)
        os.chdir(os.path.join(exportpath, os.path.pardir))
        tar = tarfile.open(filename, "w:%s"%filetype)
        tar.add(os.path.join('./', os.path.split(exportpath)[1]))
        tar.close()

    def get_revision(self):
        if self.info:
            return self.info.revision.number
        else:
            return 0

    def get_fancy_revision(self):
        return 'svn%s' % self.get_revision()

    def get_useful_filename(self):
        f = '%s-%s+svn%s' % (self.name, self.version, self.get_revision())
        return f

class BuildyGit(BuildyVCS):

    def __init__(self, project, config):
        BuildyVCS.__init__(self, project, config)
        self.repo = None

    def update(self):
        if os.path.exists(self.path):
            self.client = git.Git(self.path)
            self.client.pull()
        else:
            self.client = git.Git(os.path.split(self.path)[0])
            self.client.clone(self.repository, self.path)
            self.client = git.Git(self.path)
        self.repo = git.Repo(self.path)
        self.useheadforname = self.repo.heads[0]

        # check if we are using a branch
        if self.config.has_option(self.project, 'vcs-git-branch'):
            branchstring = self.config.get(self.project, 'vcs-git-branch')
            print "Attempting to use branch: " + branchstring
            g = git.Git(self.path)
            try:
                g.checkout(branchstring)
            except git.errors.GitCommandError:
                print "Error while attempting to checkout branch %s " % (branchstring)
                # TODO: dunno what to do here, checkout of branch failed.

            # TODO: perhaps there is a better way to get the item, returns a git.IterableList ... index(...) does not seem to work here ...
            for h in self.repo.heads:
                if h.name == branchstring:
                    print "Branch %s found" % (h.name)
                    self.useheadforname = h

    def export(self, filename, filetype):
        f = open(filename, "w")
        if filetype not in ['', 'gz']:
            raise NotImplementedError, "Only plain tar and gz files are supported for now."
        if filetype == '':
            f.write(self.repo.archive_tar(self.useheadforname.name, prefix='%s/' % self.get_useful_filename()))
        elif filetype == 'gz':
            f.write(self.repo.archive_tar_gz(self.useheadforname.name, prefix='%s/' % self.get_useful_filename()))
        f.close()

    def get_revision(self):
        return self.useheadforname.commit.id_abbrev

    def get_fancy_revision(self):
        date = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        return '%sgit%s' % (date, self.get_revision())

    def get_useful_filename(self):
        f = '%s-%s+%s' % (self.name, self.version, self.get_fancy_revision())
        return f

