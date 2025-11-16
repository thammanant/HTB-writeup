# Help Writeup - by Thammanant Thamtaranon  
- Help is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.10.37`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **21** — FTP  
  - **22** — SSH  
  - **80** — HTTP  
  - **25565** — Minecraft  
- I added `Help.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- While reviewing the website we observed the author name **Notch** and recorded it as an intelligence lead.  
- I performed a directory brute-force using `dirsearch`: `dirsearch -u http://blocky.htb`  
  ![Dirsearch_Scan](Dirsearch_Scan.png)  
- The `plugins` directory contained two JAR files.  
  ![Plugin](Plugin.png)  
- We extracted the JAR for inspection: `jar xf myfile.jar`  
  ![Extract](Extract.png)  
- In the extracted tree, under `/com/myfirstplugin`, I disassembled `BlockyCore.class` using `javap -c BlockyCore.class` and recovered embedded credentials.  
  ![SQLPASS](SQLPASS.png)

- We identified that the site is running WordPress and executed a WordPress enumeration scan:  
  `wpscan --url blocky.htb`  
  ![WP_Scan1](WP_Scan1.png)  
  ![WP_Scan2](WP_Scan2.png)  
  ![WP_Scan3](WP_Scan3.png)  
- The WordPress scan did not return any actionable findings.

- We then enumerated virtual hosts using `ffuf`:  
  `ffuf -u http://blocky.htb -H "Host: FUZZ.blocky.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`  
- No additional virtual hosts were discovered.

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
