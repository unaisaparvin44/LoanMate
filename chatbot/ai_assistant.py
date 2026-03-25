"""
AI Loan Assistant for LoanMate Chatbot
---------------------------------------
Rule-based loan advisor that analyses the user message and returns
contextual loan advice.  Called only when FAQ matcher finds no match.

Public API
----------
loan_advisor(message: str) -> str | None
    Returns an advice string if a rule triggers, or None if the message
    is outside the advisor's knowledge domain.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Internal rule definitions
# Each entry is a tuple of (keywords_list, response_string).
# The first rule whose ANY keyword appears in the lowercased message wins.
# ---------------------------------------------------------------------------

_RULES: list[tuple[list[str], str]] = [

    # ── Loan eligibility ──────────────────────────────────────────────────
    (
        ["home loan eligibility", "eligible for home", "qualify for home loan",
         "home loan qualify"],
        (
            "To be eligible for a Home Loan at LoanMate you generally need:\n"
            "• Stable employment or business income for 2+ years\n"
            "• Monthly income sufficient to keep EMI ≤ 40 % of salary\n"
            "• Credit score of 650 or above\n"
            "• Valid ID proof, income proof, and property documents\n\n"
            "Apply on your dashboard and our officers will review your profile."
        ),
    ),
    (
        ["education loan eligibility", "eligible for education",
         "qualify for education loan", "student loan eligibility"],
        (
            "Education Loan eligibility at LoanMate:\n"
            "• Admission confirmation from a recognised institution\n"
            "• Co-applicant (parent/guardian) with stable income\n"
            "• Academic records showing satisfactory progress\n"
            "• Documents: ID proof, admission letter, fee structure, income proof of co-applicant"
        ),
    ),
    (
        ["vehicle loan eligibility", "car loan eligibility",
         "eligible for vehicle loan", "bike loan eligibility"],
        (
            "Vehicle Loan eligibility at LoanMate:\n"
            "• Minimum age 21 years\n"
            "• Stable income (salaried or self-employed)\n"
            "• Credit score ≥ 650\n"
            "• EMI should not exceed 40 % of net monthly income\n"
            "• Valid driving licence and vehicle quotation required"
        ),
    ),
    (
        ["personal loan eligibility", "eligible for personal loan",
         "qualify for personal loan"],
        (
            "Personal Loan eligibility at LoanMate:\n"
            "• Age 21–60 years\n"
            "• Minimum monthly income ₹15,000\n"
            "• Credit score ≥ 650\n"
            "• Employment stability of at least 1 year\n"
            "• EMI in total should not exceed 40 % of your monthly income"
        ),
    ),

    # ── Agriculture / Farmer ─────────────────────────────────────────────
    (
        ["farmer", "agriculture loan", "agri loan", "farming loan",
         "kisan", "crop loan", "agricultural"],
        (
            "For farmers and agricultural needs, LoanMate offers an "
            "Agriculture Loan with flexible repayment tied to crop cycles.\n\n"
            "Eligibility:\n"
            "• Land ownership or lease documents\n"
            "• Proof of farming activity\n"
            "• Valid ID and bank account details\n\n"
            "Tip: Agriculture loans often have lower interest rates and "
            "government subsidy tie-ins. Apply from your dashboard!"
        ),
    ),

    # ── Income / Salary / EMI ─────────────────────────────────────────────
    (
        ["salary", "income", "emi calculation", "how much emi",
         "monthly income", "afford loan", "how much can i borrow"],
        (
            "💡 EMI Rule of Thumb:\n"
            "Your total monthly EMI obligations should NOT exceed 40 % of "
            "your net monthly income.\n\n"
            "Example:\n"
            "  Net monthly income  = ₹50,000\n"
            "  Maximum total EMI   = ₹20,000\n\n"
            "A higher income improves your loan eligibility and the amount "
            "you can borrow.  Use this rule to decide how much to apply for."
        ),
    ),

    # ── Credit Score ──────────────────────────────────────────────────────
    (
        ["credit score", "cibil", "credit rating", "improve credit",
         "bad credit", "low credit", "credit history"],
        (
            "📊 Credit Score Guide:\n"
            "• 750 and above  → Excellent — best approval chances & rates\n"
            "• 700 – 749      → Good — most loans approved\n"
            "• 650 – 699      → Fair — approval possible, may need higher income\n"
            "• Below 650      → Poor — loan likely declined; focus on rebuilding\n\n"
            "Tips to improve your credit score:\n"
            "  ✔ Pay all EMIs and credit card dues on time\n"
            "  ✔ Keep credit card utilisation below 30 %\n"
            "  ✔ Avoid multiple loan applications in a short period\n"
            "  ✔ Check your credit report annually for errors"
        ),
    ),

    # ── Loan Recommendation ───────────────────────────────────────────────
    (
        ["which loan", "what loan", "best loan", "recommend loan",
         "suggest loan", "loan for me", "loan should i take",
         "loan for business", "loan for house", "loan for car",
         "loan for studies", "loan for education"],
        (
            "🏦 LoanMate Loan Recommendation Guide:\n\n"
            "• 🏠 Home Loan       → Buying or constructing a house\n"
            "• 🎓 Education Loan  → Funding college / higher studies\n"
            "• 🚗 Vehicle Loan    → Buying a car, bike, or commercial vehicle\n"
            "• 🌾 Agriculture Loan→ Farming, equipment, or crop expenses\n"
            "• 💼 Personal Loan   → Medical, travel, wedding, or any personal need\n\n"
            "Tell me more about your purpose and I can give tailored advice!"
        ),
    ),

    # ── Loan Amount ───────────────────────────────────────────────────────
    (
        ["how much loan", "maximum loan", "loan amount", "loan limit",
         "borrow how much", "loan i can get"],
        (
            "The loan amount you can get depends on:\n"
            "1. Your net monthly income (EMI ≤ 40 % rule)\n"
            "2. Your credit score (higher score → larger limit)\n"
            "3. The type of loan (Home > Personal in typical limits)\n"
            "4. Existing debt obligations\n\n"
            "As a quick estimate: if your income is ₹X per month, you may "
            "qualify for a loan where the EMI is up to ₹0.4 × X."
        ),
    ),

    # ── Interest Rate ─────────────────────────────────────────────────────
    (
        ["interest rate", "rate of interest", "roi", "interest percent",
         "loan interest", "low interest"],
        (
            "Interest rates at LoanMate vary by loan type and your profile:\n"
            "• Agriculture Loan  → typically lower (subsidised rates available)\n"
            "• Home Loan         → moderate, linked to RBI repo rate\n"
            "• Education Loan    → competitive, may have moratorium period\n"
            "• Vehicle Loan      → fixed rate based on vehicle & tenure\n"
            "• Personal Loan     → slightly higher (unsecured)\n\n"
            "A credit score above 750 and stable income can secure better rates. "
            "Contact LoanMate support for current rate sheets."
        ),
    ),

    # ── Repayment / Tenure ────────────────────────────────────────────────
    (
        ["repayment", "loan tenure", "how long to repay", "pay back",
         "loan period", "loan duration"],
        (
            "Loan repayment tenures at LoanMate:\n"
            "• Home Loan         → up to 20 years\n"
            "• Education Loan    → up to 15 years (with possible moratorium)\n"
            "• Vehicle Loan      → 1 – 7 years\n"
            "• Agriculture Loan  → aligned to crop cycle (short to medium term)\n"
            "• Personal Loan     → 1 – 5 years\n\n"
            "Longer tenure = smaller monthly EMI but higher total interest paid. "
            "Choose based on your monthly cash-flow comfort."
        ),
    ),

    # ── Rejection / Declined ──────────────────────────────────────────────
    (
        ["loan rejected", "loan declined", "why rejected", "application rejected",
         "loan not approved", "improve chances", "was rejected", "got rejected",
         "been rejected", "loan denied"],
        (
            "Common reasons for loan rejection and how to fix them:\n\n"
            "❌ Low credit score    → Pay dues on time; reduce card utilisation\n"
            "❌ High existing EMIs  → Clear existing debts before reapplying\n"
            "❌ Insufficient income → Apply for a lower amount or wait for a raise\n"
            "❌ Incomplete documents→ Ensure all required documents are uploaded\n"
            "❌ Unstable employment → Build at least 1 year of stable job history\n\n"
            "After fixing the root cause you may re-apply. Our officers are happy to help!"
        ),
    ),

    # ── Greetings / General help ──────────────────────────────────────────
    (
        ["can you help", "what can you do", "what do you know",
         "tell me about loans", "loan advice", "loan guidance",
         "loan information"],
        (
            "I'm your LoanMate AI Loan Assistant! I can help you with:\n\n"
            "• 🏦 Loan type recommendations\n"
            "• ✅ Eligibility criteria for each loan\n"
            "• 💰 Income & EMI calculations\n"
            "• 📊 Credit score guidance\n"
            "• 📋 Required documents\n"
            "• 💡 Tips to improve approval chances\n"
            "• ❓ Rejection reasons & remedies\n\n"
            "Just type your question and I'll do my best to assist!"
        ),
    ),
]


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def loan_advisor(message: str) -> str | None:
    """
    Analyse *message* against loan-advisor rules and return advice text,
    or None if no rule matches (caller should use its own fallback).
    """
    msg = message.lower().strip()

    for keywords, response in _RULES:
        for kw in keywords:
            if kw in msg:
                return response

    return None
