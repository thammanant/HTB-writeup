# Schooled Writeup - by Thammanant Thamtaranon

**Schooled** is a **Medium**-difficulty FreeBSD machine hosted on Hack The Box.

---

## Reconnaissance
- We started the engagement with a full TCP port scan using Nmap to identify open services and determine the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The results indicated the following open ports:
  * **22/tcp:** SSH (OpenSSH 7.9 FreeBSD)
  * **80/tcp:** HTTP (Apache httpd 2.4.46)
  * **33060/tcp:** mysqlx

---

## Scanning & Enumeration
- I started with a `dirsearch` scan on port 80, which discovered the endpoints `/about.html` and `/contact.html`.
  ![Dirsearch_Scan.png](Dirsearch_Scan.png)
- Visiting the IP address in a browser displayed a static webpage for an educational institution.
  ![Main_Page.png](Main_Page.png)
- Exploring the site didn't yield much functionality. The contact page had an input form, but submitting it simply redirected to a 404 page.
- However, scrolling down the main page, we noticed the domain name `schooled.htb`. I added this to my `/etc/hosts` file for proper resolution.
  ![VHost1.png](VHost1.png)
- Next, I ran a virtual host enumeration scan and successfully discovered `moodle.schooled.htb`. I added this subdomain to the `/etc/hosts` file as well.
  ![VHost2.png](VHost2.png)
- Visiting `moodle.schooled.htb` revealed a Moodle learning management system (LMS) with various classes available for enrollment.
  ![Moodle.png](Moodle.png)
- By enumerating the platform's files, I found the Moodle version (3.9) explicitly stated at `/moodle/lib/upgrade.txt`.
  ![Moodle_Version.png](Moodle_Version.png)
- Knowing the exact version, I researched potential vulnerabilities and found **CVE-2020-25627**, a Stored Cross-Site Scripting (XSS) vulnerability affecting the `moodleNetProfile` parameter in a user's profile.
  ![CVE-2020-25627.png](CVE-2020-25627.png)
- Realizing this was likely the intended vector to hijack a higher-privileged user's session, I searched further and found **CVE-2020-14321**. This vulnerability allows a teacher to assign themselves a manager role within a course, which can then be leveraged to upload malicious plugins and achieve Remote Code Execution (RCE).
  ![CVE-2020-14321.png](CVE-2020-14321.png)

---

## Exploitation
- With an exploitation path mapped out, I registered an account on the Moodle platform. Note that the registration process required an email address ending in `@student.schooled.htb`.
  ![Register.png](Register.png)
- After registering, we were able to log in as a student.
  ![Dashboard.png](Dashboard.png)
- I navigated to my profile settings and injected an XSS payload into the `MoodleNet profile` field, designed to steal the `MoodleSession` cookie and send it to my attacker machine. I then set up a Netcat listener to catch the callback.
  ![XSS1.png](XSS1.png)
- Exploring the platform further, I found that students could self-enroll in the Mathematics class. When I enrolled, the course teacher automatically viewed my newly added profile, triggering the stored XSS payload and sending their session cookie directly to my listener.
  ![XSS2.png](XSS2.png)
- I swapped my cookie with the stolen one, hijacking the session. We were now authenticated as the math teacher, Manuel Phillips.
  ![Teacher.png](Teacher.png)
- Following the documentation for **CVE-2020-14321**, I downloaded the proof-of-concept (PoC) exploit script. The script required a manager ID, a course ID, and the teacher's cookie.
  ![Priv_Esc1.png](Priv_Esc1.png)
- In the Moodle course settings, I clicked on the other user roles and found one user assigned as a manager. I added that user to my course to view their ID.
  ![Manager1.png](Manager1.png)
  ![Manager2.png](Manager2.png)
- This revealed the necessary parameters: the manager ID was `25` and the course ID was `5`.
  ![Manager3.png](Manager3.png)
- Having gathered all the required parameters, I executed the PoC exploit.
- The exploit successfully elevated our teacher account to a manager role, packed a malicious ZIP file, and uploaded it to the server via the Moodle plugins installation feature. The default payload runs the `whoami` command, which confirmed we had execution as the `www` user.
  ![Priv_Esc2.png](Priv_Esc2.png)
- I modified the exploit command to execute a reverse shell back to our machine.
  ![Priv_Esc3.png](Priv_Esc3.png)
- We successfully caught the shell and gained access to the FreeBSD machine as the user `www`.
  ![Priv_Esc4.png](Priv_Esc4.png)
- Checking the `/home` directory revealed two users on the system: `jamie` and `steve`.
  ![Users.png](Users.png)
- Enumerating the web directory, I found MySQL database credentials stored in the Moodle `config.php` file.
  ![MySQL_Credential.png](MySQL_Credential.png)
- I connected to the local MySQL service using these credentials.
  ![MySQL1.png](MySQL1.png)
  ![MySQL2.png](MySQL2.png)
- Dumping the `mdl_user` table revealed the password hash for the user `jamie`, who is an administrator on the Moodle site.
  ![Credentials.png](Credentials.png)
- I passed the hash to John the Ripper and successfully cracked it, retrieving Jamie's plaintext password.
  ![Cracked.png](Cracked.png)
- Using the cracked credentials, we SSH'd into the machine as `jamie` and captured the `user.txt` flag.
  ![Jamie.png](Jamie.png)

---

## Privilege Escalation
- Checking our privileges with `sudo -l`, we discovered that the user `jamie` can run `/usr/sbin/pkg update` and `/usr/sbin/pkg install *` as root without a password.
  ![SUDO.png](SUDO.png)
- I referenced GTFOBins and found a known privilege escalation vector for the `pkg` package manager on FreeBSD.
  ![GTFOBins.png](GTFOBins.png)
- The exploit involves creating a malicious shell command, packaging it into a FreeBSD `.txz` installation package using `fpm`, and then installing it via `sudo pkg install`. Upon installation, the package manager runs the embedded malicious script as root.
  ![Root1.png](Root1.png)
- My payload of choice was `chmod +s /bin/sh` to assign the SUID bit to the system shell. Because the target machine does not have `bash` installed, we relied on `/bin/sh` instead.
- Because the target machine also did not have `fpm` installed, I built the malicious `.txz` package on my attacker machine and transferred it to the target via `wget`. 
- After executing the `sudo pkg install` command against our malicious package, the installation script ran successfully. We simply executed `/bin/sh -p`, instantly dropping us into a root shell, where we captured the `root.txt` flag.
  ![Root2.png](Root2.png)
