import os
import re
import hashlib
import secrets
import datetime
import sqlite3
import pandas as pd
import gradio as gr

# ==========================================
# 0. GLOBAL STORAGE CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.environ.get("POLY_DB_PATH", os.path.join(SCRIPT_DIR, "poly_med_tracker.db"))

HARDCODED_ADMIN_USER = "BeverlyCrusher"
HARDCODED_ADMIN_PASS = "Crusher22BetaCharlie"

# ==========================================
# 1. DATABASE & SECURITY INITIALIZATION
# ==========================================
def hash_password(password, salt=None):
    """Generates a secure cryptographically salted SHA-256 password hash."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"

def verify_password(stored_string, provided_password):
    """Matches a login password against a saved database hash string."""
    try:
        if not stored_string or "$" not in stored_string:
            return False
        salt, hashed = stored_string.split("$")
        check = hashlib.sha256((salt + provided_password).encode('utf-8')).hexdigest()
        return secrets.compare_digest(check, hashed)
    except Exception:
        return False

def init_db():
    """Initializes tables using safe migration steps to guarantee column presence."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Secure User Registry Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT
            )
        ''')
        
        # Check if table exists and has correct columns. If not, rebuild safely.
        try:
            cursor.execute("SELECT m1 FROM profiles LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("DROP TABLE IF EXISTS profiles")
            
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                dose_count INTEGER,
                t1 TEXT, m1 TEXT, 
                t2 TEXT, m2 TEXT, 
                t3 TEXT, m3 TEXT, 
                t4 TEXT, m4 TEXT, 
                t5 TEXT, m5 TEXT
            )
        ''')
        
        # Safe table build for compliance history tracking logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT, timestamp TEXT, time_of_day TEXT, dose_index INTEGER,
                compliance TEXT, metric_type TEXT, metric_value TEXT, sleep_score INTEGER, mood TEXT
            )
        ''')
        conn.commit()

init_db()

# ==========================================
# 2. GRADIO SESSION AUTHENTICATION MIDDLEWARE
# ==========================================
def poly_authenticator(username, password):
    """Validates login credentials via environment variables, hardcoded admin, or database."""
    env_admin_user = os.environ.get("POLY_ADMIN_USER", HARDCODED_ADMIN_USER)
    env_admin_pass = os.environ.get("POLY_ADMIN_PASS", HARDCODED_ADMIN_PASS)
    if username == env_admin_user and password == env_admin_pass:
        return True
                        
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        # FIXED: Extract string out of database tuple wrapper using row[0]
        if row and verify_password(row[0], password):
            return True
            
    return False

def is_admin(username):
    """Identifies if the current logged-in identity is the administrator."""
    env_admin_user = os.environ.get("POLY_ADMIN_USER", HARDCODED_ADMIN_USER)
    return username == env_admin_user

# ==========================================
# 3. DATABASE UTILITY FUNCTIONS
# ==========================================
def add_new_user_db(username, password):
    """Hashes a new user's password and safely inserts them into the DB."""
    clean_username = username.strip()
    if not clean_username or not password.strip():
        return "❌ Error: Username and password fields cannot be left blank."
    if is_admin(clean_username):
        return "❌ Error: Cannot override system administrator identity permissions."
        
    h_str = hash_password(password)
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (clean_username, h_str))
            conn.commit()
        return f"✅ Secure user '{clean_username}' successfully registered and hashed!"
    except sqlite3.IntegrityError:
        return "❌ Error: This username is already registered in Poly's system database."

def delete_user_db(username):
    """Removes a user and their profiles/logs entirely from the database environment."""
    clean_username = username.strip()
    if not clean_username:
        return "❌ Error: Please specify a username to delete."
    if is_admin(clean_username):
        return "❌ Error: Cannot delete the master system administrator."
        
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (clean_username,))
        if not cursor.fetchone():
            return f"❌ Error: User '{clean_username}' does not exist."
            
        cursor.execute("DELETE FROM users WHERE username = ?", (clean_username,))
        cursor.execute("DELETE FROM profiles WHERE username = ?", (clean_username,))
        cursor.execute("DELETE FROM logs WHERE username = ?", (clean_username,))
        conn.commit()
    return f"🗑️ User '{clean_username}' and all associated logs/profiles successfully deleted."

def list_system_users():
    """Fetches a list of all patient usernames currently stored in the database."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query("SELECT username FROM users ORDER BY username ASC", conn)
    if df.empty:
        return pd.DataFrame(columns=["Registered Usernames"])
    df.columns = ["Registered Users)"]
    return df

def get_user_profile(username):
    """Safely retrieves a user profile, matching the interface layout parameters exactly."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT dose_count, t1, m1, t2, m2, t3, m3, t4, m4, t5, m5 FROM profiles WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row and len(row) >= 11:
            return {
                "count": int(row[0]) if row[0] is not None else 1,
                "slots": [
                    (row[1] or "07:00", row[2] or ""), 
                    (row[3] or "", row[4] or ""), 
                    (row[5] or "", row[6] or ""), 
                    (row[7] or "", row[8] or ""), 
                    (row[9] or "", row[10] or "")
                ]
            }
    return {"count": 1, "slots": [("07:00", ""), ("", ""), ("", ""), ("", ""), ("", "")]}

def save_user_profile_db(username, count, t_vals, m_vals):
    """Pads parameter lists and explicitly extracts individual strings for column storage."""
    t_padded = list(t_vals) + [""] * (5 - len(t_vals))
    m_padded = list(m_vals) + [""] * (5 - len(m_vals))
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profiles (username, dose_count, t1, m1, t2, m2, t3, m3, t4, m4, t5, m5)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                dose_count=excluded.dose_count,
                t1=excluded.t1, m1=excluded.m1, 
                t2=excluded.t2, m2=excluded.m2, 
                t3=excluded.t3, m3=excluded.m3, 
                t4=excluded.t4, m4=excluded.m4, 
                t5=excluded.t5, m5=excluded.m5
        ''', (
            username, int(count), 
            t_padded[0], m_padded[0], 
            t_padded[1], m_padded[1], 
            t_padded[2], m_padded[2], 
            t_padded[3], m_padded[3], 
            t_padded[4], m_padded[4]
        ))
        conn.commit()
    return "✅ Poly saved your profile!"

def find_closest_dose(profile, username):
    """Calculates the closest dose within 1 hour, prioritizing the next unlogged slot."""
    now = datetime.datetime.now()
    count = profile["count"]
    
    # Track the best slot available
    best_idx = None
    min_delta = datetime.timedelta(hours=1) # 1-hour lookup window threshold boundary
    
    unlogged_slots = []
    
    # 1. First Pass: Collect all unlogged slots for today
    for i in range(count):
        if i >= len(profile["slots"]):
            continue
        t_str, m_str = profile["slots"][i]
        if not t_str or not re.match(r"^\d{2}:\d{2}$", t_str.strip()):
            continue
            
        dose_num = i + 1
        # Check if already taken today
        if not check_duplicate_dose(username, dose_num):
            unlogged_slots.append((dose_num, t_str, m_str))
            
    # 2. Sequential Logic: If Dose 1 was logged, immediately present Dose 2 next if unlogged
    if unlogged_slots:
        # Check proximity of the remaining unlogged items
        for dose_num, t_str, m_str in unlogged_slots:
            try:
                h, m = map(int, t_str.split(":"))
                target_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
                delta = abs(now - target_time)
                
                # Check if it fits securely within our 6-hour context tracking window
                if delta <= min_delta:
                    min_delta = delta
                    best_idx = dose_num
            except ValueError:
                continue
                
        # If something falls within the time window, use it
        if best_idx is not None:
            t_val, m_val = profile["slots"][best_idx - 1]
            return best_idx, t_val, m_val if m_val else " "
            
        # Fallback: If outside time window but unlogged things remain, serve the very next unlogged option right away
        next_dose, t_val, m_val = unlogged_slots[0]
        return next_dose, t_val, m_val if m_val else " "

    # 3. Complete Fallback: If all configured items are already checked in for today
    return 1, "DONE!", "All scheduled daily doses checked in. Great job! \n## Check back tomorrow."


def check_duplicate_dose(username, dose_idx):
    if dose_idx is None:
        return False
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp FROM logs WHERE username = ? AND dose_index = ? AND timestamp LIKE ?
        ''', (username, int(dose_idx), f"{today_str}%"))
        return cursor.fetchone() is not None

def log_checkin(username, tod, compliance, metric_type, metric_val, sleep, mood, dose_idx):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_dose_idx = int(dose_idx) if dose_idx is not None else 1
    
    if check_duplicate_dose(username, final_dose_idx):
        return f"❌ Submission Blocked: You have already did a check-in for Dose #{final_dose_idx} today."
    if metric_type == "Blood Pressure (120/70)" and metric_val:
        if not re.match(r"^\d{2,3}/\d{2,3}$", str(metric_val).strip()):
            return "❌ Validation Error: Blood pressure must follow standard format (e.g., 120/80)."
            
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (username, timestamp, time_of_day, compliance, metric_type, metric_value, sleep_score, mood, dose_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, now, tod, compliance, metric_type, str(metric_val) if metric_type != "None" else None, sleep, mood, final_dose_idx))
        conn.commit()
    return f"🦜 Poly successfully saved your check-in data logs at {now}!"

def fetch_logs_dataframe(username, selected_columns):
    with sqlite3.connect(DB_FILE) as conn:
        query = "SELECT timestamp, time_of_day, dose_index, compliance, metric_type, metric_value, sleep_score, mood FROM logs WHERE username = ? ORDER BY timestamp DESC"
        df = pd.read_sql_query(query, conn, params=(username,))
    if df.empty:
        return pd.DataFrame(columns=["timestamp"] + (selected_columns if selected_columns else []))
    if selected_columns:
        if "timestamp" not in selected_columns:
            selected_columns = ["timestamp"] + selected_columns
        return df[[c for c in selected_columns if c in df.columns]]
    return df

def export_data_to_file(username, selected_columns):
    df = fetch_logs_dataframe(username, selected_columns)
    if df.empty:
        return None, "⚠️ Zero data entries are currently log-indexed."
    filepath = f"{username}_poly_health_export.csv"
    df.to_csv(filepath, index=False)
    return filepath, f"🦜 Poly compiled your health report file source ({len(df)} rows)."

def get_time_of_day_context():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: return "Morning"
    elif 12 <= hour < 17: return "Mid-day"
    else: return "Night"

# ==========================================
# 4. GRADIO DYNAMIC RENDER PIPELINE
# ==========================================
def render_dynamic_dashboard(request: gr.Request):
    """Calculates context elements at login and maps structural UI elements safely."""
    username = request.username
    profile = get_user_profile(username)
    tod = get_time_of_day_context()
    
    # FIXED: Added request.username parameter context to search logs on the fly
    dose_idx, t_target, m_target = find_closest_dose(profile, username)
    is_dup = check_duplicate_dose(username, dose_idx)
    
    greeting = f"## Welcome back, **{username}**: {tod} Time Check-In"
    dup_warning = f"## ✅ **GREAT JOB!**: \nYou have already did a check-in for **Dose #{dose_idx} ({t_target})** today. \nNo need to submit anything right now." if is_dup else ""
    med_info = f"## 💊 Dose #{dose_idx} @ {t_target}]: {m_target}"
    
    return greeting, med_info, gr.update(visible=(dose_idx == 1)), gr.update(visible=(tod in ["Mid-day", "Night"] and dose_idx > 1)), f"## 🦜", dose_idx, dup_warning




# ==========================================
# 5. GRADIO INTERFACE DESIGN
# ==========================================
with gr.Blocks(title="Poly 🦜 | Med Manager") as demo:
    with gr.Row():
        with gr.Column(scale=8):
            gr.Markdown("# 🦜 Poly: Medication & Wellness Manager")
        with gr.Column(scale=2, min_width=120):
            gr.HTML(
                '<a href="/logout" style="'
                'display: block; text-align: center; background-color: #ef4444; '
                'color: white; padding: 10px 14px; border-radius: 8px; '
                'text-decoration: none; font-weight: bold; font-size: 14px; '
                'box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 15px;'
                '">🚪 Log Out</a>'
            )
            
    with gr.Tabs():
        # --- TAB 1: DAILY CHECK-IN ---
        with gr.TabItem("🕒 Daily Check-In"):
            user_greeting, duplicate_banner, user_med_summary = gr.Markdown(), gr.Markdown(), gr.Markdown()
            tracked_dose_index_state = gr.Number(visible=False, precision=0, value=1)
            
            with gr.Row():
                compliance_radio = gr.Radio(choices=["Yes, Taken", "Forgot", "Skipped"], label="Have you taken this dose yet?", value="Yes, Taken")
                dose_label_mapping = gr.Markdown("Loading calculations...")

            with gr.Group(visible=False) as morning_box:
                gr.Markdown("### 🌅 Morning Sleep Log")
                sleep_slider = gr.Slider(0, 10, value=7, step=1, label="Sleep Quality (0=Poor, 10=Excellent)")
                with gr.Row():
                    btn_poor, btn_avg, btn_great = gr.Button("😩 Poor (2)"), gr.Button("😐 Average (5)"), gr.Button("🤩 Great (9)")
                btn_poor.click(lambda: 2, outputs=sleep_slider)
                btn_avg.click(lambda: 5, outputs=sleep_slider)
                btn_great.click(lambda: 9, outputs=sleep_slider)

                
            with gr.Group(visible=False) as mood_box:
                gr.Markdown("### 🧠 Mood Tracking")
                selected_mood_state = gr.Textbox(label="Selected Mood", value="😐 Neutral", interactive=False)

                mood_options = [
                    ("😊", "Happy"), ("😢", "Sad"), ("😰", "Anxious"),
                    ("😨", "Afraid"), ("😐", "Neutral"), ("😫", "Stressed"),
                    ("😡", "Angry"), ("😤", "Frustrated"), ("😴", "Tired"),
                    ("⚡", "Energetic")
                ]

                # Display first 5 moods in one row
                with gr.Row():
                    for emoji, name in mood_options[:5]:
                        gr.Button(f"{emoji}\n{name}").click(
                            fn=lambda e=emoji, n=name: f"{e} {n}",
                            outputs=selected_mood_state
                        )
                  
                # Display remaining moods in another row
                with gr.Row():
                    for emoji, name in mood_options[5:]:
                        gr.Button(f"{emoji}\n{name}").click(
                            fn=lambda e=emoji, n=name: f"{e} {n}",
                            outputs=selected_mood_state
                        ) 

            with gr.Group():
                gr.Markdown("### 📊 Optional Data")
                vitals_type = gr.Radio(["None", "Blood Pressure (120/80)", "Blood Sugar (mg/dL)", "Other (Symptoms)"], label="Log a Vital Sign", value="None")
                vitals_value = gr.Textbox(label="Enter Value (e.g., 120/80 or 95)", visible=False)
                
                def handle_vitals_visibility(choice):
                    return gr.update(visible=(choice != "None"))
                vitals_type.change(handle_vitals_visibility, inputs=vitals_type, outputs=vitals_value)

            submit_btn = gr.Button("🔒 Let's Check-In!", variant="primary")
            
            with gr.Group(visible=False) as confirmation_container:
                gr.Markdown("### ⚠️ Confirm Submission:")
                with gr.Row():
                    confirm_yes, confirm_no = gr.Button("✅ Confirm & Save Data", variant="primary"), gr.Button("❌ Cancel Request", variant="stop")
            
            action_status = gr.Markdown()
            
            def open_confirmation():
                return gr.update(visible=True)
            submit_btn.click(open_confirmation, outputs=confirmation_container)
            
            def close_confirmation():
                return gr.update(visible=False), "❌ Submission cancelled."
            confirm_no.click(close_confirmation, outputs=[confirmation_container, action_status])

            def process_submission(request: gr.Request, compliance, v_type, v_val, sleep, mood, dose_idx):
                tod = get_time_of_day_context()
                # 1. Log the check-in entry to the SQLite database
                result = log_checkin(
                    request.username,
                    tod,
                    compliance,
                    v_type,
                    v_val,
                    sleep if dose_idx == 1 else None,  # sleep only if dose_idx == 1
                    mood if dose_idx != 1 else None,   # mood only if dose_idx != 1
                    dose_idx
                )
                
                # 2. Recalculate profile timeline metrics immediately for the next screen view state
                profile = get_user_profile(request.username)
                next_dose, t_target, m_target = find_closest_dose(profile, request.username)
                is_dup = check_duplicate_dose(request.username, next_dose)
                
                # 3. Compile updated layout components to refresh on screen seamlessly
                greeting = f"## Welcome back: {tod} Time Check-In"
                dup_banner_text = f"## ✅ **GREAT JOB!**: \nYou have already did a check-in for **Dose #{dose_idx} ({t_target})** today. \nNo need to submit anything right now." if is_dup else ""
                med_summary_text = f"## 💊 Dose #{next_dose} @ {t_target} - {m_target}"
                dose_string_text = f"## Dose #{next_dose}: {m_target}"
                
                return (
                    gr.update(visible=False),    # Hides confirmation container box 
                    result,                      # Outputs status message toast
                    greeting,                    # Refreshes user greeting string
                    med_summary_text,            # Advances medication regimen string text
                    gr.update(visible=(dose_idx == 1)), # Sleep only for dose 1
                    gr.update(visible=(dose_idx > 1)),  # Mood for all else
                    dose_string_text,            # Advances active compliance checkbox string promp
                    next_dose,                   # Updates tracked internal step count tracking box
                    dup_banner_text              # Drops duplicate banner warn indicator if needed
                )

            confirm_yes.click(
                process_submission, 
                inputs=[compliance_radio, vitals_type, vitals_value, sleep_slider, selected_mood_state, tracked_dose_index_state], 
                outputs=[
                    confirmation_container, action_status, 
                    user_greeting, user_med_summary, 
                    morning_box, mood_box, 
                    dose_label_mapping, tracked_dose_index_state, 
                    duplicate_banner
                ]
            )


        # --- TAB 2: EXPORT & HISTORY ---
        with gr.TabItem("📊 Data Export"):
            gr.Markdown("### 📂 Export Your Historical Log Data from Poly")
            column_selectors = gr.CheckboxGroup(choices=["time_of_day", "dose_index", "compliance", "metric_type", "metric_value", "sleep_score", "mood"], value=["time_of_day", "dose_index", "compliance", "metric_type", "metric_value"], label="Choose Columns to View & Export")
            refresh_btn, history_table = gr.Button("🔄 Refresh Data Table"), gr.DataFrame(interactive=False)
            export_btn, download_file, export_status = gr.Button("📥 Generate Downloadable CSV File", variant="secondary"), gr.File(label="Download File"), gr.Markdown()

            def handle_refresh(request: gr.Request, cols):
                return fetch_logs_dataframe(request.username, cols)

            def handle_export(request: gr.Request, cols):
                return export_data_to_file(request.username, cols)

            refresh_btn.click(handle_refresh, inputs=[column_selectors], outputs=history_table)
            export_btn.click(handle_export, inputs=[column_selectors], outputs=[download_file, export_status])

        # --- TAB 3: PROFILE SETTINGS ---
        with gr.TabItem("📋 Medication Setup"):
            gr.Markdown("### 📅 Medication Schedule")
            dose_count_slider = gr.Slider(1, 5, step=1, value=1, label="Number of Daily Doses")
            
            time_boxes, med_boxes = [], []
            row_groups = []
            
            for i in range(5):
                with gr.Group(visible=(i == 0)) as grp:
                    gr.Markdown(f"#### ⏱️ Dose #{i+1}")
                    time_boxes.append(gr.Textbox(label=f"Dose #{i+1} Time (Format: HH:MM)", value="08:00" if i==0 else ""))
                    med_boxes.append(gr.Textbox(label=f"Medications for Dose #{i+1}", placeholder="e.g., Lisinopril 20mg"))
                    row_groups.append(grp)

            def handle_visibility_change(count):
                return [gr.update(visible=(idx < count)) for idx in range(5)]
                
            dose_count_slider.change(handle_visibility_change, inputs=dose_count_slider, outputs=row_groups)
            
            save_profile_btn = gr.Button("💾 Save Changes to Poly")
            with gr.Group(visible=False) as profile_confirm_container:
                gr.Markdown("### ⚠️ Confirm Profile Changes:")
                with gr.Row():
                    profile_yes, profile_no = gr.Button("✅ Confirm Changes", variant="primary"), gr.Button("❌ Cancel Configuration", variant="stop")
            
            profile_status = gr.Markdown()
            save_profile_btn.click(open_confirmation, outputs=profile_confirm_container)
            
            def cancel_profile_edit():
                return gr.update(visible=False), "❌ Action Cancelled."
            profile_no.click(cancel_profile_edit, outputs=[profile_confirm_container, profile_status])

            def load_profile_on_view(request: gr.Request):
                p = get_user_profile(request.username)
                return [p["count"]] + [val for slot in p["slots"] for val in slot]

            def execute_profile_save(request: gr.Request, count, *all_args):
                half = len(all_args) // 2
                t_vals = list(all_args[:half])
                m_vals = list(all_args[half:])
                msg = save_user_profile_db(request.username, count, t_vals, m_vals)
                return gr.update(visible=False), msg

            profile_yes.click(execute_profile_save, inputs=[dose_count_slider] + time_boxes + med_boxes, outputs=[profile_confirm_container, profile_status])

        # --- TAB 4: ADMINISTRATOR CONTROLS ---
        with gr.TabItem("🔐 Admin Portal", visible=False) as admin_tab:
            gr.Markdown("### 👥 Add New Users to Poly.")
            
            with gr.Row():
                with gr.Column(scale=5):
                    gr.Markdown("#### ➕ Add New Secure Patient Account")
                    new_user_input = gr.Textbox(label="Create Username", placeholder="e.g., patient_gamma")
                    new_pass_input = gr.Textbox(label="Set Password", placeholder="••••••••••••")
                    register_btn = gr.Button("➕ Register Credentials Securely", variant="primary")
                    admin_status = gr.Markdown()
                
                with gr.Column(scale=5):
                    gr.Markdown("#### 🗑️ Remove User Account From System")
                    user_to_delete_input = gr.Textbox(label="Type Username to Delete", placeholder="e.g., patient_gamma")
                    delete_btn = gr.Button("🗑️ Permanently Delete User & Records", variant="stop")
                    delete_status = gr.Markdown()
            
            gr.Markdown("### 📋 Active System Users")
            refresh_users_btn = gr.Button("🔄 Refresh Users Directory Table")
            users_directory_table = gr.DataFrame(interactive=False)

            def handle_user_onboarding(username, password):
                msg = add_new_user_db(username, password)
                return msg, list_system_users()

            def handle_user_removal(username):
                msg = delete_user_db(username)
                return msg, list_system_users()

            register_btn.click(handle_user_onboarding, inputs=[new_user_input, new_pass_input], outputs=[admin_status, users_directory_table])
            delete_btn.click(handle_user_removal, inputs=[user_to_delete_input], outputs=[delete_status, users_directory_table])
            refresh_users_btn.click(list_system_users, outputs=users_directory_table)

    # Bind active session listeners
    demo.load(render_dynamic_dashboard, outputs=[user_greeting, user_med_summary, morning_box, mood_box, dose_label_mapping, tracked_dose_index_state, duplicate_banner])
    
    flattened_boxes = []
    for t, m in zip(time_boxes, med_boxes):
        flattened_boxes.extend([t, m])
    demo.load(load_profile_on_view, outputs=[dose_count_slider] + flattened_boxes)
    
    def check_admin_visibility(request: gr.Request):
        return gr.update(visible=is_admin(request.username)), list_system_users()
    demo.load(check_admin_visibility, outputs=[admin_tab, users_directory_table])

if __name__ == "__main__":
    demo.launch(auth=poly_authenticator, theme=gr.themes.Soft(), server_name="0.0.0.0", server_port=7436)
