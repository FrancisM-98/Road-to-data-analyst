import json
import os

# Robustly find the notebook relative to this script's location
# This script is in /scripts/, so the notebook is one level up
script_dir = os.path.dirname(os.path.abspath(__file__))
notebook_path = os.path.join(script_dir, '..', 'Final_Churn_Report.ipynb')

# The new content for the recommendations cell
new_content = [
    "### 🏆 The \"Power Conclusion\"\n",
    "\n",
    "#### 1. The Verdict (The Big Win)\n",
    "This analysis successfully moved from a generalized churn observation to a high-precision predictive model. By identifying the **'German-Age-Product'** intersection, we have narrowed the bank's focus from 10,000 noise-filled records to a high-priority **'Hit List' of 238 customers** with a **85.29% likelihood of exit**.\n",
    "\n",
    "#### 2. The Financial Stakes (The ROI)\n",
    "These 238 customers represent more than just a count; they are a significant revenue risk. With an average balance of **$91,000** in this segment, the bank is looking at approximately **$21.6 Million** in potential outflows. Saving even 20% of this group would retain over **$4 Million** in assets.\n",
    "\n",
    "#### 3. The Action Mandate (The 'Plays')\n",
    "To mitigate this risk, we recommend three immediate data-driven interventions:\n",
    "\n",
    "*   **The Ecosystem Entry:** Transitioning 'Single-Product' users into multi-product accounts to increase switching costs.\n",
    "*   **The Regional Pilot:** A 90-day retention experiment in the DACH region to address localized friction.\n",
    "*   **The Wealth Shield:** Implementing tenure-based interest rate protections for the 45+ demographic to capture aging capital."
]

try:
    print(f"Looking for notebook at: {notebook_path}")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    found = False
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            # Check if this is the summary/recommendations cell
            source_text = "".join(cell['source'])
            # We look for the previous header we set or the original one
            if "### Recommendations" in source_text or "### Conclusions" in source_text or "### Summary" in source_text:
                # Replace the content
                cell['source'] = new_content
                found = True
                break
    
    if found:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        print("Successfully updated notebook recommendations.")
    else:
        print("Could not find the Recommendations/Summary cell to update.")

except Exception as e:
    print(f"Error updating notebook: {e}")
