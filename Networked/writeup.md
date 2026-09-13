# Networked Writeup - by Thammanant Thamtaranon

**Networked** is an **Easy**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance

- We began the engagement with a full TCP port scan using Nmap to identify open services and fingerprint the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)

- The scan revealed the following open ports:
  * **22/tcp:** OpenSSH 7.4 (protocol 2.0)
  * **80/tcp:** Apache httpd 2.4.6 (CentOS) running PHP/5.4.16

---

## Scanning & Enumeration

- Visiting port 80, we found a simple homepage note.
  ![Port80.png](Port80.png)
- Running `dirsearch` for directory enumeration revealed `/backup`, `photos.php`, `upload.php`, and `/uploads`.
  ![Dirsearch.png](Dirsearch.png)
- Navigating to `/backup`, we discovered a `backup.tar` archive and downloaded it to our local machine for analysis.
  ![Backup1.png](Backup1.png)
- Visiting `photos.php`, we observed an image gallery displaying uploaded files.
  ![Photos.png](Photos.png)
- Navigating to `upload.php`, we located a file upload interface.
  ![Upload1.png](Upload1.png)
- We extracted `backup.tar` to inspect the source code of the web application.
  ![Backup2.png](Backup2.png)
- Analyzing `upload.php`, we identified the validation checks performed on uploaded files:
  ![Upload2.png](Upload2.png)

**Source Code Logic Breakdown:**
1. **File Size & Magic Bytes:** `check_file_type()` verifies image magic bytes, while `filesize()` enforces a maximum file size of 60,000 bytes (~60 KB).
2. **Extension Validation:** `substr_compare()` checks whether the raw filename ends with an allowed extension (`.jpg`, `.png`, `.gif`, `.jpeg`).
3. **File Renaming Logic:** `getnameUpload()` splits the filename on the first dot (`.`), placing everything after it into `$ext`.

**Bypass Strategy:**
1. Use a valid PNG file header (magic bytes) to pass `check_file_type()`.
2. Keep the overall file size under 60 KB.
3. Append a PHP payload beneath the magic bytes section.
4. Name the file `cat.php.png`. This satisfies the extension check (it ends in `.png`), while `getnameUpload()` extracts `php.png` as `$ext`, so the saved file becomes `10_10_16_49.php.png`.

---

## Exploitation

- We created a test file satisfying the magic bytes and size constraints, to confirm the upload feature worked before adding a payload.
  ![Uploaded1.png](Uploaded1.png)
- We confirmed successful upload and rendering in `photos.php`.
  ![Uploaded2.png](Uploaded2.png)
- We then uploaded our PHP web shell, disguised as `cat.php.png`.
  ![WebShell1.png](WebShell1.png)
- The gallery confirmed the new upload, saved server-side as `10_10_16_49.php.png`.
  ![WebShell2.png](WebShell2.png)
- We confirmed remote code execution by passing `?cmd=id` to our shell, obtaining output as the `apache` user.
  ![ID.png](ID.png)
- We used Penelope to generate a base64-encoded reverse-shell one-liner and executed it through our web shell's `?cmd=` parameter, upgrading our access into an interactive session.
  ![Apache.png](Apache.png)

---

## Privilege Escalation
- Enumerating user home directories, we found a cron job script (`check_attack.php`) and its crontab configuration (`crontab.guly`) inside `/home/guly`.
  ![Script.png](Script.png)

**Script Mechanics:**
* A system cron job executes `php /home/guly/check_attack.php` every 3 minutes.
* The script iterates through files in `/var/www/html/uploads/` using `scandir()`.
* For files failing IP format verification, the script invokes system commands via `exec()`: `exec("nohup /bin/rm -f $path$value > /dev/null 2>&1 &");`
* Because `$value` (the filename) is directly interpolated into `exec()` without sanitization, filenames containing shell command separators (`;`) execute arbitrary commands as user `guly`.

- We validated command injection by creating a file named `;touch success.txt` inside `/var/www/html/uploads/`.
  ![Command1.png](Command1.png)
- After the cron job executed, `success.txt` was created in `/home/guly`, confirming code execution.
- We generated a base64-encoded reverse shell payload:
  ![Command2.png](Command2.png)
- We created a file designed to decode and execute our reverse shell upon processing.
  ![Command3.png](Command3.png)
- Our listener caught the incoming connection, granting us a shell as user `guly`.
  ![Guly.png](Guly.png)
- We retrieved the **User flag**. To maintain shell stability, we added our SSH public key to `/home/guly/.ssh/authorized_keys` and logged in over SSH.
  ![SSH1.png](SSH1.png)
  ![SSH2.png](SSH2.png)
  ![SSH3.png](SSH3.png)

- Running `sudo -l`, we observed that user `guly` can run `/usr/local/sbin/changename.sh` as `root` without a password.
  ![SUDO.png](SUDO.png)
- We inspected the contents of `changename.sh`:
  ![Changename.png](Changename.png)

**Script Mechanics & Vulnerability:**
* The script prompts for network configuration variables (`NAME`, `PROXY_METHOD`, `BROWSER_ONLY`, `BOOTPROTO`) and appends them to `/etc/sysconfig/network-scripts/ifcfg-guly`.
* User input `$x` is validated against the regex `^[a-zA-Z0-9_\ /-]+$`, which permits space characters.
* At the end of execution, the script runs `/sbin/ifup guly0` as root.
* RedHat/CentOS network init scripts source their configuration files by evaluating them as shell snippets (`. /etc/sysconfig/network-scripts/ifcfg-guly`).
* Because the regex allows spaces, supplying `test /home/guly/test` as an answer writes a line like `NAME=test /home/guly/test` into `ifcfg-guly`. In Bash, `VAR=value command` sets `VAR` for the duration of `command` and then runs `command`. so sourcing this file runs `/home/guly/test` as root.

**Exploitation Steps:**

1. We created an executable script `/home/guly/test` containing a command to verify root execution.
  ![Root1.png](Root1.png)
2. We overwrote `/home/guly/test` with a payload that grants the SUID bit to `/bin/bash`.
3. We ran `sudo /usr/local/sbin/changename.sh` and entered `test /home/guly/test` at each of the four prompts.
  ![Root2.png](Root2.png)
4. `ifup` reported that device `guly0` doesn't exist, but by that point it had already sourced `ifcfg-guly`, which ran `/home/guly/test` as root and set the SUID bit on `/bin/bash` before that error was even reached.
5. We ran `/bin/bash -p` to drop into a root shell and captured the **Root flag**.
