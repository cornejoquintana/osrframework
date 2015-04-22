# !/usr/bin/python
# -*- coding: cp1252 -*-
#
##################################################################################
#
#    Copyright 2015 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This program is part of OSRFramework. You can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################################################################################

import argparse
import json
import logging
import re
import sys
import urllib2

import osrframework.utils.browser as browser
from osrframework.utils.platforms import Platform

import Skype4Py

class Skype(Platform):
    """ 
        A <Platform> object for Skype.
    """
    def __init__(self):
        """ 
            Constructor... 
        """
        self.platformName = "Skype"
        self.tags = ["messaging"]

        ########################
        # Defining valid modes #
        ########################
        self.isValidMode = {}        
        self.isValidMode["phonefy"] = False
        self.isValidMode["usufy"] = True
        self.isValidMode["searchfy"] = True      
        
        ######################################
        # Search URL for the different modes #
        ######################################
        # Strings with the URL for each and every mode
        self.url = {}        
        #self.url["phonefy"] = "http://anyurl.com//phone/" + "<phonefy>"
        self.url["usufy"] = "http://www.instagram.com/" + "<usufy>"       
        self.url["searchfy"] = "http://anyurl.com/search/" + "<searchfy>"       

        ######################################
        # Whether the user needs credentials #
        ######################################
        self.needsCredentials = {}        
        #self.needsCredentials["phonefy"] = False
        self.needsCredentials["usufy"] = False
        self.needsCredentials["searchfy"] = False 
        
        #################
        # Valid queries #
        #################
        # Strings that will imply that the query number is not appearing
        self.validQuery = {}
        # The regular expression '.*' will match any query.
        #self.validQuery["phonefy"] = re.compile(".*")
        self.validQuery["usufy"] = re.compile(".*")   
        self.validQuery["searchfy"] = re.compile(".*")
        
        ###################
        # Not_found clues #
        ###################
        # Strings that will imply that the query number is not appearing
        self.notFoundText = {}
        #self.notFoundText["phonefy"] = []
        self.notFoundText["usufy"] = [] # N/A in Skype
        self.notFoundText["searchfy"] = [] # N/A in Skype
        
        #########################
        # Fields to be searched #
        #########################
        self.fieldsRegExp = {}
        
        # Definition of regular expressions to be searched in phonefy mode
        #self.fieldsRegExp["phonefy"] = {}
        # Example of fields:
        #self.fieldsRegExp["phonefy"]["i3visio.location"] = ""
        
        # Definition of regular expressions to be searched in usufy mode
        self.fieldsRegExp["usufy"] = {}
        # Example of fields:
        #self.fieldsRegExp["usufy"]["i3visio.location"] = ""
        # Definition of regular expressions to be searched in searchfy mode
        self.fieldsRegExp["searchfy"] = {}
        # Example of fields:
        #self.fieldsRegExp["searchfy"]["i3visio.location"] = ""        
        
        ################
        # Fields found #
        ################
        # This attribute will be feeded when running the program.
        self.foundFields = {}
    

    def processData(self, uri=None, data=None, mode=None):
        '''
            Method that process the data in a Skype User.
            
            :return:    A i3visio-like object.
        '''
        info = []
        
        # splitting info
        pairs = data.split('; ')
        
        for p in pairs:
            parts = p.split(':')
            
            aux = {}
            aux["type"] = parts[0]
            aux["value"] = parts[1]        
            aux["attributes"] = {}
            
            info.append(aux)
        return json.dumps(info)

    def processSkypeUser(self, user, handle=None):
        '''
        '''
        aux = {}
        aux["type"] = "i3visio.profile"
        if handle==None:
            handle = str(user.Handle)
        aux["value"] = self.platformName + " - " + handle       
        #info = "Username:"#Aliases;Nombre Completo;País;Provincia;Ciudad;Página web;Tfno.Casa;Tfno.Móvil;TfnoOficina;OnlineStatus;MoodText\n"
        #info += user.Handle + ";" #+ str(user.Aliases) +";" + user.FullName + ";" + user.Country + ";" + user.Province + ";" + user.City + ";" + user.Homepage + ";"  + user.PhoneHome +";" + user.PhoneMobile + ";" + user.PhoneOffice  +  ";" + user.OnlineStatus + ";" + user.MoodText +'\n'
        info = ""
        try:
            info += "i3visio.aliases:" + str(user.Aliases)+";i3visio.fullname:" + str(user.FullName) + ";i3visio.location:" + str(user.Country)
            aux["attributes"] = self.processData(data=info, mode=mode)
            
        except:
            # Capturing exception in case any kind of special character was found
            aux["attributes"] = []                          

        return aux 
    def getInfo(self, query=None, process = False, mode="usufy"):
        ''' 
            Method that checks the presence of a given query and recovers the first list of complains.

            :param query: Phone number to verify.
            :param proces:  Calling the processing function.
            :param mode:    Mode to be executed.            

            :return:    Python structure for the html processed.
        '''
        # Defining variables for this process
        results = {}
        data = ""
        if not self.modeIsValid(mode=mode):
            # TO-DO: InvalidModeException
            #print "InvalidModeException"
            return json.dumps(results)
               
        try:
            logger = logging.getLogger("osrframework.wrappers")
            # Verifying if the nick is a correct nick
            if self._isValidQuery(query, mode):
                logger.debug("Starting Skype client...")

                logger.warning("A Skype client must be set up... Note that the program will need a valid session of Skype having been started. If you were performing too many searches, the server may block or ban your account depending on the ToS. Please run this program under your own responsibility.")
                # Instantiate Skype object, all further actions are done
                # using this object.

                skype = Skype4Py.Skype()

                # Start Skype if it's not already running.
                if not skype.Client.IsRunning:
                    skype.Client.Start()
                    if not skype.Client.IsRunning:
                        logger.error("The Skype application could NOT be started...")
                        return None
            
                # Set our application name.
                skype.FriendlyName = 'i3visio - OSRFramework'


                # Attach to Skype. This may cause Skype to open a confirmation
                # dialog.
                skype.Attach()

                # Set up an event handler.
                def new_skype_status(status):
                    # If Skype is closed and reopened, it informs us about it
                    # so we can reattach.
                    if status == Skype4Py.apiAttachAvailable:
                        skype.Attach()
                skype.OnAttachmentStatus = new_skype_status        

                # Dealing with UTF8
                import codecs
                import sys

                UTF8Writer = codecs.getwriter('utf8')
                sys.stdout = UTF8Writer(sys.stdout)
   
                # Search for users and display their Skype name, full name
                # and country.
                data = skype.SearchForUsers(query)
        except:
            # No information was found, then we return a null entity
            return json.dumps(results)            
                
        # Verifying if the platform exists
        if mode == "usufy":
            for user in data:
                if user.Handle.lower() == query.lower():            
                    results = self.processSkypeUser(user)
             
        elif mode == "searchfy":
            results["type"] = "i3visio.search"
            results["value"] = self.platformName + " Search - " + query
            results["attributes"] = []                 
            for user in data:
                results["attributes"].append(self.processSKypeUser(user, handle=query))
               
        return json.dumps(results)

