from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView,DeleteView, CreateView, ListView, UpdateView, DetailView, FormView, RedirectView
from .models import Users, Post, Profile,Like, FollowersCount,UserImages,UserSocialLinks
from django.contrib import messages
from django.contrib.auth import authenticate,logout, login, update_session_auth_hash
from .forms import SignupForm, LoginForm, UserprofileForm,Password_ResetForm
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .token import token_generator
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from django.db.models.query_utils import Q

from itertools import chain
# from django.contrib.sessions.models import Session




# @login_required(login_url='signin')
class Home(TemplateView):
    template_name = 'home.html'


    def post(self, request, *args, **kwargs):

        caption = request.POST.get('caption')
        image = request.FILES.get('image')
        post_obj = Post.objects.create(user=request.user, image=image, caption=caption)
        post_obj.save()
        return redirect('userhome')


    def get(self,request,*args,**kwargs):
        post_list = Post.objects.filter(user_id=self.request.user.id).order_by('-created_at')
        users_following = []
        posts = []
        ppl_may_konw = []

        following_list = FollowersCount.objects.filter(follower_id=self.request.user.id,status='accepted')

        for user in following_list:
            users_following.append(user)

        for uid_obj in users_following:
            all_following_posts= Post.objects.filter(user_id=uid_obj.user_id)
            posts.append(all_following_posts)
            post_list = list(chain(*posts))

            ppl_may_konw= FollowersCount.objects.filter(follower_id=uid_obj.user_id).exclude(user_id=self.request.user.id)


        followrqst= FollowersCount.objects.filter(user_id=self.request.user.id,status='pending')


        context={
            'reqst':followrqst,
            'all_posts': post_list,
            'peopleyou_know': ppl_may_konw
        }




        return render(request, 'home.html', context)



class Signup(CreateView):
    template_name = 'signup.html'
    model = Users
    form_class = SignupForm
    success_url = reverse_lazy('check_email')

    def form_valid(self, form):
        to_return = super().form_valid(form)
        user = form.save()
        user.is_active = False  # Turns the user status to inactive
        user.save()
        form.send_activation_email(self.request, user)
        return to_return


class CheckEmailView(TemplateView):
    template_name = 'check_email.html'


class ActivateView(RedirectView):
    url = reverse_lazy('success')

    # Custom get method
    def get(self, request, uidb64, token):

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
            print(user)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None

        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            profile_info= Profile.objects.create(user=user)
            profile_img = UserImages.objects.create(user=user)
            profile_social_link = UserSocialLinks.objects.create(user=user)

            profile_info.save()
            profile_img.save()
            profile_social_link.save()

            login(request, user)
            return super().get(request, uidb64, token)
        else:
            return render(request, 'activate_account_invalid.html')


class SuccessView(TemplateView):
    template_name = 'success.html'
    # form_class = LoginForm


class SigninView(FormView):
    template_name = 'signin.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            if user is not None:

                if user.is_active:
                    login(request, user)

                    return redirect('/')
                else:
                    return render(request, self.template_name, {'form': form,'errmsg1':'Inactive Account.Check Your Email and activate using the link'})


            else:
                return render(request, self.template_name, {'form': form,'errmsg1': 'Invalid Credentials'})
        else:
            for error in list(form.errors.values()):
             messages.error(request, error)
             return render(request, self.template_name, {'form': form, 'errmsg': 'Invalid Credentials'})


@login_required(login_url='signin')
def signout(request):
    logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def view_userprofile(request,*args,**kwargs):
    qry_st = Profile.objects.get(user=request.user)

    if request.method == 'GET':

        basic_info_form= UserprofileForm(instance=qry_st, initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': request.user.phone,
                'username': request.user,

            })
        return render(request, 'user_profile.html', {'form': basic_info_form})
    else:
        basic_info_form = UserprofileForm(instance=qry_st, data=request.POST)
        if basic_info_form.is_valid():
            fname = basic_info_form.cleaned_data.pop('first_name')
            lname = basic_info_form.cleaned_data.pop('last_name')
            email = basic_info_form.cleaned_data.pop('email')
            phone = basic_info_form.cleaned_data.pop('phone')
            uname = basic_info_form.cleaned_data.pop('username')
            basic_info_form.save()
            logged_user = Users.objects.get(id=request.user.id)
            logged_user.first_name = fname
            logged_user.last_name = lname
            logged_user.email = email
            logged_user.phone = phone
            logged_user.username = uname
            logged_user.save()
            return redirect('user-profile')

        else:
            return render(request, 'user_profile.html', {'form': basic_info_form})



@login_required(login_url='signin')
def updateproimage(request):
    profile=UserImages.objects.get(user_id=request.user.id)
    if request.method == "POST":


         if request.FILES.get('files') != None:

            photograph=request.FILES.get('files')
            profile.user_img= photograph
            profile.save()
    return redirect('user-profile')

@login_required(login_url='signin')
def deleteproimg(request,**kwargs):
    profileobj = UserImages.objects.get(user_id=request.user.id)
    profileobj.user_img.delete()
    return redirect('user-profile')


@login_required(login_url='signin')
def usersocial_profile(request):

    profileobj = UserSocialLinks.objects.get(user_id=request.user.id)
    if request.method == "POST":
        profileobj.insta_link= request.POST.get('insta_link')
        profileobj.fb_link = request.POST.get('fb_link')
        profileobj.youtube_link = request.POST.get('youtube_link')
        profileobj.git_link = request.POST.get('git_link')
        profileobj.save()

        return redirect('user-profile')



class ChangePassword(TemplateView):
    template_name = 'change-pasword.html'

    def post(self, request, *args, **kwargs):
        # ErrorF = {'error': False, "msg": ""}
        if request.method == "POST":
            curr_pwd = request.POST.get('CurrentPassword', None)
            new_pwd = request.POST.get('NewPassword', None)
            conf_new_pwd = request.POST.get('ConfrimNewPassword',None)
            user = authenticate(request, username=request.user, password=curr_pwd)
            if user:
                if new_pwd==conf_new_pwd:
                    user=Users.objects.get(username=request.user)
                    user.set_password(new_pwd)
                    user.save()
                    update_session_auth_hash(request,user)

                    response = {'error': False, 'msg': "Password changed successfully"}
                    return JsonResponse(response)
                else:
                    response = {'error': True, 'msg': "New Password missmatch"}

                    return JsonResponse(response)
            else:
                response = {'curr_pwd_errr':True, 'msg': "Incorrect current Password"}
                return JsonResponse(response)

@login_required
def like_unlike_post(request):

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        # profile = Users.objects.get(id=request.user.id)

        if request.user in post_obj.liked.all():
            post_obj.liked.remove(request.user.id)

        else:
            post_obj.liked.add(request.user.id)

        like, created = Like.objects.get_or_create(user_id=request.user.id, post_id=post_id)

        if not created:
            if like.value=='Like':
                like.value='Unlike'
                like.save()
            else:
                like.value='Like'
                like.save()
        else:
            like.value='Like'
            like.save()

            post_obj.save()

            data = {
                'value': like.value,
                'likes': post_obj.liked.all().count()
            }

            return JsonResponse(data, safe=False)
        return redirect('userhome')

class Forgot_Password(FormView):
    form_class = Password_ResetForm
    template_name = 'forgotpassword.html'

    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user = Users.objects.filter(Q(email=user_email)).first()
            if user:
                 self.form_class.send_confirm_email(self.request, user)


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('homepage')

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "You must pass the reCAPTCHA test")
                continue

    form = PasswordResetForm()
    return render(
        request=request,
        template_name="password_reset.html",
        context={"form": form}
        )

class UserProfiles(DetailView):
    model = Users
    template_name = 'userprofiles.html'
    context_object_name = 'user_detail'
    pk_url_kwarg = 'userid'

    def get_queryset(self):
        uid = self.kwargs.get('userid')
        return Profile.objects.filter(user_id=uid)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        uimg= UserImages.objects.get(user_id=self.kwargs.get('userid'))

        user_posts = []
        if self.kwargs.get('userid')==self.request.user.id:
            user_posts = Post.objects.filter(user_id=self.kwargs.get('userid')).order_by('-created_at')

        social_links= UserSocialLinks.objects.get(user_id=self.kwargs.get('userid'))

        if FollowersCount.objects.filter(user=self.kwargs.get('userid'), follower=self.request.user, status='accepted'):
            f_button_value='Following'
            user_posts = Post.objects.filter(user_id=self.kwargs.get('userid')).order_by('-created_at')

        elif FollowersCount.objects.filter(user=self.kwargs.get('userid'), follower=self.request.user, status='pending'):
            f_button_value = 'Requested'

        # elif FollowersCount.objects.filter(follower=self.kwargs.get('userid'), user=self.request.user,status='pending'):
        #     f_button_value = 'Accept Request'

        elif FollowersCount.objects.filter(user=self.request.user, follower=self.kwargs.get('userid'), status='accepted'):
            f_button_value = 'FollowBack'

        else:
            f_button_value = 'Follow'
        followers_count= len(FollowersCount.objects.filter(user=self.kwargs.get('userid'), status='accepted'))
        following_count= len(FollowersCount.objects.filter(follower=self.kwargs.get('userid'),status='accepted'))
        user_posts_count = Post.objects.filter(user_id=self.kwargs.get('userid'))

        data['userimg'] = uimg
        data['user_posts']=user_posts
        data['followers_count']= followers_count
        data['following_count'] = following_count
        data['f_button_value']=f_button_value
        data['user_social_links']= social_links
        data['user_posts_count']=len(user_posts_count)
        return data


class FollowUnfollow(View):

    def post(self, request, *args, **kwargs):
        uid= self.request.POST.get('userid')
        user_obj=Users.objects.get(id=uid)



        follower_obj=Users.objects.get(id=self.request.user.id)

        if FollowersCount.objects.filter(user=user_obj, follower=follower_obj).first():
            del_follow_unfollow_obj= FollowersCount.objects.get(user=user_obj,follower=follower_obj)
            del_follow_unfollow_obj.delete()


            return redirect('usersprofileview', pk=user_obj, userid=uid)
        else:
            FollowersCount.objects.create(user=user_obj, follower= follower_obj,status='pending')

            return redirect('usersprofileview', pk=user_obj, userid=uid)


@login_required
def buddy_request_manage(request):
    if request.method=="POST":
        folowerid= request.POST.get('followers_id')

        btn_status=request.POST.get('btn_status')
        # print(btn_status)
        # print(folowerid)

        allfollower_data=FollowersCount.objects.filter(user_id=request.user.id, follower_id=folowerid)
        for alldata in allfollower_data:

            if alldata.status=='pending':

                if btn_status=='Accept':
                    alldata.status='accepted'
                    alldata.save()

            if alldata.status=='accepted':
                if btn_status == 'UndoAccept':
                    alldata.status = 'pending'
                    alldata.save()
            data = {
                'value': btn_status

                }

            return JsonResponse(data, safe=False)
        return redirect('userhome')












