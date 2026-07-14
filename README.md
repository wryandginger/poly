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

### Check-In / Submit Data
![Daily Check-In](https://github.com/wryandginger/poly/blob/main/screenshots/checkin.png?raw=true))

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
<summary><b>🕸️ Option 2: Portainer Web UI Stack Deployment</b></summary>

### Step 1: Open Portainer Dashboard
Log into your local Portainer framework instance and navigate over to your primary deployment environment.

### Step 2: Create a New App Stack
1. Select **Stacks** from the sidebar and click **Add stack**.
2. Name your stack environment profile (e.g., `poly-medication-manager`).
3. Copy and paste the following recipe config directly inside the web interface **Web editor** field canvas block:

```yaml
services:
  poly-app:
    build: .
    container_name: poly_med_manager
    ports:
      - "7436:7436"
    environment:
      - TZ=America/Los_Angeles
      # Overrides the default admin credentials here:
      - POLY_ADMIN_USER=BeverlyCrusher
      - POLY_ADMIN_PASS=Crusher22BetaCharlie
      - POLY_DB_PATH=/data/poly_med_tracker.db
    volumes:
      # Maps a local folder named 'poly_data' on your computer to '/data' inside the container
      - ./poly_data:/data
    restart: unless-stopped
```

### Step 3: Deploy Stack
Scroll down to the footer actions menu block and press **Deploy the stack**. Your deployment runner environment initializes background layers automatically.

</details>

---

## 🔓 Defaults
* localhost:7436
* **Admin Username**: `BeverlyCrusher` *(Override using environment variable: `POLY_ADMIN_USER`)*
* **Admin Password**: `Crusher22BetaCharlie` *(Override using `POLY_ADMIN_PASS`)*
