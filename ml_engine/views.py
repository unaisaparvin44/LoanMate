from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from loans.models import LoanApplication
from ml_engine.predictor import predict


@login_required
def predict_loan(request, application_id):
    """
    Return an ML eligibility prediction for a given loan application as JSON.

    Access: Any authenticated user. Officers see a richer UI panel;
            regular users see a simplified summary. The view is read-only
            and does NOT modify any application data.

    Response JSON:
        {
            "score": int,
            "recommendation": { "label", "color", "message" },
            "breakdown": [ { "factor", "label", "points", "max" }, ... ]
        }
    """
    # Officers may query any application; users may only query their own.
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'user':
        application = get_object_or_404(LoanApplication, pk=application_id, user=request.user)
    else:
        application = get_object_or_404(LoanApplication, pk=application_id)

    result = predict(application)

    return JsonResponse({
        "score": result["score"],
        "bar_color": result["bar_color"],
        "recommendation": result["recommendation"],
        "breakdown": result["breakdown"],
    })
