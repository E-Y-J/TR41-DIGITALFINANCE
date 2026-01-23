# =============================================================================
# Digital Finance Tracker - AI API Routes
# PURPOSE: REST API endpoints for AI-powered features
# =============================================================================
"""
AI Routes Module

This module provides API endpoints for AI features:
- Transaction categorization
- Chat interactions (NLP commands)
- Spending insights
- Clarification handling
- Health monitoring

Endpoints:
    POST /api/v1/ai/categorize - Categorize a transaction
    POST /api/v1/ai/chat - Send chat message
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
        user_id = UUID(g.user.id) if hasattr(g, "user") and g.user else None

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

        user_id = UUID(g.user.id) if hasattr(g, "user") else None
        if not user_id:
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "User not found"},
            }), 401

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

        user_id = UUID(g.user.id) if hasattr(g, "user") else None
        if not user_id:
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "User not found"},
            }), 401

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

        user_id = UUID(g.user.id) if hasattr(g, "user") else None
        if not user_id:
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "User not found"},
            }), 401

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
# MODULE EXPORTS
# =============================================================================

__all__ = ["bp"]
