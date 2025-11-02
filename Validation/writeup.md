# Validation Writeup - by Thammanant Thamtaranon  
- Validation is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- -Pn 10.10.11.116`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **22** — SSH  
  - **80** — HTTP  
  - **4556** — HTTP
  - **8080** — HTTP

## Scanning & Enumeration  
- Visiting the port 80 show a website.
  ![80](80.png)  
- I performed a directory brute-force using `dirsearch`: `dirsearch -u 10.10.11.116`  
  ![Dirsearch_Scan](Dirsearch_Scan.png)  
- Visiting `/account.php` ask for registeration first.
- 

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
