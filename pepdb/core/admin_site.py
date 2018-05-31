from django_otp.admin import OTPAdminSite


class GrappelliOTPAdminSite(OTPAdminSite):
    name = 'otpadmin'

    login_template = "grappelli_admin_login.html"
