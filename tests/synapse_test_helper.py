import os
import uuid
from core.param_store import ParamStore
from core.synapse import Synapse
import synapseclient
from synapseclient import Project, Folder, File, Team, Wiki


class SynapseTestHelper:
    """
    Test helper for working with Synapse.
    """
    _test_id = uuid.uuid4().hex
    _trash = []

    def test_id(self):
        """
        Gets a unique value to use as a test identifier.
        This string can be used to help identify the test instance that created the object.
        """
        return self._test_id

    def uniq_name(self, prefix='', postfix=''):
        return "{0}{1}_{2}{3}".format(prefix, self.test_id(), uuid.uuid4().hex, postfix)

    def dispose_of(self, *syn_objects):
        """
        Adds a Synapse object to the list of objects to be deleted.
        """
        for syn_object in syn_objects:
            if syn_object in self._trash:
                continue
            self._trash.append(syn_object)

    def dispose(self):
        """
        Cleans up any Synapse objects that were created during testing.
        This method needs to be manually called after each or all tests are done.
        """
        projects = []
        folders = []
        files = []
        teams = []
        wikis = []
        others = []

        for obj in self._trash:
            if isinstance(obj, Project):
                projects.append(obj)
            elif isinstance(obj, Folder):
                folders.append(obj)
            elif isinstance(obj, File):
                files.append(obj)
            elif isinstance(obj, Team):
                teams.append(obj)
            elif isinstance(obj, Wiki):
                wikis.append(obj)
            else:
                others.append(obj)

        failed_to_deletes = []

        for syn_obj in wikis:
            try:
                Synapse.client().delete(syn_obj)
            except:
                pass
            self._trash.remove(syn_obj)

        for syn_obj in files:
            try:
                Synapse.client().delete(syn_obj)
            except:
                pass
            self._trash.remove(syn_obj)

        for syn_obj in folders:
            try:
                Synapse.client().delete(syn_obj)
            except:
                pass
            self._trash.remove(syn_obj)

        for syn_obj in projects:
            try:
                Synapse.client().delete(syn_obj)
            except:
                pass
            self._trash.remove(syn_obj)

        for syn_obj in teams:
            try:
                Synapse.client().delete(syn_obj)
            except:
                pass
            self._trash.remove(syn_obj)

        for obj in others:
            print('WARNING: Non-Synapse object found: {0}'.format(obj))
            self._trash.remove(obj)

        for syn_obj in failed_to_deletes:
            print('WARNING: Failed to delete: {0}'.format(syn_obj))

    def create_project(self, **kwargs):
        """
        Creates a new Project and adds it to the trash queue.
        """
        if not 'name' in kwargs:
            kwargs['name'] = self.uniq_name(prefix=kwargs.get('prefix', ''))

        kwargs.pop('prefix', None)

        project = Synapse.client().store(Project(**kwargs))
        self.dispose_of(project)
        return project

    def create_file(self, **kwargs):
        """
        Creates a new File and adds it to the trash queue.
        """
        if not 'name' in kwargs:
            kwargs['name'] = self.uniq_name(prefix=kwargs.get('prefix', ''))

        kwargs.pop('prefix', None)

        file = Synapse.client().store(File(**kwargs))
        self.dispose_of(file)
        return file

    def create_team(self, **kwargs):
        """
        Creates a new Team and adds it to the trash queue.
        """
        if not 'name' in kwargs:
            kwargs['name'] = self.uniq_name(prefix=kwargs.get('prefix', ''))

        kwargs.pop('prefix', None)

        team = Synapse.client().store(Team(**kwargs))
        self.dispose_of(team)
        return team

    def create_wiki(self, **kwargs):
        """
        Creates a new Wiki and adds it to the trash queue.
        """
        if not 'title' in kwargs:
            kwargs['title'] = self.uniq_name(prefix=kwargs.get('prefix', ''))
        kwargs.pop('prefix', None)

        if not 'markdown' in kwargs:
            kwargs['markdown'] = 'My Wiki {0}'.format(kwargs['title'])

        wiki = Synapse.client().store(Wiki(**kwargs))
        self.dispose_of(wiki)
        return wiki
