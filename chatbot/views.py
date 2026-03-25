from django.http import JsonResponse
from chatbot.faq import FAQ_RESPONSES
from chatbot.ai_assistant import loan_advisor
from ml_engine.predictor import predict_loan_approval
from difflib import get_close_matches
import re

# ---------------------------------------------------------------------------
# Internal FAQ matcher that returns None on no-match
# (keeps get_faq_reply in faq.py completely untouched)
# ---------------------------------------------------------------------------

def _faq_match(message: str):
    """
    3-tier FAQ matcher that returns None on no-match (instead of a fallback
    string), letting the view route to the AI advisor.

    Pre-check: if the message contains AI-owned topic words (eligibility,
    interest rate advice, repayment terms, rejection, etc.) we skip FAQ
    entirely so the AI advisor can give a richer, contextual answer.
    """
    msg = message.lower().strip()

    # ── AI pre-emption: topics that belong to the AI advisor ──────────────
    # If ANY of these phrases appear, bypass FAQ and go straight to AI.
    _AI_TOPICS = [
        'eligibility', 'eligible', 'qualify', 'qualify for',
        'interest rate', 'rate of interest', 'roi',
        'repay', 'repayment', 'tenure', 'how long to repay',
        'rejected', 'declined', 'rejection', 'not approved',
        'improve chances', 'bad credit', 'low credit',
        'income analysis', 'emi calculation', 'how much emi',
        'how much can i borrow', 'how much loan', 'borrow how much',
        'recommend', 'suggest', 'which loan', 'what loan for',
        'loan advice', 'loan guidance',
    ]
    for ai_topic in _AI_TOPICS:
        if ai_topic in msg:
            return None   # hand off to AI advisor

    # ── Tier 1: substring match (longest keys first) ───────────────────────
    keys = sorted(FAQ_RESPONSES.keys(), key=len, reverse=True)
    for kw in keys:
        if kw in msg:
            return FAQ_RESPONSES[kw]

    # ── Tier 2a: fuzzy full-message ────────────────────────────────────────
    hits = get_close_matches(msg, keys, n=1, cutoff=0.5)
    if hits:
        return FAQ_RESPONSES[hits[0]]

    # ── Tier 2b: fuzzy per-word ────────────────────────────────────────────
    for word in msg.split():
        if len(word) < 3:
            continue
        hits = get_close_matches(word, keys, n=1, cutoff=0.72)
        if hits:
            return FAQ_RESPONSES[hits[0]]

    return None   # signals "no FAQ match found"





# ---------------------------------------------------------------------------
# ML Loan Approval Predictor helper
# ---------------------------------------------------------------------------

# Trigger phrases that activate the ML predictor layer
_ML_TRIGGERS = [
    "will my loan be approved",
    "loan approval probability",
    "approval chance",
]

def _ml_predict(message: str):
    msg = message.lower().strip()

    if not any(trigger in msg for trigger in _ML_TRIGGERS):
        return None

    income_match = re.search(r'(?:salary|income)\D*(\d+)', msg)
    credit_score_match = re.search(r'credit\s*score\D*(\d+)', msg)
    loan_amount_match = re.search(r'loan\s*amount\D*(\d+)', msg)

    if not (income_match and credit_score_match and loan_amount_match):
        return "Please provide income, credit score and loan amount."

    income = int(income_match.group(1))
    credit_score = int(credit_score_match.group(1))
    loan_amount = int(loan_amount_match.group(1))

    probability = predict_loan_approval({
        "income": income,
        "credit_score": credit_score,
        "loan_amount": loan_amount,
    })

    pct = int(probability * 100)

    return f"Based on our AI model, your loan approval probability is {pct}%."


# ---------------------------------------------------------------------------
# Chatbot endpoint
# ---------------------------------------------------------------------------

_FALLBACK = (
    "I'm not sure about that. Try asking about loan eligibility, "
    "credit score, income & EMI, loan types, or required documents."
)


def chatbot_response(request):
    user_message = request.GET.get("message", "").strip()

    if not user_message:
        return JsonResponse({"reply": "Please type a message to get started."})

    # 1. FAQ check
    faq_reply = _faq_match(user_message)
    if faq_reply:
        return JsonResponse({"reply": faq_reply})

    # 2. ML prediction check
    ml_reply = _ml_predict(user_message)
    if ml_reply:
        return JsonResponse({"reply": ml_reply})

    # 3. AI assistant check
    ai_reply = loan_advisor(user_message)
    if ai_reply:
        return JsonResponse({"reply": ai_reply})

    # 4. fallback
    return JsonResponse({"reply": _FALLBACK})

