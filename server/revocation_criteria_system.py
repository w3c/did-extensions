#!/usr/bin/env python3
"""
Revocation Criteria System
Defines rules and criteria for revoking DIDs, VCs, and Service Grants
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class RevocationReason(Enum):
    """Standard revocation reasons"""
    # VC Revocation Reasons
    VC_EXPIRED = "VC_EXPIRED"
    VC_SUSPECTED_FRAUD = "VC_SUSPECTED_FRAUD"
    VC_DATA_BREACH = "VC_DATA_BREACH"
    VC_CITIZEN_REQUEST = "VC_CITIZEN_REQUEST"
    VC_GOVERNMENT_ORDER = "VC_GOVERNMENT_ORDER"
    VC_CREDENTIAL_MISUSE = "VC_CREDENTIAL_MISUSE"
    VC_IDENTITY_THEFT = "VC_IDENTITY_THEFT"
    VC_COMPLIANCE_VIOLATION = "VC_COMPLIANCE_VIOLATION"
    VC_ADMINISTRATIVE = "VC_ADMINISTRATIVE"
    
    # DID Revocation Reasons
    DID_COMPROMISED = "DID_COMPROMISED"
    DID_KEY_ROTATION = "DID_KEY_ROTATION"
    DID_ACCOUNT_CLOSURE = "DID_ACCOUNT_CLOSURE"
    DID_FRAUD_DETECTED = "DID_FRAUD_DETECTED"
    DID_CITIZEN_REQUEST = "DID_CITIZEN_REQUEST"
    DID_ADMINISTRATIVE = "DID_ADMINISTRATIVE"
    
    # Service Grant Revocation Reasons
    GRANT_SERVICE_ABUSE = "GRANT_SERVICE_ABUSE"
    GRANT_VC_REVOKED = "GRANT_VC_REVOKED"
    GRANT_MISUSE = "GRANT_MISUSE"
    GRANT_TERMS_VIOLATION = "GRANT_TERMS_VIOLATION"
    GRANT_CITIZEN_REQUEST = "GRANT_CITIZEN_REQUEST"
    GRANT_EXPIRED = "GRANT_EXPIRED"
    GRANT_ADMINISTRATIVE = "GRANT_ADMINISTRATIVE"

class RevocationCriteria:
    """Revocation criteria and rules"""
    
    # VC Revocation Criteria
    VC_REVOCATION_RULES = {
        RevocationReason.VC_EXPIRED: {
            "name": "VC Expired",
            "description": "Verifiable Credential has reached its expiration date",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This credential is no longer valid because it has passed its expiration date. The credential holder must apply for renewal.",
            "actions_required": ["Credential renewal application"],
            "can_reissue": True
        },
        RevocationReason.VC_SUSPECTED_FRAUD: {
            "name": "Suspected Fraud",
            "description": "Credential is suspected of being used for fraudulent activities",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This credential has been flagged due to suspicious activity or potential fraud. Government investigation may be required.",
            "actions_required": ["Investigation", "Identity verification", "Document review"],
            "can_reissue": False
        },
        RevocationReason.VC_DATA_BREACH: {
            "name": "Data Breach",
            "description": "Credential data has been compromised in a security breach",
            "severity": "CRITICAL",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This credential has been revoked due to a security breach that compromised the credential data. A new credential must be issued.",
            "actions_required": ["Security audit", "New credential issuance", "Identity re-verification"],
            "can_reissue": True
        },
        RevocationReason.VC_CITIZEN_REQUEST: {
            "name": "Citizen Request",
            "description": "Credential revoked at the request of the citizen",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This credential was revoked because the citizen requested its cancellation. This is usually done when switching to a new credential or for personal reasons.",
            "actions_required": ["New credential application (if needed)"],
            "can_reissue": True
        },
        RevocationReason.VC_GOVERNMENT_ORDER: {
            "name": "Government Order",
            "description": "Credential revoked by government administrative order",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This credential has been revoked by official government order. Contact the issuing authority for more information.",
            "actions_required": ["Contact government authority", "Compliance review"],
            "can_reissue": False
        },
        RevocationReason.VC_CREDENTIAL_MISUSE: {
            "name": "Credential Misuse",
            "description": "Credential has been used in violation of terms and conditions",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This credential has been revoked due to misuse or violation of usage terms. Examples include sharing credentials with unauthorized parties or using for illegal purposes.",
            "actions_required": ["Terms review", "Appeal process (if applicable)", "New credential application"],
            "can_reissue": True
        },
        RevocationReason.VC_IDENTITY_THEFT: {
            "name": "Identity Theft",
            "description": "Credential revoked due to suspected identity theft",
            "severity": "CRITICAL",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This credential has been revoked due to suspected identity theft. If this is an error, please contact support immediately for identity verification.",
            "actions_required": ["Identity verification", "Police report (if applicable)", "New credential issuance"],
            "can_reissue": True
        },
        RevocationReason.VC_COMPLIANCE_VIOLATION: {
            "name": "Compliance Violation",
            "description": "Credential revoked due to regulatory compliance violation",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This credential has been revoked due to non-compliance with government regulations or policies.",
            "actions_required": ["Compliance review", "Regulatory compliance", "New credential application"],
            "can_reissue": True
        },
        RevocationReason.VC_ADMINISTRATIVE: {
            "name": "Administrative",
            "description": "Administrative revocation for record keeping or system maintenance",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This credential was revoked for administrative reasons such as system maintenance or record updates.",
            "actions_required": ["Automatic reissue (if applicable)"],
            "can_reissue": True
        }
    }
    
    # DID Revocation Criteria
    DID_REVOCATION_RULES = {
        RevocationReason.DID_COMPROMISED: {
            "name": "DID Compromised",
            "description": "DID private keys have been compromised",
            "severity": "CRITICAL",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This DID has been revoked because the private keys associated with it have been compromised. A new DID must be created for security.",
            "actions_required": ["New DID generation", "Credential migration", "Key regeneration"],
            "can_reissue": True
        },
        RevocationReason.DID_KEY_ROTATION: {
            "name": "Key Rotation",
            "description": "DID revoked due to scheduled key rotation",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This DID has been revoked as part of a scheduled key rotation process. A new DID with updated keys will be issued.",
            "actions_required": ["New DID generation", "Automatic credential migration"],
            "can_reissue": True
        },
        RevocationReason.DID_ACCOUNT_CLOSURE: {
            "name": "Account Closure",
            "description": "DID revoked due to citizen account closure",
            "severity": "MEDIUM",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This DID has been revoked because the citizen has closed their account or requested DID deactivation.",
            "actions_required": ["Account reactivation (if needed)", "New DID registration"],
            "can_reissue": True
        },
        RevocationReason.DID_FRAUD_DETECTED: {
            "name": "Fraud Detected",
            "description": "DID revoked due to detected fraudulent activity",
            "severity": "CRITICAL",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This DID has been revoked due to detected fraudulent activity or misuse. All associated credentials have also been revoked.",
            "actions_required": ["Investigation", "Identity verification", "New DID registration"],
            "can_reissue": False
        },
        RevocationReason.DID_CITIZEN_REQUEST: {
            "name": "Citizen Request",
            "description": "DID revoked at citizen's request",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This DID was revoked because the citizen requested its deactivation. All associated credentials have been marked for review.",
            "actions_required": ["New DID registration (if needed)"],
            "can_reissue": True
        },
        RevocationReason.DID_ADMINISTRATIVE: {
            "name": "Administrative",
            "description": "Administrative DID revocation",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This DID was revoked for administrative purposes such as system updates or record maintenance.",
            "actions_required": ["System notification", "Automatic reissue (if applicable)"],
            "can_reissue": True
        }
    }
    
    # Service Grant Revocation Criteria
    SERVICE_GRANT_REVOCATION_RULES = {
        RevocationReason.GRANT_SERVICE_ABUSE: {
            "name": "Service Abuse",
            "description": "Service grant revoked due to abuse or misuse of the service",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This service grant has been revoked because the service was used inappropriately or violated terms of service.",
            "actions_required": ["Terms review", "Appeal process", "Service reapplication"],
            "can_reissue": True
        },
        RevocationReason.GRANT_VC_REVOKED: {
            "name": "VC Revoked",
            "description": "Service grant revoked because the underlying VC was revoked",
            "severity": "HIGH",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This service grant was automatically revoked because the Verifiable Credential used to obtain it has been revoked. You must renew your VC to regain service access.",
            "actions_required": ["VC renewal", "Service reapplication"],
            "can_reissue": True
        },
        RevocationReason.GRANT_MISUSE: {
            "name": "Grant Misuse",
            "description": "Service grant revoked due to misuse",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This service grant has been revoked due to misuse or violation of service terms.",
            "actions_required": ["Terms compliance", "Service reapplication"],
            "can_reissue": True
        },
        RevocationReason.GRANT_TERMS_VIOLATION: {
            "name": "Terms Violation",
            "description": "Service grant revoked due to violation of terms and conditions",
            "severity": "HIGH",
            "auto_revocable": False,
            "requires_approval": True,
            "explanation": "This service grant has been revoked because you violated the terms and conditions of the service.",
            "actions_required": ["Terms review", "Compliance", "Service reapplication"],
            "can_reissue": True
        },
        RevocationReason.GRANT_CITIZEN_REQUEST: {
            "name": "Citizen Request",
            "description": "Service grant revoked at citizen's request",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This service grant was revoked because you requested its cancellation.",
            "actions_required": ["Service reapplication (if needed)"],
            "can_reissue": True
        },
        RevocationReason.GRANT_EXPIRED: {
            "name": "Grant Expired",
            "description": "Service grant has expired",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This service grant has expired. You can reapply for the service if needed.",
            "actions_required": ["Service reapplication"],
            "can_reissue": True
        },
        RevocationReason.GRANT_ADMINISTRATIVE: {
            "name": "Administrative",
            "description": "Administrative service grant revocation",
            "severity": "INFO",
            "auto_revocable": True,
            "requires_approval": False,
            "explanation": "This service grant was revoked for administrative reasons.",
            "actions_required": ["Service reapplication (if needed)"],
            "can_reissue": True
        }
    }
    
    @staticmethod
    def get_revocation_details(reason_code: str, entity_type: str) -> Dict[str, Any]:
        """Get detailed revocation information for a reason code"""
        try:
            reason = RevocationReason(reason_code)
            
            if entity_type == "VC":
                rules = RevocationCriteria.VC_REVOCATION_RULES
            elif entity_type == "DID":
                rules = RevocationCriteria.DID_REVOCATION_RULES
            elif entity_type == "SERVICE_GRANT":
                rules = RevocationCriteria.SERVICE_GRANT_REVOCATION_RULES
            else:
                return {
                    "error": f"Unknown entity type: {entity_type}"
                }
            
            if reason in rules:
                return {
                    "success": True,
                    "reason_code": reason_code,
                    "entity_type": entity_type,
                    "details": rules[reason],
                    "severity_color": RevocationCriteria._get_severity_color(rules[reason]["severity"])
                }
            else:
                return {
                    "success": False,
                    "error": f"Reason code {reason_code} not found for {entity_type}"
                }
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid reason code: {reason_code}"
            }
    
    @staticmethod
    def _get_severity_color(severity: str) -> str:
        """Get color code for severity level"""
        severity_colors = {
            "INFO": "#17a2b8",      # Blue
            "MEDIUM": "#ffc107",    # Yellow
            "HIGH": "#fd7e14",      # Orange
            "CRITICAL": "#dc3545"   # Red
        }
        return severity_colors.get(severity, "#6c757d")
    
    @staticmethod
    def get_all_revocation_reasons(entity_type: str) -> List[Dict[str, Any]]:
        """Get all available revocation reasons for an entity type"""
        if entity_type == "VC":
            rules = RevocationCriteria.VC_REVOCATION_RULES
        elif entity_type == "DID":
            rules = RevocationCriteria.DID_REVOCATION_RULES
        elif entity_type == "SERVICE_GRANT":
            rules = RevocationCriteria.SERVICE_GRANT_REVOCATION_RULES
        else:
            return []
        
        return [
            {
                "code": reason.value,
                "name": details["name"],
                "description": details["description"],
                "severity": details["severity"],
                "auto_revocable": details["auto_revocable"],
                "can_reissue": details["can_reissue"]
            }
            for reason, details in rules.items()
        ]
    
    @staticmethod
    def create_revocation_record(entity_type: str,
                                entity_id: str,
                                reason_code: str,
                                revoked_by: str,
                                additional_details: Optional[str] = None,
                                evidence: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a comprehensive revocation record"""
        details = RevocationCriteria.get_revocation_details(reason_code, entity_type)
        
        if not details.get("success"):
            return {
                "success": False,
                "error": details.get("error", "Failed to get revocation details")
            }
        
        revocation_record = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reason_code": reason_code,
            "reason_name": details["details"]["name"],
            "description": details["details"]["description"],
            "explanation": details["details"]["explanation"],
            "severity": details["details"]["severity"],
            "severity_color": details["severity_color"],
            "revoked_by": revoked_by,
            "revoked_at": datetime.now().isoformat(),
            "revoked_timestamp": datetime.now().timestamp(),
            "additional_details": additional_details,
            "evidence": evidence or [],
            "actions_required": details["details"]["actions_required"],
            "can_reissue": details["details"]["can_reissue"],
            "requires_approval": details["details"]["requires_approval"],
            "auto_revocable": details["details"]["auto_revocable"]
        }
        
        return {
            "success": True,
            "revocation_record": revocation_record
        }

