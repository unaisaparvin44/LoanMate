"""
FAQ Knowledge Base for LoanMate Chatbot
Each key is a keyword/phrase; value is the answer shown to the user.
"""

FAQ_RESPONSES = {
    "loan types": "LoanMate offers Agriculture, Education, Home, Personal and Vehicle loans.",
    "agriculture": "LoanMate offers Agriculture loans to support farming needs.",
    "education": "Education loans are available to help you fund your studies.",
    "home loan": "Home loans are available for purchasing or constructing a home.",
    "personal loan": "Personal loans are available for your personal financial needs.",
    "vehicle loan": "Vehicle loans help you finance a car, bike, or other vehicle.",
    "apply loan": "Go to the loan section and choose a loan type to apply.",
    "how to apply": "Go to the loan section and choose a loan type to apply.",
    "apply": "Click 'Apply for Loan' on your dashboard, select a loan type, and fill in the details.",
    "loan approval time": "Loan approval usually takes 2–5 working days.",
    "approval time": "Loan approval usually takes 2–5 working days.",
    "how long": "Loan approval usually takes 2–5 working days after submission.",
    "documents": "Required documents include ID proof, income proof, and bank details.",
    "required documents": "You need a valid ID proof, recent income proof, and your bank account details.",
    "id proof": "Acceptable ID proofs include Aadhaar Card, PAN Card, or Passport.",
    "income proof": "Income proof can be salary slips, bank statements, or an income tax return.",
    "loan status": "You can check your application status in the My Applications page.",
    "status": "Visit 'My Applications' on your dashboard to track your loan status.",
    "track": "Open the 'My Applications' section to track the status of all your loans.",
    "credit score": "A credit score of 650 or above is generally required for loan approval.",
    "credit": "Maintaining a good credit score (650+) improves your chances of approval.",
    "emi": "Your EMI (Equated Monthly Installment) is calculated based on amount, rate, and tenure.",
    "contact": "You can contact LoanMate support through the contact form on our website.",
    "support": "For help, reach out to LoanMate support via the website contact page.",
    "hello": "Hello! I'm the LoanMate FAQ Bot. Ask me anything about loans!",
    "hi": "Hi there! How can I help you today?",
    "help": "I can help with loan types, application process, documents, approval time, and status tracking.",
}


def get_faq_reply(user_message: str) -> str:
    """
    3-tier matching against FAQ_RESPONSES:
      1. Exact / partial substring match  (fast, handles clear keywords)
      2. difflib fuzzy match on individual words  (handles typos / paraphrasing)
      3. Fallback message
    """
    from difflib import get_close_matches

    msg = user_message.lower().strip()
    keys = list(FAQ_RESPONSES.keys())

    # --- Tier 1: substring match (original behaviour, keep it fast) ---
    for keyword in keys:
        if keyword in msg:
            return FAQ_RESPONSES[keyword]

    # --- Tier 2a: fuzzy match on the full message vs every key ---
    full_matches = get_close_matches(msg, keys, n=1, cutoff=0.5)
    if full_matches:
        return FAQ_RESPONSES[full_matches[0]]

    # --- Tier 2b: fuzzy match on each individual word the user typed ---
    for word in msg.split():
        if len(word) < 3:          # skip very short words (is, of, a…)
            continue
        word_matches = get_close_matches(word, keys, n=1, cutoff=0.72)
        if word_matches:
            return FAQ_RESPONSES[word_matches[0]]

    # --- Tier 3: fallback ---
    return (
        "Sorry, I didn't understand that. "
        "Try asking about loan types, how to apply, required documents, "
        "approval time, or loan status."
    )

