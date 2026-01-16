import random

def get_ticket_status(ticket_id: str) -> str:
    """
    Look up the status of a support ticket by its ID.
    
    Args:
        ticket_id: The ID of the ticket (e.g., TKT-123)
        
    Returns:
        The status of the ticket (e.g., "Open", "In Progress", "Resolved")
    """
    # Mock database
    statuses = ["Open", "In Progress", "Waiting for Customer", "Resolved", "Closed"]
    
    # Deterministic mock based on ID hash for consistent testing
    seed = sum(ord(c) for c in ticket_id)
    random.seed(seed)
    
    return random.choice(statuses)
