import secrets
import logging
from typing import List, Dict, Any, Optional, Tuple

from database import execute_query, execute_one, execute_insert, execute_update, log_audit

logger = logging.getLogger(__name__)

def generate_invite_code(parent_id: int, relationship: str = "Child") -> str:
    """
    Generates a unique, secure invitation code for a parent to invite a child/family member.
    """
    # Generate unpredictable 8-character token
    code = f"HB-{secrets.token_hex(3).upper()}"
    
    # Store in family_links
    execute_insert("""
        INSERT INTO family_links (parent_id, invite_code, relationship, status)
        VALUES (?, ?, ?, 'pending')
    """, (parent_id, code, relationship.strip()))
    
    log_audit(
        actor_id=parent_id,
        target_id=parent_id,
        action="FAMILY_INVITE_GENERATED",
        resource_type="family_links",
        resource_id=code
    )
    return code

def connect_with_invite_code(child_user: Dict[str, Any], invite_code: str) -> Tuple[bool, str]:
    """
    A child inputs an invitation code to request a connection to the parent's health record.
    Requires parent's explicit subsequent approval.
    """
    code_clean = invite_code.strip().upper()
    if child_user["role"] != "child":
        return False, "Only child/caregiver accounts can link using an invitation code."
        
    link = execute_one("""
        SELECT id, parent_id, child_id, status FROM family_links
        WHERE invite_code = ?
    """, (code_clean,))
    
    if not link:
        return False, "Invalid invitation code. Please check with your parent."
        
    if link["parent_id"] == child_user["id"]:
        return False, "You cannot connect to your own account."
        
    if link["child_id"] == child_user["id"] and link["status"] == "approved":
        return False, "You are already connected to this parent."
        
    if link["child_id"] and link["child_id"] != child_user["id"]:
        return False, "This invitation code has already been claimed by another user."
        
    # Associate child with the invite
    execute_update("""
        UPDATE family_links
        SET child_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (child_user["id"], link["id"]))
    
    log_audit(
        actor_id=child_user["id"],
        target_id=link["parent_id"],
        action="FAMILY_LINK_REQUESTED",
        resource_type="family_links",
        resource_id=str(link["id"])
    )
    
    return True, "Connection request sent successfully! Awaiting your parent's approval."

def update_link_status(link_id: int, parent_user: Dict[str, Any], new_status: str) -> Tuple[bool, str]:
    """
    Parent approves or revokes family access.
    """
    if new_status not in ("approved", "revoked"):
        return False, "Invalid status transition."
        
    link = execute_one("SELECT id, parent_id, child_id FROM family_links WHERE id = ?", (link_id,))
    if not link:
        return False, "Family link not found."
        
    if link["parent_id"] != parent_user["id"]:
        log_audit(
            actor_id=parent_user["id"],
            target_id=link["parent_id"],
            action="UNAUTHORIZED_LINK_UPDATE_ATTEMPT",
            resource_type="family_links",
            resource_id=str(link_id)
        )
        return False, "Unauthorized: Only the account owner can approve or revoke access."
        
    if new_status == "approved":
        execute_update("""
            UPDATE family_links
            SET status = 'approved', approved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (link_id,))
    else:
        execute_update("""
            UPDATE family_links
            SET status = 'revoked', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (link_id,))
        
    log_audit(
        actor_id=parent_user["id"],
        target_id=link["child_id"],
        action=f"FAMILY_LINK_{new_status.upper()}",
        resource_type="family_links",
        resource_id=str(link_id)
    )
    
    return True, f"Family access status updated to '{new_status}'."

def get_parent_family_members(parent_id: int) -> List[Dict[str, Any]]:
    """
    Returns all invited or connected family members for a parent.
    """
    rows = execute_query("""
        SELECT fl.id, fl.invite_code, fl.relationship, fl.status, fl.created_at, fl.approved_at,
               u.id as child_user_id, u.full_name as child_name, u.email as child_email, u.phone as child_phone
        FROM family_links fl
        LEFT JOIN users u ON fl.child_id = u.id
        WHERE fl.parent_id = ?
        ORDER BY fl.created_at DESC
    """, (parent_id,))
    return [dict(r) for r in rows]

def get_child_connected_parents(child_id: int) -> List[Dict[str, Any]]:
    """
    Returns list of parents whose health data the child is approved to view.
    """
    rows = execute_query("""
        SELECT fl.id as link_id, fl.relationship, fl.approved_at,
               u.id as parent_id, u.full_name as parent_name, u.email as parent_email, u.phone as parent_phone
        FROM family_links fl
        JOIN users u ON fl.parent_id = u.id
        WHERE fl.child_id = ? AND fl.status = 'approved'
        ORDER BY u.full_name ASC
    """, (child_id,))
    return [dict(r) for r in rows]
