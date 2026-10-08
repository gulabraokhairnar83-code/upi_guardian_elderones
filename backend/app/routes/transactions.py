"""UPI Guardian - Transactions Blueprint."""

from flask import Blueprint, request
from app.services.transaction_service import TransactionService
from app.schemas.validators import validate_analyze_transaction
from app.utils.responses import json_response

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transactions", methods=["GET"])
def list_transactions():
    """List transactions with optional filters.

    GET /api/transactions?status=critical&q=Rahul
    """
    status = request.args.get("status")
    query = request.args.get("q")
    transactions = TransactionService.list_transactions(status=status, query=query)
    return json_response(transactions, status_code=200)


@transactions_bp.route("/transactions/<transaction_id>", methods=["GET"])
def get_transaction(transaction_id: str):
    """Get single transaction by ID.

    GET /api/transactions/<transaction_id>
    """
    transaction = TransactionService.get_transaction(transaction_id)
    return json_response(transaction, status_code=200)


@transactions_bp.route("/analyze-transaction", methods=["POST"])
def analyze_transaction():
    """Analyze a proposed or completed transaction for behavioral anomaly risk.

    POST /api/analyze-transaction
    """
    data = request.get_json(silent=True)
    validated = validate_analyze_transaction(data)
    result = TransactionService.analyze_transaction(validated)
    return json_response(result, status_code=200)
