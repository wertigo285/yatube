from tempfile import NamedTemporaryFile
from uuid import uuid1

from django.test import TestCase, Client
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from PIL import Image
from sorl.thumbnail import delete

from .models import Post, User, Group, Follow


class Test(TestCase):
    def create_user_post(self):
        author = User.objects.create_user(
            username=str(uuid1()), email='test@example.com', password='test_password')
        post = Post.objects.create(text=str(uuid1()), author=author)
        return post

    def create_temp_image_file(self):
        image_file = NamedTemporaryFile(
            suffix='.jpg', dir=settings.MEDIA_ROOT, delete=False)

        image_data = Image.new('RGB', (1, 1), (0, 0, 0))
        image_data.save(image_file, 'JPEG')

        return image_file

    def create_temp_text_file(self):
        text_file = NamedTemporaryFile(
            suffix='.txt', dir=settings.MEDIA_ROOT, delete=False)

        text_file.write('test'.encode())
        text_file.seek(0)

        return text_file

    def check_image_error(self, response, msg):
        image_errors = response.context['form']['image'].errors
        self.assertEqual(image_errors and image_errors.data[0].code, 'invalid_image',
                         msg=msg)

    def post_image_check(self, response, post, page_definition):
        if post.image:
            self.assertContains(response, '<img', count=1,
                                msg_prefix='На {page_definition} не отображается изображения записи.')
        else:
            self.assertNotContains(response, '<img',
                                   msg_prefix='На {page_definition} отображается тег <img> у записи без изображения.')

    def post_check(self, post):
        cache.clear()
        response = self.client.get('/')
        self.assertContains(response, post.text, count=1,
                            msg_prefix='Текст сообщения на главной странице несоответствует ожидаемому.')
        self.post_image_check(response, post, 'главной странице')

        response = self.client.get(f'/{self.user.username}/{post.id}/')
        self.assertContains(response, post.text, count=1,
                            msg_prefix='Текст сообщение несоответствует ожидаемому.')
        self.post_image_check(response, post, 'странице записи')

        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, post.text, count=1,
                            msg_prefix='Текст сообщения в профиле пользователя несоответствует ожидаемому.')
        self.post_image_check(response, post, 'странице профиля пользователя')

    def post_follow_check(self, post, follow=False):
        cache.clear()
        response = self.client.get('/follow/')
        if follow:
            self.assertContains(response, post.text, msg_prefix='На странице ленты подписок не отображается пост подписанного автора')
        else:
            self.assertNotContains(response, post.text, msg_prefix='На странице ленты подписок отображается пост подписанного автора')

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user', email='test@example.com', password='test_password')

    def test_profile(self):
        self.client.force_login(self.user)
        response = self.client.get('/test_user/')
        self.assertEqual(response.status_code, 200,
                         msg='Недоступна страница нового пользователя.')
        self.assertIsInstance(response.context['profile'], User,
                              msg='На страницу профиля не передан пользователь.')
        self.assertEqual(response.context['profile'].username, self.user.username,
                         msg='На странице профиля отображен некорректный пользователь.')

    def test_authorized_new_post(self):
        self.client.force_login(self.user)

        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200,
                         msg='Авторизованному пользователю недоступна страница нового сообщения.')

        test_text = str(uuid1())
        response = self.client.post('/new/', {'text': test_text})
        self.assertTrue(Post.objects.filter(text=test_text, author=self.user).exists(),
                        msg='Созданное авторизованным пользователем сообщение не добавленно а базу данных')
        self.assertRedirects(response, '/',
                             msg_prefix='Авторизованному пользователю недоступно создание нового сообщения.')

    def test_unauthorized_new_post(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             msg_prefix='Неавторизованному пользователю доступна страница нового сообщения.')

        response = self.client.post('/new/', {'text': 'test'})
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             msg_prefix='Неавторизованному пользователю доступно создание нового сообщения.')

    def test_new_post_without_image(self):
        self.client.force_login(self.user)
        new_post = Post.objects.create(text=str(uuid1()), author=self.user)
        self.post_check(new_post)

    def test_edit_post_without_image(self):
        self.client.force_login(self.user)

        new_post = Post.objects.create(text=str(uuid1()), author=self.user)

        response = self.client.get(
            f'/{self.user.username}/{new_post.id}/edit/')
        self.assertEqual(response.status_code, 200,
                         msg='Авторизованному пользователю недоступна страница редактирования своего сообщения.')

        response = self.client.post(
            f'/{self.user.username}/{new_post.id}/edit/', {'text': str(uuid1())})
        self.assertRedirects(response, f'/{self.user.username}/{new_post.id}/',
                             msg_prefix='Авторизованному пользователю недоступно редактирование своего сообщения.')

        post = Post.objects.get(id=new_post.id)
        self.post_check(post)

    def test_new_post_with_image(self):
        self.client.force_login(self.user)
        with self.create_temp_text_file() as text_file:
            response = self.client.post(
                '/new/', {'text': 'test', 'image': text_file})

            self.check_image_error(
                response, 'При отправке нового сообщения не работает проверка формата изображения.')
        text_file.close()
        delete(text_file)

        with self.create_temp_image_file() as image_file:
            new_post = Post.objects.create(
                text=str(uuid1()), author=self.user, image=image_file.name)

            self.post_check(new_post)
        image_file.close()
        delete(image_file)

    def test_edit_post_with_image(self):
        self.client.force_login(self.user)
        new_post = Post.objects.create(text=str(uuid1()), author=self.user)
        with self.create_temp_text_file() as text_file:
            response = self.client.post(
                f'/{self.user.username}/{new_post.id}/edit/', {'text': str(uuid1()), 'image': text_file})
            self.check_image_error(
                response, 'При редактировании сообщения не работает проверка формата изображения.')
        text_file.close()
        delete(text_file)

    def test_404_if_not_found(self):
        self.client.force_login(self.user)
        response = self.client.get('/empty_user/')
        self.assertEqual(response.status_code, 404,
                         msg='При запросе несуществующей страницы код ответа отличен от 404')

    def test_cache(self):
        self.client.force_login(self.user)

        response = self.client.get('/')

        test_text = str(uuid1())

        response = self.client.get('/')
        self.assertNotContains(
            response, test_text, msg_prefix='На главной странице не работает кэширование')

        key = make_template_fragment_key('index_page', [1])
        cache.delete(key)

        response = self.client.get('/')
        self.assertContains(
            response, test_text, msg_prefix='На главной странице не появился новый пост после очистки кэша')

    def test_follow(self):
        post = self.create_user_post()

        response = self.client.get('/follow/')
        self.assertRedirects(response, '/auth/login/?next=/follow/',
                             msg_prefix='Неавторизованному пользователю доступна страница ленты подписки')

        self.client.force_login(self.user)
        self.post_follow_check(post, False)

        self.client.get(f'/{post.author.username}/follow/')
        self.post_follow_check(post, True)

        self.client.get(f'/{post.author.username}/unfollow/')
        self.post_follow_check(post, False)

    def test_comment(self):
        post = self.create_user_post()

        comment_text = str(uuid1())
        response = self.client.post(f'/{post.author.username}/{post.id}/comment/', {'text': comment_text})
        self.assertRedirects(response, f'/auth/login/?next=/{post.author.username}/{post.id}/comment/', msg_prefix='Отправка комментариев доступна неавторизованному пользователю')

        self.client.force_login(self.user)
        self.client.post(f'/{post.author.username}/{post.id}/comment/', {'text': comment_text})
        response = self.client.get(f'/{post.author.username}/{post.id}/')
        self.assertContains(response, comment_text, msg_prefix='Отправленный авторизованным пользователем комментарий не отображается на странице просмотра записи')
