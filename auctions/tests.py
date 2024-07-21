"""Contains app's tests."""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import User, Auction, AuctionImage, AuctionVideo
from .views import CreateListingForm
import os
from django.contrib.auth import get_user_model
from . import fileUtils
from commerce.settings import MEDIA_ROOT

####################################################################################################
# SmokeTests
####################################################################################################
class SmokeTests(TestCase):
    """
    Test if pages are accessible and responding to basic requests.
    """
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a test auction
        self.auction = Auction.objects.create(
            seller=self.user,
            title='Test Auction',
            description='This is a test auction',
            category='OTH'
        )
        
        # Create a test client
        self.client = Client()


    def test_index_page(self):
        response = self.client.get(reverse('auctions:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/index.html')

    def test_login_page(self):
        response = self.client.get(reverse('auctions:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_user_panel_page(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('auctions:user_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/user_panel.html')

    def test_watchlist_page(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('auctions:watchlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/watchlist.html')

    def test_register_page(self):
        response = self.client.get(reverse('auctions:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/register.html')

    def test_create_listing_page(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('auctions:create_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/create_listing.html')

    def test_edit_listing_page(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('auctions:edit_auction', args=[self.auction.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/edit_listing.html')

    def test_listing_page(self):
        response = self.client.get(reverse('auctions:listing_page', args=[self.auction.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing_page.html')

    def test_categories_page(self):
        response = self.client.get(reverse('auctions:categories', args=['AI']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/category.html')


####################################################################################################
# CreateListingTests
####################################################################################################

class CreateListingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.url = reverse('auctions:create_listing')
        self.media_base_path = MEDIA_ROOT

    def tearDown(self):
        fileUtils.del_testing_imgsVids(self.media_base_path)

    def test_create_listing_page_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/create_listing.html')
        self.assertIsInstance(response.context['form'], CreateListingForm)

    def test_create_listing_POST_invalid_data(self):
        data = {
            'title': '',  # Title is required
            'description': 'This is a test auction',
            'category': 'OTH',
        }
        
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, 200)  # Should return to the same page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('title', response.context['form'].errors)
        self.assertEqual(response.context['form'].errors['title'][0], 'This field is required.')
        self.assertEqual(Auction.objects.count(), 0)

    def test_create_listing_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('auctions:login')}?next={self.url}")

    def test_create_listing_with_invalid_image_format(self):
        invalid_image = SimpleUploadedFile("testDel.txt", b"invalid_content", content_type="text/plain")
        
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': 'OTH',
            'image_url': 'http://example.com/image.jpg',
            'images': [invalid_image],
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 200)  # Should return to the same page
        errors = response.context['form'].errors['images']

        self.assertIsNotNone(errors)

    def test_create_listing_with_invalid_video_format(self):
        invalid_video = SimpleUploadedFile("testDel.txt", b"invalid_content", content_type="text/plain")
        
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': 'OTH',
            'image_url': 'http://example.com/image.jpg',
            'videos': [invalid_video],
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 200)  # Should return to the same page
        errors = response.context['form'].errors['videos']
        self.assertIsNotNone(errors)

    def test_create_listing_max_file_size_image(self):
        large_image = SimpleUploadedFile("testDel_large.jpg", b"0" * 1024 * 1024 * 11, content_type="image/jpeg")  # 11MB file
        
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': 'OTH',
            'image_url': 'http://example.com/image.jpg',
            'images': [large_image],
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 200)  # Should return to the same page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('images', response.context['form'].errors)
        self.assertIn('The maximum file size that can be uploaded is 10MB', response.context['form'].errors['images'][0])

    def test_create_listing_max_file_size_video(self):
        large_video = SimpleUploadedFile("testDel_large.mp4", b"0" * 1024 * 1024 * 11, content_type="video/mp4")  # 11MB file
        
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': 'OTH',
            'image_url': 'http://example.com/image.jpg',
            'videos': [large_video],
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, 200)  # Should return to the same page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('videos', response.context['form'].errors)
        self.assertIn('The maximum file size that can be uploaded is 10MB', response.context['form'].errors['videos'][0])

####################################################################################################
# EditListingTests
####################################################################################################
class EditListingTestCase(TestCase):
    """
    Tests for the edit_auction view/functionality.
    """
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='testpass123'
        )
        self.auction = Auction.objects.create(
            seller=self.user,
            title='Test Auction',
            description='This is a test auction',
            category=Auction.WEB_DEV,
            image_url='http://example.com/image.jpg'
        )
        self.edit_url = reverse('auctions:edit_auction', kwargs={'auction_id': self.auction.id})
        self.media_base_path = MEDIA_ROOT

    def tearDown(self):
        fileUtils.del_testing_imgsVids(self.media_base_path)

    def test_edit_auction_successful(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'Updated Test Auction',
            'description': 'This is an updated test auction',
            'category': Auction.AI,
            'image_url': 'http://example.com/new_image.jpg',
            'supporting_link': 'http://example.com/support',
            'supporting_link_description': 'Support link'
        }
        response = self.client.post(self.edit_url, data)
        self.assertRedirects(response, reverse('auctions:listing_page', kwargs={'auction_id': self.auction.id}))
        
        # Refresh the auction from the database
        self.auction.refresh_from_db()
        self.assertEqual(self.auction.title, 'Updated Test Auction')
        self.assertEqual(self.auction.category, Auction.AI)

    def test_edit_auction_add_image(self):
        self.client.login(username='testuser', password='testpass123')
        image = SimpleUploadedFile("testDel_image.jpg", b"file_content", content_type="image/jpeg")
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': Auction.WEB_DEV,
            'image_url': 'http://example.com/image.jpg',
            'images': [image]
        }
        response = self.client.post(self.edit_url, data, format='multipart')
        self.assertRedirects(response, reverse('auctions:listing_page', kwargs={'auction_id': self.auction.id}))
        self.assertEqual(self.auction.images.count(), 1)

    def test_edit_auction_delete_image(self):
        self.client.login(username='testuser', password='testpass123')
        # First, add an image
        image = AuctionImage.objects.create(image='path/to/image.jpg')
        self.auction.images.add(image)
        
        # Now, delete the image
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': Auction.WEB_DEV,
            'image_url': 'http://example.com/image.jpg',
            'delete_images': [image.id]
        }
        response = self.client.post(self.edit_url, data)
        self.assertRedirects(response, reverse('auctions:listing_page', kwargs={'auction_id': self.auction.id}))
        self.assertEqual(self.auction.images.count(), 0)

    def test_edit_auction_add_video(self):
        self.client.login(username='testuser', password='testpass123')
        video = SimpleUploadedFile("testDel_video.mp4", b"file_content", content_type="video/mp4")
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': Auction.WEB_DEV,
            'image_url': 'http://example.com/image.jpg',
            'videos': [video]
        }
        response = self.client.post(self.edit_url, data, format='multipart')
        self.assertRedirects(response, reverse('auctions:listing_page', kwargs={'auction_id': self.auction.id}))
        self.assertEqual(self.auction.videos.count(), 1)

    def test_edit_auction_delete_video(self):
        self.client.login(username='testuser', password='testpass123')
        # First, add a video
        video = AuctionVideo.objects.create(video='path/to/video.mp4')
        self.auction.videos.add(video)
        
        # Now, delete the video
        data = {
            'title': 'Test Auction',
            'description': 'This is a test auction',
            'category': Auction.WEB_DEV,
            'image_url': 'http://example.com/image.jpg',
            'delete_videos': [video.id]
        }
        response = self.client.post(self.edit_url, data)
        self.assertRedirects(response, reverse('auctions:listing_page', kwargs={'auction_id': self.auction.id}))
        self.assertEqual(self.auction.videos.count(), 0)

####################################################################################################
# 
####################################################################################################