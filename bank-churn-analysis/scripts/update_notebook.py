import json
import os

# Robustly find the notebook relative to this script's location
# This script is in /scripts/, so the notebook is one level up
script_dir = os.path.dirname(os.path.abspath(__file__))
notebook_path = os.path.join(script_dir, '..', 'Final_Churn_Report.ipynb')

# The new content for the recommendations/conclusion cell
new_content = [
    "### 🏆 Final Conclusion: Strategic Optimization & Business Case\n",
    "\n",
    "#### 1. The Verdict: From Noise to Signal\n",
    "This project successfully transitioned from a global observation of 20.4% churn to a high-precision predictive model. Through iterative testing, we isolated a specific **\"High-Risk Intersection\"**—German customers, aged 45+, who fall outside the established \"Product Sweet Spot.\"\n",
    "\n",
    "**The Result:** A high-priority **'Hit List' of 271 customers** with a **87.08% likelihood of exit**.\n",
    "\n",
    "#### 2. The Discovery: The \"Product Paradox\" (U-Curve Theory)\n",
    "The most significant technical breakthrough in this analysis was the rejection of the \"More is Better\" product hypothesis.\n",
    "\n",
    "*   **Initial Assumption:** Increasing product count linearly increases loyalty.\n",
    "*   **The Reality:** Exploratory Data Analysis (EDA) revealed a **U-shaped risk curve**.\n",
    "    *   **The Sweet Spot:** Customers with **exactly 2 products** are the most loyal segment (lowest churn).\n",
    "    *   **The Danger Zones:** Both **\"Low Engagement\" (1 product)** and **\"Product Saturation\" (3-4 products)** lead to extreme churn rates (reaching 100% in the 4-product segment).\n",
    "\n",
    "By optimizing the Danger Score to flag any customer **outside the 2-product \"Safety Zone,\"** we increased model precision by over 2%, capturing the bank's most dissatisfied \"Power Users.\"\n",
    "\n",
    "#### 3. The Financial Stakes (ROI of Retention)\n",
    "These 271 customers represent the bank's most significant capital flight risk:\n",
    "\n",
    "*   **Segment Average Balance:** ~$120,000\n",
    "*   **Total Assets at Risk:** $32.7 Million\n",
    "*   **Projected Savings:** By applying the recommended strategic plays (Ecosystem Entry, Regional Pilot, and Wealth Shield), a conservative **20% retention rate** would protect **$6.5 Million** in assets that are otherwise statistically certain to leave."
]

try:
    print(f"Looking for notebook at: {notebook_path}")
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    found = False
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            source_text = "".join(cell['source'])
            
            # 1. Update the Recommendations/Conclusion
            # We look for any of the previous headers to identify the correct cell
            if "### Recommendations" in source_text or "### Conclusions" in source_text or "### Summary" in source_text or "Power Conclusion" in source_text or "Final Conclusion" in source_text:
                cell['source'] = new_content
                found = True
            
            # 2. Update the Danger Score Definition Table (New Logic)
            if "| **Single Product Trap** |" in source_text:
                new_source = []
                for line in cell['source']:
                    if "| **Single Product Trap** |" in line:
                        new_source.append("| **Product Instability** | Customer has 1, 3, or 4 bank products |\n")
                    else:
                        new_source.append(line)
                cell['source'] = new_source
                print("Updated Danger Score Definition Table.")
    
    if found:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        print("Successfully updated notebook recommendations.")
    else:
        print("Could not find the Recommendations/Summary/Conclusion cell to update.")

except Exception as e:
    print(f"Error updating notebook: {e}")
