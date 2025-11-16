# Help Writeup - by Thammanant Thamtaranon  
- Help is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.10.121`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **22** — SSH  
  - **80** — HTTP  
  - **3000** — HTTP  
- I added `Help.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I run the Vhost enumeratoin with `ffuf -u http://help.htb -H "Host: FUZZ.help.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`, but nothing was founded.
- I then run `dirsearch` on both port 80 and 3000
  ![Dirsearch_Scan1](Dirsearch_Scan1.png)
  ![Dirsearch_Scan2](Dirsearch_Scan2.png)
- Visiting `http://htb.help/support/` found a website using `HelpDeskZ`.
  ![HelpDeskZ](HelpDeskZ.png)
- Visiting `http://htb.help:3000` found the message for user `Shiv`.
  ![Message](Message.png)

## Exploitation  
- Using the credential recovered from the JAR, I authenticated to phpMyAdmin at `http://blocky.htb/phpmyadmin/` and gained access to the application database.  
  ![PHPMyAdmin](PHPMyAdmin.png)  
- Within phpMyAdmin we found Notch's credentials.  
  ![Notch_Credential](Notch_Credential.png)  
- I updated Notch's password in the database and verified the new credentials by logging in as Notch.  
  ![New_Password](New_Password.png)  
  ![Notch](Notch.png)  
- The WordPress instance did not yield further privilege escalation, so we shifted focus to system access via SSH. Using the recovered credentials: `notch:8YsqfCTnvxAUeduzjNSXe22`
- I established an SSH session to the target and obtained the user flag.  
![SSH](SSH.png)

## Privilege Escalation  
- We enumerated sudo privileges with `sudo -l` and found that the `notch` user had sudo rights.  
![SUDO](SUDO.png)  
- To escalate, I executed the permitted sudo command to obtain a root shell: `sudo su -`  
![Root](Root.png)  
- After escalation we captured the root flag.
