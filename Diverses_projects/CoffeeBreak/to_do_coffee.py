import streamlit as st
from datetime import datetime, timedelta
import time
import base64
import os

# Page configuration
st.set_page_config(page_title="☕ Coffee Break To-Do List", page_icon="☕", layout="wide")

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []

if 'last_coffee_time' not in st.session_state:
    # Set first coffee at 8:15 AM today
    today = datetime.now().replace(hour=8, minute=15, second=0, microsecond=0)
    st.session_state.last_coffee_time = today

if 'time_bonus_minutes' not in st.session_state:
    st.session_state.time_bonus_minutes = 0

if 'coffees_today' not in st.session_state:
    st.session_state.coffees_today = 1  # First coffee at 8:15

if 'task_id_counter' not in st.session_state:
    st.session_state.task_id_counter = 0

# Task difficulty settings
TASK_CATEGORIES = {
    '☕ Easy (5 min bonus)': {'difficulty': 'Easy', 'time_bonus': 5, 'emoji': '🟢'},
    '☕☕ Medium (10 min bonus)': {'difficulty': 'Medium', 'time_bonus': 10, 'emoji': '🟡'},
    '☕☕☕ Hard (15 min bonus)': {'difficulty': 'Hard', 'time_bonus': 15, 'emoji': '🔴'}
}

COFFEE_INTERVAL_MINUTES = 120  # 2 hours between coffees

def calculate_next_coffee_time():
    """Calculate when the next coffee break is available"""
    base_next_time = st.session_state.last_coffee_time + timedelta(minutes=COFFEE_INTERVAL_MINUTES)
    next_time_with_bonus = base_next_time - timedelta(minutes=st.session_state.time_bonus_minutes)
    return next_time_with_bonus

def is_coffee_ready():
    """Check if it's time for a coffee break"""
    next_coffee = calculate_next_coffee_time()
    return datetime.now() >= next_coffee

def take_coffee_break():
    """Reset the coffee timer and increment counter"""
    st.session_state.last_coffee_time = datetime.now()
    st.session_state.time_bonus_minutes = 0
    st.session_state.coffees_today += 1

def add_task(task_name, category):
    """Add a new task to the list"""
    st.session_state.task_id_counter += 1
    task = {
        'id': st.session_state.task_id_counter,
        'name': task_name,
        'category': TASK_CATEGORIES[category]['difficulty'],
        'time_bonus': TASK_CATEGORIES[category]['time_bonus'],
        'emoji': TASK_CATEGORIES[category]['emoji'],
        'added_at': datetime.now()
    }
    st.session_state.tasks.append(task)

def complete_task(task_index):
    """Move task to completed and add time bonus"""
    task = st.session_state.tasks.pop(task_index)
    task['completed_at'] = datetime.now()
    st.session_state.completed_tasks.append(task)
    st.session_state.time_bonus_minutes += task['time_bonus']

def delete_task(task_index):
    """Remove a task without completing it"""
    st.session_state.tasks.pop(task_index)

def reset_day():
    """Clear all tasks and reset for a new day"""
    st.session_state.tasks = []
    st.session_state.completed_tasks = []
    st.session_state.time_bonus_minutes = 0
    st.session_state.task_id_counter = 0
    today = datetime.now().replace(hour=8, minute=15, second=0, microsecond=0)
    st.session_state.last_coffee_time = today
    st.session_state.coffees_today = 1

@st.cache_data
def get_image_base64(filename):
    """Load image from assets folder and return base64 encoded string (cached)"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, 'assets', filename)
    try:
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        return ""

def generate_coffee_mug_html(minutes_remaining):
    """Generate HTML/CSS coffee mug that fills based on time remaining"""
    # Calculate fill percentage (0% at 120 min, 100% at 0 min)
    fill_percentage = max(0, min(100, (120 - minutes_remaining) / 120 * 100))
    
    # Calibrate to visual range (60% to 90% of image height)
    min_height = 60
    max_height = 90
    visual_height = min_height + ((fill_percentage / 100) * (max_height - min_height))
    
    # Load mug images
    img_empty = get_image_base64('mug_empty.png')
    img_full = get_image_base64('mug_full.png')
    
    html = f"""
    <style>
        .mug-container {{
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto;
        }}
        .mug-base {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
            z-index: 1;
        }}
        .fill-container {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: {visual_height}%;
            overflow: hidden;
            z-index: 2;
            transition: height 0.5s ease;
        }}
        .mug-full {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 200px;
            object-fit: contain;
        }}
        .fill-text {{
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            color: #666;
            margin-top: 10px;
        }}
    </style>
    <div class="mug-container">
        <img src="data:image/png;base64,{img_empty}" class="mug-base">
        <div class="fill-container">
            <img src="data:image/png;base64,{img_full}" class="mug-full">
        </div>
    </div>
    <div class="fill-text">{int(fill_percentage)}%</div>
    """
    return html

# Main UI
st.title("☕ Coffee Break To-Do List")
st.markdown("*Complete tasks to earn your coffee breaks faster!*")

# Header with current time and coffee status
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric("Current Time", datetime.now().strftime("%H:%M"))

with col2:
    st.metric("Coffees Today", f"☕ × {st.session_state.coffees_today}")

# Calculate minutes left once (reused below)
next_coffee = calculate_next_coffee_time()
time_until_coffee = next_coffee - datetime.now()
minutes_left = max(0, int(time_until_coffee.total_seconds() / 60))

with col3:
    if is_coffee_ready():
        st.success("☕ COFFEE BREAK READY!")
        if st.button("☕ Take Coffee Break", type="primary"):
            take_coffee_break()
            st.rerun()
    else:
        st.metric("Next Coffee In", f"{minutes_left} min")

# Display coffee mug visualization
st.markdown("---")
col_left, col_center, col_right = st.columns([1, 1, 1])

with col_center:
    # Generate and display the coffee mug
    mug_html = generate_coffee_mug_html(minutes_left)
    st.components.v1.html(mug_html, height=260)
    
    if is_coffee_ready():
        st.markdown("### 🔥 **HOT & READY!** 🔥")
    else:
        st.markdown(f"### ⏳ {minutes_left} minutes until coffee")

st.markdown("---")

# Show time bonus accumulated
if st.session_state.time_bonus_minutes > 0:
    st.info(f"⚡ You've earned **{st.session_state.time_bonus_minutes} minutes** of coffee time bonus from completed tasks!")

st.divider()

# Add new task section
st.subheader("➕ Add New Task")

# Use a form to enable Enter key submission
with st.form(key="add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        task_name = st.text_input("Task description", placeholder="e.g., Write project report", label_visibility="collapsed", key="task_input")
    
    with col2:
        category = st.selectbox("Difficulty", options=list(TASK_CATEGORIES.keys()), label_visibility="collapsed", key="category_select")
    
    with col3:
        submit_button = st.form_submit_button("Add Task", type="primary", use_container_width=True)
    
    # Handle form submission
    if submit_button:
        if task_name.strip():
            add_task(task_name.strip(), category)
            st.rerun()
        else:
            st.error("Please enter a task name")

st.divider()

# Display active tasks
st.subheader(f"📋 Active Tasks ({len(st.session_state.tasks)})")

if len(st.session_state.tasks) == 0:
    st.info("No active tasks. Add one above to get started!")
else:
    for idx, task in enumerate(st.session_state.tasks):
        col1, col2, col3, col4 = st.columns([0.5, 3, 1.5, 1])
        
        with col1:
            st.write(task['emoji'])
        
        with col2:
            st.write(f"**{task['name']}**")
        
        with col3:
            st.caption(f"{task['category']} (+{task['time_bonus']} min)")
        
        with col4:
            col_complete, col_delete = st.columns(2)
            with col_complete:
                if st.button("✅", key=f"complete_{idx}", help="Complete task"):
                    complete_task(idx)
                    st.rerun()
            with col_delete:
                if st.button("❌", key=f"delete_{idx}", help="Delete task"):
                    delete_task(idx)
                    st.rerun()

st.divider()

# Completed tasks section
with st.expander(f"✅ Completed Tasks Today ({len(st.session_state.completed_tasks)})", expanded=False):
    if len(st.session_state.completed_tasks) == 0:
        st.info("No completed tasks yet. Keep going!")
    else:
        total_bonus = sum(task['time_bonus'] for task in st.session_state.completed_tasks)
        st.success(f"🎉 Great work! You've earned **{total_bonus} minutes** of coffee time bonuses total!")
        
        for task in reversed(st.session_state.completed_tasks):
            st.write(f"{task['emoji']} ~~{task['name']}~~ - *{task['category']} (+{task['time_bonus']} min)*")

# Sidebar with stats and controls
with st.sidebar:
    st.header("📊 Daily Statistics")
    
    st.metric("Active Tasks", len(st.session_state.tasks))
    st.metric("Completed Tasks", len(st.session_state.completed_tasks))
    st.metric("Total Time Earned", f"{sum(t['time_bonus'] for t in st.session_state.completed_tasks)} min")
    
    st.divider()
    
    st.header("⚙️ Controls")
    
    if st.button("🔄 Reset Day", use_container_width=True):
        reset_day()
        st.rerun()
    
    st.divider()
    
    st.header("ℹ️ How It Works")
    st.markdown("""
    **Coffee Schedule:**
    - First coffee: 8:15 AM ☕
    - Next coffees: Every 2 hours
    
    **Task Bonuses:**
    - 🟢 Easy: -5 minutes
    - 🟡 Medium: -10 minutes
    - 🔴 Hard: -15 minutes
    
    Complete tasks to reduce your wait time for the next coffee break!
    """)

# Note: For auto-refresh, consider using st.rerun() with a timer or st_autorefresh component
