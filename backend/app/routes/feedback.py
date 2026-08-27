from fastapi import APIRouter, Depends, HTTPException, Header, status, Response
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.product import Product
from backend.app.models.feedback import Feedback
from backend.app.schemas.request import FeedbackSubmitRequest
from backend.app.schemas.response import FeedbackData, HistoricalData, FeedbackRecord
from backend.app.schemas.common import APIResponse
from backend.app.auth.bearer import verify_token
from backend.app.services.sentiment import analyze_sentiment
from backend.app.logging.middleware import request_id_ctx
import uuid

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("", response_model=APIResponse)
def submit_feedback(
    payload: FeedbackSubmitRequest,
    response: Response,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    # Set request_id in contextvars for middleware logging
    request_id_str = str(payload.request_id)
    request_id_ctx.set(request_id_str)

    try:
        # Check for idempotency (if the request_id was already processed)
        existing_feedback = db.query(Feedback).filter(Feedback.request_id == request_id_str).first()
        if existing_feedback:
            product = db.query(Product).filter(Product.id == existing_feedback.product_id).first()
            product_name = product.name if product else "Unknown Product"
            
            data = FeedbackData(
                request_id=payload.request_id,
                product_name=product_name,
                product_id=existing_feedback.product_id,
                feedback=existing_feedback.feedback_text,
                sentiment=existing_feedback.sentiment,
                confidence=existing_feedback.confidence_score,
                created_at=existing_feedback.created_at
            )
            return APIResponse(
                success=True,
                status_code=status.HTTP_200_OK,
                message="Feedback with this request ID has already been analyzed and stored.",
                error_message=None,
                data=data
            )

        cleaned_product_name = payload.product_name.strip()

        # Find or create Product (case-insensitive search)
        product = db.query(Product).filter(Product.name.ilike(cleaned_product_name)).first()
        if not product:
            product = Product(name=cleaned_product_name)
            db.add(product)
            db.commit()
            db.refresh(product)

        # Run spaCy-based sentiment analysis
        sentiment, confidence = analyze_sentiment(payload.product_feedback)

        # Write to database
        feedback_obj = Feedback(
            request_id=request_id_str,
            product_id=product.id,
            feedback_text=payload.product_feedback,
            sentiment=sentiment,
            confidence_score=confidence
        )
        db.add(feedback_obj)
        db.commit()
        db.refresh(feedback_obj)

        data = FeedbackData(
            request_id=payload.request_id,
            product_name=product.name,
            product_id=product.id,
            feedback=feedback_obj.feedback_text,
            sentiment=feedback_obj.sentiment,
            confidence=feedback_obj.confidence_score,
            created_at=feedback_obj.created_at
        )

        response.status_code = status.HTTP_201_CREATED
        return APIResponse(
            success=True,
            status_code=status.HTTP_201_CREATED,
            message="Feedback analyzed and persisted successfully.",
            error_message=None,
            data=data
        )

    except Exception as e:
        db.rollback()
        raise e

@router.get("/products", response_model=APIResponse)
def list_products(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """
    Utility endpoint to retrieve all registered products and their IDs.
    Helps the frontend display a clean selection interface.
    """
    products = db.query(Product).order_by(Product.name.asc()).all()
    product_list = [{"id": p.id, "name": p.name} for p in products]
    
    return APIResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Product listing retrieved successfully.",
        error_message=None,
        data=product_list
    )

@router.get("/historical/{product_id}", response_model=APIResponse)
def get_historical_analysis(
    product_id: int,
    x_request_id: str = Header(..., description="UUID-format request ID for header verification"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    # Set request_id in contextvars for logging
    request_id_ctx.set(x_request_id)

    # Validate header UUID format
    try:
        uuid_obj = uuid.UUID(x_request_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header 'x-request-id' must be a valid UUIDv4 string."
        )

    # Query product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} does not exist."
        )

    # Query all feedback for product ordered by creation time desc
    feedbacks = db.query(Feedback).filter(Feedback.product_id == product_id).order_by(Feedback.created_at.desc()).all()

    records = [
        FeedbackRecord(
            request_id=uuid.UUID(fb.request_id),
            feedback=fb.feedback_text,
            sentiment=fb.sentiment,
            confidence=fb.confidence_score,
            created_at=fb.created_at
        )
        for fb in feedbacks
    ]

    data = HistoricalData(
        request_id=uuid_obj,
        product_id=product.id,
        product_name=product.name,
        feedbacks=records
    )

    return APIResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Historical sentiment analysis records retrieved.",
        error_message=None,
        data=data
    )
