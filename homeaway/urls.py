from django.urls import path
from homeaway import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


urlpatterns = [

    # path('', login_required(views.UserHome.as_view(), login_url='signin'),name='userhome'),
    path('', login_required(views.Home.as_view(), login_url='signin'),name='userhome'),
    path('signup', views.Signup.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', views.ActivateView.as_view(), name="activate"),
    path('check-email/', views.CheckEmailView.as_view(), name="check_email"),
    path('success/', views.SuccessView.as_view(), name="success"),
    path('signin', views.SigninView.as_view(), name='signin'),
    path('signout', views.signout, name='signout'),
    path('user/my-profile', views.view_userprofile, name= 'user-profile'),
    path('update-profile_image', views.updateproimage, name='update_proimage'),
    path('deleteprofilepic',views.deleteproimg, name='delete-proimg'),
    path('update-sociallinks',views.usersocial_profile, name='usersocprofile'),
    path('accounts/password/reset',views.ChangePassword.as_view(),name='resetpassword'),
    path('liked/',views.like_unlike_post, name='likeaction'),
    path('account/forgotpassword/',views.Forgot_Password.as_view(),name='forgotpswd'),
    path('accounts/profile/<str:pk>/<int:userid>',views.UserProfiles.as_view(),name='usersprofileview'),
    path('follow_unfollow/',views.FollowUnfollow.as_view(), name='followunfollow'),
    path('reqstmanage/',views.buddy_request_manage,name='reqstmanages'),
    path('pplfollowunfollows/', views.ppl_folow_unflw, name='followunfollows'),
    path('people/', views.Ppls.as_view(), name='ppls'),
    path('post/<str:pk>',views.PostView.as_view(), name='post-view')



]
