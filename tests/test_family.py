import pytest
from database import init_db
from auth import register_user, check_parent_access
from family_service import (
    generate_invite_code,
    connect_with_invite_code,
    update_link_status,
    get_child_connected_parents,
)
from medicine_service import add_medicine, get_user_medicines

import uuid

@pytest.fixture
def family_setup():
    init_db()
    uid = uuid.uuid4().hex[:8]
    _, _, parent = register_user(f"parent_fam_{uid}@example.com", "Password123!", "Fam Parent", "parent")
    _, _, child = register_user(f"child_fam_{uid}@example.com", "Password123!", "Fam Child", "child")
    _, _, outsider = register_user(f"outsider_{uid}@example.com", "Password123!", "Outsider", "parent")
    return parent, child, outsider

def test_family_invite_approval_and_revocation(family_setup):
    parent, child, outsider = family_setup

    # 1. Parent generates invite code
    code = generate_invite_code(parent["id"], "Daughter")
    assert code.startswith("HB-")

    # 2. Before approval, child has no access
    assert check_parent_access(child, parent["id"]) is False

    # 3. Child requests connection with code
    ok, msg = connect_with_invite_code(child, code)
    assert ok is True

    # Access is still pending, so child cannot access yet
    assert check_parent_access(child, parent["id"]) is False

    # 4. Parent approves link
    from database import execute_one
    link = execute_one("SELECT id FROM family_links WHERE invite_code = ?", (code,))
    ok_app, msg_app = update_link_status(link["id"], parent, "approved")
    assert ok_app is True

    # 5. Access now granted
    assert check_parent_access(child, parent["id"]) is True

    # Child can see parent in approved list
    approved_parents = get_child_connected_parents(child["id"])
    assert any(p["parent_id"] == parent["id"] for p in approved_parents)

    # 6. Child can read parent's medicines
    add_medicine(parent["id"], "Cardio Med", "20mg", "Daily", ["morning"])
    meds = get_user_medicines(parent["id"], child)
    assert len(meds) >= 1

    # 7. Outsider has NO access (Cross-user data isolation)
    assert check_parent_access(outsider, parent["id"]) is False
    with pytest.raises(PermissionError):
        get_user_medicines(parent["id"], outsider)

    # 8. Parent revokes access
    ok_rev, msg_rev = update_link_status(link["id"], parent, "revoked")
    assert ok_rev is True
    assert check_parent_access(child, parent["id"]) is False

    # Revoked child is now blocked from medicines
    with pytest.raises(PermissionError):
        get_user_medicines(parent["id"], child)
