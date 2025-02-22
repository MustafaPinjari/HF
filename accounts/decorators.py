from django.contrib.auth.decorators import user_passes_test

def faculty_sports_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-sports')(view_func)

def faculty_lab_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-lab')(view_func)

def faculty_transport_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-transport')(view_func)

def faculty_hod_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-hod')(view_func)

def faculty_teaching_required(view_func):
    return user_passes_test(lambda u: u.role == 'faculty-teaching')(view_func) 