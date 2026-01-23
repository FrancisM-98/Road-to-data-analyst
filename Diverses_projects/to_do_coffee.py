import streamlit as st
from datetime import datetime, timedelta
import time

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
    task = {
        'id': len(st.session_state.tasks) + len(st.session_state.completed_tasks),
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
    today = datetime.now().replace(hour=8, minute=15, second=0, microsecond=0)
    st.session_state.last_coffee_time = today
    st.session_state.coffees_today = 1

def generate_coffee_mug_svg(minutes_remaining):
    """Generate an SVG coffee mug that fills based on time remaining"""
    # Calculate fill percentage (0% at 120 min, 100% at 0 min)
    fill_percentage = max(0, min(100, (120 - minutes_remaining) / 120 * 100))
    
    # Mug dimensions
    mug_height = 100
    mug_width = 80
    coffee_max_height = 75
    
    # Calculate coffee fill height
    coffee_height = (fill_percentage / 100) * coffee_max_height
    coffee_y = 20 + (coffee_max_height - coffee_height)
    
    # Color gradient based on fill (lighter when empty, darker when full)
    coffee_lightness = 70 - (fill_percentage / 100 * 40)  # 70% to 30%
    coffee_color = f"hsl(25, 80%, {coffee_lightness}%)"
    
    # Steam animation when ready
    steam_opacity = 0.8 if minutes_remaining <= 0 else 0
    
    svg = f"""
    <svg width="120" height="140" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
        <!-- Steam (when ready) -->
        <g opacity="{steam_opacity}">
            <path d="M 35 10 Q 30 5, 35 0" stroke="#aaa" stroke-width="2" fill="none" opacity="0.6">
                <animate attributeName="d" 
                    values="M 35 10 Q 30 5, 35 0;M 35 10 Q 40 5, 35 0;M 35 10 Q 30 5, 35 0" 
                    dur="2s" repeatCount="indefinite"/>
            </path>
            <path d="M 50 15 Q 45 8, 50 2" stroke="#aaa" stroke-width="2" fill="none" opacity="0.5">
                <animate attributeName="d" 
                    values="M 50 15 Q 45 8, 50 2;M 50 15 Q 55 8, 50 2;M 50 15 Q 45 8, 50 2" 
                    dur="2.5s" repeatCount="indefinite"/>
            </path>
            <path d="M 65 10 Q 60 5, 65 0" stroke="#aaa" stroke-width="2" fill="none" opacity="0.6">
                <animate attributeName="d" 
                    values="M 65 10 Q 60 5, 65 0;M 65 10 Q 70 5, 65 0;M 65 10 Q 60 5, 65 0" 
                    dur="1.8s" repeatCount="indefinite"/>
            </path>
        </g>
        
        <!-- Mug body outline -->
        <rect x="20" y="20" width="{mug_width}" height="{mug_height}" 
              fill="#f5f5f5" stroke="#8B4513" stroke-width="3" rx="5"/>
        
        <!-- Coffee fill -->
        <rect x="23" y="{coffee_y}" width="{mug_width - 6}" height="{coffee_height}" 
              fill="{coffee_color}" rx="3">
            <animate attributeName="height" 
                from="{max(0, coffee_height - 2)}" 
                to="{coffee_height}" 
                dur="1s" 
                repeatCount="1"/>
        </rect>
        
        <!-- Mug handle -->
        <path d="M 100 40 Q 115 50, 115 70 Q 115 90, 100 100" 
              stroke="#8B4513" stroke-width="3" fill="none"/>
        
        <!-- Shine effect on mug -->
        <ellipse cx="35" cy="35" rx="8" ry="12" fill="white" opacity="0.3"/>
        
        <!-- Fill percentage text -->
        <text x="60" y="135" text-anchor="middle" font-size="14" font-weight="bold" fill="#666">
            {int(fill_percentage)}%
        </text>
    </svg>
    """
    return svg

# Main UI
st.title("☕ Coffee Break To-Do List")
st.markdown("*Complete tasks to earn your coffee breaks faster!*")

# Header with current time and coffee status
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric("Current Time", datetime.now().strftime("%H:%M"))

with col2:
    st.metric("Coffees Today", f"☕ × {st.session_state.coffees_today}")

with col3:
    next_coffee = calculate_next_coffee_time()
    time_until_coffee = next_coffee - datetime.now()
    minutes_left = int(time_until_coffee.total_seconds() / 60)
    if minutes_left < 0:
        minutes_left = 0
    
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
    next_coffee = calculate_next_coffee_time()
    time_until_coffee = next_coffee - datetime.now()
    minutes_left = int(time_until_coffee.total_seconds() / 60)
    if minutes_left < 0:
        minutes_left = 0
    
    # Generate and display the coffee mug
    mug_svg = generate_coffee_mug_svg(minutes_left)
    st.components.v1.html(mug_svg, height=160)
    
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

# Auto-refresh every 30 seconds to update timers
time.sleep(0.1)  # Small delay to prevent constant reloading
