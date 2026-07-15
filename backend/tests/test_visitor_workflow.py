import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.api.visitors import register_visitor, take_action
from app.db.base import Base
from app.models.notification import UserNotification
from app.models.resident import Resident
from app.models.society import Block, Flat, Society
from app.models.user import Role, User
from app.models.visitor import Visitor, VisitorStatus
from app.schemas.visitor import VisitorActionRequest, VisitorCreate


class VisitorWorkflowTests(unittest.TestCase):
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
        roles = {name: Role(name=name) for name in ("resident", "admin", "committee", "security")}
        self.db.add_all(roles.values())
        self.db.flush()
        self.ravi = User(email="ravi@test.local", full_name="Ravi", hashed_password="x", society_id=society.id, roles=[roles["resident"]])
        self.admin = User(email="admin@test.local", full_name="Admin", hashed_password="x", society_id=society.id, roles=[roles["admin"]])
        self.committee = User(email="committee@test.local", full_name="Committee", hashed_password="x", society_id=society.id, roles=[roles["committee"]])
        self.security = User(email="security@test.local", full_name="Security", hashed_password="x", society_id=society.id, roles=[roles["security"]])
        self.db.add_all([self.ravi, self.admin, self.committee, self.security])
        self.db.flush()
        self.db.add(Resident(user_id=self.ravi.id, flat_id=flat.id, ownership="owner"))
        self.db.commit()
        self.flat = flat
        self.society = society

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def create_pass(self):
        return register_visitor(VisitorCreate(
            society_id=self.society.id,
            flat_id=self.flat.id,
            name="Ajay Patil",
            purpose="Guest visit",
        ), self.db, self.ravi)

    def test_resident_cannot_approve_own_pass(self):
        visitor = self.create_pass()
        with self.assertRaises(HTTPException) as raised:
            take_action(visitor.id, VisitorActionRequest(action="approve"), self.db, self.ravi)
        self.assertEqual(raised.exception.status_code, 403)
        self.assertEqual(self.db.get(Visitor, visitor.id).status, VisitorStatus.pending)

    def test_committee_approval_notifies_security(self):
        visitor = self.create_pass()
        pending_targets = self.db.execute(select(UserNotification.user_id).where(UserNotification.kind == "visitor_approval_required")).scalars().all()
        self.assertEqual(set(pending_targets), {self.admin.id, self.committee.id})
        approved = take_action(visitor.id, VisitorActionRequest(action="approve"), self.db, self.committee)
        self.assertEqual(approved.status, VisitorStatus.approved)
        security_notice = self.db.execute(select(UserNotification).where(
            UserNotification.user_id == self.security.id,
            UserNotification.kind == "visitor_approved",
        )).scalar_one()
        self.assertIn("Ajay Patil", security_notice.message)
        self.assertIn("Flat 101", security_notice.message)

    def test_security_cannot_approve_but_can_check_in_after_approval(self):
        visitor = self.create_pass()
        with self.assertRaises(HTTPException) as raised:
            take_action(visitor.id, VisitorActionRequest(action="approve"), self.db, self.security)
        self.assertEqual(raised.exception.status_code, 403)
        take_action(visitor.id, VisitorActionRequest(action="approve"), self.db, self.admin)
        checked_in = take_action(visitor.id, VisitorActionRequest(action="check_in"), self.db, self.security)
        self.assertEqual(checked_in.status, VisitorStatus.checked_in)


if __name__ == "__main__":
    unittest.main()
