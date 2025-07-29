# Sea Writeup - by Thammanant Thamtaranon
  - Sea is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance
  - Initially, we performed a full TCP port scan with version detection and OS fingerprinting using the command:  
    `nmap -A -T4 -p- 10.10.11.28`  
![Nmap_Scan](Nmap_Scan.png)
  - We then add sea.htb to `/etc/hosts`.

## Scanning & Enumeration
  - We enumerated web directories using `dirsearch -u http://10.10.11.28`.
![Dirsearch_Scan1](Dirsearch_Scan1.png)
  - We found `/contact.php`.
![Contact](Contact.png)
  - Enumerate furthur shown.
![Dirsearch_Scan2](Dirsearch_Scan2.png)
  - We then found that the websiite use WonderCMS version 3.2.0
![CMS](CMS.png)
![CMS_Version](CMS_Version.png)

## Exploitation
  - We search for WonderCMS 3.2 CVE and found `CVE-2023-41425`.
  - WonderCMS login is `/loginURL`, So in this website it is `http://10.10.11.28/loginURL`
  - Now we grab the POC and run the exploit.
![Exploit](Exploit.png)
  - Now we got in as www-data
![Shell](Shell.png)
  - We verify the users using command `cat /etc/passwd`.
![Users](Users.png)
  - We found password in the file `/var/www/sea/data/database.js`.
  - We then use john to crack the hash.
![Cracked](Cracked.png)
  - We try to ssh using founded credential, and got in as user amay.
  - We got the user flag.
  - We try run `sudo -l`, unfortuanly user amay cannot run sudo.
  - We use the command `ss -tulpn`.
![Services](Services.png)
  - There are two instesting port, 8080 and 53173.
  - We will try 8080 first which should be internal service.
  - We use the command `ssh amay@sea.htb -L 8080:localhost:8080` to SSH tunnel forward port 8080 to our 8080.
![Internal](Internal.png)
  - 


