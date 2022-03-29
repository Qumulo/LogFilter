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

import shutil
import sys
import argparse

# Import non-os libraries

from Logger import Logger, Level
from ConfigFile import ConfigFile


class LogFilter(object):
    def __init__(self,args, config, logger):
        self.args = args
        self.config = config
        self.logger = logger

        # Define variables used in class. These need to be done here so that we don't violate
        # pep8 coding standards

        self.conf_file = None
        self.filter = None
        self.filters = None
        self.hostname = None
        self.port_type = None
        self.port = None
        self.log_details = None
        self.client_ips = None
        self.users = None
        self.protocols = None
        self.operations = None
        self.results = None
        self.ids = None
        self.file_path_1s = None
        self.file_path_2s = None
        self.indent_amt = 0
        self.brace_amt = 0
        self.paren_amt = 0

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
            
            self.write_output("\n\n#Log filtering rules that log_filter.py script generated")
            self.write_output("if ($app-name startswith \"qumulo\") then")
            self.open_brace()
            
            self.definition_counter = 0
            for self.definitions in self.log_details.values():
                if self.definitions:
                    self.definition_counter +=1
            if self.definition_counter > 0:
                self.write_output("if")
                self.open_paren()

                self.parameters_list = list(self.log_details.keys())
                for self.prm in self.parameters_list:
                    self.defined_prm_count = 0
                    for self.defined_prm in self.parameters_list[self.parameters_list.index(self.prm)+1:]:
                        if len(self.log_details[self.defined_prm]) > 0:
                            self.defined_prm_count += 1
                    #create_config(prm,log_details, defined_prm_count)
                    
                    self.parameters = self.log_details[self.prm]
                    if len(self.parameters) > 0:
                        if any(self.item.startswith('!') for self.item in self.parameters):
                            self.write_output("not")
                            self.open_paren()

                            for self.param in self.parameters[:-1]:
                                self.write_output("$!"+self.prm+" contains \"" + self.param.split("!",2)[1] +"\" or ")
                            self.write_output("$!"+self.prm+" contains \"" + self.parameters[-1].split("!",2)[1] +"\" ")
                        else:
                            self.open_paren()
                            for self.param in self.parameters[:-1]:
                                self.write_output("$!"+self.prm+" contains \"" + self.param +"\" or ")
                            self.write_output("$!"+self.prm+" contains \"" + self.parameters[-1] +"\" ")
                        if self.defined_prm_count > 0:
                            self.close_paren()
                            self.write_output("and")
                        else:
                            self.close_paren()

                self.close_paren()
                self.write_output("then")
                self.open_brace()
            
            self.write_output("action(type=\"omfwd\" target=\""+self.hostname+"\" port=\""+self.port+"\" protocol=\""+self.port_type+"\" template=\"QumuloAuditFormat\")")
            self.close_brace()
            self.write_output("else")
            self.open_brace()
            self.write_output("action(type=\"omfile\" file=\"/dev/null\" template=\"QumuloAuditFormat\")")
            self.write_finish()
        
    # Teardown everything once this class is done... There might not be anything to do here

    def TearDown(self):
        return

    # Routine to write the output file... This is only necessary because we have to count the number of indents
    # to make sure the formatting looks really good

    def write_output(self, out_line):

        # Write out the number of spaces based upon our indent level

        for indx in range(self.indent_amt):
            self.conf_file.write("    ")

         # Write the data

        self.conf_file.write(f'{out_line}\n')

    # Write out the open brace and set the indent level

    def open_brace(self):

        self.write_output('{')
        self.indent_amt = self.indent_amt + 1
        self.brace_amt = self.brace_amt + 1

    # Write out the open parentheses and set the indent level

    def open_paren(self):

        self.write_output('(')
        self.indent_amt = self.indent_amt + 1
        self.paren_amt = self.paren_amt + 1

    # Write out the close brace and set the indent level

    def close_brace(self):

        if self.indent_amt > 0:
            self.indent_amt = self.indent_amt - 1

        if self.brace_amt > 0:
            self.write_output('}')
            self.brace_amt = self.brace_amt - 1

    # Write out the close parentheses and set the indent level

    def close_paren(self):

        if self.indent_amt > 0:
            self.indent_amt = self.indent_amt - 1

        if self.paren_amt > 0:
            self.write_output(')')
            self.paren_amt = self.paren_amt - 1

    # If we are done writing the definition, determine if we need one more brace to close it out

    def write_finish(self):

        paren_amt = self.paren_amt
        for indx in range(paren_amt):
            self.close_paren()

        brace_amt = self.brace_amt
        for indx in range(brace_amt):
            self.close_brace()

    # Copy template file into our output file and then open the output file for appending

    def _configuration_info(self, config, logger=None):

        """
        [
            {
                "hostname": "10.220.150.34",
                "port_type": "udp",
                "port": "514",
                "log_details":
                {
                    "client_ips" : [],
                    "users" : [],
                    "protocols": [],
                    "operations": [],
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

        base_dir = config.dir_name()

        self.template_file = f'{base_dir}/qumulo-audit.conf.template'
        self.config_file = "outputs/10-qumulo-audit.conf"
        self.filters = config.json_data()

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