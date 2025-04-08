from django.contrib.admin import AdminSite
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

class HealthDiaryAdminSite(AdminSite):
    # Site branding
    site_header = _('Health Diary Administration')
    site_title = _('Health Diary Admin')
    index_title = _('Health Diary Management')
    
    # Extra admin site config
    enable_nav_sidebar = True
    
    def each_context(self, request):
        """
        Add extra context variables to each admin page.
        """
        context = super().each_context(request)
        
        # Add dashboard stats in a real app these would be actual database queries
        context.update({
            'user_count': 25,  # Placeholder, should be User.objects.count()
            'meal_count': 350,  # Placeholder, should be Meal.objects.count()
            'health_log_count': 180,  # Placeholder, should be HealthLog.objects.count()
            'sleep_log_count': 120,  # Placeholder, should be Sleep.objects.count()
        })
        
        return context

    def get_app_list(self, request):
        """
        Customize the order of applications in the admin index.
        """
        app_list = super().get_app_list(request)
        
        # Custom ordering - move core app to the top
        app_dict = {app['app_label']: app for app in app_list}
        if 'core' in app_dict:
            core_app = app_dict.pop('core')
            app_list = [core_app] + [app for label, app in app_dict.items()]
        
        return app_list

# Create a new admin site instance
health_diary_admin = HealthDiaryAdminSite(name='health_diary_admin') 