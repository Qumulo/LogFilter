
# Log Filtering and Forward for Qumulo Audit Logs
Configuring Rsyslog to filter and forward Qumulo audit logs to the different target systems

<img src="./docs/logfilter.png" style="width: 800px;">

## Table of Contents

   * [Requirements](#requirements)
   * [Introduction](#introduction)
   * [Additional Documentations](#additional-documentations)
   * [Qumulo Log Field Definitions](#qumulo-log-field-definitions)
   * [Why Filter and Forward?](#why-filter-and-forward)
   * [Why would I use UDP for rsyslog data?](#why-would-i-use-udp-for-rsyslog-data)
   * [Getting Started](#getting-started)
   * [Configuration with rsyslog](#configuration-with-rsyslog)
   * [Define Parameters and Run LogFilter.py Script](#define-parameters-and-run-logfilter.py-script)
   * [Help](#help)
   * [Copyright](#copyright)
   * [License](#license)
   * [Trademarks](#trademarks)
   * [Contributors](#contributors)

## Requirements
-   python 3.6+
-   A Linux machine with Rsyslog

## Introduction

This script generates a rsyslog configuration file for filtering and forwarding Qumulo audit logs to the other systems.

Here is a <a href="./docs/sample.conf">configuration file sample</a>.

## Additional Documentations

For help better understanding of Qumulo audit logs and rsyslog configuration details see the table of documents below.

|Documentation|Description|
|-------------|-----------|
|[Qumulo Audit Logging](https://care.qumulo.com/hc/en-us/articles/360021454193-Qumulo-Core-Audit-Logging) | Qumulo Audit Logging Care Article|
|[Configure Audit Logging](https://care.qumulo.com/hc/en-us/articles/360021454193-Qumulo-Core-Audit-Logging#details-0-2) | How to enable audit logging on Qumulo|
|[What is Rsyslog?](https://www.rsyslog.com/) | Rsyslog details and official website|
|[Templates](https://www.rsyslog.com/doc/v8-stable/configuration/templates.html) | Rsyslog templates are a key feature that allow to specify any format a user might want. |
|[Properties](https://www.rsyslog.com/doc/v8-stable/configuration/properties.html) | Properties are data items in rsyslog.|
|[Control Structures](https://www.rsyslog.com/doc/v8-stable/rainerscript/control_structures.html) | Rsyslog control structures in RainerScript are similar in semantics to a lot of other mainstream languages.|
|[Setting Variables](https://www.rsyslog.com/how-to-use-set-variable-and-exec_template/) | Setting a variable allows you to use either a static value or from a given property.|
|[Filters](https://www.rsyslog.com/doc/v8-stable/configuration/filters.html) | Expression based filters allow filtering on arbitrary complex expressions, which can include boolean, arithmetic and string operations.|

## Qumulo Log Field Definitions
The fields are described below in the order that they display within the Qumulo audit log message body:
```
W.X.Y.Z,groot-1,"AD\alice",smb2,fs_read_data,ok,123,"/Mike/docs/image.png",""
```
Where **W.X.Y.Z** would equal a valid IP address.

The fields within the log file entries are:

**User IP** - The IP address of the user in IPV4/IPV6 format

**Node** - The node in the Qumulo cluster that generated the log entry

**User ID** - The user that performed the action. The user id can be of the form:

- AD username
- Qumulo local username
- POSIX UID
- Windows SID
- Qumulo auth ID (only if Qumulo fails to resolve the user ID to any of the previous types)

**Logins** - Any successful or unsuccessful login attempt by the user for the operation below:

- Session login via the Web UI
- Session login via the qq CLI
- SMB login
- NFS mount
- FTP login

**Protocol** - The protocol that the user request came through

- nfs3
- nfs4
- smb2
- smb3
- ftp
- api

**File System Operation** - The operation that the user attempted

- fs_create_directory
- fs_create_file
- fs_create_hard_link
- fs_create_symlink
- fs_create (a filetype other than the types capture above)
- fs_delete
- fs_fsstat
- fs_read_metadata
- fs_list_directory
- fs_open
- fs_read_data
- fs_read_link
- fs_rename
- fs_write_data
- fs_write_metadata

**Management Operation** - Any operation that modified the cluster configuration

- auth_create_user
- smb_create_share
- smb_login
- nfs_create_export
- nfs_mount
- snapshot_create_snapshot
- replication_create_source_relationship

**Error Status** - "ok" if the operation succeeded or a Qumulo specified error code if the operation failed.

Keep in mind that error status codes are subject to change with new releases of Qumulo Core and may differ
depending on the version you have installed on your cluster

<table>
  <tr>
    <th>**Error Status**</th>
    <th>**Details**</th>
  </tr>
  <tr>
    <td>ok</td>
    <td>The operation was successful.</td>
  </tr>
  <tr>
    <td>fs_no_such_path_error</td>
    <td>The directory portion of the path contains a name that doesn't exist.</td>
  </tr>
  <tr>
    <td>fs_no_space_error</td>
    <td>The file system has no available space. Your cluster is 100% full.</td>
  </tr>
  <tr>
    <td>fs_invalid_file_type_error</td>
    <td>The operation isn't valid for this filetype.</td>
  </tr>
  <tr>
    <td>fs_not_a_file_error</td>
    <td>The operation (e.g. read) is only valid for a file.</td>
  </tr>
  <tr>
    <td>fs_sharing_violation_error</td>
    <td>The file or directory is opened by another party in an exclusive manner.</td>
  </tr>
  <tr>
    <td>fs_no_such_entry_error</td>
    <td>The directory, file, or link does not exist in the file system.</td>
  </tr>
  <tr>
    <td>fs_access_denied_error</td>
    <td>The user does not have access to perform the operation.</td>
  </tr>
  <tr>
    <td>fs_access_perm_not_owner_error</td>
    <td>The user would need superuser or owner access to perform the operation.</td>
  </tr>
  <tr>
    <td>fs_entry_exists_error</td>
    <td>A file system object with the given name already exists.</td>
  </tr>
  <tr>
    <td>fs_directory_not_empty_error</td>
    <td>The directory cannot be removed because it is not empty.</td>
  </tr>
  <tr>
    <td>fs_no_such_inode_error</td>
    <td>The file system object does not exist.</td>
  </tr>
  <tr>
    <td>http_unauthorized_error</td>
    <td>The user does not have access to perform the management operation.</td>
  </tr>
  <tr>
    <td>share_fs_path_doesnt_exist_error</td>
    <td>The directory does not exist on the cluster.</td>
  </tr>
  <tr>
    <td>decode_error</td>
    <td>Invalid json was passed to the API.</td>
  </tr>
</table>

**File id** - The ID of the file that the operation was on

**File path** - The path of the file that the operation was on

When accessing a file through a snapshot, the path is prefixed with a "/.snapshot/<snapshot-directory>";
which is the same path prefix used to access snapshot files via nfs and smb.

**Secondary file path** - Any rename or move operations

**IMPORTANT!!** In order to keep the amount of audit log message to a minimum, similar operations performed
in rapid succession will be de-duplicated. For example, if a user reads the same file 100,000 times in a
minute, only one message corresponding to the first read will be generated.

## Why Filter and Forward?

There are several reasons why you may wish to filter and forward your Qumulo audit logs.

1. You wish to aggregate all of your logs onto one machine. This is known as log aggregation.
2. There is a requirement to filter specific logs for better understanding.
3. Qumulo only uses TCP as the delivery mechanism for rsyslog, but your application requires UDP.

## Why would I use UDP for rsyslog data?

The rsyslogd daemon was originally configured to use UDP for log forwarding to reduce overhead. While UDP
is an unreliable protocol, it's streaming method does not require the overhead of establishing a network
session. This protocol also reduces network load as the network stream requires no receipt verification
or window adjustment.

You may find that UDP is preferred if:

1. The receiving device does not support TCP delivery
2. The receiving device, or hosting network, are severely resource limited
3. The logs being delivered are considered low priority

When choosing UDP log delivery, it is important to keep in mind that there is no message delivery
verification or **recovery**. So, while the likelihood of data loss may not be high, logs can be
missed due to network packet loss.

## Getting Started

Before you can run and create a rsyslog configuration file on your system, you will need to clone this repository on your machine. For that, you will need to have `git` installed on your machine.

Once git is operational, then find or create a directory where you wish to store the contents of the `LogFilter` repository and
clone it to your machine with the command `git clone https://github.com/Qumulo/LogFilter.git`

You will notice that the `git clone` command will create a new directory in your current location call `LogFilter`.

The contents of that directory should look like:
```
-rw-r--r--  1 someone  somegroup  1063 Mar 17 08:24 LICENSE
-rw-r--r--  1 someone  somegroup  6972 Mar 17 08:38 README.md
drwxr-xr-x  4 someone  somegroup   128 Mar 17 08:24 config
drwxr-xr-x  4 someone  somegroup   128 Mar 17 08:24 docs
drwxr-xr-x  4 someone  somegroup   128 Mar 17 08:24 outputs
drwxr-xr-x  4 someone  somegroup   128 Mar 17 08:24 utils
-rwxr-xr-x  1 someone  somegroup   301 Mar 17 08:24 LogFilter.py
```
Of course, the owner will not be `someone` and the group will not be `somegroup`, but will show you as the owner and the group as whatever group you currently belong to. If in doubt, simply type `id -gn` to see your current group and `id -un` to see your current login id.

You will need to modify the **log_filter.json** file under **config** and then run **LogFilter.py** file to run in your environment. Let us start with the configurations.

## Configuration with Rsyslog

For the following example, our client will be running Ubuntu 20.04. If you are using a different version
of Linux, you may need to Google how to configure rsyslog for specifics.

### Global rsyslog configuration

Start by updating the global rsyslog configuration to allow receiving syslog messages over TCP connections.
In the **/etc/rsyslog.conf** file, uncomment the following lines to listen for TCP connections on port 514.
If you choose to use a different port, then also change the port referenced to match your desired
configuration.
```
# provides TCP syslog reception
module(load="imtcp")
input(type="imtcp" port="514")
```

## Define Parameters and Run LogFilter.py Script

In the directory `config`, there is a file called `log_filter.json` that must be modified in order to run the LogFilter script.

This application depends upon the file name `log_filter.json` in the subdirectory `config`. Due to that restriction, this file and the directory it is contained in should not be moved or renamed.

Here is the empty file and, in the following paragraphs, we will describe each field
and their proper values. Multiple definitions can be defined inside the square brackets.

```
[
   {
      "hostname": "",
      "port_type": "",
      "port": "",
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
```
There are two main sections in the configuration file `log_filter.json`. 
1. Remote Host Details
   - `hostname` - FQDN or IP address of the machine that Qumulo audit logs will be forwarded to.
   - `port_type` - `tcp` or `udp`
   - `port` - Port number.
 
2. Log Details

**IMPORTANT!!** *If you leave any of the below definitions empty, the script will generate a conditional definition for log forwarding to the defined remote host over the TCP or UDP port.*

**IMPORTANT!!** *If you define any of the below definitions, the script will generate a conditional definition for filtering the defined parameters and forwarding them to the remote host. Other logs won't be seen on the remote host*

**IMPORTANT!!** *If you define any of the below definitions with `!` like `!fs_list_directory`, the script will generate a conditional definition for excluding the defined parameters and the other logs will be forwarded to the remote host.*

**IMPORTANT!!** *Multiple parameters can be defined with command seperated inside the square brackets.*

   - `client_ips` - Client ip addresses can be specified for filtering. Example: `"10.0.0.1"`, `"10.0.0.1","10.0.0.2"`.
   - `users` - Users can be specified for filtering. Example: `"user01"` , `"AD\user01"`.
   - `protocols` - Protocols can be specified for filtering. Example: `"nfs3"`,  `"smb3"`,  and `"api"`.
   - `operations` - Operations can be specified for filtering. Example: `"fs_create_file"`, `"smb_login"`.
   - `results` - Results can be specified for filtering. Example: `"ok"`, `"fs_not_a_file_error"`.
   - `ids` - Ids can be specified for filtering. Example: `"10001"`
   - `file_paths_1s` - Original file paths can be specified for filtering. Example: `"/home/user01"`, `"/smb_share1"`.
   - `file_paths_2s` - Secondary file paths can be specified for filtering. Example: `"/home/user01"`, `"/smb_share1"` 

Please [Qumulo audit log details](#log-field-definitions) section for more details about the log structure.

Please don't touch other files inside **config** directory.

### Create the new Qumulo audit Log configuration via LogFilter.py script
**LogFilter.py** is the main script file that allow you to create a new Rsyslog configuration file for filtering and forwarding Qumulo audit logs to the defined hosts.

Run the script in this directory by typing 

`./LogFilter.py --config ./config/log_filters.json` 

in a terminal window. If there are no errors, a rsyslog configuration file will be created in **outputs** directory.

### Verify the configuration file

Before copying the configuration file that you created via **LogFilter.py**, you can verify the config file doesn't have any syntax error with the command below.

`rsyslogd -f ./outputs/10-qumulo-audit.conf -N7`

### Copy the new configuration file 
Rsyslog loads dedicated log file format definitions from the **/etc/rsyslog.d** directory. You will need
to create a new configuration file (**10-qumulo-audit.conf** inside **outputs**) via **LogFilter.py**  script for defining the Qumulo Audit Log format.

Simply copy this file into **/etc/rsyslog.d**. 

`cp ./outputs/10-qumulo-audit.conf /etc/rsyslog.d/` 

### Restart the rsyslog daemon
In order for the new Qumulo Audit Log configuration to be active, you must first restart the
rsyslog daemon on the server.

`systemctl restart rsyslog`

## Help

To post feedback, submit feature ideas, or report bugs, use the [Issues](https://github.com/Qumulo/LogFilter/issues) section of this GitHub repo.

## Copyright

Copyright © 2022 [Qumulo, Inc.](https://qumulo.com)

## License

[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

See [LICENSE](LICENSE) for full details

    MIT License
    
    Copyright (c) 2022 Qumulo, Inc.
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## Trademarks

All other trademarks referenced herein are the property of their respective owners.

## Contributors

 - [Berat Ulualan](https://github.com/beratulualan)
 - [Michael Kade](https://github.com/mikekade)


