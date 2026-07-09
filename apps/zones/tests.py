from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser


class ZoneRoutesTest(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            username='zone-admin',
            password='testpass123',
            role='admin',
            status='approved',
            is_active_user=True,
        )

    def test_zone_management_urls_are_available(self):
        self.assertEqual(reverse('zones:zone_list'), '/zones/')
        self.assertEqual(reverse('zones:zone_create'), '/zones/create/')
        self.assertEqual(reverse('zones:zone_detail', kwargs={'pk': 1}), '/zones/1/')
        self.assertEqual(reverse('zones:zone_edit', kwargs={'pk': 1}), '/zones/1/edit/')
        self.assertEqual(reverse('zones:zone_delete', kwargs={'pk': 1}), '/zones/1/delete/')

    def test_zone_create_page_renders_form_for_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('zones:zone_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Zone')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="description"')
