def get_dashboard_url(user):
    """
    Returns the appropriate dashboard URL based on user role
    """
    role_dashboard_mapping = {
        'faculty-sports': 'accounts:faculty_sports_dashboard',
        'faculty-lab': 'accounts:faculty_lab_dashboard',
        'faculty-transport': 'accounts:faculty_transport_dashboard',
        'faculty-hod': 'accounts:faculty_hod_dashboard',
        'faculty-teaching': 'accounts:faculty_teaching_dashboard',
        'admin': 'accounts:admin_dashboard',
        'student': 'accounts:dashboard'
    }
    
    return role_dashboard_mapping.get(user.role, 'accounts:dashboard') 