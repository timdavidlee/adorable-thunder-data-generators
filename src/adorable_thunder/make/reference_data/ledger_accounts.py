from typing import NamedTuple


class LedgerAccount(NamedTuple):
    account_code: str
    account_name: str


ASSET_ACCOUNTS: list[LedgerAccount] = [
    # Assets
    LedgerAccount("1000", "Cash – Operating Account"),
    LedgerAccount("1010", "Cash – Payroll Account"),
    LedgerAccount("1020", "Petty Cash"),
    LedgerAccount("1030", "Cash – Money Market Reserve"),
    LedgerAccount("1100", "Accounts Receivable – Trade"),
    LedgerAccount("1110", "Accounts Receivable – Intercompany"),
    LedgerAccount("1120", "Allowance for Doubtful Accounts"),
    LedgerAccount("1130", "Unbilled Revenue"),
    LedgerAccount("1200", "Prepaid Expenses – General"),
    LedgerAccount("1210", "Prepaid Insurance"),
    LedgerAccount("1220", "Prepaid Software Subscriptions"),
    LedgerAccount("1230", "Prepaid Rent"),
    LedgerAccount("1300", "Inventory – Raw Materials"),
    LedgerAccount("1310", "Inventory – Work in Progress"),
    LedgerAccount("1320", "Inventory – Finished Goods"),
    LedgerAccount("1400", "Fixed Assets – Computer Equipment"),
    LedgerAccount("1410", "Fixed Assets – Office Furniture & Fixtures"),
    LedgerAccount("1420", "Fixed Assets – Leasehold Improvements"),
    LedgerAccount("1430", "Fixed Assets – Vehicles"),
    LedgerAccount("1440", "Accumulated Depreciation – Equipment"),
    LedgerAccount("1450", "Accumulated Depreciation – Leasehold Improvements"),
    LedgerAccount("1500", "Right-of-Use Assets – Operating Leases"),
    LedgerAccount("1510", "Intangible Assets – Software Development Costs"),
    LedgerAccount("1520", "Intangible Assets – Patents & Trademarks"),
    LedgerAccount("1530", "Accumulated Amortization – Intangibles"),
    LedgerAccount("1600", "Security Deposits"),
    LedgerAccount("1610", "Long-Term Investments"),
    LedgerAccount("1620", "Deferred Tax Asset"),
]

LIABILITY_ACCOUNTS: list[LedgerAccount] = [
    # Liabilities
    LedgerAccount("2000", "Accounts Payable – Trade"),
    LedgerAccount("2010", "Accounts Payable – Intercompany"),
    LedgerAccount("2020", "Accrued Liabilities – General"),
    LedgerAccount("2030", "Accrued Payroll"),
    LedgerAccount("2040", "Accrued Bonuses"),
    LedgerAccount("2050", "Accrued Commissions"),
    LedgerAccount("2060", "Accrued Vacation & PTO"),
    LedgerAccount("2070", "Sales Tax Payable"),
    LedgerAccount("2080", "Income Tax Payable"),
    LedgerAccount("2090", "Deferred Revenue – Current"),
    LedgerAccount("2100", "Deferred Revenue – Long-Term"),
    LedgerAccount("2110", "Customer Deposits"),
    LedgerAccount("2120", "Short-Term Debt – Line of Credit"),
    LedgerAccount("2130", "Current Portion of Long-Term Debt"),
    LedgerAccount("2200", "Long-Term Debt – Term Loan"),
    LedgerAccount("2210", "Operating Lease Liability – Long-Term"),
    LedgerAccount("2220", "Deferred Tax Liability"),
    LedgerAccount("2230", "Other Long-Term Liabilities"),
]

EQUITY_ACCOUNTS: list[LedgerAccount] = [
    # Equity
    LedgerAccount("3000", "Common Stock"),
    LedgerAccount("3010", "Additional Paid-In Capital"),
    LedgerAccount("3020", "Retained Earnings"),
    LedgerAccount("3030", "Accumulated Other Comprehensive Income"),
    LedgerAccount("3040", "Treasury Stock"),
    LedgerAccount("3050", "Distributions to Shareholders"),
]

REVENUE_ACCOUNTS: list[LedgerAccount] = [
    # Revenue
    LedgerAccount("4000", "Revenue – Product Sales"),
    LedgerAccount("4010", "Revenue – SaaS Subscriptions"),
    LedgerAccount("4020", "Revenue – Professional Services"),
    LedgerAccount("4030", "Revenue – Support & Maintenance Contracts"),
    LedgerAccount("4040", "Revenue – License Fees"),
    LedgerAccount("4050", "Revenue – Usage-Based Fees"),
    LedgerAccount("4060", "Revenue – Training & Certification"),
    LedgerAccount("4070", "Revenue – Partner & Reseller Channel"),
    LedgerAccount("4080", "Revenue – Government Contracts"),
    LedgerAccount("4090", "Discounts & Allowances"),
    LedgerAccount("4100", "Refunds & Returns"),
    LedgerAccount("4110", "Other Revenue"),
]

COGS_ACCOUNTS: list[LedgerAccount] = [
    # Cost of Goods Sold / Cost of Revenue
    LedgerAccount("5000", "COGS – Product & Materials"),
    LedgerAccount("5010", "COGS – Third-Party Software & Licenses"),
    LedgerAccount("5020", "COGS – Cloud Hosting & Infrastructure"),
    LedgerAccount("5030", "COGS – Professional Services Delivery"),
    LedgerAccount("5040", "COGS – Support Labor"),
    LedgerAccount("5050", "COGS – Shipping & Fulfillment"),
]

OPEX_ACCOUNTS: list[LedgerAccount] = [
    # Operating Expenses – Compensation
    LedgerAccount("6000", "Salaries & Wages – Regular"),
    LedgerAccount("6010", "Salaries & Wages – Overtime"),
    LedgerAccount("6020", "Bonuses & Incentive Pay"),
    LedgerAccount("6030", "Commissions – Sales"),
    LedgerAccount("6040", "Contractor & Freelancer Fees"),
    LedgerAccount("6050", "Payroll Taxes – Employer"),
    LedgerAccount("6060", "Employee Benefits – Health Insurance"),
    LedgerAccount("6070", "Employee Benefits – Dental & Vision"),
    LedgerAccount("6080", "Employee Benefits – 401(k) Match"),
    LedgerAccount("6090", "Employee Benefits – Life & Disability Insurance"),
    LedgerAccount("6100", "Stock-Based Compensation Expense"),
    # Operating Expenses – Technology
    LedgerAccount("6200", "Software & SaaS Subscriptions"),
    LedgerAccount("6210", "IT Hardware & Equipment"),
    LedgerAccount("6220", "Cloud & Hosting Services"),
    LedgerAccount("6230", "Telecommunications & Internet"),
    LedgerAccount("6240", "IT Support & Managed Services"),
    # Operating Expenses – Facilities & Admin
    LedgerAccount("6300", "Rent & Occupancy"),
    LedgerAccount("6310", "Utilities"),
    LedgerAccount("6320", "Office Supplies & Materials"),
    LedgerAccount("6330", "Postage & Shipping"),
    LedgerAccount("6340", "Repairs & Maintenance"),
    LedgerAccount("6350", "Janitorial & Facilities Services"),
    LedgerAccount("6360", "Security Services"),
    # Operating Expenses – Sales & Marketing
    LedgerAccount("6400", "Advertising & Paid Media"),
    LedgerAccount("6410", "Content & Creative Production"),
    LedgerAccount("6420", "Events & Conferences"),
    LedgerAccount("6430", "Sponsorships & Partnerships"),
    LedgerAccount("6440", "Marketing Agency & Consulting Fees"),
    LedgerAccount("6450", "Sales Tools & CRM Software"),
    LedgerAccount("6460", "Customer Entertainment & Gifts"),
    # Operating Expenses – General & Administrative
    LedgerAccount("6500", "Legal & Professional Fees"),
    LedgerAccount("6510", "Accounting & Audit Fees"),
    LedgerAccount("6520", "Insurance – General Liability"),
    LedgerAccount("6530", "Insurance – Directors & Officers"),
    LedgerAccount("6540", "Business Licenses & Permits"),
    LedgerAccount("6550", "Dues & Memberships"),
    LedgerAccount("6560", "Travel & Lodging"),
    LedgerAccount("6570", "Meals & Entertainment"),
    LedgerAccount("6580", "Employee Training & Development"),
    LedgerAccount("6590", "Recruiting & Background Check Fees"),
    LedgerAccount("6600", "Depreciation Expense"),
    LedgerAccount("6610", "Amortization Expense"),
    LedgerAccount("6620", "Bad Debt Expense"),
]

OTHER_INCOME_EXPENSE_ACCOUNTS: list[LedgerAccount] = [
    # Other Income & Expense
    LedgerAccount("7000", "Interest Income"),
    LedgerAccount("7010", "Interest Expense"),
    LedgerAccount("7020", "Gain on Sale of Assets"),
    LedgerAccount("7030", "Loss on Sale of Assets"),
    LedgerAccount("7040", "Foreign Currency Gain/Loss"),
    LedgerAccount("7050", "Other Non-Operating Income"),
    LedgerAccount("7060", "Other Non-Operating Expense"),
    LedgerAccount("7070", "Income Tax Expense"),
]

GENERAL_LEDGER_ACCOUNTS: list[LedgerAccount] = (
    ASSET_ACCOUNTS
    + LIABILITY_ACCOUNTS
    + EQUITY_ACCOUNTS
    + REVENUE_ACCOUNTS
    + COGS_ACCOUNTS
    + OPEX_ACCOUNTS
    + OTHER_INCOME_EXPENSE_ACCOUNTS
)
