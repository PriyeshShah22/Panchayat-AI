import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.notification import UserNotification
from app.models.resident import Resident
from app.models.society import Block, Flat, Society
from app.models.user import Role, User
from app.models.visitor import Visitor, VisitorStatus
from app.services.ai_service import (
    _create_action,
    _falsely_denies_available_tool,
    _requests_visitor_pass,
    _tools_for,
    confirm_action,
)


class AIVisitorPassTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        society = Society(name="Test Society", address="Test address")
        self.db.add(society)
        self.db.flush()
        block = Block(society_id=society.id, name="A", floors=4)
        self.db.add(block)
        self.db.flush()
        flat = Flat(society_id=society.id, block_id=block.id, number="101", floor=1)
        self.db.add(flat)
        roles = {name: Role(name=name) for name in ("resident", "admin", "committee")}
        self.db.add_all(roles.values())
        self.db.flush()
        self.resident = User(email="resident@test.local", full_name="Asha", hashed_password="x", society_id=society.id, roles=[roles["resident"]])
        self.admin = User(email="admin@test.local", full_name="Admin", hashed_password="x", society_id=society.id, roles=[roles["admin"]])
        self.committee = User(email="committee@test.local", full_name="Committee", hashed_password="x", society_id=society.id, roles=[roles["committee"]])
        self.db.add_all([self.resident, self.admin, self.committee])
        self.db.flush()
        self.db.add(Resident(user_id=self.resident.id, flat_id=flat.id, ownership="owner"))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_resident_has_visitor_tool_and_confirmation_creates_pending_pass(self):
        self.assertIn("create_visitor_pass", {tool["name"] for tool in _tools_for(self.resident)})
        _result, action = _create_action(self.db, self.resident, "create_visitor_pass", {
            "visitor_name": "Ajay Patil",
            "purpose": "Family visit",
            "expected_at": "2027-01-20T18:00:00+05:30",
            "phone": None,
            "vehicle_number": "mh12ab1234",
            "duration": "one day",
        })
        self.assertIsNotNone(action)
        self.assertEqual(0, self.db.query(Visitor).count())

        result = confirm_action(self.db, self.resident, action.id)

        visitor = self.db.get(Visitor, result["entity_id"])
        self.assertEqual(VisitorStatus.pending, visitor.status)
        self.assertEqual("MH12AB1234", visitor.vehicle_number)
        self.assertIn("one day", visitor.purpose)
        targets = self.db.execute(select(UserNotification.user_id).where(UserNotification.kind == "visitor_approval_required")).scalars().all()
        self.assertEqual({self.admin.id, self.committee.id}, set(targets))

    def test_user_without_resident_profile_does_not_receive_visitor_tool(self):
        self.assertNotIn("create_visitor_pass", {tool["name"] for tool in _tools_for(self.admin)})

    def test_optional_contact_fields_are_explicitly_never_solicited(self):
        tool = next(tool for tool in _tools_for(self.resident) if tool["name"] == "create_visitor_pass")
        properties = tool["parameters"]["properties"]
        self.assertIn("Never ask", properties["phone"]["description"])
        self.assertIn("Never ask", properties["vehicle_number"]["description"])

    def test_hindi_visitor_request_and_false_denial_are_detected(self):
        self.assertTrue(_requests_visitor_pass("Priyesh के लिए visitor pass बना दो"))
        self.assertTrue(_falsely_denies_available_tool("इस चैट में tool access नहीं मिल रही। society office जाएँ।"))
        self.assertFalse(_requests_visitor_pass("आज कौन से visitors अंदर हैं?"))


if __name__ == "__main__":
    unittest.main()
