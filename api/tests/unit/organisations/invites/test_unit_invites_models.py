import typing
from datetime import timedelta
from unittest import TestCase

import pytest
from django.db.utils import IntegrityError
from django.utils import timezone

from organisations.invites.exceptions import InviteLinksDisabledError
from organisations.invites.models import Invite, InviteLink
from organisations.models import Organisation

if typing.TYPE_CHECKING:
    from django.core.mail import EmailMessage
    from pytest_django.fixtures import SettingsWrapper


@pytest.mark.django_db
class InviteLinkTestCase(TestCase):
    def setUp(self) -> None:
        self.organisation = Organisation.objects.create(name="Test organisation")

    def test_is_expired_expiry_date_in_past(self):
        # Given
        yesterday = timezone.now() - timedelta(days=1)
        expired_link = InviteLink.objects.create(
            organisation=self.organisation, expires_at=yesterday
        )

        # When
        is_expired = expired_link.is_expired

        # Then
        assert is_expired

    def test_is_expired_expiry_date_in_future(self):
        # Given
        tomorrow = timezone.now() + timedelta(days=1)
        expired_link = InviteLink.objects.create(
            organisation=self.organisation, expires_at=tomorrow
        )

        # When
        is_expired = expired_link.is_expired

        # Then
        assert not is_expired

    def test_is_expired_no_expiry_date(self):
        # Given
        expired_link = InviteLink.objects.create(
            organisation=self.organisation, expires_at=None
        )

        # When
        is_expired = expired_link.is_expired

        # Then
        assert not is_expired


@pytest.mark.django_db
def test_cannot_create_invite_link_if_disabled(settings: "SettingsWrapper") -> None:
    # Given
    settings.DISABLE_INVITE_LINKS = True

    # When & Then
    with pytest.raises(InviteLinksDisabledError):
        InviteLink.objects.create()


@pytest.mark.django_db
def test_save_invalid_invite__dont_send(mailoutbox: "list[EmailMessage]") -> None:
    # Given
    email = "unknown@test.com"
    organisation = Organisation.objects.create(name="ssg")
    invite = Invite(email=email, organisation=organisation)
    invite.save()
    invalid_invite = Invite(email=email, organisation=organisation)

    # When
    with pytest.raises(IntegrityError):
        invalid_invite.save()

    # Then
    assert len(mailoutbox) == 1
