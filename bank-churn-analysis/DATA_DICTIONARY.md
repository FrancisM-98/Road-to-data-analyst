# Data Dictionary - Bank Customer Churn Analysis

## Dataset Information
- **Source:** [Kaggle - Bank Customer Churn Prediction](https://www.kaggle.com/datasets/shrutimechlearn/churn-modelling)
- **Total Records:** 10,000 customers
- **Original Features:** 14
- **Engineered Features:** 5
- **Total Features:** 19
- **Target Variable:** `Exited` (1 = Churned, 0 = Retained)

---

## Original Features (Kaggle Dataset)

### Removed Features (Non-Predictive)
These columns were removed during data cleaning as they contain no predictive value:

| Variable | Type | Description | Reason for Removal |
|----------|------|-------------|-------------------|
| RowNumber | Integer | Sequential row identifier (1-10,000) | Non-predictive index |
| CustomerId | Integer | Unique client ID (15565701-15815690) | Arbitrary identifier with no business meaning |
| Surname | String | Customer last name | Personally identifiable information, no predictive value |

---

### Retained Features (Analysis Variables)

| Variable | Type | Description | Values/Range | Importance | Business Impact |
|----------|------|-------------|--------------|------------|-----------------|
| **CreditScore** | Integer | Client's credit score | 350-850 | Medium | Represents a client's financial health and stability. Losing a high credit score member is more impactful than lower ones. |
| **Geography** | Categorical | Client's country of residence | France, Germany, Spain | **High** | **Identifies regional friction.** Germany shows 32% churn (2x other markets). |
| **Gender** | Categorical | Client's gender | Male, Female | Medium | Useful for targeted retention campaigns. If a gender has a higher churn rate, the communication strategy may not be resonating with the specific demography. |
| **Age** | Integer | Client's age in years | 18-92 | **High** | **Represents client's financial lifecycle.** Age 45+ shows elevated churn (retirement/consolidation behavior). |
| **Tenure** | Integer | Years as bank customer | 0-10 | Medium | Represents loyalty depth. Identifies whether friction points exist according to time with the bank. |
| **Balance** | Float | Current account balance (USD) | $0-$250,898 | **High** | **Represents capital at risk.** The expected financial loss when a client exits. |
| **NumOfProducts** | Integer | Number of bank products owned | 1-4 | **Critical** | **The ideal number is 2 (sweet spot).** 1 shows lack of stickiness; 3-4 shows over-servicing or dissatisfaction. |
| **HasCrCard** | Binary | Client owns a credit card | 0 (No), 1 (Yes) | Low | A "hook product" that measures whether owning a credit card increases switching costs. |
| **IsActiveMember** | Binary | Frequently uses bank services | 0 (Inactive), 1 (Active) | **Critical** | **Inactivity is an early warning sign.** Represents the customer has mentally checked out before physically closing the account. |
| **EstimatedSalary** | Float | Client's estimated annual salary (USD) | $11-$199,992 | High | Represents the potential a client has and the services a bank could offer (wealth management, premium products). |
| **Exited** | Binary | **TARGET VARIABLE** - Client left the bank | 0 (Retained), 1 (Churned) | **Critical** | **What we're predicting.** Measures customer attrition. Helps identify Customer Acquisition Cost (CAC) and loss of future revenue. |

---

## Engineered Features (Created During Analysis)

These features were created to enable interpretable analysis and Power BI filtering:

| Variable | Type | Derived From | Logic/Formula | Business Rationale |
|----------|------|--------------|---------------|-------------------|
| **DangerScore** | Integer (0-4) | Multi-factor | See calculation below | **Primary risk segmentation model.** Composite indicator combining the 4 highest-correlated churn drivers. |
| **BalanceBr** | Categorical | Balance | • Zero: Balance = 0<br>• Low: Balance ≤ $90,000<br>• Medium: $90,000 < Balance ≤ $130,000<br>• High: Balance > $130,000 | Groups wealth demographics to analyze balance impact on churn. Enables "high-value at-risk" filtering in dashboards. |
| **EstimatedSalaryBr** | Categorical | EstimatedSalary | • Low: Salary ≤ $50,000<br>• Medium: $50,000 < Salary ≤ $100,000<br>• High: $100,000 < Salary ≤ $150,000<br>• Very High: Salary > $150,000 | Groups income demographics to analyze salary impact on churn. Identifies premium customer segments. |
| **CreditScoreRange** | Categorical | CreditScore | 50-point buckets:<br>350-400, 400-450, ..., 800-850 | Granular credit score distribution for detailed analysis. Identifies credit quality patterns in churn. |
| **CreditScoreQuality** | Categorical | CreditScore | • Bad: < 580<br>• Fair: 580-669<br>• Good: 670-739<br>• Excellent: ≥ 740 | FICO-style quality tiers for business-friendly segmentation. Aligns with industry standards for credit assessment. |

---

## Danger Score Calculation

The **DangerScore** is a transparent, rule-based risk indicator (0-4 points) designed for business interpretability over black-box accuracy.

### Scoring Logic

Each customer receives **0 to 4 points** based on the following criteria:

| Risk Factor | Condition | Points | Strategic Rationale | Key Question |
|-------------|-----------|--------|---------------------|--------------|
| **Geography** | Located in Germany | +1 | Germany has 32% churn rate (2× France/Spain). Regional market dynamics (digital challengers N26, C24) create friction. | *What could we do to improve retention in the German region?* |
| **Age** | Age ≥ 45 years | +1 | At what maturity threshold does "loyalty decay" begin? Age 45+ shows consolidation/retirement behavior. | *How could we improve customer loyalty for people above 45?* |
| **Product Count** | NumOfProducts ≠ 2 | +1 | There's a sweet spot at 2 products. 1 = insufficient stickiness; 3-4 = over-servicing or system gaming. | *How could we improve product range to maintain the 2-product sweet spot?* |
| **Activity Status** | IsActiveMember = 0 | +1 | Inactivity is the strongest early warning signal. Customer has mentally disengaged before account closure. | *What is the "Golden Window" between inactivity and closure? How can we automate re-engagement?* |

### Python Implementation
```python
def calculate_danger_score(row):
    score = 0
    if row['Geography'] == 'Germany': score += 1
    if row['Age'] >= 45: score += 1
    if row['NumOfProducts'] != 2: score += 1
    if row['IsActiveMember'] == 0: score += 1
    return score
```

### Performance by Score Segment

| DangerScore | Churn Rate | Customer Count | Avg Balance | Total Assets at Risk |
|-------------|------------|----------------|-------------|---------------------|
| **4 (Critical)** | **87.08%** | 271 | $120,495 | **$32.65M** |
| 3 (High) | 55.11% | 1,281 | $103,690 | $73.28M |
| 2 (Medium) | 23.27% | 3,172 | $96,190 | $71.04M |
| 1 (Low) | 8.11% | 3,837 | $65,023 | $20.24M |
| 0 (Minimal) | 3.20% | 1,439 | $31,112 | $1.43M |
| **Baseline** | **20.37%** | 10,000 | — | — |

**Key Insight:** Score 4 customers are **27× more likely** to churn than Score 0 customers (87.08% vs 3.20%), validating the model's stratification power.

---

## Data Quality Summary

### Validation Results
- ✅ **No missing values** across all 10,000 records
- ✅ **No duplicate rows** found
- ✅ **All numeric ranges validated** (no outliers outside expected bounds)
- ✅ **Categorical variables consistent** (no typos or unexpected values)

### Notable Data Patterns
- **Zero Balance Accounts:** 3,607 customers (36.07%) have Balance = $0
  - *Hypothesis:* Dormant accounts or checking-only customers
  - *Impact:* May indicate "zombie accounts" at high churn risk
  
- **4-Product Customers:** Only 60 customers (0.6%) own 4 products
  - **100% churn rate** — complete attrition
  - *Hypothesis:* System abuse, promotional gaming, or over-servicing failure
  - *Recommendation:* Audit these accounts for fraud/compliance

- **Inactive Members:** 5,151 customers (51.51%) are inactive
  - *Critical risk factor* appearing in 45% of Score 4 customers
  - *Opportunity:* Re-activation campaigns could prevent 1,000+ churns

---

## Usage Guidelines

### For Python/Pandas Analysis
```python
# Load processed dataset
df = pd.read_csv('data/Final_Portfolio_Dataset_v2.csv')

# Filter high-risk customers
critical_risk = df[df['DangerScore'] == 4]

# Segment by wealth and risk
high_value_risk = df[(df['BalanceBr'] == 'High') & (df['DangerScore'] >= 3)]

# Profile inactive Germans
german_inactive = df[(df['Geography'] == 'Germany') & (df['IsActiveMember'] == 0)]
```

### For Power BI Dashboard
- **DangerScore:** Powers the main risk gauge and KPI cards
- **Bracket Fields:** Enable user-friendly slicers without DAX complexity
- **CreditScoreQuality:** Pre-calculated tiers for demographic filtering

All engineered features are **pre-computed** in the CSV, eliminating need for DAX recalculation.

---

## Strategic Questions Answered by This Dictionary

1. **Geography:** What drives Germany's 2× higher churn? → *Competitive market analysis required*
2. **Age:** When does loyalty decay start? → *Age 45+ is the inflection point*
3. **Products:** What's the optimal product count? → *Exactly 2 products (7.58% churn)*
4. **Activity:** How long between inactivity and exit? → *Requires time-series analysis (future work)*

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| March 2025 | 1.0 | Initial dictionary creation with 14 original + 5 engineered features |

---

*This data dictionary supports the [Bank Customer Churn Analysis](./README.md) portfolio project.*  
*For questions or clarifications, contact: multanifrancis@gmail.com*
