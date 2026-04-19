# TheNotebook Writeup - by Thammanant Thamtaranon

**TheNotebook** is a **Medium**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- The engagement began with a full TCP port scan to identify open services and determine the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The results indicated that ports **22/tcp** (SSH) and **80/tcp** (HTTP) were open.

---

## Scanning & Enumeration
- Navigating to port 80 in the browser revealed the "Notebook" web application.
  ![Home.png](Home.png)
- Running a directory brute-force scan using `dirsearch` confirmed three main endpoints: `/admin`, `/register`, and `/login`. Access to `/admin` was forbidden for standard users.
  ![Dirsearch_Scan.png](Dirsearch_Scan.png)
  ![Register.png](Register.png)
  ![Login.png](Login.png)
  ![Forbidden.png](Forbidden.png)
- I registered a new user account and successfully logged in.
  ![Registered.png](Registered.png)
- After authenticating, I accessed the "Notes" tab, which allowed users to create notes with a title and body. I tested for several vulnerabilities, such as Cross-Site Scripting (XSS), but was unsuccessful.
  ![Note.png](Note.png)
- However, inspecting the HTTP request for my created note showed a parameter pointing to note ID `5`, suggesting there were at least four other notes stored on the application that might contain sensitive information.
  ![Note_Request.png](Note_Request.png)
- I also noticed the application assigned a JWT (JSON Web Token) for session management. Inspecting the JWT using `jwt.io` revealed a `kid` (Key ID) parameter in the header pointing to a localhost URL, indicating the server uses an RSA key pair to sign its tokens.
  ![Original_JWT.png](Original_JWT.png)
- This configuration is vulnerable to Key Injection. If we can host our own public key and force the server to fetch it via the `kid` parameter, we can forge a JWT signed with our own private key.
  
---

## Exploitation
- First, we generated our own RSA public and private key pair.
  ![New_RSA.png](New_RSA.png)
- Next, we used a JWT tampering tool to modify our existing token.
  ![Tamper_JWT1.png](Tamper_JWT1.png)
- We modified the JWT payload by changing the `admin_cap` value to `1` to elevate our privileges, and we changed the `kid` parameter in the header to point to our attacking machine's IP address, where we would host our newly generated public key.
  ![Tamper_JWT2.png](Tamper_JWT2.png)
- The tool then signed the forged JWT using our private key, and we opened a local HTTP server to allow the target web application to fetch our public key.
  ![Tamper_JWT3.png](Tamper_JWT3.png)
  ![Tamper_JWT4.png](Tamper_JWT4.png)
- Going back to the restricted `/admin` path, we replaced our session cookie with the newly forged JWT.
  ![Forbidden_Request.png](Forbidden_Request.png)
  ![Tamper_JWT_Request.png](Tamper_JWT_Request.png)
- The server fetched our public key, validated the forged token, and granted us access to the Admin Panel.
  ![Admin_Panel.png](Admin_Panel.png)
- Within the Admin Panel's notes section, we could view all notes stored on the server, including those created by other users.
  ![Admin_Notes.png](Admin_Notes.png)
- We found two critical clues in these notes. One mentioned a need to fix PHP execution, hinting at a potential file upload vulnerability allowing PHP web shells. Another note referenced backup files stored on the server.
  ![Clue1.png](Clue1.png)
  ![Clue2.png](Clue2.png)
- The Admin Panel featured an "Upload" tab. Based on the clues, I attempted to upload a PHP web shell, which successfully executed on the server.
  ![Web_Shell1.png](Web_Shell1.png)
  ![Web_Shell2.png](Web_Shell2.png)
- I used this web shell to execute a bash reverse shell payload, connecting back to my attacking machine and granting a shell as the `www-data` user.
  ![Rev_Shell1.png](Rev_Shell1.png)
  ![Rev_Shell2.png](Rev_Shell2.png)
- Reading the `/etc/passwd` file revealed a user named `noah`, who was likely our next target for lateral movement.
  ![PASSWD.png](PASSWD.png)
- Following up on the second clue, further enumeration revealed a `home.tar.gz` archive in a backups directory.
  ![Backups.png](Backups.png)
- I moved `home.tar.gz` to the `/tmp` directory and extracted it. The contents revealed it was a full backup of user `noah`'s home directory, which conveniently included his private SSH key.
  ![Noah_SSH.png](Noah_SSH.png)
- I copied the private SSH key to my machine, set the correct permissions, and successfully SSH'd into the machine as user `noah` to capture the `user.txt` flag.
  ![Noah.png](Noah.png)

---

## Privilege Escalation
- With a stable shell as `noah`, I ran `sudo -l` to check for elevated privileges. The output showed that `noah` was allowed to run `docker exec -it webapp-dev01*` commands as `root` without providing a password.
  ![SUDO.png](SUDO.png)
- Investigating the installed Docker version revealed it was outdated and vulnerable to **CVE-2019-5736**.
  ![Docker_Version.png](Docker_Version.png)
  ![CVE.png](CVE.png)
- **Understanding CVE-2019-5736:**
  This is a container breakout vulnerability within `runc`, the underlying container runtime used by Docker. When a privileged user on the host system (like root) uses `docker exec` to enter an existing container, the container processes can interact with the host's `runc` binary via `/proc/self/exe`. A malicious container can exploit this to overwrite the host's `runc` executable, allowing the attacker to execute arbitrary code on the host machine with root privileges.
- To exploit this, I downloaded a well-known PoC exploit written by Frichetten from GitHub.
- I compiled the exploit, started a Python HTTP server on my attacking machine, and waited to transfer the binary.\
  ![PoC1.png](PoC1.png)
  ![PoC2.png](PoC2.png)
- **Exploitation Steps:**
  1. Using my current SSH session, I utilized `docker exec -it webapp-dev01 bash` to gain a shell inside of the running container.
  2. Inside the container, I downloaded my compiled exploit binary and executed it. The exploit hung, waiting for the `/bin/sh` process to be invoked by the host.
  ![PoC3.png](PoC3.png)
  3. I opened a second terminal window, connected back to the target via SSH as `noah`, and executed `sudo docker exec -it webapp-dev01 sh`. 
  ![PoC4.png](PoC4.png)
- The moment the host ran the `docker exec` command, the payload inside the container triggered, successfully breaking out and setting the SUID bit on the host's `/bin/bash` binary.
- Returning to my host shell, I simply ran `/bin/bash -p` to drop into a high-privileged root shell and captured the `root.txt` flag.
