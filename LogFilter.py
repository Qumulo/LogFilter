#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2022 Qumulo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
# LogFilter.py
#
# Class to create a Rsyslog configuration file for a Qumulo cluster with filtering capabilities.

"""
== Usage:
LogFilter.py --config path
=== Required:
[--config] path                    The path where the configuration file is found.
=== Options:
-h | --help                        Print out the command usage/help
=== Examples:
./LogFilter.py --path ./config/log_filters.json
"""

# Import python libraries

import json
import shutil
import sys
import argparse
import os


# Import non-os libraries

from utils.Logger import Logger, Level
from utils.ConfigFile import ConfigFile


class LogFilter(object):
    def __init__(self,args, config, logger):
        self.args = args
        self.config = config
        self.logger = logger
        
    def SetUp(self):
        
        # Get configuration info from the file

        self._configuration_info(self.config, self.logger)
        
    def Run(self):
                
        for self.filter in self.filters:
            self.hostname = self.filter['hostname']
            self.port_type = self.filter['port_type']
            self.port = self.filter['port']
            self.log_details = self.filter['log_details']
            self.client_ips = self.log_details['client_ips']
            self.users = self.log_details['users']
            self.protocols = self.log_details['protocols']
            self.operations = self.log_details['operations']
            self.results = self.log_details['results']
            self.ids = self.log_details['ids']
            self.file_path_1s = self.log_details['file_path_1s']
            self.file_path_2s = self.log_details['file_path_2s']
            
            self.ending=""
            
            self.conf_file.write("\n\n#Log filtering rules that log_filter.py script generated\n")
            self.conf_file.write("if ($app-name startswith \"qumulo\") then {\n")
            
            self.definition_counter = 0
            for self.definitions in self.log_details.values():
                if self.definitions:
                    self.definition_counter +=1
            if self.definition_counter > 0:
                self.conf_file.write("\tif ( \n")
                self.parameters_list = list(self.log_details.keys())
                for self.prm in self.parameters_list:
                    self.defined_prm_count = 0
                    for self.defined_prm in self.parameters_list[self.parameters_list.index(self.prm)+1:]:
                        if len(self.log_details[self.defined_prm]) > 0:
                            self.defined_prm_count += 1
                    #create_config(prm,log_details, defined_prm_count)
                    
                    self.parameters = self.log_details[self.prm]
                    if len(self.parameters) > 0:
                        self.conf_file.write("\t\t")
                        if any(self.item.startswith('!') for self.item in self.parameters):
                            self.conf_file.write("not (")
                            for self.param in self.parameters[:-1]:
                                self.conf_file.write("$!"+self.prm+" contains \"" + self.param.split("!",2)[1] +"\" or ")
                            self.conf_file.write("$!"+self.prm+" contains \"" + self.parameters[-1].split("!",2)[1] +"\" ")
                        else:
                            self.conf_file.write("(")
                            for self.param in self.parameters[:-1]:
                                self.conf_file.write("$!"+self.prm+" contains \"" + self.param +"\" or ")
                            self.conf_file.write("$!"+self.prm+" contains \"" + self.parameters[-1] +"\" ")
                        if self.defined_prm_count > 0:
                            self.conf_file.write(")\n\t\tand \n")
                        else:
                            self.conf_file.write(")")
                        
                        self.ending="}"
                
                self.conf_file.write("\n\t) then {\n") 
            
            self.conf_file.write("\t\taction(type=\"omfwd\" target=\""+self.hostname+"\" port=\""+self.port+"\" protocol=\""+self.port_type+"\")\n\t}\n")
            self.conf_file.write("\telse\n")
            self.conf_file.write("\t\taction(type=\"omfile\" file=\"/dev/null\" template=\"QumuloAuditFormat\")\n")
            self.conf_file.write(self.ending+"\n\n")
        
    
    def TearDown(self):
        return
    
    def _configuration_info(self, config, logger=None):

        # Open configuration file and get arguments
        # A sample log_filters.json file:

        """
        [
            {
            "hostname": "10.220.150.34",
            "port_type": "udp",
            "port": "514",
            "log_details": {
                "client_ips" : [],
                "users" : [],
                "protocols": [],
                "operations": [],
                "results": [],
                "ids": [],
                "file_path_1s": [],
                "file_path_2s": []
            }
            },
            {
                "hostname": "10.220.150.18",
                "port_type": "tcp",
                "port": "514",
                "log_details": {
                "client_ips" : [],
                "users" : [],
                "protocols": [],
                "operations": ["!fs_delete", "!fs_rename", "!fs_write_data"],
                "results": [],
                "ids": [],
                "file_path_1s": [],
                "file_path_2s": []
                } 
            },
            {
                "hostname": "10.220.150.33",
                "port_type": "tcp",
                "port": "514",
                "log_details": {
                "client_ips" : [],
                "users" : ["admin"],
                "protocols": ["api"],
                "operations": ["nfs_delete_export"],
                "results": [],
                "ids": [],
                "file_path_1s": [],
                "file_path_2s": []
                } 
            }
        ]
        """

        # Get the data required from the configuration file...
        # The good news is that we don't have to worry about getting the
        # required data. It would have failed in the validation routine if
        # it didn't exist

        self.log_filter_file = "config/log_filters.json"
        self.template_file = "config/qumulo-audit.conf.template"
        self.config_file = "outputs/10-qumulo-audit.conf"

        with open(self.log_filter_file, 'r') as filter_file:
            self.filters = json.load(filter_file)

        # Prepare config file from the template
        shutil.copy(self.template_file, self.config_file)
        self.conf_file = open(self.config_file, 'a')
   
   
def main():

    # Define the name of the Program, Description, and Version.

    progName = "Log Filter"
    progDesc = "Create a rsyslog configuration file with log filtering parameter for a Qumulo cluster."
    progVers = "5.0"

    # Turn on the logger and set DEBUG level

    logger = Logger(progName, Level.DEBUG)

    # Get command line arguments

    args = CommandArgs(progDesc, progName, progVers)

    # Change the log level based upon the command line arguments

    logger.setLevel(args.loglevel)

    # Create log entry

    logger.debug(f"Reading from config file: {args.config}")

    # Get the configuration file so that we can figure out how often to run the program

    config = ConfigFile(args.config, logger)

    # Validate the config

    try:
        config.validate()
    except Exception as err:
        logger.error(f'Configuration would not validate, error is {err}')
        sys.exit(1)

    # Run the configuration creation

    Run(args, config, logger)

    # We need to trap SIGINT (ctrl-C)

    try:
        pass

    except KeyboardInterrupt:
        print("Caught ctrl-C. Wait while we cleanup the program.")
        sys.exit(0)

# Simple program to instantiate the class and run the report

def Run(args, config, logger):

    # Setup the program

    logger.debug('Starting to generate a Rsyslog config file')

    logfilter = LogFilter(args, config, logger)
    logfilter.SetUp()
    logfilter.Run()
    logfilter.TearDown()
    

    logger.debug('The Rsyslog config file has been generated. You can find it in ./outputs directory.')

    del logfilter

# Get arguments from the command line

def CommandArgs(progDesc, progName, progVers):

    parser = argparse.ArgumentParser(description=progDesc)
    parser.add_argument(
        "--version",
        action="version",
        version=(f"{progName} - Version {progVers}"),
    )
    parser.add_argument(
        "--log",
        default="INFO",
        required=False,
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "DEBUG"],
        help="Set the logging level.",
    )
    parser.add_argument(
        "--config",
        default="./config/log_filters.json",
        required=True,
        dest="config",
        help="Configuration file pathname.",
    )

    try:
        return parser.parse_args()
    except argparse.ArgumentTypeError:
        # Log an error
        sys.exit(1)

# Calling the main routine... Everything starts here!!

if __name__ == "__main__":
    main()
