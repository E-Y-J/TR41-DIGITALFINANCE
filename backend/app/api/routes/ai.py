# =============================================================================
# Digital Finance Tracker - AI API Routes
# PURPOSE: REST API endpoints for AI-powered features
# =============================================================================
"""
AI Routes Module

This module provides API endpoints for AI features:
- Transaction categorization
- Chat interactions (NLP commands)
- Chat history retrieval
- Spending insights
- Clarification handling
- Health monitoring

Endpoints:
    POST /api/v1/ai/categorize - Categorize a transaction
    POST /api/v1/ai/chat - Send chat message
    GET  /api/v1/ai/chat/history - Get user's chat history
    GET  /api/v1/ai/insights - Get spending insights
    GET  /api/v1/ai/clarifications - Get pending clarifications
    POST /api/v1/ai/clarifications/{id}/resolve - Resolve a clarification
    POST /api/v1/ai/clarifications/{id}/dismiss - Dismiss a clarification
    GET  /api/v1/ai/status - Get AI system status (requires auth)
    GET  /api/v1/ai/health - Health check for monitoring (no auth required)

All endpoints require authentication via Auth0 except /health.
"""

import logging
from flask import Blueprint, request, jsonify, g
from uuid import UUID
from marshmallow import Schema, fields, validate, ValidationError

from app.auth.decorators import requires_auth
from app.auth.user_sync import sync_user_from_claims
from app.utils.errors import ValidationError as AppValidationError
from app.utils.errors import NotFoundError

logger = logging.getLogger(__name__)

bp = Blueprint("ai", __name__, url_prefix="/api/v1/ai")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class CategorizeRequestSchema(Schema):
    """Schema for categorization request."""

    text = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    amount = fields.Float(required=False, validate=validate.Range(min=0))
    transaction_type = fields.Str(
        required=False, validate=validate.OneOf(["expense", "income"])
    )


class ChatRequestSchema(Schema):
    """Schema for chat request."""

    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    context = fields.Dict(required=False)


class ResolveClarificationSchema(Schema):
    """Schema for resolving a clarification."""

    choice = fields.Str(required=True, validate=validate.Length(min=1, max=100))


# Initialize schemas
categorize_schema = CategorizeRequestSchema()
chat_schema = ChatRequestSchema()
resolve_schema = ResolveClarificationSchema()


# =============================================================================
# CATEGORIZATION ENDPOINT
# =============================================================================


@bp.route("/categorize", methods=["POST"])
@requires_auth
def categorize_transaction():
    """
    Categorize a transaction based on text.

    Request Body:
        {
            "text": "Starbucks Coffee",
            "amount": 5.50,
            "transaction_type": "expense"
        }

    Response:
        {
            "success": true,
            "data": {
                "category": "Food & Dining",
                "category_id": "uuid",
                "confidence": 0.95,
                "source": "huggingface",
                "alternatives": [...]
            }
        }
    """
    try:
        # Validate request
        data = categorize_schema.load(request.get_json() or {})
    except ValidationError as e:
        raise AppValidationError(str(e.messages))

    try:
        from app.ai.orchestrator import get_orchestrator

        orchestrator = get_orchestrator()

        # Get user_id from auth context for personalized learning
        user = sync_user_from_claims(g.current_user)
        user_id = user.id if user else None

        result = orchestrator.categorize(
            merchant_name=data["text"],
            amount=data.get("amount"),
            transaction_type=data.get("transaction_type"),
            user_id=user_id,
        )

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Categorization failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "CATEGORIZATION_FAILED",
                "message": "Could not categorize the transaction",
            }
        }), 500


# =============================================================================
# CHAT ENDPOINTS
# =============================================================================


@bp.route("/chat", methods=["POST"])
@requires_auth
def chat():
    """
    Process a chat message.

    Request Body:
        {
            "message": "Add $50 for lunch at Subway",
            "context": {}
        }

    Response:
        {
            "success": true,
            "data": {
                "intent": "create_transaction",
                "response": "I'll add a $50 expense...",
                "requires_confirmation": true,
                "parsed_data": {...},
                "alternatives": []
            }
        }
    """
    try:
        data = chat_schema.load(request.get_json() or {})
    except ValidationError as e:
        raise AppValidationError(str(e.messages))

    try:
        from app.ai.chat_handler import get_chat_handler

        handler = get_chat_handler()
        handler.initialize()

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        result = handler.process_message(
            user_id=user_id,
            message=data["message"],
            context=data.get("context"),
        )

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Chat processing failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "CHAT_FAILED",
                "message": "Could not process your message",
            }
        }), 500


# =============================================================================
# CHAT HISTORY ENDPOINT
# =============================================================================


@bp.route("/chat/history", methods=["GET"])
@requires_auth
def get_chat_history():
    """
    Get all chat history for the authenticated user.

    Returns all chat sessions with conversation history, ordered by
    most recent first. Supports pagination.

    Query Parameters:
        page (int): Page number, 1-indexed (default: 1)
        per_page (int): Sessions per page, max 50 (default: 20)
        include_inactive (bool): Include expired sessions (default: false)

    Response:
        {
            "success": true,
            "data": {
                "sessions": [
                    {
                        "id": "uuid",
                        "conversation_history": [
                            {
                                "role": "user",
                                "content": "Add $50 for lunch",
                                "timestamp": "2026-02-03T10:30:00Z"
                            },
                            {
                                "role": "assistant",
                                "content": "I'll add a $50 expense...",
                                "timestamp": "2026-02-03T10:30:01Z"
                            }
                        ],
                        "last_intent": "create_transaction",
                        "is_active": true,
                        "created_at": "2026-02-03T10:00:00Z",
                        "updated_at": "2026-02-03T10:30:01Z"
                    }
                ]
            },
            "meta": {
                "page": 1,
                "per_page": 20,
                "total": 5,
                "has_more": false
            }
        }
    """
    try:
        from app.models.ai_session import AISession

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        # Parse query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        include_inactive = request.args.get("include_inactive", "false").lower() == "true"

        # Validate pagination
        page = max(1, page)
        per_page = max(1, min(per_page, 50))

        # Get sessions
        sessions, total, has_more = AISession.get_all_for_user(
            user_id=user_id,
            include_inactive=include_inactive,
            page=page,
            per_page=per_page,
        )

        return jsonify({
            "success": True,
            "data": {
                "sessions": [session.to_dict() for session in sessions],
            },
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "has_more": has_more,
            }
        }), 200

    except Exception as e:
        logger.error(f"Get chat history failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "CHAT_HISTORY_FAILED",
                "message": "Could not retrieve chat history",
            }
        }), 500


# =============================================================================
# INSIGHTS ENDPOINT
# =============================================================================


@bp.route("/insights", methods=["GET"])
@requires_auth
def get_insights():
    """
    Get AI-powered spending insights.

    Query Parameters:
        period: day, week, month, year (default: month)

    Response:
        {
            "success": true,
            "data": {
                "period": "month",
                "top_categories": [...],
                "spending_trend": "increasing",
                "recommendations": [...],
                "anomalies": [...]
            }
        }
    """
    try:
        from app.ai.anomaly_detector import get_detector

        period = request.args.get("period", "month")

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        detector = get_detector()
        insights = detector.get_spending_insights(user_id)

        return jsonify({"success": True, "data": insights}), 200

    except Exception as e:
        logger.error(f"Insights failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "INSIGHTS_FAILED",
                "message": "Could not generate insights",
            }
        }), 500


# =============================================================================
# CLARIFICATION ENDPOINTS
# =============================================================================


@bp.route("/clarifications", methods=["GET"])
@requires_auth
def get_clarifications():
    """
    Get pending clarifications for the user.

    Response:
        {
            "success": true,
            "data": [
                {
                    "id": "uuid",
                    "type": "category",
                    "alternatives": [...],
                    "created_at": "2024-01-01T12:00:00Z"
                }
            ]
        }
    """
    try:
        from app.ai.clarification import get_clarification_manager

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        manager = get_clarification_manager()
        pending = manager.get_pending_requests(user_id)

        return jsonify({
            "success": True,
            "data": [r.to_dict() for r in pending]
        }), 200

    except Exception as e:
        logger.error(f"Get clarifications failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "CLARIFICATION_FAILED",
                "message": "Could not retrieve clarifications",
            }
        }), 500


@bp.route("/clarifications/<clarification_id>/resolve", methods=["POST"])
@requires_auth
def resolve_clarification(clarification_id: str):
    """
    Resolve a clarification with user's choice.

    Request Body:
        {"choice": "Food & Dining"}

    Response:
        {"success": true, "data": {"id": "uuid", "status": "resolved"}}
    """
    try:
        data = resolve_schema.load(request.get_json() or {})
    except ValidationError as e:
        raise AppValidationError(str(e.messages))

    try:
        from app.ai.clarification import get_clarification_manager

        manager = get_clarification_manager()
        request_obj = manager.resolve_request(
            UUID(clarification_id),
            data["choice"],
        )

        if not request_obj:
            raise NotFoundError("Clarification not found")

        return jsonify({
            "success": True,
            "data": request_obj.to_dict()
        }), 200

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Resolve clarification failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "RESOLVE_FAILED",
                "message": "Could not resolve clarification",
            }
        }), 500


@bp.route("/clarifications/<clarification_id>/dismiss", methods=["POST"])
@requires_auth
def dismiss_clarification(clarification_id: str):
    """
    Dismiss a clarification without responding.

    Response:
        {"success": true, "data": {"id": "uuid", "status": "dismissed"}}
    """
    try:
        from app.ai.clarification import get_clarification_manager

        manager = get_clarification_manager()
        request_obj = manager.dismiss_request(UUID(clarification_id))

        if not request_obj:
            raise NotFoundError("Clarification not found")

        return jsonify({
            "success": True,
            "data": request_obj.to_dict()
        }), 200

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Dismiss clarification failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "DISMISS_FAILED",
                "message": "Could not dismiss clarification",
            }
        }), 500


# =============================================================================
# STATUS ENDPOINT
# =============================================================================


@bp.route("/status", methods=["GET"])
@requires_auth
def get_status():
    """
    Get AI system status.

    Response:
        {
            "success": true,
            "data": {
                "orchestrator": {"is_ready": true, ...},
                "gemini": {"is_initialized": true, ...},
                "chat": {"is_initialized": true},
                "intent_classifier": {"is_initialized": true, ...},
                "guardrails": {"is_initialized": true, ...},
                "model_router": {"is_ready": true, ...},
                "clarifications": {"total_pending": 5}
            }
        }
    """
    try:
        status = {}

        # Orchestrator status
        try:
            from app.ai.orchestrator import get_orchestrator

            orchestrator = get_orchestrator()
            status["orchestrator"] = orchestrator.get_info()
        except Exception as e:
            status["orchestrator"] = {"error": str(e)}

        # Gemini status
        try:
            from app.ai.gemini_client import get_gemini_client

            gemini = get_gemini_client()
            status["gemini"] = gemini.get_status()
        except Exception as e:
            status["gemini"] = {"error": str(e)}

        # Chat status
        try:
            from app.ai.chat_handler import get_chat_handler

            chat = get_chat_handler()
            status["chat"] = {"is_initialized": chat.is_initialized}
        except Exception as e:
            status["chat"] = {"error": str(e)}

        # Intent Classifier status
        try:
            from app.ai.intent_classifier import get_intent_classifier

            classifier = get_intent_classifier()
            status["intent_classifier"] = classifier.get_info()
        except Exception as e:
            status["intent_classifier"] = {"error": str(e)}

        # Guardrails status
        try:
            from app.ai.guardrails import get_guardrails

            guardrails = get_guardrails()
            status["guardrails"] = guardrails.get_info()
        except Exception as e:
            status["guardrails"] = {"error": str(e)}

        # Model Router status
        try:
            from app.ai.model_router import get_model_router

            router = get_model_router()
            status["model_router"] = router.get_info()
        except Exception as e:
            status["model_router"] = {"error": str(e)}

        # Clarification status
        try:
            from app.ai.clarification import get_clarification_manager

            manager = get_clarification_manager()
            status["clarifications"] = manager.get_stats()
        except Exception as e:
            status["clarifications"] = {"error": str(e)}

        return jsonify({"success": True, "data": status}), 200

    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "STATUS_FAILED",
                "message": "Could not retrieve AI status",
            }
        }), 500


@bp.route("/health", methods=["GET"])
def get_health():
    """
    Health check endpoint for monitoring systems.

    Does NOT require authentication - for load balancers/k8s probes.

    Response:
        {
            "status": "healthy" | "degraded" | "unhealthy",
            "components": {
                "gemini": "ok" | "unavailable",
                "intent_classifier": "ok" | "fallback" | "unavailable",
                "categorizer": "ok" | "unavailable",
                "guardrails": "ok" | "unavailable"
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
    """
    from datetime import datetime, timezone

    components = {}
    overall_status = "healthy"

    # Check Gemini
    try:
        from app.ai.gemini_client import get_gemini_client
        gemini = get_gemini_client()
        components["gemini"] = "ok" if gemini.is_initialized else "unavailable"
    except Exception:
        components["gemini"] = "unavailable"

    # Check Intent Classifier
    try:
        from app.ai.intent_classifier import get_intent_classifier
        classifier = get_intent_classifier()
        if classifier.is_initialized:
            if hasattr(classifier, '_use_fallback') and classifier._use_fallback:
                components["intent_classifier"] = "fallback"
                overall_status = "degraded"
            else:
                components["intent_classifier"] = "ok"
        else:
            components["intent_classifier"] = "unavailable"
    except Exception:
        components["intent_classifier"] = "unavailable"

    # Check Categorizer
    try:
        from app.ai.categorizer import get_categorizer
        categorizer = get_categorizer()
        components["categorizer"] = "ok" if categorizer.is_ready else "unavailable"
    except Exception:
        components["categorizer"] = "unavailable"

    # Check Guardrails
    try:
        from app.ai.guardrails import get_guardrails
        guardrails = get_guardrails()
        components["guardrails"] = "ok" if guardrails.is_initialized else "unavailable"
    except Exception:
        components["guardrails"] = "unavailable"

    # Check RAG
    try:
        from app.ai.rag import get_rag_engine
        rag = get_rag_engine()
        components["rag"] = "ok" if rag.is_enabled else "unavailable"
    except Exception:
        components["rag"] = "unavailable"

    # Check Recurring Detector
    try:
        from app.ai.recurring_detector import get_recurring_detector
        recurring = get_recurring_detector()
        components["recurring_detector"] = "ok" if recurring.is_initialized else "unavailable"
    except Exception:
        components["recurring_detector"] = "unavailable"

    # Determine overall status
    unavailable_count = sum(1 for v in components.values() if v == "unavailable")
    if unavailable_count >= 2:
        overall_status = "unhealthy"
    elif unavailable_count >= 1 or "fallback" in components.values():
        overall_status = "degraded"

    return jsonify({
        "status": overall_status,
        "components": components,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200 if overall_status != "unhealthy" else 503


# =============================================================================
# RECURRING TRANSACTIONS ENDPOINTS
# =============================================================================


@bp.route("/recurring", methods=["GET"])
@requires_auth
def get_recurring_patterns():
    """
    Get detected recurring transaction patterns.

    Analyzes user's transaction history to identify subscriptions
    and regular bills.

    Query Parameters:
        force_refresh (bool): Force recalculation (ignore cache)

    Response:
        {
            "success": true,
            "data": {
                "patterns": [
                    {
                        "merchant_name": "Netflix",
                        "category_name": "Entertainment",
                        "average_amount": 15.99,
                        "interval": "monthly",
                        "next_expected": "2026-02-01",
                        "confidence": 0.95
                    }
                ],
                "monthly_total": 150.00,
                "pattern_count": 5
            }
        }
    """
    try:
        from app.ai.recurring_detector import get_recurring_detector

        force_refresh = request.args.get("force_refresh", "false").lower() == "true"

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        detector = get_recurring_detector()
        patterns = detector.detect_patterns(user_id, force_refresh=force_refresh)
        monthly_totals = detector.get_monthly_recurring_total(user_id)

        return jsonify({
            "success": True,
            "data": {
                "patterns": [p.to_dict() for p in patterns],
                "monthly_total": monthly_totals["monthly_total"],
                "yearly_projected": monthly_totals["yearly_projected"],
                "pattern_count": monthly_totals["pattern_count"],
                "by_category": monthly_totals["by_category"],
            }
        }), 200

    except Exception as e:
        logger.error(f"Get recurring patterns failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "RECURRING_FAILED",
                "message": "Could not detect recurring patterns",
            }
        }), 500


@bp.route("/recurring/upcoming", methods=["GET"])
@requires_auth
def get_upcoming_bills():
    """
    Get predicted upcoming recurring bills.

    Query Parameters:
        days (int): Days to look ahead (default: 30, max: 90)

    Response:
        {
            "success": true,
            "data": {
                "upcoming": [
                    {
                        "merchant_name": "Netflix",
                        "expected_amount": 15.99,
                        "expected_date": "2026-02-01",
                        "days_until": 5
                    }
                ],
                "total_expected": 45.99
            }
        }
    """
    try:
        from app.ai.recurring_detector import get_recurring_detector

        days_ahead = min(request.args.get("days", 30, type=int), 90)

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        detector = get_recurring_detector()
        upcoming = detector.get_upcoming_bills(user_id, days_ahead=days_ahead)

        total_expected = sum(b["expected_amount"] for b in upcoming)

        return jsonify({
            "success": True,
            "data": {
                "upcoming": upcoming,
                "total_expected": round(total_expected, 2),
                "days_ahead": days_ahead,
            }
        }), 200

    except Exception as e:
        logger.error(f"Get upcoming bills failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "UPCOMING_FAILED",
                "message": "Could not predict upcoming bills",
            }
        }), 500


@bp.route("/recurring/missed", methods=["GET"])
@requires_auth
def get_missed_payments():
    """
    Check for potentially missed recurring payments.

    Returns payments that were expected but haven't occurred.

    Response:
        {
            "success": true,
            "data": {
                "missed": [
                    {
                        "merchant_name": "Spotify",
                        "expected_amount": 9.99,
                        "expected_date": "2026-01-15",
                        "days_overdue": 5
                    }
                ],
                "count": 1
            }
        }
    """
    try:
        from app.ai.recurring_detector import get_recurring_detector

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        detector = get_recurring_detector()
        missed = detector.check_missed_payments(user_id)

        return jsonify({
            "success": True,
            "data": {
                "missed": missed,
                "count": len(missed),
            }
        }), 200

    except Exception as e:
        logger.error(f"Check missed payments failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSED_CHECK_FAILED",
                "message": "Could not check missed payments",
            }
        }), 500


@bp.route("/rag/stats", methods=["GET"])
@requires_auth
def get_rag_stats():
    """
    Get RAG engine statistics.

    Response:
        {
            "success": true,
            "data": {
                "is_enabled": true,
                "total_vectors": 150,
                "users_indexed": 5
            }
        }
    """
    try:
        from app.ai.rag import get_rag_engine

        engine = get_rag_engine()
        stats = engine.get_stats()

        return jsonify({
            "success": True,
            "data": stats
        }), 200

    except Exception as e:
        logger.error(f"Get RAG stats failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "RAG_STATS_FAILED",
                "message": "Could not get RAG statistics",
            }
        }), 500


@bp.route("/rag/query", methods=["POST"])
@requires_auth
def query_rag():
    """
    Query transactions using natural language via RAG.

    Request Body:
        {
            "query": "coffee shop purchases",
            "top_k": 10
        }

    Response:
        {
            "success": true,
            "data": {
                "results": [
                    {"merchant_name": "Starbucks", "amount": 5.50, "similarity": 0.85}
                ]
            }
        }
    """
    try:
        from app.ai.rag import get_rag_engine

        data = request.get_json() or {}
        query = data.get("query", "").strip()
        top_k = min(data.get("top_k", 10), 50)

        if not query:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": "Query is required"},
            }), 400

        user = sync_user_from_claims(g.current_user)
        user_id = user.id

        engine = get_rag_engine()
        results = engine.query_transactions(user_id, query, top_k=top_k)

        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "query": query,
                "count": len(results),
            }
        }), 200

    except Exception as e:
        logger.error(f"RAG query failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": "RAG_QUERY_FAILED",
                "message": "Could not query transactions",
            }
        }), 500


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = ["bp"]
