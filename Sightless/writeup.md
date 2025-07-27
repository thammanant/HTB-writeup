# Sightless Writeup - by Thammanant Thamtaranon
  - Sightless is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance
  - Initially, we performed a full TCP port scan with version detection and OS fingerprinting using the command:
    `nmap -A -T4 -p- 10.10.11.32`  
![Nmap_Scan](Nmap_Scan.png)
  - We then add `sightless.htb` to `/etc/hosts`.

## Scanning & Enumeration
  - We then run the command `dirsearch -u 10.10.11.32`, but found nothing of interesting.
  - We then move on to ftp, however the ftp does not allow anonymous login.
  - So we inspect the page source and found `sqlpad.sightless.htb` so we add this to `/etc/hosts` as well.
  - We then visit the page and using burp suite revealed the version of `6.10.0`
![Burp](Burp.png)
  - We search for sqlpad version 6.10 CVE and found `CVE-2022-0944`.
![CVE](CVE.png)
  - We downloaded and run the POC.
![RCE1](RCE1.png)
  - We got in as root, but we are inside a container.
![RCE2](RCE2.png)
  - Since, we are root we can use the command `cat /etc/shadow` to see user michael password.
![Shadow](Shadow.png)
  - So we use john to crack the password.
![Password](Password.png)
  - We then SSH into the machine using michael credential.
  - We digging around and find the config file
![Config](Condfig.png)
  - So we use the command `ssh michael@10.10.11.32 -L 8080:localhost:8080` to create a SSh tunnel forward port 8080 to our machine.
  - We also add `admin.sightless.htb` to `/etc/hosts` as well.
  - We can then visit `[localhost:8080](http://admin.sightless.htb:8080/)`.
![Local](Local.png)
  - We try find the version of Froxlor but did not found it.
  - On the machine, ssh as michael we use the command `ss -tulpn` and found serveral interesting internal web.
![Internal](Internal.png)
  - 
## Exploitation
