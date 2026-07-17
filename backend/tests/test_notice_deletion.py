import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.notices import delete_notice
from app.db.base import Base
from app.models.notice import Notice
from app.models.society import Society
from app.models.user import Role, User
from app.services.ai_service import _create_action, confirm_action


class NoticeDeletionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        society = Society(name="Test Society", address="Test address")
        admin_role = Role(name="admin")
        committee_role = Role(name="committee")
        self.db.add_all([society, admin_role, committee_role])
        self.db.flush()
        self.admin = User(email="admin@tests.local", full_name="Admin", hashed_password="x", society_id=society.id, roles=[admin_role])
        self.committee = User(email="committee@tests.local", full_name="Committee", hashed_password="x", society_id=society.id, roles=[committee_role])
        self.db.add_all([self.admin, self.committee])
        self.db.flush()
        self.notice = Notice(society_id=society.id, author_id=self.admin.id, title="Water shutdown", body="Water will stop at noon.")
        self.db.add(self.notice)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_only_admin_can_remove_notice_manually(self):
        with self.assertRaises(HTTPException) as raised:
            delete_notice(self.notice.id, self.db, self.committee)
        self.assertEqual(403, raised.exception.status_code)
        self.assertIsNotNone(self.db.get(Notice, self.notice.id))

        result = delete_notice(self.notice.id, self.db, self.admin)
        self.assertEqual("deleted", result["detail"])
        self.assertIsNone(self.db.get(Notice, self.notice.id))

    def test_ai_notice_removal_requires_confirmation(self):
        _result, action = _create_action(self.db, self.admin, "delete_notice", {"notice_id": self.notice.id})
        self.assertIsNotNone(action)
        self.assertIsNotNone(self.db.get(Notice, self.notice.id))

        result = confirm_action(self.db, self.admin, action.id)

        self.assertEqual("completed", result["status"])
        self.assertIsNone(self.db.get(Notice, self.notice.id))


if __name__ == "__main__":
    unittest.main()
