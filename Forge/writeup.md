# Forge Writeup - by Thammanant Thamtaranon

**Forge** is a **Medium**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- The engagement began with a full TCP port scan to identify open services and determine the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The results indicated the following open ports:
  * **22/tcp:** SSH (OpenSSH 8.2p1 Ubuntu)
  * **80/tcp:** HTTP (Apache httpd 2.4.41)
- I added `forge.htb` to my local `/etc/hosts` file to interact with the web application properly.

---

## Scanning & Enumeration
- I used `dirsearch` to enumerate directories on port 80 and discovered an `/uploads` endpoint.
  ![Dirsearch_Scan.png](Dirsearch_Scan.png)
- Next, I used `ffuf` for virtual host (vhost) enumeration and successfully identified `admin.forge.htb`. I added this to my `/etc/hosts` file as well.
  ![VHost.png](VHost.png)
- Visiting `http://forge.htb` showed a gallery of pictures and an "Upload an image" page.
  ![Main_Page.png](Main_Page.png)
  ![Upload_Page.png](Upload_Page.png)
- Attempting to visit `http://admin.forge.htb` returned an error stating that the page could only be accessed from `localhost`.
  ![Admin_Page1.png](Admin_Page1.png)
- The upload page presented two options: uploading a local file or uploading via a URL. Testing the local file upload revealed that the application changes the file name and strips the extension. Since the admin panel is restricted to localhost, I attempted a Server-Side Request Forgery (SSRF) attack via the URL upload feature, but URL payloads pointing to `forge.htb` were blocked by a blacklist.
  ![Local_Upload.png](Local_Upload.png)
  ![Blacklist.png](Blacklist.png)

---

## Exploitation
- I managed to bypass the SSRF blacklist by using uppercase lettering in the domain name.
  ![Bypass.png](Bypass.png)
- By downloading the resulting image file, which was actually the HTML response, I revealed a link to a hidden `/announcements` endpoint on the admin panel.
  ![SSRF_Admin.png](SSRF_Admin.png)
- I repeated the SSRF technique to fetch the `/announcements` page.
  ![Admin_Page2.png](Admin_Page2.png)
  ![Announcements_Page.png](Announcements_Page.png)
- The `/announcements` page revealed internal FTP credentials (`user:heightofsecurity123!`) and explicitly mentioned that the upload endpoint supports the `ftp://` protocol (which is restricted externally but works internally).
- I attempted to SSH into the machine using these credentials, but the server was configured to only accept RSA key authentication.
  ![SSH_Failed.png](SSH_Failed.png)
- To obtain this SSH RSA key, I combined the SSRF vulnerability with the newly discovered FTP credentials using the payload: `http://admin.Forge.htb/upload?u=ftp://user:heightofsecurity123!@10.129.30.46/`.
  ![SSRF_FTP.png](SSRF_FTP.png)
- This allowed me to list the contents of the user's home directory, revealing the `user.txt` flag. I downloaded and captured the user flag.
  ![User_Flag.png](User_Flag.png)
- To gain a shell, I crafted another SSRF FTP request to retrieve the user's private SSH key.
  ![SSRF_FTP_RSA.png](SSRF_FTP_RSA.png)
- I downloaded the `id_rsa` key to my attacking machine, assigned it the proper permissions, and successfully SSH'd into the machine as the `user`.
  ![ID_RSA.png](ID_RSA.png)

---

## Privilege Escalation
- With a stable shell, I ran `sudo -l` to check for elevated privileges. The output showed that the user was allowed to execute the python script `/opt/remote-manage.py` as `root` without providing a password.
  ![SUDO.png](SUDO.png)
  ![Remote-manage.png](Remote-manage.png)
- Reading the source code of `/opt/remote-manage.py` revealed several critical functions:
  1. The script imports the `pdb` (Python Debugger) module.
  2. It opens a socket listening on localhost on a random port between 1025 and 65535.
  3. It requires a hardcoded secret password (`secretadminpassword`) to access a menu.
  4. The menu expects integer input (1-4) using `int()`.
  5. The entire program is wrapped in a `try-except` block. If an exception occurs, it triggers `pdb.post_mortem(e.__traceback__)`, dropping the user into an interactive debugging shell.
- To exploit this, I executed the script with `sudo` in my primary SSH session. It started listening on a local port.
- I opened a second SSH session, connected to the local port using `nc localhost 35837`, and entered the secret password to reach the menu.
- When prompted to choose an option, I intentionally sent a non-integer character (`a`). This caused a `ValueError` exception on the host script when it attempted to convert the string to an integer.
- Returning to my first SSH session, the exception had successfully triggered the `pdb` module, dropping me into an interactive `(Pdb)` shell running as root. 
- From the `(Pdb)` prompt, I imported the `os` module and executed a system command to set the SUID bit on the bash binary: `import os; os.system("chmod +s /bin/bash")`.
- After exiting the debugger, I confirmed the SUID bit was set with `ls -la /bin/bash`, executed `/bin/bash -p`, and successfully dropped into a high-privileged root shell to capture the `root.txt` flag.
![Root1.png](Root1.png)
![Root2.png](Root2.png)
