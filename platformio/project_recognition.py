#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module read all the information related with the project/file open:

File Path, Project Path (Same Path Without filename), Parent Path, File Name, 
File Extension, Temp Path, if the project is initialized, the path of the
platformio.ini file, if it's native (platformio structure or not), list of
environments initialized and if the src_dir flag is set.

You can call to the "ProjectDetails" class and it will show all the information
available. This code is intended to work as a standalone so you can call it from
the sublime console and see the results.

Version: 1.0.0
Author: Guillermo Díaz
Contact: gepd@outlook.com
Licence: Same as the project (Read the LICENCE file in the root)
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime


class ProjectRecognition(object):
    def __init__(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        self.native = None

    def get_file_path(self):
        """File Path
        
        Full path of the file loaded in the current view,
        including the file name
        
        Returns:
            [str] -- path of the file path/path/file.ext
        """
        return self.view.file_name()

    def get_project_path(self):
        """Project Path
        
        Path (without file name) from the current file loaded 
        in the current view.
        
        Returns:
            [str] -- path of the file path/path/
        """
        full_path = self.get_file_path()
        project_path = os.path.dirname(full_path)
        return project_path

    def get_temp_project_path(self):
        """Temp Project Path

        Path of project in a temporal folder, this folder
        do not neccessarilly exits

        
        Returns:
            [str] -- temp_path/project_name/
        """
        file_name = self.get_file_name(ext=False)
        temp = self.get_temp_path(file_name)

        return temp

    def get_parent_path(self):
        """Parent Path
        
        Parent path or one folder behind of the file currently
        loaded in the current  view the path do not include 
        the file name
        
        Returns:
            [str] -- path/parent_path/
        """
        project_path = self.get_project_path()
        parent = os.path.dirname(project_path)

        return parent

    def get_file_name(self, ext=True):
        """File Name
        
        Name of the file loaded in the current view. 
        
        Keyword Arguments:
            ext {bool} -- if is set to false removes the 
                          extension of the filename 
                          (default: {True})
        
        Returns:
            [str] -- filename.ext or filename
        """
        full_path = self.get_file_path()
        file_name = os.path.basename(full_path)

        if(not ext):
            file_name = os.path.splitext(file_name)[0]

        return file_name

    def get_file_extension(self):
        """Extension
        
        Extract the extension of the file loaded in the current
        view and return it (without the dot)
        
        Returns:
            [str] -- ext
        """
        file_name = self.get_file_name()
        extension = file_name.split(".")[1]
        return extension

    def get_ini_path(self):
        """platformio.ini File

        Usually the platformio.ini file in one folder behind
        of the file open, but deviot can also work with a file
        estructure like arduino, this means, all the compile
        files are stored in other folder, in this case this
        folder is located in the temporal folder of your current
        operative system
        
        platformio.ini is searched in the parent folder or in
        the temp folder and return the path, if the file is not
        found in any of this folders it will returns None
        
        Returns:
            [str/none] -- path/platformio.ini / none
        """
        parent = self.get_parent_path()
        ini_path = self.search_pio_ini(parent)
        
        if(not ini_path):
            temp = self.get_temp_project_path()
            ini_path = self.search_pio_ini(temp)

        return ini_path

    def get_envs_initialized(self):
        """Initialized Environments
        
        List with all the available (initialized) environments in
        the platformio.ini file of the current file. If the file did
        not exits or there are none environment initialized it will
        return none
        
        Returns:
            [list/none] -- [environment, environment] / none
        """
        ini_path = self.get_ini_path()
        environments = []

        if(ini_path and os.path.exists(ini_path)):
            from .configobj.configobj import ConfigObj

            ini_file = ConfigObj(ini_path)

            for pio_env in ini_file:
                if('env:' in pio_env):
                    environments.append(pio_env.split(":")[1])

        if(not environments):
            return None

        return environments


    def get_src_dir(self):
        """SRC DIR
        
        Check if the src_dir flag has been set in the platformio.ini,
        if it has been set, will return the value otherwise it will 
        return none
        
        Returns:
            [str/none] -- src_dir_path/none
        """
        ini_path = self.get_ini_path()

        if(ini_path and os.path.exists(ini_path)):
            from .configobj.configobj import ConfigObj

            ini_file = ConfigObj(ini_path)

            if('platformio' in ini_file):
                if('src_dir' in ini_file['platformio']):
                    return ini_file['platformio']['src_dir']
            return None

    def is_initialized(self):
        """Project Initialized
        
        True if the platformio.ini file is found in the parent
        folder or in the temporal folder, false if not
        
        Returns:
            bool -- true if it's found
        """

        if(self.get_ini_path()):
            return True
        return False

    def is_native(self):
        """Native Project
        
        When the platformio.ini file is located in the temp folder
        the project is not native, otherwise it's native, if it's
        not initialized (file nonexistent file) return None
        
        Returns:
            [bool/none] -- True if is native/none if the file not exists
        """
        ini_file_path = self.get_ini_path()

        if(ini_file_path is None):
            return None

        parent_path = self.get_parent_path()
        ini_path = os.path.dirname(ini_file_path)

        if(parent_path == ini_path):
            return True
        return False

    def search_pio_ini(self, path):
        """Search platformio.ini
        
        Iterates over the given path and search the platformio.ini file
        if the file is found return the full path of the file otherwise None
        
        Arguments:
            path {str} -- string with the path to search platformio.ini
        
        Returns:
            [str/none] -- path/platformio.ini / none
        """
        if(os.path.isdir(path)):
            for file in os.listdir(path):
                if(file.endswith('platformio.ini')):
                    return os.path.join(path, file)
            return None

    def get_temp_path(self, extra_str=''):
        """Temp Path
        
        Path of the temp folder, if the extra_str argument
        is given it will add that string to the final path
        
        Keyword Arguments:
            extra_str {str} --extring to add at the temp path  (default: '')
        
        Returns:
            [str] -- temp_path | temp_path/extra_str
        """
        tmp_path = '/tmp'
        os_name = sublime.platform()
        if os_name == 'windows':
            tmp_path = os.environ['tmp']

        tmp_path = os.path.join(tmp_path, 'Deviot')

        if(extra_str):
            tmp_path = os.path.join(tmp_path, extra_str)

        return tmp_path


class ProjectDetails(ProjectRecognition):
    """Details
    
    Show all the information related with the current project/file
    it includes platformIO information (platformio.ini)
    
    Extends:
        ProjectRecognition
    """
    def __init__(self):
        super(ProjectDetails, self).__init__()

        width = 25
        
        details = ["File Path", "Project Path", "Paren Path",
                    "File Name", "File Extension", "Temp Path",
                    "Ini Path", "Initialized", "Native",
                    "Envs Initialized", "SRC-DIR"]
        
        infos = [self.get_file_path(), self.get_project_path(),
                self.get_parent_path(), self.get_file_name(),
                self.get_file_extension(), self.get_temp_path(),
                self.get_ini_path(), self.is_initialized(),
                self.is_native(), self.get_envs_initialized(),
                self.get_src_dir()]

        for detail, info in zip(details, infos):
            print ("{}: {}".format(detail.ljust(width), str(info).ljust(width)))