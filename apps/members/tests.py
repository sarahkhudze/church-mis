from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.members.models import Member


class MemberStatusTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username='adminuser',
            password='Test1234!',
            role='admin',
            status='approved',
            email='admin@example.com',
        )
        self.active_member = Member.objects.create(
            first_name='Active',
            last_name='Member',
            date_of_birth='1990-01-01',
            gender='M',
            phone_number='1111111111',
            email='active@example.com',
            residential_address='123 Active Road',
            member_status=Member.ACTIVE,
        )
        self.left_member = Member.objects.create(
            first_name='Left',
            last_name='Member',
            date_of_birth='1985-01-01',
            gender='F',
            phone_number='2222222222',
            email='left@example.com',
            residential_address='123 Left Road',
            member_status=Member.LEFT,
        )
        self.deceased_member = Member.objects.create(
            first_name='Deceased',
            last_name='Member',
            date_of_birth='1975-01-01',
            gender='M',
            phone_number='3333333333',
            email='deceased@example.com',
            residential_address='123 Deceased Road',
            member_status=Member.DECEASED,
        )

    def test_active_queryset_only_returns_active_members(self):
        active_members = Member.objects.active()

        self.assertEqual(active_members.count(), 1)
        self.assertTrue(all(member.member_status == Member.ACTIVE for member in active_members))
        self.assertIn(self.active_member, active_members)

    def test_inactive_queryset_returns_left_and_deceased_members(self):
        inactive_members = Member.objects.inactive()

        self.assertEqual(inactive_members.count(), 2)
        self.assertCountEqual(
            [member.member_status for member in inactive_members],
            [Member.LEFT, Member.DECEASED],
        )

    def test_admin_can_toggle_inactive_members_in_list_view(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('members:member_list'), {'show_inactive': 'on'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.left_member, response.context['members'])
        self.assertIn(self.deceased_member, response.context['members'])
        self.assertIn(self.active_member, response.context['members'])
