ASSET_ACCOUNTS = [
    # Assets
    ("1000", "Cash – Operating Account"),
    ("1010", "Cash – Payroll Account"),
    ("1020", "Petty Cash"),
    ("1030", "Cash – Money Market Reserve"),
    ("1100", "Accounts Receivable – Trade"),
    ("1110", "Accounts Receivable – Intercompany"),
    ("1120", "Allowance for Doubtful Accounts"),
    ("1130", "Unbilled Revenue"),
    ("1200", "Prepaid Expenses – General"),
    ("1210", "Prepaid Insurance"),
    ("1220", "Prepaid Software Subscriptions"),
    ("1230", "Prepaid Rent"),
    ("1300", "Inventory – Raw Materials"),
    ("1310", "Inventory – Work in Progress"),
    ("1320", "Inventory – Finished Goods"),
    ("1400", "Fixed Assets – Computer Equipment"),
    ("1410", "Fixed Assets – Office Furniture & Fixtures"),
    ("1420", "Fixed Assets – Leasehold Improvements"),
    ("1430", "Fixed Assets – Vehicles"),
    ("1440", "Accumulated Depreciation – Equipment"),
    ("1450", "Accumulated Depreciation – Leasehold Improvements"),
    ("1500", "Right-of-Use Assets – Operating Leases"),
    ("1510", "Intangible Assets – Software Development Costs"),
    ("1520", "Intangible Assets – Patents & Trademarks"),
    ("1530", "Accumulated Amortization – Intangibles"),
    ("1600", "Security Deposits"),
    ("1610", "Long-Term Investments"),
    ("1620", "Deferred Tax Asset"),
]

LIABILITY_ACCOUNTS = [
    # Liabilities
    ("2000", "Accounts Payable – Trade"),
    ("2010", "Accounts Payable – Intercompany"),
    ("2020", "Accrued Liabilities – General"),
    ("2030", "Accrued Payroll"),
    ("2040", "Accrued Bonuses"),
    ("2050", "Accrued Commissions"),
    ("2060", "Accrued Vacation & PTO"),
    ("2070", "Sales Tax Payable"),
    ("2080", "Income Tax Payable"),
    ("2090", "Deferred Revenue – Current"),
    ("2100", "Deferred Revenue – Long-Term"),
    ("2110", "Customer Deposits"),
    ("2120", "Short-Term Debt – Line of Credit"),
    ("2130", "Current Portion of Long-Term Debt"),
    ("2200", "Long-Term Debt – Term Loan"),
    ("2210", "Operating Lease Liability – Long-Term"),
    ("2220", "Deferred Tax Liability"),
    ("2230", "Other Long-Term Liabilities"),
]

EQUITY_ACCOUNTS = [
    # Equity
    ("3000", "Common Stock"),
    ("3010", "Additional Paid-In Capital"),
    ("3020", "Retained Earnings"),
    ("3030", "Accumulated Other Comprehensive Income"),
    ("3040", "Treasury Stock"),
    ("3050", "Distributions to Shareholders"),
]

REVENUE_ACCOUNTS = [
    # Revenue
    ("4000", "Revenue – Product Sales"),
    ("4010", "Revenue – SaaS Subscriptions"),
    ("4020", "Revenue – Professional Services"),
    ("4030", "Revenue – Support & Maintenance Contracts"),
    ("4040", "Revenue – License Fees"),
    ("4050", "Revenue – Usage-Based Fees"),
    ("4060", "Revenue – Training & Certification"),
    ("4070", "Revenue – Partner & Reseller Channel"),
    ("4080", "Revenue – Government Contracts"),
    ("4090", "Discounts & Allowances"),
    ("4100", "Refunds & Returns"),
    ("4110", "Other Revenue"),
]

COGS_ACCOUNTS = [
    # Cost of Goods Sold / Cost of Revenue
    ("5000", "COGS – Product & Materials"),
    ("5010", "COGS – Third-Party Software & Licenses"),
    ("5020", "COGS – Cloud Hosting & Infrastructure"),
    ("5030", "COGS – Professional Services Delivery"),
    ("5040", "COGS – Support Labor"),
    ("5050", "COGS – Shipping & Fulfillment"),
]

OPEX_ACCOUNTS = [
    # Operating Expenses – Compensation
    ("6000", "Salaries & Wages – Regular"),
    ("6010", "Salaries & Wages – Overtime"),
    ("6020", "Bonuses & Incentive Pay"),
    ("6030", "Commissions – Sales"),
    ("6040", "Contractor & Freelancer Fees"),
    ("6050", "Payroll Taxes – Employer"),
    ("6060", "Employee Benefits – Health Insurance"),
    ("6070", "Employee Benefits – Dental & Vision"),
    ("6080", "Employee Benefits – 401(k) Match"),
    ("6090", "Employee Benefits – Life & Disability Insurance"),
    ("6100", "Stock-Based Compensation Expense"),
    # Operating Expenses – Technology
    ("6200", "Software & SaaS Subscriptions"),
    ("6210", "IT Hardware & Equipment"),
    ("6220", "Cloud & Hosting Services"),
    ("6230", "Telecommunications & Internet"),
    ("6240", "IT Support & Managed Services"),
    # Operating Expenses – Facilities & Admin
    ("6300", "Rent & Occupancy"),
    ("6310", "Utilities"),
    ("6320", "Office Supplies & Materials"),
    ("6330", "Postage & Shipping"),
    ("6340", "Repairs & Maintenance"),
    ("6350", "Janitorial & Facilities Services"),
    ("6360", "Security Services"),
    # Operating Expenses – Sales & Marketing
    ("6400", "Advertising & Paid Media"),
    ("6410", "Content & Creative Production"),
    ("6420", "Events & Conferences"),
    ("6430", "Sponsorships & Partnerships"),
    ("6440", "Marketing Agency & Consulting Fees"),
    ("6450", "Sales Tools & CRM Software"),
    ("6460", "Customer Entertainment & Gifts"),
    # Operating Expenses – General & Administrative
    ("6500", "Legal & Professional Fees"),
    ("6510", "Accounting & Audit Fees"),
    ("6520", "Insurance – General Liability"),
    ("6530", "Insurance – Directors & Officers"),
    ("6540", "Business Licenses & Permits"),
    ("6550", "Dues & Memberships"),
    ("6560", "Travel & Lodging"),
    ("6570", "Meals & Entertainment"),
    ("6580", "Employee Training & Development"),
    ("6590", "Recruiting & Background Check Fees"),
    ("6600", "Depreciation Expense"),
    ("6610", "Amortization Expense"),
    ("6620", "Bad Debt Expense"),
]

OTHER_INCOME_EXPENSE_ACCOUNTS = [
    # Other Income & Expense
    ("7000", "Interest Income"),
    ("7010", "Interest Expense"),
    ("7020", "Gain on Sale of Assets"),
    ("7030", "Loss on Sale of Assets"),
    ("7040", "Foreign Currency Gain/Loss"),
    ("7050", "Other Non-Operating Income"),
    ("7060", "Other Non-Operating Expense"),
    ("7070", "Income Tax Expense"),
]

GENERAL_LEDGER_ACCOUNTS = (
    ASSET_ACCOUNTS
    + LIABILITY_ACCOUNTS
    + EQUITY_ACCOUNTS
    + REVENUE_ACCOUNTS
    + COGS_ACCOUNTS
    + OPEX_ACCOUNTS
    + OTHER_INCOME_EXPENSE_ACCOUNTS
)
