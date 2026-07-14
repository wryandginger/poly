# 🦜 Poly: A Medication & Wellness Manager

Poly is a secure, context-aware medication tracking and compliance dashboard built with Python and Gradio. 

It handles multiple users or a whole family, tracking vitals and medications.

- ✨ I vibecoded Poly from Google's free AI mode, I'm sorry.
- ⚠️ Future edits are coming to clean up the UI and Python mess. 
- 🕵️ While I used AI to help me build this, this project does NOT interact with ANY generative AI service/system.
- ⓘ This is basic and simple. This is designed for homelab folks who need to manage multiple meds.
- 🏛️ I did a lot of philosophical work for you: It's morally fine, as long as you don't commercialize this, exploit me, or use Poly for evil.

- 🖨️ Pairs well with my 3D printable [Polypharmacy Kit](https://github.com/wryandginger/polypharmacy-kit)
---

## 🚀 Core Features

<details>
<summary><b>🔍 Features</b></summary>

* Context-Aware Data Tracking: Adjusts automatically to present sleep metrics in the morning and structured emotional grid selections during mid-day or night.
* Sedcured Data: Isolates user records dynamically using absolute relational database keys, preventing cross-profile lookups.
* Exportable Data: Filter and preview compliance history as a table right on the interface before downloading a customized CSV file you can share with a health provider.
* Admin User/Panel: Restricted management portal for system administrators/heads of household to add or delete users.

</details>

---

## 📸 Interface Previews

<details>
<summary><b>🖼️ Example Screenshots</b></summary>

### Check-In / Track Sleep
![Daily Check-In](https://github.com/wryandginger/poly/blob/main/screenshots/checkin.png?raw=true))

### Track Mood
![Daily Check-In](https://github.com/wryandginger/poly/blob/main/screenshots/mood.png?raw=true))

### Export
![Export Data](https://github.com/wryandginger/poly/blob/main/screenshots/export.png?raw=true))

### Setup
![Export Data](https://github.com/wryandginger/poly/blob/main/screenshots/setup.png?raw=true))

### Administrator Portal & Directory
![Admin User Manager]((https://github.com/wryandginger/poly/blob/main/screenshots/setup.png?raw=true))

</details>

---

## 🛠️ Installation & Deployment

Select your preferred platform setup method below to initialize your application environment instance.

<details>
<summary><b>🐳 Option 1: Docker CLI Deployment</b></summary>

### Step 1: Clone and Prepare Workspace
Move your `poly.py` file and your `Dockerfile` into a target deployment directory on your host engine.

### Step 2: Build and Run Container Instance
Execute the statement block below in your command-line workspace terminal interface. This binds storage variables and sets local timezone constraints matching your context targets:

```bash
docker run -d \
  --name poly_med_tracker \
  -p 7436:7436 \
  -e TZ=America/Los_Angeles \
  -e POLY_ADMIN_USER="ChiefMedicalOfficer" \
  -e POLY_ADMIN_PASS="UltraSecurePass2026!" \
  -e POLY_DB_PATH="/data/poly_med_tracker.db" \
  -v ./poly_data:/data \
  --restart unless-stopped \
  \$(docker build -q .)
```

</details>

<details>
<summary><b>🕸️ Option 2: Portainer Deployment</b></summary>

### Step 1: Open Portainer Dashboard
 - Create a New Web Stack via Git Repository
   - Navigate to your Portainer web portal dashboard.
   - Click on Stacks in the left sidebar menu, and press the Add stack button.
   - Under Build method, select Repository.
 - Configure Git Repository Settings:
   - Paste the repository path: https://github.com/wryandginger/poly/
   - Leave the rest as default in this top section.

### 🚨 Step 2: Adjust Environment Variables inside Portainer: 
  - Scroll down to the Environment variables configuration section on the page.
  - Click Add environment variable to   override your app's default login security values:
```
Set POLY_ADMIN_USER to your preferred username (e.g., Jane).
Set POLY_ADMIN_PASS to a strong unique credential password.
```

### Step 3: Deploy Stack
Scroll down to the footer actions menu block and press **Deploy the stack**. Your deployment runner environment initializes background layers automatically.


### Step 4: Verify/Change Your Host Local Volume Mount Points
  - Portainer deploys stack folders out of a default directory.
  - To change where your text templates and grade rules are permanently saved on your server's host file system, deploy the default project from github.
  - Then detach the stack from github.
  - You should then be able to change the docker-compose.yml properties or add host volume path adjustments.

</details>

---

## 🔓 Defaults
* localhost:7436
* **Admin Username**: `BeverlyCrusher` *(Override using environment variable: `POLY_ADMIN_USER`)*
* **Admin Password**: `Crusher22BetaCharlie` *(Override using `POLY_ADMIN_PASS`)*
