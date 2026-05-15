from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import Author, Blog, Subscriber
from io import BytesIO
from PIL import Image


class BaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.author, _ = Author.objects.get_or_create(
            user=self.user,
            defaults={
                'first_name': 'Test',
                'last_name': 'Author',
                'email': self.user.email,
            }
        )

    def create_test_image(self):
        img = BytesIO()
        image = Image.new('RGB', (100, 100), 'white')
        image.save(img, 'PNG')
        img.name = 'test.png'
        img.seek(0)
        return img

    def create_blog(self):
        return Blog.objects.create(
            title='Test Blog',
            author=self.author,
            content='Test content for the blog post.'
        )


class IndexViewTest(BaseTest):
    def test_index_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_index_guest_name(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Guest')

    def test_index_authenticated_name(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'testuser')


class AboutContactTest(BaseTest):
    def test_about_200(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_contact_200(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)


class BlogListDetailTest(BaseTest):
    def test_blog_list_empty(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_list.html')

    def test_blog_list_with_blogs(self):
        self.create_blog()
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_404(self):
        response = self.client.get(reverse('blog_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_200(self):
        blog = self.create_blog()
        response = self.client.get(reverse('blog_detail', args=[blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)


class SubscribeTest(BaseTest):
    def test_subscribe_page_200(self):
        response = self.client.get(reverse('subscribe'))
        self.assertEqual(response.status_code, 200)

    def test_subscribe_post_success(self):
        response = self.client.post(reverse('subscribe'), {'email': 'new@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Subscriber.objects.filter(email='new@example.com').exists())

    def test_subscribe_post_duplicate(self):
        Subscriber.objects.create(email='dup@example.com')
        response = self.client.post(reverse('subscribe'), {'email': 'dup@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subscriber.objects.filter(email='dup@example.com').count(), 1)

    def test_subscribe_post_empty(self):
        response = self.client.post(reverse('subscribe'), {'email': ''})
        self.assertEqual(response.status_code, 302)


class AddBlogTest(BaseTest):
    def test_add_blog_redirects_anonymous(self):
        response = self.client.get(reverse('add_blog'))
        self.assertEqual(response.status_code, 302)

    def test_add_blog_200_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('add_blog'))
        self.assertEqual(response.status_code, 200)

    def test_add_blog_post(self):
        self.client.login(username='testuser', password='testpass123')
        img = self.create_test_image()
        response = self.client.post(reverse('add_blog'), {
            'title': 'New Blog',
            'content': 'Blog content',
            'image': img,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Blog.objects.filter(title='New Blog').exists())


class AuthorSignalTest(BaseTest):
    def test_author_created_on_user_creation(self):
        new_user = User.objects.create_user(
            username='newuser', password='newpass123'
        )
        self.assertTrue(Author.objects.filter(user=new_user).exists())

    def test_author_not_duplicated(self):
        self.assertEqual(Author.objects.filter(user=self.user).count(), 1)


class AllauthPageTest(BaseTest):
    def test_login_page_200(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_200(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_page_200(self):
        response = self.client.get(reverse('account_reset_password'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        response = self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_post_fail(self):
        response = self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 302)


class TwoFATest(BaseTest):
    def test_profile_page_redirects_anonymous(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_page_200_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_enable_2fa_page(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('enable_2fa'))
        self.assertEqual(response.status_code, 200)

    def test_enable_2fa_post_invalid_token(self):
        self.client.login(username='testuser', password='testpass123')
        device, _ = TOTPDevice.objects.get_or_create(
            user=self.user, name='default', defaults={'confirmed': False}
        )
        response = self.client.post(reverse('enable_2fa'), {'token': '000000'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TOTPDevice.objects.get(id=device.id).confirmed)

    def test_verify_2fa_redirects_anonymous(self):
        response = self.client.get(reverse('verify_2fa'))
        self.assertEqual(response.status_code, 302)

    def test_verify_2fa_page_200_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('verify_2fa'))
        self.assertEqual(response.status_code, 200)

    def test_verify_2fa_no_devices(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('verify_2fa'), {'token': '123456'})
        self.assertEqual(response.status_code, 302)

    def test_middleware_redirects_to_verify_with_2fa(self):
        self.client.login(username='testuser', password='testpass123')
        device = TOTPDevice.objects.create(
            user=self.user, name='default', confirmed=True
        )
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('verify_2fa'), response.url)


class SocialSignupTemplateTest(BaseTest):
    def test_social_signup_template_exists(self):
        from django.template.loader import get_template
        template = get_template('socialaccount/signup.html')
        self.assertIsNotNone(template)

    def test_social_signup_renders(self):
        response = self.client.get('/accounts/3rdparty/signup/')
        self.assertIn(response.status_code, [200, 302, 403])


class StaticFileTest(BaseTest):
    def test_styles_css_exists(self):
        import os
        from django.conf import settings
        css_path = settings.BASE_DIR / 'static' / 'css' / 'styles.css'
        self.assertTrue(os.path.exists(css_path))

    def test_tailwind_css_exists(self):
        import os
        from django.conf import settings
        css_path = settings.BASE_DIR / 'static' / 'css' / 'tailwind.css'
        self.assertTrue(os.path.exists(css_path))
