import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.models.ad import Ad
from app.models.alert import Alert
from app.models.competitor import Competitor
from app.models.opportunity import ObjectionCluster, Opportunity
from app.schemas.alert import AlertResponse, WeeklyDigestResponse

logger = get_logger("service.alert")


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def list_alerts(self, unread_only: bool = False, limit: int = 50) -> List[AlertResponse]:
        query = self.db.query(Alert).join(Competitor)
        if unread_only:
            query = query.filter(Alert.is_read == False)
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

        return [
            AlertResponse(
                id=a.id,
                competitor_id=a.competitor_id,
                competitor_name=a.competitor.name,
                alert_type=a.alert_type,
                title=a.title,
                message=a.message,
                data=json.loads(a.data_json) if a.data_json else {},
                is_read=a.is_read,
                created_at=a.created_at,
            )
            for a in alerts
        ]

    def mark_read(self, alert_id: int) -> bool:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_read = True
            self.db.commit()
            return True
        return False

    def mark_all_read(self) -> int:
        count = self.db.query(Alert).filter(Alert.is_read == False).update({"is_read": True})
        self.db.commit()
        return count

    def create_alert(
        self,
        competitor_id: int,
        alert_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> Alert:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        alert = Alert(
            competitor_id=competitor_id,
            alert_type=alert_type,
            title=title,
            message=message,
            data_json=json.dumps(data or {}),
            is_read=False,
            created_at=now,
        )
        self.db.add(alert)
        self.db.commit()
        return alert

    def get_weekly_digest(self) -> WeeklyDigestResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        week_ago = now - timedelta(days=7)

        active_comps = self.db.query(Competitor).filter(Competitor.is_active == True).count()
        total_ads = self.db.query(Ad).filter(Ad.is_active == True).count()
        new_ads = self.db.query(Ad).filter(Ad.first_seen >= week_ago).count()
        unread_alerts = self.db.query(Alert).filter(Alert.is_read == False).count()

        # Top rising objections
        clusters = (
            self.db.query(ObjectionCluster)
            .order_by(ObjectionCluster.intensity.desc())
            .limit(3)
            .all()
        )
        rising_objections = [
            {
                "label": c.label,
                "category": c.category,
                "intensity": c.intensity,
                "competitor_count": c.competitor_count,
            }
            for c in clusters
        ]

        # Top opportunities
        opportunities = (
            self.db.query(Opportunity)
            .order_by(Opportunity.score.desc())
            .limit(3)
            .all()
        )
        top_opps = [
            {
                "id": o.id,
                "score": o.score,
                "category": o.cluster.category,
                "counter_angle": o.counter_angle,
            }
            for o in opportunities
        ]

        summary = (
            f"Ad Desk tracked {total_ads} active competitor ads across {active_comps} local institutes this week. "
            f"{new_ads} new creative campaigns were launched. "
            + (f"The top market doubt is '{rising_objections[0]['label']}'." if rising_objections else "Market intelligence is active.")
        )

        return WeeklyDigestResponse(
            generated_at=now,
            active_competitors_count=active_comps,
            total_active_ads=total_ads,
            new_ads_this_week=new_ads,
            unread_alerts_count=unread_alerts,
            top_rising_objections=rising_objections,
            top_opportunities=top_opps,
            summary=summary,
        )

