from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, ForeignKey, Text, String, BigInteger, DateTime, Float, Integer
from datetime import datetime, timezone

db = SQLAlchemy()


class Calibration(db.Model):
    __tablename__ = 'calibrations'

    id = Column(BigInteger, primary_key=True)
    calibration_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    username = Column(String(100), nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'calibration_type': self.calibration_type,
            'value': self.value,
            'username': self.username,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,

        }

    def __repr__(self):
        return f'<Calibration {self.id}: {self.calibration_type}={self.value} by {self.username}>'


class Tag(db.Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Tag {self.id}: {self.name}>'


class CalibrationTag(db.Model):
    __tablename__ = 'calibration_tags'

    id = Column(Integer, primary_key=True)
    calibration_id = Column(BigInteger, ForeignKey('calibrations.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    removed_at = Column(DateTime, nullable=True)
    added_by = Column(String(100), nullable=True)  # Track who added the relationship


    # Relationships
    calibration = db.relationship('Calibration', backref='calibration_tags')
    tag = db.relationship('Tag', backref='calibration_tags')

    def to_dict(self):
        return {
            'id': self.id,
            'calibration_id': self.calibration_id,
            'tag_id': self.tag_id,
            'tag_name': self.tag.name if self.tag else None,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'removed_at': self.removed_at.isoformat() if self.removed_at else None,
            'added_by': self.added_by,
            'is_active': self.removed_at is None
        }

    def __repr__(self):
        status = "active" if self.removed_at is None else "removed"
        return f'<CalibrationTag calibration_id={self.calibration_id} tag_id={self.tag_id} {status}>'

    @property
    def is_active(self):
        """Check if the calibration-tag relationship is currently active"""
        return self.removed_at is None

    def soft_delete(self):  # ← Update this method
        """Mark the relationship as removed without actually deleting it"""
        self.removed_at = datetime.utcnow()

    def reactivate(self):
        """Reactivate a previously removed relationship"""
        self.removed_at = None

    @classmethod
    def get_active_for_calibration(cls, calibration_id):
        """Get active relationships for a calibration"""
        return cls.query.filter_by(calibration_id=calibration_id, removed_at=None).all()

    @classmethod
    def get_active_for_tag(cls, tag_id):
        """Get active relationships for a tag"""
        return cls.query.filter_by(tag_id=tag_id, removed_at=None).all()

    @classmethod
    def get_historical_for_tag(cls, tag_id, at_time):
        """Get relationships that were active for a tag at a specific time"""
        from sqlalchemy import and_, or_
        return cls.query.filter(
            and_(
                cls.tag_id == tag_id,
                cls.added_at <= at_time,
                or_(
                    cls.removed_at.is_(None),
                    cls.removed_at > at_time
                )
            )
        ).all()
