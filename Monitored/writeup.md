# Monitored Writeup - by Thammanant Thamtaranon

**Monitored** is a **Medium**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- We began the engagement with a full TCP port scan using Nmap to identify open services and fingerprint the underlying operating system.
  ![Nmap_Scan1.png](Nmap_Scan1.png)
  ![Nmap_Scan2.png](Nmap_Scan2.png)
- The notable open ports on the machine were:
  * **22/tcp:** SSH (OpenSSH 8.4p1)
  * **80/tcp:** HTTP (Apache httpd 2.4.56)
  * **389/tcp:** LDAP (OpenLDAP 2.2.X - 2.3.X)
  * **443/tcp:** HTTPS (Apache httpd 2.4.56)
  * **161/udp:** SNMP
- We then added `nagios.monitored.htb` and `monitored.htb` to our `/etc/hosts` file.

---

## Scanning & Enumeration
- We started by checking the SNMP service and found the `svc` user's password.
  ![SVC_Password.png](SVC_Password.png)
- Visiting port 80 (HTTP) redirected us to port 443 (HTTPS), where we found the Nagios XI login page.
  ![Port443.png](Port443.png)
- When entering an invalid username and password, the application responded with an "Invalid username or password." error.
  ![Account1.png](Account1.png)
- However, when logging in with the `svc` username and password, the application returned a different error: "The specified user account has been disabled or does not exist." This indicated the credentials were valid, but web access for that account was restricted.
  ![Account2.png](Account2.png)

---

## Exploitation
- With this information, we searched the internet for alternative Nagios XI login APIs.
  ![Login_API.png](Login_API.png)
- Sending a POST request with the `svc` credentials returned an `auth_token`.
  ![Token.png](Token.png)
- We then researched how to authenticate using this `auth_token`.
  ![Usage.png](Usage.png)
- By appending the token, we successfully authenticated to Nagios XI as the user `svc`. We also noticed the software version at the bottom left of the screen: Nagios XI 5.11.0.
  ![Login.png](Login.png)
- We then searched for CVEs related to Nagios XI 5.11.0 and found **CVE-2023-40931**.
    - **CVE-2023-40931** is a SQL injection vulnerability that allows authenticated attackers to execute arbitrary SQL commands via the ID parameter in the POST request to `/nagiosxi/admin/banner_message-ajaxhelper.php`.
  ![CVE.png](CVE.png)
- We found a PoC on [Github](https://github.com/G4sp4rCS/CVE-2023-40931-POC) and downloaded it to our machine.
  ![PoC1.png](PoC1.png)
- Running the PoC automatically executed a `sqlmap` command.
  ![PoC2.png](PoC2.png)
- Once the `sqlmap` command finished, we successfully retrieved the Admin API key.
  ![Admin_API_Key.png](Admin_API_Key.png)
- The PoC included an `admin_exploit` script designed to escalate our privileges to admin and trigger a reverse shell. Although the reverse shell failed, the exploit successfully created an administrative account for us. We used these new credentials to log in as an administrator.
  ![PoC_Failed.png](PoC_Failed.png)
- Now that we were logged in, we needed to trigger a reverse shell manually, so we navigated to `Core Config Manager`.
  ![Core_Config.png](Core_Config.png)
- Next, we selected `Commands`.
  ![Commands.png](Commands.png)
- We clicked on `Add New` and added a command to send a reverse shell back to our machine.
  ![Shell.png](Shell.png)
- To execute this command, we navigated to the `Hosts` menu.
  ![Hosts.png](Hosts.png)
- We clicked on `localhost`, selected our reverse shell payload as the `Check command`, and finally clicked `Run Check Command`.
  ![Localhost.png](Localhost.png)
- This successfully executed our payload, sending a reverse shell back to our listener as the user `nagios`, allowing us to capture the user flag.
  ![Nagios.png](Nagios.png)
- For easier access and persistence, we added our SSH public key to `/home/nagios/.ssh/authorized_keys` and logged in via SSH.
  ![SSH.png](SSH.png)
  
---

## Privilege Escalation
- Running `sudo -l` revealed that the user `nagios` could run several commands as root without a password, including `/usr/bin/php /usr/local/nagiosxi/scripts/migrate/migrate.php *`. While there are likely multiple paths to root, we focused on this script.
  ![SUDO.png](SUDO.png)
- Reading the `/usr/local/nagiosxi/scripts/migrate/migrate.php` file showed that it requires three other PHP files: `constants.inc.php`, `config.inc.php`, and `bootstrap.php`.
  ![Root1.png](Root1.png)
- Checking the permissions of these three files revealed that two of them (`constants.inc.php` and `bootstrap.php`) were owned by the `nagios` user and were writable.
  ![Root2.png](Root2.png)
- We chose to target `bootstrap.php` and used `echo` to inject a PHP payload (`<?php chmod('/bin/bash', 04755); ?>`) into the file to add a SUID bit to `/bin/bash`. We then executed `sudo /usr/bin/php /usr/local/nagiosxi/scripts/migrate/migrate.php *`. The script threw some errors, but our injected PHP code successfully executed and set the SUID bit on the `/bin/bash` binary.
  ![Root3.png](Root3.png)
- Finally, we ran `/bin/bash -p`, which dropped us into a root shell, allowing us to capture the root flag.
  ![Root4.png](Root4.png)
