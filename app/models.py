from typing import Dict, Any, Optional
from datetime import datetime
from app import db


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    @staticmethod
    def create_admin(username: str, password: str) -> Dict[str, Any]:
        _admin = Admin(username=username, password=password)
        db.session.add(_admin)
        db.session.commit()
        return {"id": _admin.id, "username": _admin.username, "password": _admin.password}

    @staticmethod
    def get_admin_by_id(id: int):
        return Admin.query.filter_by(id=id).first()

    @staticmethod
    def update_admin_by_id(id: int, username: str, password: str) -> Dict[str, Any]:
        """
        Updates the admin's username and password by ID.

        :param id: Admin ID to update
        :param username: New username
        :param password: New password
        :return: A dictionary containing updated admin info
        """
        # Retrieve the admin by id
        _admin = Admin.query.filter_by(id=id).first()

        # If admin not found, return an error message
        if not _admin:
            return {"error": "Admin not found"}

        # Update the admin details
        _admin.username = username
        _admin.password = password

        # Commit the changes to the database
        db.session.commit()

        # Return updated admin info
        return {"id": _admin.id, "username": _admin.username, "password": _admin.password}

    @staticmethod
    def delete_admin_by_id(id: int) -> Dict[str, Any]:
        _admin = Admin.query.filter_by(id=id).first()

        if not _admin:
            return {"error": "Admin not found"}

        # Delete the admin from the database
        db.session.delete(_admin)
        db.session.commit()

        # Return a confirmation message with deleted admin's info
        return {"id": _admin.id, "username": _admin.username, "password": _admin.password}


class ScannedImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_image = db.Column(db.LargeBinary)                    # Raw binary data of the scanned image
    annotated_image = db.Column(db.LargeBinary)              # Annotated version of the image, if available
    extracted_text = db.Column(db.Text, nullable=False)      # Extracted text from the image
    scanned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of scan

    @staticmethod
    def create_scanned_image(raw_image: bytes, annotated_image: Optional[bytes], extracted_text: str) -> Dict[str, Any]:
        """
        Creates a new ScannedImages entry.
        """
        scanned_image = ScannedImages(
            raw_image=raw_image,
            annotated_image=annotated_image,
            extracted_text=extracted_text,
            scanned_at=datetime.utcnow()
        )
        db.session.add(scanned_image)
        db.session.commit()

        return {
            "id": scanned_image.id,
            "extracted_text": scanned_image.extracted_text,
            "scanned_at": scanned_image.scanned_at
        }

    @staticmethod
    def get_scanned_image_by_id(id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a ScannedImages entry by ID.
        """
        scanned_image = ScannedImages.query.filter_by(id=id).first()

        if not scanned_image:
            return None

        return {
            "id": scanned_image.id,
            "extracted_text": scanned_image.extracted_text,
            "scanned_at": scanned_image.scanned_at
        }

    @staticmethod
    def update_scanned_image_by_id(id: int, raw_image: Optional[bytes], annotated_image: Optional[bytes],
                                   extracted_text: Optional[str]) -> Dict[str, Any]:
        """
        Updates a ScannedImages entry by ID.
        """
        scanned_image = ScannedImages.query.filter_by(id=id).first()

        if not scanned_image:
            return {"error": "Scanned image not found"}

        # Update fields only if new values are provided
        if raw_image is not None:
            scanned_image.raw_image = raw_image
        if annotated_image is not None:
            scanned_image.annotated_image = annotated_image
        if extracted_text is not None:
            scanned_image.extracted_text = extracted_text

        db.session.commit()

        return {
            "id": scanned_image.id,
            "extracted_text": scanned_image.extracted_text,
            "scanned_at": scanned_image.scanned_at
        }

    @staticmethod
    def delete_scanned_image_by_id(id: int) -> Dict[str, Any]:
        """
        Deletes a ScannedImages entry by ID.
        """
        scanned_image = ScannedImages.query.filter_by(id=id).first()

        if not scanned_image:
            return {"error": "Scanned image not found"}

        db.session.delete(scanned_image)
        db.session.commit()

        return {
            "message": "Scanned image deleted successfully",
            "id": id
        }
